import json
import logging
from unittest import TestCase

from constants import Realm, ScrapeResult
from event_processor import EventProcessor

from utility import setup_logger
log = setup_logger()
log.info("Application started")

class TestEventProcessor(TestCase):

    def test_process_one(self):
        r, ev = self.ep.process_one(self.data)
        self.assertEqual(r, ScrapeResult.SUCCESS)

    def test_full_one(self):
        self.ep.process_loop()

    def test_process_equipment(self):
        eq = self.data.get('Killer').get('Equipment')
        a, b, c = self.ep.process_equipment(data=eq, event_id=self.data.get('EventId'), kill_event=True)
        self.assertEqual(a, [1, 2, 3])

    @classmethod
    def setUpClass(cls):
        realm = Realm.europe
        cls.ep = EventProcessor(realm)
        with open('./event.json', 'r') as f:
            cls.data = json.load(f)