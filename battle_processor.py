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

@dataclass()
class Battle:
    id: int
    startTime: datetime.datetime
    endTime: datetime.datetime
    timeout: datetime.datetime
    totalFame: int
    totalKills: int
    players: [int]
    guilds: [int]


class BattleProcessor:
    def __init__(self, srv: Realm):
        pf_start = perf_counter_ns()
        log.info(f'Init connections')
        self.consumer = KafkaConsumer(realm=srv, topic=EntityType.battles)
        self.producer = KafkaProducer(realm=srv, topic=EntityType.battlebatch)
        self.pg = PostgresDB()
        self.player_cache = Player(pg_db=self.pg, realm=srv)
        self.guild_cache = Guild(pg_db=self.pg, realm=srv)
        pf_end = perf_counter_ns()
        log.info(f'Init connections done, took {(pf_end - pf_start) / 1000000} ms')
        self.scraper = API_Scraper(server=srv, api_type=ApiType.BATTLE_EVENTS)

    def process_json(self, battle: json):
        battle_item = {}
        battle_item.update({'id': battle.get('id')})
        battle_item.update({'startTime': battle.get('startTime')})
        battle_item.update({'endTime': battle.get('endTime')})
        battle_item.update({'timeout': battle.get('timeout')})
        battle_item.update({'totalFame': battle.get('totalFame')})
        battle_item.update({'totalKills': battle.get('totalKills')})
        players = []
        for plr in battle.get('players').values():
            guildId = plr.get('guildId')
            guildName = plr.get('guildName')
            playerId = plr.get('id')
            playerName = plr.get('name')
            kills = plr.get('kills')
            deaths = plr.get('deaths')
            killFame = plr.get('killFame')
            guild_internal_id = None
            if guildId is not None:
                guild_internal_id = self.guild_cache.find_guild(gld_id=guildId, gld_name=guildName)
            player_internal_id = self.player_cache.find_player(plr_id=playerId, plr_name=playerName, gld_id=guildId)
            players.append(
                {"id": player_internal_id,
                 "guild_id": guild_internal_id,
                 "kills": kills,
                 "deaths": deaths,
                 "killFame": killFame})
        battle_item.update({'players': players})
        return json.dumps(battle_item)

    @timer_decorator(logger=log)
    def process_single(self):
        battle = self.consumer.get()
        return self.process_json(battle)

    def do_process(self):
        i = 0
        while(True):
            with timer(logger=log, descriptor=f"Main cycle {i}"):
                log.info(f"Waiting for data from topic: {self.consumer.get_topic()}")
                battle = self.consumer.get()
                self.producer.begin_tran()
                with timer(logger=log, descriptor=f"{i}: do_process: fetch"):
                    battle_id = battle.get('id')
                if battle_id == "":
                    log.error(f"ERROR: Cannot fetch battle id {battle}")
                    continue
                with timer(logger=log, descriptor=f"{i}: do_process: convert"):
                    converted_battle = self.process_json(battle)
                with timer(logger=log, descriptor=f"{i}: do_process: scrape"):
                    self.scraper.paged_scrape(id=battle_id, full=True)
                with timer(logger=log, descriptor=f"{i}: do_process: write"):
                    self.producer.send_message(message=converted_battle, key=battle.get('id'), tx_scope=TX_Scope.TX_EXTERNAL)
                i += 1
                self.producer.commit_tran()
                self.consumer.commit()
