import json
import time
import logging
from typing import List, Union

from item import Item
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

stored = ('numberOfParticipants',
          'groupMemberCount',
          'EventId',
          'TimeStamp',
          'BattleId',
          'AverageItemPower',
          'DeathFame',
          'KillFame'
          )

import datetime
from dataclasses import dataclass
import json


class EventProcessor:

    def __init__(self, srv: Realm):
        pf_start = perf_counter_ns()
        log.info(f'Init connections')
        self.consumer = KafkaConsumer(realm=srv, entity=EntityType.event)
        self.producer = KafkaProducer(realm=srv, entity=EntityType.eventbatch)
        self.pg = PostgresDB(realm=srv)
        self.player_cache = Player(pg_db=self.pg, realm=srv)
        self.guild_cache = Guild(pg_db=self.pg, realm=srv)
        self.item_cache = Item(pg_db=self.pg, realm=srv)
        pf_end = perf_counter_ns()
        log.info(f'Init connections done, took {(pf_end - pf_start) / 1000000} ms')
        self.battle_scraper = API_Scraper(server=srv, api_type=ApiType.BATTLE_EVENTS)

    @timer(logger=log, descriptor="EventProcessor: fetch_one")
    def fetch_one(self):
        ev = self.consumer.get()
        return ev

    def process_inventory(self, inv: list) -> [json]:
        stored_keys = ('Type', 'Count', 'Quality')
        retval = []
        if len(inv) == 0:
            return retval
        item: json
        for item in inv:
            if item is None:
                continue
            r_item = {}
            for k, v in item.items():
                if k in stored_keys:
                    if k == 'Type':
                        id = self.item_cache.find_item(item.get('Type'))
                        r_item.update({'id': id})
                    else:
                        r_item.update({k: v})
            retval.append(r_item)
        return retval

    def process_equipment(self, data:json) -> [json]:


    def process_one(self, data: json) -> (ScrapeResult, json):
        evt = {}
        # состав всей группы
        group = {}
        # участники
        part = {}
        for tag, val in data.items():
            if tag == 'Killer':
                for tag, kval in val.items():
                    if tag == 'GuildId':
                        id = self.guild_cache.find_guild(gld_name=val['Name'], gld_id=kval)
                        evt.update({'killer_guild_id': id})
                    elif tag == 'Id':
                        id = self.player_cache.find_player(plr_id=kval, plr_name=val['Name'], gld_id=val['GuildId'])
                        evt.update({'killer_id': id})
                    elif tag == 'Equipment':
                        pass
                    elif tag in stored:
                        evt.update({f'killer_{str.lower(tag)}': kval})
            elif tag == 'Victim':
                for tag, kval in val.items():
                    if tag == 'GuildId':
                        id = self.guild_cache.find_guild(gld_name=val['Name'], gld_id=kval)
                        evt.update({'victim_guild_id': id})
                    elif tag == 'Id':
                        id = self.player_cache.find_player(plr_id=kval, plr_name=val['Name'], gld_id=val['GuildId'])
                        evt.update({'victim_id': id})
                    elif tag == 'Equipment':
                        pass
                    elif tag == 'Inventory':
                        evt.update({'victim_inventory': self.process_inventory(kval)})
                    elif tag in stored:
                        evt.update({f'victim_{str.lower(tag)}': kval})
            elif tag == 'Participants':
                pass
            elif tag == 'GroupMembers':
                pass
            elif tag == 'BattleId':
                pass
            elif tag in stored:
                evt.update({str.lower(tag): val})
        return ScrapeResult.SUCCESS, evt

    def process_loop(self):
        ev = self.fetch_one()
        res = self.process_one(ev)
