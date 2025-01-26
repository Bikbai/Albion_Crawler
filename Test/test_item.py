from unittest import TestCase

from constants import EntityType, Realm
from item import Item
from postgresdb import PostgresDB
from rediscache import RedisCache

import logging
from constants import LOGGER_NAME
from utility import setup_logger
log = setup_logger(logging.DEBUG)


class TestItem(TestCase):

    @classmethod
    def setUpClass(cls):
        entity_type = EntityType.item
        cls.entity_type = entity_type
        realm=Realm.europe
        cls.item = Item(pg_db=PostgresDB(realm=realm), realm=realm)

    def test_fetch_item_data(self):
        t1 = self.item.find_item('T7_POTION_REVIVE')
        t2 = self.item.find_item('T4_SILVERBAG_NONTRADABLE')
        self.assertNotEqual(t1, t2)

    def test_find_item(self):
        code = 'T5_HEAD_CLOTH_HELL@3'
        x = self.item.find_item(item_code=code, quality=2)
        log.info(f'item_id: {x}')
        self.assertNotEqual(0, x)

    def test_db(self):
        i = self.item.internal_test()
        self.assertNotEqual(0, i)

