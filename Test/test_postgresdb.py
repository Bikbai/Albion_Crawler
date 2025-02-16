from unittest import TestCase

from constants import Realm
from postgresdb import PostgresDB
import json

class TestPostgresDB(TestCase):


    def test_select(self):
        id = "wtqzxhOLStCwyD_ixIxC3A"
        with self.pg.conn.cursor() as cur:
            x = cur.execute(f"select internal_id from {self.pg.realm.name}.guild where id = (%s)", (id,)).fetchone()
            print(x[0])

    def test_insert_dummy_guild(self):
        id = 'dummy_id'
        name = 'dummy_name'
        internal_id = self.pg.insert_dummy_guild(id, name)
        self.assertIsNotNone(internal_id)
        internal_id = self.pg.insert_dummy_guild(id, name)
        self.assertIsNone(internal_id)

    def test_insert_dummy_player_no_guild(self):
        id = "dummy_id"
        name = "dummy_name"
        internal_id = self.pg.insert_dummy_player(id, None, name)
        self.assertIsNotNone(internal_id)

    def test_insert_dummy_player_dummy_guild(self):
        self.insert_dummy_guild()
        guild_id = 'dummy_id'
        id = "dummy_id2"
        name = "dummy_name2"
        internal_id = self.pg.insert_dummy_player(id, guild_id, name)
        self.assertIsNotNone(internal_id)
        pass





    @classmethod
    def setUpClass(cls):
        guild_data_str = '{\
            "Id": "dummy_id",\
            "Name": "dummy name",\
            "FounderId": "MhQi0UOVRNW_VJdXd9Jj6w",\
            "FounderName": "Rezky",\
            "Founded": "2019-05-25T18:08:57.307249Z",\
            "AllianceTag": "",\
            "AllianceId": "",\
            "AllianceName": null,\
            "Logo": null,\
            "killFame": 3737579059,\
            "DeathFame": 2191050796,\
            "AttacksWon": null,\
            "DefensesWon": null,\
            "MemberCount": 27}'
        cls.pg = PostgresDB(realm=Realm.europe)
        with cls.pg.conn.cursor() as cur:
            cur.execute(f"delete from {cls.pg.realm.name}.player where id like 'dummy_id%'")
            cur.execute(f"delete from {cls.pg.realm.name}.guild where id = 'dummy_id'")
            cls.pg.conn.commit()
        cls.test_data: json
        cls.test_data = json.loads(guild_data_str)