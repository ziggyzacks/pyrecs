import logging
from sanic import Sanic, log
from sanic.response import json, redirect
from responder import Movies
from models import IMF
from datasets import RatingsData, MovieMetaData
from utils import chunks, Redis
from sanic_jinja2 import SanicJinja2
from sanic_session import InMemorySessionInterface

# disables existing root logger and allows for sanic's default format w/no duplicates
log.LOGGING_CONFIG_DEFAULTS['loggers']['sanic.access']['propagate'] = False

app = Sanic()
app.static('/static', './static')

jinja = SanicJinja2(app)
session = InMemorySessionInterface(cookie_name=app.name, prefix=app.name)

logger = logging.getLogger('pyrecs')


@app.listener('before_server_start')
async def prepare_metadata(app, loop):
    logger.info('Preparing metadata')
    dataset = MovieMetaData.load()
    dataset.toredis()
    logger.info('Metadata loaded')


@app.listener('before_server_start')
async def prepare_model(app, loop):
    logger.info('Preparing ratings')
    dataset = RatingsData.load(cutoff=4)
    log.logger.info('Loading model from ratings')
    imf = IMF.fromds(dataset)
    logger.info('Fitting model')
    imf.fit()
    # imf.toredis()
    app.model = imf


@app.listener('before_server_start')
async def prepare_db(app, loop):
    app.redis = Redis().redis
    app.movies = Movies(redis=app.redis)


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session.save(request, response)


@app.route("/api/metadata")
async def classmeta(request):
    movies = request.args.getlist('movies')
    pipe = app.movies.fetch(movies)
    return json({'movies': pipe.execute()})


@app.route('/api/similar')
async def similar(request):
    response = {}

    movies = request.args.getlist('movies')
    n = request.args.get('n', 10)

    idxs = app.movies.movie_to_index(movies)
    similar = app.model.similar(idxs, n)

    # use pipeline to minimize network traffic
    pipe = app.redis.pipeline()
    for sims in similar:
        pipe = app.movies.fetch(sims, pipe=pipe, from_index=True)

    # iterate through chunked response building up dict
    for movie, chunk in zip(movies, chunks(pipe.execute(), n + 1)):
        response[movie] = {}
        response[movie]['metadata'] = chunk[0]
        response[movie]['similar'] = chunk[1:]

    return json(response)


@app.route('/')
async def index(request):
    request['session']['user'] = 'pyrecs-test'
    return jinja.render('index.html', request, greetings='🚧🚧🚧🚧🚧🚧🚧🚧')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
