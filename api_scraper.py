import datetime
import json
import concurrent.futures
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import List, Union
import threading

from rediscache import RedisCache
from constants import Realm, ApiHelper, EntityType, ScrapeResult, ApiType, EntityKeys
from kafka import KafkaProducer, TX_Scope
import requests as rq
from utility import timer


from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class API_Scraper:
    def __init__(self, server: Realm, api_type: ApiType):
        h = ApiHelper(server)
        self.entityType = h.apitype4api(api_type)
        log.info(f"Scraper init started, server: {server.name}, entity: {self.entityType}, api: {api_type.name}")
        self.cache = RedisCache(server, self.entityType)
        self.helper = ApiHelper(server)
        self.kafka = KafkaProducer(server, self.entityType)
        self.apiType = api_type
        log.info("Scraper init done")
        self.full_scrape = False


    def scrape_worker(self, offsets: [], id: int):
        QUERY_ERROR_LIMIT = 100
        returning_data = []
        current_query_error_count = 0
        log.info(f'Scrape thread started, entity: {self.entityType.name}')
        for offset in offsets:
            skipped_count = 0
            records_prepared = 0
            res: json
            res = self.scrape_endpoint(offset, id)
            if len(res) == 0:
                log.warning(f"Offset {offset} returns zero length response.")
                return returning_data
            else:
                for json_item in res:
                    id = json_item.get(EntityKeys.get(self.entityType))
                    if self.cache.check_value(id) is not None:
                        skipped_count += 1
                        continue
                    returning_data.append([json.dumps(json_item), id])
                    records_prepared += 1
                log.info(
                    f'skipped {skipped_count} messages, prepared {records_prepared} messages.')
            if records_prepared == 0:
                log.info(f"Offset {offset} returns no data, breaking loop.")
                return returning_data
        return returning_data

    def paged_scrape(self, id: str = "") -> Union[None, list[json]]:

        returning_data = []
        offsets = [[0, 200, 400, 600, 800, 1000],
                   [50, 250, 450, 650, 850],
                   [100, 300, 500, 700, 900],
                   [150, 350, 550, 750, 950]]

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.scrape_worker, offsets, repeat(id)))

        from itertools import chain
        for r in results:
            for i in r:
                returning_data.append(i)
        return returning_data

    def do_scrape(self, id: str = ""):
        with timer(logger=log, descriptor='do_scrape: '):
            data = self.paged_scrape(id)
            # были данные, сбрасываем таймер
            try:
                self.kafka.begin_tran()
                # вначале пишем в кафку, если успешно - пишем в редис
                with timer(logger=log, descriptor=f"do_scrape: kafka write"):
                    for row in data:
                        message = row[0]
                        key = row[1]
                        self.kafka.send_message(
                            message=message,
                            key=key,
                            tx_scope=TX_Scope.TX_EXTERNAL)
                with timer(logger=log, descriptor=f"do_scrape: redis write"):
                    for row in data:
                        key = row[1]
                        self.cache.put_value(key)
                self.kafka.commit_tran()
                log.info(f"Written {len(data)} rows to kafka {self.kafka.info()}.")
            except Exception as ex:
                self.kafka.rollback_tran()
                log.error(f"Caught exception when writing data:")
                log.error(ex, stack_info=True, exc_info=True)

    def scrape_endpoint(self, offset: int = 0, id: str = "", custom_uri: str | None = None) -> json:
        current_query_error_count = 0
        while current_query_error_count < 100:
            current_query_error_count += 1
            try:
                if custom_uri is None:
                    uri = self.helper.get_uri(self.apiType, offset, id)
                else:
                    uri = custom_uri
                with timer(logger=log, descriptor=f'querying uri: {uri}'):
                    headers = {'id': f'{datetime.datetime.now()}'}
                    resp = rq.get(uri, headers=headers)
                if resp.status_code == 200:
                    js = resp.json()
                    return js
                else:
                    log.error(f"queriyng {uri} returns {resp.status_code}")
                    time.sleep(1)
                    continue
            except Exception as e:
                log.error(e, stack_info=True, exc_info=True)
                # спим, а вдруг прочухается
                time.sleep(1)
                continue
        return {}
