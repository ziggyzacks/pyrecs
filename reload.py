from datasets import MovieMetaData, RatingsData
from models import IMF

# meta
meta = MovieMetaData.load()
meta.toredis()
# model
imf = IMF.fromds(RatingsData.load())
imf.fit()
imf.toredis()
imf.tos3()
