import json
from unittest import TestCase

from constants import Realm, ScrapeResult
from event_processor import EventProcessor

class TestEventProcessor(TestCase):
    def test_process_one(self):
        r, ev = self.ep.process_one(self.data)
        self.assertEqual(r, ScrapeResult.SUCCESS)

    @classmethod
    def setUpClass(cls):
        realm = Realm.europe
        cls.ep = EventProcessor(realm)
        with open('./event.json', 'r') as f:
            cls.data = json.load(f)