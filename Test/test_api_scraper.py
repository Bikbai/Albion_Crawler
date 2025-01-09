from unittest import TestCase
from api_scraper import API_Scraper
from constants import Realm, EntityType, ApiType, ScrapeResult, LOGGER_NAME

import logging
log = logging.getLogger(LOGGER_NAME)


class TestAPI_Scraper(TestCase):
    def test_scrape_endpoint(self):
        j = self.test_obj.scrape_endpoint(0)
        self.assertEqual(len(j), 50, "Returns unexpected count of rows")

    def test_paged_scrape(self):
        res, j = self.test_obj.paged_scrape()
        self.assertEqual(res, ScrapeResult.SUCCESS)
        self.assertEqual(len(j), 1050, "Returns unexpected count of rows")
        self.assertIsInstance(j, list)

    def test_do_scrape(self):
        self.test_obj.do_crape()

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        cls.test_obj = API_Scraper(server=Realm.europe, api_type=ApiType.EVENTS)