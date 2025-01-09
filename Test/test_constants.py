from unittest import TestCase
from constants import ApiHelper, Realm, ApiType
import requests

class TestAlbionServer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testobj = ApiHelper(realm=Realm.asia)

    def test_get_uri(self):

        test_data = [
            self.testobj.get_uri(ApiType.BATTLES, 0, "100"),
            self.testobj.get_uri(ApiType.EVENTS, 0, "100"),
            self.testobj.get_uri(ApiType.BATTLE_EVENTS, 0, "312510276"),
            self.testobj.get_uri(ApiType.GUILD_MEMBERS, 0, "czW5nQJ_Tgebf__rd2SSMA"),
            self.testobj.get_uri(ApiType.PLAYER, 0, "dB6T6plORumVaNfmm5lgMg"),
            self.testobj.get_uri(ApiType.PLAYER_KILLS, 0, "dB6T6plORumVaNfmm5lgMg"),
            self.testobj.get_uri(ApiType.PLAYER_DEATHS, 0, "dB6T6plORumVaNfmm5lgMg"),
            self.testobj.get_uri(ApiType.EVENT, 0, "312510314"),
            self.testobj.get_uri(ApiType.GUILD, 0, "czW5nQJ_Tgebf__rd2SSMA")
            ]

        for uri in test_data:
            res = requests.get(uri)
            print(uri)
            if res.status_code != 200:
                self.fail(f"{ApiType.name} faulted")
            if len(res.json()) == 0:
                self.fail(f"{ApiType.name} faulted")
        self.assertTrue(True)