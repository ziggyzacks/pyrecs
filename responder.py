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

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def fetch(self, movies, pipe=None, from_index=False):
        """ hydrates class ids with metadata, return redis pipeline that must be executed """
        if from_index:
            movies = self.redis.mget(('inverse:index:movie:{}'.format(idx) for idx in movies))

        if pipe is None:
            pipe = self.redis.pipeline()

        for movie in movies:
            pipe.hgetall('movie:{}'.format(movie))

        return pipe

    def movie_to_index(self, movies):
        return self.redis.mget(('index:movie:{}'.format(m) for m in movies))