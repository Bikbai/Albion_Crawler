import json
import time
from unittest import TestCase

import requests

from api_scraper import API_Scraper
from constants import Realm, EntityType, ApiType, ScrapeResult, LOGGER_NAME
from confluent_kafka.serialization import StringSerializer, StringDeserializer

import logging

from utility import setup_logger
logging.basicConfig(level=logging.WARNING)  # Optional: Minimal configuration for the root logger
log = setup_logger()

class TestAPI_Scraper(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        cls.test_obj = API_Scraper(server=Realm.asia, api_type=ApiType.EVENTS)
    def test_scrape_endpoint(self):
        custom_uri = 'https://gameinfo-ams.albiononline.com/api/gameinfo/events?sort=recent&limit=1'
        j = self.test_obj.scrape_endpoint(custom_uri=custom_uri)
        self.assertEqual(j[0]['EventId'], 136380642, "Returns unexpected count of rows")
        time.sleep(300)
        j = self.test_obj.scrape_endpoint(custom_uri=custom_uri)
        self.assertEqual(j[0]['EventId'], 136380642, "Returns unexpected count of rows")


    def test_paged_scrape(self):
        j = self.test_obj.paged_scrape()
        self.assertEqual(len(j), 1050, "Returns unexpected count of rows")
        self.assertIsInstance(j, list)

    def test_requests(self):
        uri = 'https://gameinfo-ams.albiononline.com/api/gameinfo/events?sort=recent&limit=1'
        x = requests.get(uri)
        self.assertEqual(len(x.json()), 1)

    def test_do_scrape(self):
        self.test_obj.do_scrape()

    def test_serializer(self):
        j = json.loads('{"key": "value", "key2": 2}')
        if isinstance(j, dict):
            print(json.dumps(j))
        self.assertEqual(1, 2)

