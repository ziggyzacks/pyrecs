import os
import abc
import hashlib
from implicit.approximate_als import NMSLibAlternatingLeastSquares
from utils import LogMixin, timeit, S3Resource, Redis
import time

s3 = S3Resource()


class Model(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def upload(self, key, filename, config):
        return s3.upload(key=key, filename=key, config=config)

    @abc.abstractclassmethod
    def fit(self):
        """ load data """
        return

    @abc.abstractmethod
    def tos3(self):
        """ save pickled model to s3 """
        return

    @abc.abstractmethod
    def toredis(self):
        """ save (fit) model data to redis """
        return


class IMF(Model, LogMixin):
    __all__ = ['similar_items_index', 'recommend_index']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def tos3(self):
        for key in self.__all__:
            self.model.__dict__[key].saveIndex(key)
            self.model.__dict__[key] = None
            self.upload(key=key, filename=key, config=self.config)
            os.remove(key)

    @classmethod
    def fromds(cls, ds):
        DEFAULT = {
            'factors': 40,
            'regularization': 0.01,
            'iterations': 10,
        }

        coo, users, movies = ds.model_input
        attrs = {
            'ds': ds,
            'model': NMSLibAlternatingLeastSquares(**DEFAULT),
            'config': hashlib.md5(str(DEFAULT).encode()).hexdigest(),
            '_fit': False,
            'data': coo,
            'user_lookup': users,
            'movie_lookup': movies,
            'redis': Redis().redis
        }
        return cls(**attrs)

    @timeit
    def fit(self):
        self.model.fit(self.data)
        self._fit = True

    @timeit
    def toredis(self):
        if not self._fit:
            raise Exception('must fit model before persisting to redis')

        r = self.redis.pipeline()
        recdata = self.data.T.tocsr()

        t0 = time.time()
        for k, v in self.user_lookup.items():
            r.set('user:{}:{}'.format(self.config, k), v)
            vector_key = 'user:vec:{}:{}'.format(self.config, v)
            # mark old user vector as old
            if r.exists(vector_key):
                r.delete(vector_key)
            # push vector to redis as list
            r.rpush(vector_key, *self.model.user_factors[v].tolist())
            # viewing
            viewed_key = 'user:viewed:{}:{}'.format(self.config, v)
            if r.exists(viewed_key):
                r.delete(viewed_key)
            r.rpush(viewed_key, *recdata[v].indices.tolist())
        self.logger.info('User keys: {}'.format(round(time.time() - t0, 2)))

        for k, v in self.movie_lookup.items():
            r.set('movie:{}:{}'.format(self.config, k), v)
            r.set('movie:idx:{}:{}'.format(self.config, v), k)
            vector_key = 'movie:vec:{}:{}'.format(self.config, v)
            # delete movie vector
            if r.exists(vector_key):
                r.delete(vector_key)
            # push vector to redis as list
            r.rpush(vector_key, *self.model.item_factors[v].tolist())

        self.logger.info('Loading keys into redis..')
        return r.execute()

    def similar(self, ids, n):
        movie_vectors = self.model.item_factors[list(map(int, ids))]
        batch = self.model.similar_items_index.knnQueryBatch(movie_vectors, n + 1, num_threads=4)
        return [neighbors.tolist() for neighbors, _ in batch]
