from unittest import TestCase
from battle_processor import BattleProcessor
from constants import Realm, ApiType

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.INFO)


class TestBattleProcessor(TestCase):
    def test_loop(self):
        self.t.do_process()

    def test_process_single(self):
        x = self.t.process_single()
        print(x)
        self.assertGreater(len(x), 1)

    @classmethod
    def setUpClass(cls):
        cls.t = BattleProcessor(Realm.europe)
