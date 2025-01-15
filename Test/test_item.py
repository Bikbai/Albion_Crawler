from unittest import TestCase

from constants import EntityType, Realm
from item import Item
from postgresdb import PostgresDB
from rediscache import RedisCache


class TestItem(TestCase):

    @classmethod
    def setUpClass(cls):
        entity_type = EntityType.item
        cls.entity_type = entity_type
        realm=Realm.europe
        cls.item = Item(pg_db=PostgresDB(realm=realm), realm=realm)

    def test_fetch_item_data(self):
        t = self.item.find_item('T5_2H_DUALAXE_KEEPER')
        x = self.item.fetch_item_data('T5_2H_DUALAXE_KEEPER@3')
        self.assertEqual(x.get('uniqueName'), 'T5_2H_DUALAXE_KEEPER')
