import redis
from .settings import REDIS_URL

redis_url = REDIS_URL
conn = redis.from_url(redis_url)
