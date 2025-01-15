import json

import psycopg
from psycopg import cursor
from psycopg.types.json import Json
from constants import EntityType
from constants import Realm

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class PostgresDB:
    def __del__(self):
        self.conn.close()
    def __init__(self, realm: Realm):
        self.realm = realm
        self.conn = psycopg.connect(f"postgresql://postgres@dbserver.lan/albion")

    def insert_item(self, item_code: str, json_data: json) -> int | None:
        cur: cursor
        with self.conn.cursor() as cur:
            sql = f"\
insert into {self.realm.name}.item (code, json_data) \
values (%s, %s) \
on conflict on constraint uc_item_code do nothing \
returning internal_id"
            cur.execute(sql, (item_code, Json(json_data)), prepare=True)
            row = cur.fetchone()
            self.conn.commit()
            if row is None:
                return None
        return row[0]


    def insert_dummy_player(self, id: str, guild_internal_id: str| None, name: str) -> int | None:
        cur: cursor
        with self.conn.cursor() as cur:
            sql = f"\
insert into {self.realm.name}.player (id, guild_id, player_name) \
values (%s, %s, %s) \
on conflict on constraint uc_player_id do nothing \
returning internal_id"
            cur.execute(sql, (id, guild_internal_id, name), prepare=True)
            row = cur.fetchone()
            self.conn.commit()
            if row is None:
                return None
        return row[0]

    def insert_dummy_guild(self,  id: str, name: str) -> int | None:
        cur: cursor
        with self.conn.cursor() as cur:
            sql = f"\
insert into {self.realm.name}.guild (id, guild_name) \
values (%s, %s) \
on conflict on constraint uc_id do nothing \
returning internal_id"
            cur.execute(sql, (id, name), prepare=True)
            row = cur.fetchone()
            self.conn.commit()
            if row is None:
                return None
        return row[0]

    def get_cached_dict(self, entity: EntityType):
        # считаем, что содержимое EntityType - имена таблиц
        table_name = entity.name
        cur: cursor
        with self.conn.cursor() as cur:
            sql = f"\
select id, internal_id from {self.realm.name}.{table_name}"
            cur.execute(sql)
            return cur.fetchall()
