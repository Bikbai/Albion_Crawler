import json
import time
import logging
from typing import List, Union

from rediscache import RedisCache
from constants import Realm, ApiHelper, EntityType, ScrapeResult, ApiType, EntityKeys
from kafka import KafkaConsumer
from battle import Battle
import requests as rq
from time import perf_counter_ns

from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

srv = Realm.europe

pf_start = perf_counter_ns()
log.info(f'Init connections')
consumer = KafkaConsumer(realm=srv, entity=EntityType.battles)
player_cache = RedisCache(realm=srv, cache_type=EntityType.player)
guild_cache = RedisCache(realm=srv, cache_type=EntityType.guild)
pf_end = perf_counter_ns()
log.info(f'Init connections done, took {(pf_end-pf_start)/1000000} ms')


x = consumer.get()

print(x)



