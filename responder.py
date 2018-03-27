import abc
from utils import LogMixin


class Reponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def redis(self):
        """ redis connection """
        return

    @abc.abstractmethod
    def fetch(self, ids):
        """ hydrate relevant ids with data """
        return


class Movies(Reponse, LogMixin):
    DEFAULT_FIELDS = ['title', 'year', 'genres']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def fetch(self, movies, fields=None, from_index=False):
        """ hydrates class ids with metadata, return redis pipeline that must be executed """
        if fields is None:
            fields = Movies.DEFAULT_FIELDS

        if from_index:
            movies = self.redis.mget(('inverse:index:movie:{}'.format(idx) for idx in movies))

        response = []
        for movie in movies:
            values = self.redis.hmget('movie:{}'.format(movie), fields)
            obj = dict(zip(fields, values))
            if 'genres' in obj:
                obj['genres'] = obj['genres'].split(',')
            if 'year' in obj:
                obj['year'] = int(obj['year'])
            response.append(obj)
        return response

    def movie_to_index(self, movies):
        return self.redis.mget(('index:movie:{}'.format(m) for m in movies))
