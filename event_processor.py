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

pt_stored = ('AverageItemPower',
          'DamageDone',
          'SupportHealingDone',
          )

import datetime
from dataclasses import dataclass
import json


class EventProcessor:
    eq_type_map = {
        "MainHand":  0,
        "OffHand":   1,
        "Head":      2,
        "Armor":     3,
        "Shoes":     4,
        "Bag":       5,
        "Cape":      6,
        "Mount":     7,
        "Potion":    8,
        "Food":      9
    }

    def __init__(self, srv: Realm):
        pf_start = perf_counter_ns()
        log.info(f'Init connections')
        self.consumer = KafkaConsumer(realm=srv, topic=EntityType.event)
        self.producer = KafkaProducer(realm=srv, topic=EntityType.eventbatch)
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

    def process_inventory(self, inv: list, event_id: int) -> [json]:
        retval = []
        if len(inv) == 0:
            return retval
        item: json
        for item in inv:
            if item is None:
                continue
            r_item = {}
            type = item.get('Type')
            count = item.get('Count')
            quality = item.get('Quality')
            legendary = item.get('LegendarySoul')
            internal_id = self.item_cache.find_item(type, quality)
            if legendary is not None:
                self.pg.insert_legendary(event_id=event_id, kill_event=False, item_id=internal_id, data=legendary)
            r_item.update({f'{internal_id}': count})
            retval.append(r_item)
        return retval

    def process_equipment(self, data:json, kill_event: bool, event_id: int = 0) -> ([], [], []):
        """
        :param data: внутренний json элемента Equipment
        :param event_id: ссылка на eventId для учёта легендарок
        :return: кортеж колонок вид, тип итема, количество
        """
        retval = []
        if len(data) == 0:
            return retval
        spec = []
        type = []
        cnt = []
        i_descr: json
        for i_type, i_descr in data.items():
            if i_descr is None:
                continue
            item = self.item_cache.find_item(i_descr.get('Type'), i_descr.get('Quality'))
            legend = i_descr.get('LegendarySoul')
            if legend is not None:
                self.pg.insert_legendary(item, legend, event_id, kill_event)
            qty = i_descr.get('Count')
            spec.append(i_type) # MainHand
            type.append(item) # T5_2H_DUALSICKLE_UNDEAD@4.1 -> int
            cnt.append(qty) # 1
        return (spec, type, cnt)

    def parse_participants(self, j: json, event_id: int, data: json, participant_mode: bool = True) -> {}:
        for participant in j:
            pt = {}
            for tag, kval in participant.items():
                if tag == 'GuildId':
                    id = self.guild_cache.find_guild(gld_name=participant['Name'], gld_id=kval)
                    pt.update({'guild_id': id})
                elif tag == 'Id':
                    id = self.player_cache.find_player(plr_id=kval, plr_name=participant['Name'], gld_id=participant['GuildId'])
                    pt.update({'id': id})
                elif tag == 'Equipment':
                    kind, type, qty = self.process_equipment(data=kval, event_id=event_id, kill_event=True)
                    pt.update({'eq.kind': kind})
                    pt.update({'eq.type': type})
                    pt.update({'eq.qty': qty})
                elif tag in pt_stored:
                    pt.update({f'{str.lower(tag)}': kval})
            if participant_mode:
                data.update({pt.get("id"): pt})
            else:
                if data.get(pt.get("id")) is None:
                    data.update({pt.get("id"): pt})
        return data
    def process_one(self, data: json) -> (ScrapeResult, json):
        evt = {}
        # состав всей группы
        group = {}
        # участники
        part = {}
        event_id = data.get('EventId')
        for tag, val in data.items():
            if tag == 'Participants':
                part = self.parse_participants(val, event_id, part, True)
            if tag == 'GroupMembers':
                part = self.parse_participants(val, event_id, part, False)
            if tag == 'Killer':
                for tag, kval in val.items():
                    if tag == 'GuildId':
                        id = self.guild_cache.find_guild(gld_name=val['Name'], gld_id=kval)
                        evt.update({'killer_guild_id': id})
                    elif tag == 'Id':
                        id = self.player_cache.find_player(plr_id=kval, plr_name=val['Name'], gld_id=val['GuildId'])
                        evt.update({'killer_id': id})
                    elif tag == 'Equipment':
                        kind, type, qty = self.process_equipment(data=kval, event_id=event_id, kill_event=True)
                        evt.update({'killer_eq.kind': kind})
                        evt.update({'killer_eq.type': type})
                        evt.update({'killer_eq.qty': qty})
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
                        kind, type, qty = self.process_equipment(data=kval, event_id=event_id, kill_event=False)
                        evt.update({'victim_eq.kind': kind})
                        evt.update({'victim_eq.type': type})
                        evt.update({'victim_eq.qty': qty})
                    elif tag == 'Inventory':
                        evt.update({'victim_inventory': self.process_inventory(kval, event_id=event_id)})
                    elif tag in stored:
                        evt.update({f'victim_{str.lower(tag)}': kval})
            elif tag == 'BattleId':
                pass
            elif tag in stored:
                evt.update({str.lower(tag): val})
        evt.update({"Group": part})
        return ScrapeResult.SUCCESS, evt

    def write_one(self, data: json):
        self.producer.send_message(message=data, key=data.get('EventId'), tx_scope=TX_Scope.TX_INTERNAL_COMMIT)

    def process_loop(self):
        i = 1
        while True:
            with timer(logger=log, descriptor=f"{i}:process_loop:fetch_one: "):
                ev = self.fetch_one()
            with timer(logger=log, descriptor=f"{i}:process_loop:process_one: "):
                res = self.process_one(ev)
            with timer(logger=log, descriptor=f"{i}:process_loop:write_one: "):
                self.write_one(res[1])
            i += 1
