import redis

REDIS_SERVER = redis.StrictRedis(host='localhost', port=6379, db=0)
