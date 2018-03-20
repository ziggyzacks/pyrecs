import logging
import time
import datetime
import boto3
import json
import os
from redis import StrictRedis
from scipy.sparse import coo_matrix

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Util: pass


class LogMixin(object):

    @property
    def logger(self):
        name = '.'.join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)

class Redis(Util, LogMixin):
    """ redis connection class """
    HOST = '35.196.81.228' if os.environ.get('ENV') is not None else 'localhost'
    PORT = 6379

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self._redis = StrictRedis(host=host, port=port, decode_responses=True)

    @property
    def redis(self):
        return self._redis

class S3Resource(Util, LogMixin):
    """ helper class for dealing with interactions with S3 """
    BUCKET = 'pyrecs-io'
    BATCH_TIME = datetime.datetime.utcnow()

    __fields__ = ['s3', 'time', 'env', 'prefix']

    def __init__(self, bucket=BUCKET, time=BATCH_TIME):
        self.s3 = boto3.resource('s3')
        self.bucket = bucket
        self.time = time
        self.prefix = "data/models"

    @property
    def __keys__(self):
        return self.__fields__

    def get_config(self, key):
        content_object = self.s3.Object(self.bucket, 'config/{}.json'.format(key))
        file_content = content_object.get()['Body'].read().decode('utf-8')
        return json.loads(file_content)

    def _key(self, key, suffix='.pkl', config=None):
        dt = self.time.strftime("%Y-%m-%d-%H:%M:%S")
        if config is not None:
            return os.path.join(self.prefix, config, dt, key) + suffix
        else:
            return os.path.join(self.prefix, dt, key) + suffix

    def _fp(self, key, suffix='.pkl', config=None):
        return os.path.join(self.bucket, self._key(key, suffix=suffix, config=config))

    def put(self, key, value, config=None):
        self.logger.info('Saving to: {}'.format(self._fp(key, config=config)))
        return self.s3.Bucket(self.bucket).put_object(Key=self._key(key, config=config), Body=value)

    def upload(self, key, filename, config=None):
        self.logger.info('Saving to: {}'.format(self._fp(key, suffix='.bin', config=config)))
        return self.s3.Bucket(self.bucket).upload_file(Key=self._key(key, suffix='.bin', config=config),
                                                       Filename=filename)


def timeit(method):
    log = logging.getLogger('timer')

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            log.info('{} - {}s'.format(method.__name__, round(te - ts, 5)))
        return result

    return timed


def dftocoo(data, metric):
    """ converts a pandas dataframe into a scipy coomatrix """
    data['userId'] = data['userId'].astype('category')
    data['movieId'] = data['movieId'].astype('category')

    rows = data.movieId.cat.codes
    cols = data.userId.cat.codes

    user_lookup = dict(zip(data.userId.cat.categories, set(data.userId.cat.codes)))
    movie_lookup = dict(zip(data.movieId.cat.categories, set(data.movieId.cat.codes)))

    i = max(rows) + 1
    j = max(cols) + 1

    matrix = coo_matrix((data[metric], (rows, cols)), shape=(i, j))
    return matrix, user_lookup, movie_lookup


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
