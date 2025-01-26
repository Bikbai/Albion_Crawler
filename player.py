import json
from rediscache import RedisCache
from constants import Realm, EntityType
from postgresdb import PostgresDB

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class Player(RedisCache):
    def __del__(self):
        self.pg.conn.close()

    def __init__(self, pg_db: PostgresDB, realm: Realm):
        self.pg = pg_db
        super(Player, self).__init__(realm, EntityType.player)

    def find_player(self, plr_id: str, plr_name: str, gld_id: str | None) -> int:
        plr_internal_id = super(Player, self).check_value(plr_id)
        if plr_internal_id is None:
            plr_internal_id = self.pg.insert_dummy_player(plr_id, gld_id, plr_name)
            super(Player, self).put_value(key=plr_id, value=str(plr_internal_id))
            log.info(f"inserted dummy new player record: {plr_id}, {plr_name}. internal_id: {plr_internal_id}")
        return plr_internal_id

    def do_reload(self):
        result = self.pg.get_cached_dict(entity=EntityType.player)
        self.reload_from_db(result)
        return result
