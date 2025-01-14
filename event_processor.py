import json
import time
import logging
from typing import List, Union
from player import Player
from guild import  Guild
from utility import timer_decorator, timer
from api_scraper import API_Scraper

from postgresdb import PostgresDB
from rediscache import RedisCache
from constants import Realm, ApiHelper, EntityType, ScrapeResult, ApiType, EntityKeys
from kafka import KafkaConsumer, KafkaProducer, TX_Scope
from time import perf_counter_ns

from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


import datetime
from dataclasses import dataclass
import json


class EventProcessor:

    def __init__(self, srv: Realm):
        pf_start = perf_counter_ns()
        log.info(f'Init connections')
        self.consumer = KafkaConsumer(realm=srv, entity=EntityType.event)
        self.producer = KafkaProducer(realm=srv, entity=EntityType.eventbatch)
        self.pg = PostgresDB()
        self.player_cache = Player(pg_db=self.pg, realm=srv)
        self.guild_cache = Guild(pg_db=self.pg, realm=srv)
        self.item_cache = Item(pg_db=self.pg)
        pf_end = perf_counter_ns()
        log.info(f'Init connections done, took {(pf_end - pf_start) / 1000000} ms')
        self.scraper = API_Scraper(server=srv, api_type=ApiType.BATTLE_EVENTS)