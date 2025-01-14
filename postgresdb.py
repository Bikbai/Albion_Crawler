import psycopg
from psycopg import cursor
from psycopg_pool import ConnectionPool
from constants import EntityType

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class PostgresDB:
    def __del__(self):
        self.conn.close()
    def __init__(self):
        self.conn = psycopg.connect("postgresql://postgres@dbserver.lan/albion")

    def insert_dummy_player(self, id: str, guild_internal_id: str| None, name: str) -> int | None:
        cur: cursor
        with self.conn.cursor() as cur:
            sql = "\
        insert into player (id, guild_id, player_name) \
values (%s, %s, %s) \
on conflict on constraint uc_player_id do nothing \
returning internal_id"
            cur.execute(sql, (id, guild_internal_id, name))
            row = cur.fetchone()
            self.conn.commit()
            if row is None:
                return None
        return row[0]

    def insert_dummy_guild(self,  id: str, name: str) -> int | None:
        cur: cursor
        with self.conn.cursor() as cur:
            sql = "\
insert into guild (id, guild_name) \
values (%s, %s) \
on conflict on constraint uc_id do nothing \
returning internal_id"
            cur.execute(sql, (id, name))
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
select id, internal_id from {table_name}"
            cur.execute(sql)
            return cur.fetchall()
