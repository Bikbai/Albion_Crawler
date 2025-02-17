import unittest
from rediscache import RedisCache
from constants import Realm, EntityType
from postgresdb import PostgresDB

class RedisCacheTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        entity_type = EntityType.guild
        realm = Realm.asia
        cls.entity_type = entity_type
        cls.pg = PostgresDB(realm)
        cls.cache = RedisCache(realm, entity_type)

    def test_check_value(self):
        key = 'NaFnj3ksQ3Wa3Z96Ixh0dQ'
        test = self.cache.check_value(key=str(key))
        self.assertEqual(test, str(25))

    def test_put_get(self):
        self.cache.put_value(100)
        self.cache.put_value("101")
        if not self.cache.check_value(100):
            self.assertTrue(False, "Check for int value 100")
        if not self.cache.check_value("101"):
            self.assertTrue(False, "Check for str value 100")
        self.assertTrue(True)  # add assertion here

    def test_reload(self):
        rows = self.pg.get_cached_dict(self.entity_type)
        self.assertGreater(len(rows), 0)
        redis_count = self.cache.ext_info()
        #self.assertEqual(len(rows), redis_count)
        self.cache.reload_from_db(rows)
        redis_count = self.cache.ext_info()
        self.assertEqual(len(rows), redis_count)

    def test_dict(self):
        v = self.cache.test_dict()
        self.assertEqual(v, True)

if __name__ == '__main__':
    unittest.main()
