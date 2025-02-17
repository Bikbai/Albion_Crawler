import redis
from constants import Realm, EntityType

from constants import LOGGER_NAME
import logging
log = logging.getLogger(LOGGER_NAME)

class RedisCache:
    entity_db_map = {
        EntityType.guild: 1,
        EntityType.player: 2,
        EntityType.battles: 3,
        EntityType.event: 4,
        EntityType.test:  5,
        EntityType.item: 9
    }

    def __del__(self):
        self.__redis.close()

    def __init_redis__(self, realm: Realm, cache_type: EntityType):
        log.info("REDIS: init started")
        MAX_BATCH_SIZE = 100000
        db_num = self.entity_db_map.get(cache_type)
        if db_num is None:
            raise Exception(f'Non-cached entity type requested: {cache_type.name}')
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

    def internal_test(self):
        i = 0
        cursor = '0'
        data = {}
        while cursor != 0:
            cursor, keys = self.__redis.scan(cursor=cursor, count=1000000)
            values = self.__redis.mget(*keys)
            values = [value for value in values if not value == None]
            data.update(dict(zip(keys, values)))
        for k, v in data.items():
            if v is None:
                log.error(f"Key {k} has none value!!")
                i += 1
        log.info(f"Internal_test done, bad keys count: {i}")
        return i

    def reload_from_db(self, query_result: [[str, str]]):
        log.warning(f"REDIS: begin reload cache, DB number: {self.__redis_db_number}")
        self.__redis.flushdb()
        for row in query_result:
            self.__redis.set(name=row[0], value=row[1])
        log.warning(f"REDIS: reload cache done, rows: {len(query_result)}, DB number: {self.__redis_db_number}.")

    def put_value(self, key, value=""):
        self.__redis.set(name=key, value=value)

    def test_dict(self):
        items = []
        for key in self.__redis.scan_iter():
            value = self.__redis.get(key)
            if value is None or value == 'NULL':
                items.append(key)
        if len(items) > 0:
            print(items)
            return False
        return True

    def flush(self):
        log.warning(f"REDIS: cache {self.__redis_db_number} was erased!")
        self.__redis.flushdb()

