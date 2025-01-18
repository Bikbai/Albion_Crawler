from unittest import TestCase
from api_scraper import API_Scraper
from constants import Realm, EntityType, ApiType


class TestAPI_Scraper(TestCase):
    def test_inner_scrape(self):
        x = self.test_obj.scrape_endpoint(offset=10)
        self.assertGreater(len(x), 0)

    @classmethod
    def setUpClass(cls):
        cls.test_obj = API_Scraper(server=Realm.asia, api_type=ApiType.EVENT)
