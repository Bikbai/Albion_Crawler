import redis
from constants import Realm, EntityType

from constants import LOGGER_NAME
import logging
log = logging.getLogger(LOGGER_NAME)

class RedisCache:
    def __init_redis__(self, realm: Realm, cache_type: EntityType):
        log.info("Redis init started")
        MAX_BATCH_SIZE = 100000
        self.__redis_db_number = realm * 10 + cache_type
        pool = redis.ConnectionPool(host='redis.lan', port=6379, db=self.__redis_db_number)
        self.__redis = redis.Redis(connection_pool=pool)
        log.info("Redis init done")

    def __init__(self, realm, cache_type: EntityType):
        self.__init_redis__(realm, cache_type)

    def info(self):
        return f'db: {self.__redis_db_number}'

    def check_value(self, key):
        value = self.__redis.get(key)
        if value is None:
            return False
        else:
            return True

    def put_value(self, key):
        self.__redis.set(name=key, value="")

    def flush(self):
        self.__redis.flushdb()