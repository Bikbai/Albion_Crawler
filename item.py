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
        """
        :param item_code: код, например T6_OFF_SHIELD@4
        :return: внутренний идентификатор
        """
        code = item_code
        if '@' in code:
            code = code[:-2]
        uri = f'https://gameinfo.albiononline.com/api/gameinfo/items/{code}/data'
        res = requests.get(uri)
        if res.status_code == 200:
            return res.json()
        else:
            log.error(f"Item {item_code} info not found")
        return {}

    def find_item(self, item_code: str, quality: int = 0) -> int:
        """
        :param item_code: код, например T6_OFF_SHIELD@4
        :param quality: качество, число от 0 (обычка) до 4 (шедевр)
        :return: внутренний идентификатор
        """
        code = f'{item_code}.{quality}'

        item_id = super(Item, self).check_value(code)
        if item_id is None:
            item_data = self.fetch_item_data(item_code)
            item_id = self.pg.insert_item(code, item_data)
            super(Item, self).put_value(key=code, value=str(item_id))
            log.info(f"ITEM: Inserted new item data: {code}. internal_id: {item_id}")
        return item_id

