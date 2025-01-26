from unittest import TestCase


import logging
from constants import LOGGER_NAME, EntityType, Realm
from player import Player
from postgresdb import PostgresDB
from utility import setup_logger
log = setup_logger(logging.DEBUG)

class TestPlayer(TestCase):

    @classmethod
    def setUpClass(cls):
        entity_type = EntityType.item
        cls.entity_type = entity_type
        realm=Realm.europe
        cls.player = Player(pg_db=PostgresDB(realm=realm), realm=realm)

    def test_reload(self):
        rows = self.player.do_reload()
        for row in rows:
            self.assertNotEqual(row[1], self.player.find_player(plr_id=row[0], plr_name="", gld_id=None))

    def test_db(self):
        i = self.player.internal_test()
        self.assertNotEqual(0, i)
