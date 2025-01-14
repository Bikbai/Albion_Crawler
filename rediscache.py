import redis
from constants import Realm, EntityType

from constants import LOGGER_NAME
import logging
log = logging.getLogger(LOGGER_NAME)

class RedisCache:
    def __init_redis__(self, realm: Realm, cache_type: EntityType):
        log.info("REDIS: init started")
        MAX_BATCH_SIZE = 100000
        self.__redis_db_number = realm * 10 + cache_type
        pool = redis.ConnectionPool(host='redis.lan', port=6379, db=self.__redis_db_number)
        self.__redis = redis.Redis(connection_pool=pool)
        log.info("REDIS: init done")

    def __init__(self, realm, cache_type: EntityType):
        self.__init_redis__(realm, cache_type)
        self.__redis.info()

    def ext_info(self):
        return self.__redis.dbsize()

    def info(self):
        return f'db: {self.__redis_db_number}'

    def check_value(self, key) -> str | None:
        retval = self.__redis.get(key)
        if retval is None:
            return retval
        return retval.decode('UTF-8')

    def reload_from_db(self, query_result: [[str, str]]):
        log.warning(f"REDIS: begin reload cache, DB number: {self.__redis_db_number}")
        self.__redis.flushdb()
        for row in query_result:
            self.__redis.set(name=row[0], value=row[1])
        log.warning(f"REDIS: reload cache done, rows: {len(query_result)}, DB number: {self.__redis_db_number}.")

    def put_value(self, key, value=""):
        self.__redis.set(name=key, value=value)

    def flush(self):
        log.warning(f"REDIS: cache {self.__redis_db_number} was erased!")
        self.__redis.flushdb()