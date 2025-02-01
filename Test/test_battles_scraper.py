from unittest import TestCase
from api_scraper import API_Scraper
from constants import Realm, EntityType, ApiType


class TestAPI_Scraper(TestCase):
    def test_inner_scrape(self):
        x = self.test_obj.paged_scrape(id='141209534')
        y = self.test_obj.scrape_worker([0], id='141209534')
        self.assertEqual(len(x), len(y))

    @classmethod
    def setUpClass(cls):
        cls.test_obj = API_Scraper(server=Realm.europe, api_type=ApiType.SINGLE_BATTLE)
