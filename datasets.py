import pandas as pd
import numpy as np
import os
import abc
import pathlib
from redis import StrictRedis
from utils import LogMixin, timeit, dftocoo, Redis

S3BASEPATH = 's3://pyrecs-io/input-data'
LOCALBASEPATH = '/'.join((os.path.dirname(os.path.abspath(__file__)), 'data'))


class Dataset(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractclassmethod
    def load(self):
        """ load data """
        return

    @abc.abstractmethod
    def toredis(self):
        """ write records to redis """
        return


class MovieMetaData(Dataset, LogMixin):
    FILES = ['movies.csv']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def todisk(cls, data, path):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return data.to_csv(path, index=False)

    @classmethod
    def __cleanup(cls, data):
        # extract the years
        years = data.title.str.strip().str.slice(-5, -1)
        data['year'] = pd.to_numeric(years, errors='coerce')
        # remove years from titles where the casting succeeded
        data['title'] = data.apply(lambda row: row.title[:-6].strip() if not np.isnan(row.year) else row.title,
                                   axis=1)
        # remove any whitespace still hanging around
        data['title'] = data['title'].str.strip()
        # don't like the pipe delimiters to switching em out for commas
        data['genres'] = data['genres'].str.replace('|', ',')
        return data

    @classmethod
    @timeit
    def load(cls, persist=True):
        attrs = {}
        s3paths = ['/'.join((S3BASEPATH, fp)) for fp in cls.FILES]
        localpaths = ['/'.join((LOCALBASEPATH, fp)) for fp in cls.FILES]

        if all(os.path.exists(p) for p in localpaths):
            paths = localpaths
            ondisk = True
        else:
            paths = s3paths
            ondisk = False

        def __getname(path):
            return os.path.split(path)[1].split('.')[0]

        for i, fp in enumerate(paths):
            attr = __getname(fp)
            tmp_data = pd.read_csv(fp)
            if not ondisk and persist:
                cls.todisk(tmp_data, localpaths[i])
            clean_metadata = cls.__cleanup(data=tmp_data)
            attrs[attr] = clean_metadata
        return cls(**attrs)

    @timeit
    def toredis(self):
        pipe = Redis().redis.pipeline()
        # movie hashes
        # convert year to int with default of all 0s
        self.movies['year'] = self.movies.year.replace(np.NaN, 0000).astype(int)
        for index, movie in enumerate(self.movies.to_dict('records')):
            key = movie['movieId']
            movie.pop('movieId')
            pipe.hmset('movie:{}'.format(key), movie)
            pipe.set('inverse:index:movie:{}'.format(index), key)
            pipe.set('index:movie:{}'.format(key), index)

        s = self.movies.genres.str.split(',').apply(pd.Series, 1).stack()
        s.index = s.index.droplevel(-1)  # to line up with df's index
        s.name = 'genres'  # needs a name to join
        # sets for intersection later (genre, year, ...)
        genres = (self.movies.drop('genres', axis=1).join(s)
                  .groupby('genres')
                  .movieId
                  .apply(set))
        # genres
        for genre, ids in genres.iteritems():
            pipe.sadd('genre:{}'.format(genre), *ids)

        # years
        years = self.movies.groupby('year').movieId.apply(set)
        for year, ids in years.iteritems():
            pipe.sadd('year:{}'.format(year), *ids)

        pipe.execute()


class RatingsData(Dataset, LogMixin):
    FILES = ['ratings.csv']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def todisk(cls, data, path):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return data.to_csv(path, index=False)

    @classmethod
    @timeit
    def load(cls, cutoff=4, persist=True):
        attrs = {}
        s3paths = ['/'.join((S3BASEPATH, fp)) for fp in cls.FILES]
        localpaths = ['/'.join((LOCALBASEPATH, fp)) for fp in cls.FILES]

        if all(os.path.exists(p) for p in localpaths):
            paths = localpaths
            ondisk = True
        else:
            paths = s3paths
            ondisk = False

        def __getname(path):
            return os.path.split(path)[1].split('.')[0]

        for i, fp in enumerate(paths):
            attr = __getname(fp)
            tmp_data = pd.read_csv(fp)
            if not ondisk and persist:
                cls.todisk(tmp_data, localpaths[i])
            tmp_data = tmp_data.loc[tmp_data.rating >= cutoff].reset_index(drop=True)
            attrs[attr] = tmp_data
        return cls(**attrs)

    @property
    def model_input(self):
        return dftocoo(data=self.ratings, metric="rating")

    @timeit
    def toredis(self):
        raise NotImplementedError
