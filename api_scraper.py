import datetime
import json
import time
import logging
from typing import List, Union

from rediscache import RedisCache
from constants import Realm, ApiHelper, EntityType, ScrapeResult, ApiType, EntityKeys
from kafka import KafkaProducer, TX_Scope
import requests as rq
from time import perf_counter_ns

from constants import LOGGER_NAME
from utility import timer

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

    def paged_scrape(self, id: str = "", full: bool = True) -> tuple[ScrapeResult, Union[None, list[json]]]:
        QUERY_ERROR_COUNT = 100
        offset = 0
        no_data_flag = False
        current_query_error_count = 0
        returning_data = []
        self.full_scrape = full
        skipped_count = 0
        while offset < 1001:
            res = self.scrape_endpoint(offset, id)
            if res is None:
                # error logged earlier
                current_query_error_count += 1
                #спим, а вдруг прочухается
                time.sleep(current_query_error_count)
                if current_query_error_count > QUERY_ERROR_COUNT:
                    # выставляем флаг, следующий раз листаем до конца
                    self.full_scrape = True
                    return ScrapeResult.FAIL, None
                continue
            elif len(res) == 0:
                if len(returning_data) == 0:
                    return ScrapeResult.NO_DATA, None
                else:
                    break
            else:
                #write data to kafka
                records_prepared = 0
                skipped_count = 0
                for json_item in res:
                    id = json_item.get(EntityKeys.get(self.entityType))
                    if self.cache.check_value(id) is not None:
                        # log.info(f'battle {id} exists, skipping')
                        skipped_count += 1
                        log.info(f"Checking EventId: {id}: exists")
                        continue
                    returning_data.append([json.dumps(json_item), id])
                    log.info(f"Checking EventId: {id}: new")
                    records_prepared += 1
                log.info(
                    f'skipped {skipped_count} messages, prepared {records_prepared} messages.')
            offset += 50
        if skipped_count == len(returning_data):
            if len(returning_data) > 0:
                return ScrapeResult.SUCCESS, returning_data
        return ScrapeResult.SUCCESS, returning_data

    def do_scrape(self):
        base_sleep_duration_seconds = 60 * 5  # 5 minutes
        fail_sleep_duration_seconds = 10  # 10 seconds
        current_delay = base_sleep_duration_seconds
        iter_num = 0
        with timer(logger=log, descriptor='Scrape job started'):
            pf_start = perf_counter_ns()
            iter_num += 1
            full_scrape = True
            result, data = self.paged_scrape(full=full_scrape)
            if result in (ScrapeResult.FAIL, ):
                current_delay = fail_sleep_duration_seconds
            else:
                current_delay = base_sleep_duration_seconds
            log.info(f"job done, sleeping for {current_delay} seconds")
            # были данные, сбрасываем таймер
            if result == ScrapeResult.SUCCESS:
                try:
                    self.kafka.begin_tran()
                    # вначале пишем в кафку, если успешно - пишем в редис
                    for row in data:
                        message = row[0]
                        key = row[1]
                        with timer(logger=log, descriptor=f"do_scrape: kafka write"):
                            self.kafka.send_message(
                                message=message,
                                key=key,
                                tx_scope=TX_Scope.TX_EXTERNAL)
                    for row in data:
                        key = row[1]
                        self.cache.put_value(key)
                    self.kafka.commit_tran()
                    log.info(f"Written {len(data)} rows to kafka {self.kafka.info()}.")
                except Exception as ex:
                    self.kafka.rollback_tran()
                    log.error(f"Caught exception when writing data:")
                    log.error(ex, stack_info=True, exc_info=True)
            pf_end = perf_counter_ns()
            log.info(f'Iteration {iter_num} finished, it took {(pf_end-pf_start)/1000000} ms')
            #time.sleep(current_delay)

    def scrape_endpoint(self, offset: int = 0, id: str = "", custom_uri: str | None = None) -> json:
        try:
            if custom_uri is None:
                uri = self.helper.get_uri(self.apiType, offset, id)
            else:
                uri = custom_uri
            log.info(f'querying uri: {uri}')
            pf_start = perf_counter_ns()
            headers = {'id': f'{datetime.datetime.now()}'}
            resp = rq.get(uri, headers=headers)
            pf_stop = perf_counter_ns()
            log.info(f'querying uri done, it took {(pf_stop - pf_start)/1000000} ms ')
            if resp.status_code == 200:
                js = resp.json()
                return js
            else:
                log.error(f"queriyng {uri} returns {resp.status_code}")
                return None
        except Exception as e:
            log.error(e, stack_info=True, exc_info=True)
            return None
