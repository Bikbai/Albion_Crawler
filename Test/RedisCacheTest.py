import unittest
from rediscache import RedisCache
from constants import Realm, EntityType

class RedisCacheTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache = RedisCache(Realm.america, EntityType.battles)

    def test_put_get(self):
        self.cache.put_value(100)
        self.cache.put_value("101")
        if not self.cache.check_value(100):
            self.assertTrue(False, "Check for int value 100")
        if not self.cache.check_value("101"):
            self.assertTrue(False, "Check for str value 100")
        self.assertTrue(True)  # add assertion here

if __name__ == '__main__':
    unittest.main()
