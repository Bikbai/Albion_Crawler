import json
from rediscache import RedisCache
from constants import Realm, EntityType
from postgresdb import PostgresDB

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class Guild(RedisCache):
    def __del__(self):
        self.pg.conn.close()

    def __init__(self, pg_db: PostgresDB, realm: Realm):
        self.pg = pg_db
        super(Guild, self).__init__(realm, EntityType.guild)

    def find_guild(self, gld_id: str, gld_name: str) -> int:
        gld_internal_id = super(Guild, self).check_value(gld_id)
        if gld_internal_id is None:
            gld_internal_id = self.pg.insert_dummy_guild(gld_id, gld_name)
            super(Guild, self).put_value(key=gld_id, value=str(gld_internal_id))
            log.info(f"inserted dummy new guild record: {gld_id}, {gld_name}. internal_id: {gld_internal_id}")
        return gld_internal_id

