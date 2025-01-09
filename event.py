import datetime
import json
from dataclasses import dataclass

@dataclass
class Event:
    numberOfParticipants: int
    groupMemberCount: int
    EventId: int
    TS: datetime.datetime
    Killer: json
    Victim: json
    TotalVictimKillFame: int
    Participants: [json]
    GroupMembers: [json]
    BattleId: int

    @classmethod
    def build_from_json(cls, j: json):
        return cls(j['numberOfParticipants'],
            j["groupMemberCount"],
            j["EventId"],
            j["TimeStamp"],
            j["Killer"],
            j["Victim"],
            j["TotalVictimKillFame"],
            j["Participants"],
            j["GroupMembers"],
            j["BattleId"])
