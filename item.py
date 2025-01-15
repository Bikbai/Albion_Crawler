import json
from rediscache import RedisCache
from constants import Realm, EntityType
from postgresdb import PostgresDB
import requests

import logging
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class Item(RedisCache):
    def __del__(self):
        self.pg.conn.close()

    def __init__(self, pg_db: PostgresDB, realm: Realm):
        self.pg = pg_db
        super(Item, self).__init__(realm, EntityType.item)

    def fetch_item_data(self, item_code: str):
        code = item_code
        if '@' in code:
            code = code[:-2]
        uri = f'https://gameinfo.albiononline.com/api/gameinfo/items/{code}/data'
        res = requests.get(uri)
        if res.status_code == 200:
            return res.json()
    def find_item(self, item_code: str) -> int:
        item_id = super(Item, self).check_value(item_code)
        if item_id is None:
            item_data = self.fetch_item_data(item_code)
            item_id = self.pg.insert_item(item_code, item_data)
            super(Item, self).put_value(key=item_code, value=str(item_id))
            log.info(f"ITEM: Inserted new item data: {item_code}, {item_data}. internal_id: {item_id}")
        return item_id

