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

    @classmethod
    def from_json(cls, battle: json):
        id = battle.get('id')
        startTime = battle.get('startTime')
        endTime = battle.get('endTime')
        timeout = battle.get('timeout')
        totalFame = battle.get('totalFame')
        totalKills = battle.get('totalKills')
        p = []
        for plr_id, plr_json in battle.get('players').items():
            print(plr_id, plr_json)
        return cls(id, startTime, endTime, timeout, totalFame, totalKills, [], [])