import json
from unittest import TestCase
from api_scraper import API_Scraper
from constants import Realm, EntityType, ApiType, ScrapeResult, LOGGER_NAME
from confluent_kafka.serialization import StringSerializer, StringDeserializer

import logging
log = logging.getLogger(LOGGER_NAME)


class TestAPI_Scraper(TestCase):
    def test_scrape_endpoint(self):
        custom_uri = 'https://gameinfo-ams.albiononline.com/api/gameinfo/events/battle/131330357?limit=50'
        j = self.test_obj.scrape_endpoint(custom_uri=custom_uri)
        self.assertEqual(len(j), 50, "Returns unexpected count of rows")

    def test_paged_scrape(self):
        res, j = self.test_obj.paged_scrape()
        self.assertEqual(res, ScrapeResult.SUCCESS)
        self.assertEqual(len(j), 1050, "Returns unexpected count of rows")
        self.assertIsInstance(j, list)

    def test_do_scrape(self):
        self.test_obj.do_crape()

    def test_serializer(self):
        j = json.loads('{"key": "value", "key2": 2}')
        if isinstance(j, dict):
            print(json.dumps(j))
        self.assertEqual(1,2)

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        cls.test_obj = API_Scraper(server=Realm.europe, api_type=ApiType.BATTLE_EVENTS)