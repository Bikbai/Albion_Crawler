from enum import IntEnum, StrEnum

LOGGER_NAME = "API_SCRAPER"

class Realm(IntEnum):
    europe = 0
    america = 1
    asia = 2


class ScrapeResult(IntEnum):
    SUCCESS = 1
    FAIL = 2
    NO_DATA = 3


# типы сущностей
class EntityType(IntEnum):
    def __str__(self):
        return str(self.value)
    guild = 1
    player = 2
    battles = 3
    event = 4
    test = 5
    battlebatch = 7
    eventbatch = 8
    item = 9

# Типы API
class ApiType(IntEnum):
    def __str__(self):
        return str(self.value)
    BATTLES = 1
    EVENTS = 2
    BATTLE_EVENTS = 3
    GUILD_MEMBERS = 4
    PLAYER = 5
    PLAYER_KILLS = 6
    PLAYER_DEATHS = 7
    EVENT = 8
    GUILD = 9

EntityKeys = {
    EntityType.guild: "Id",
    EntityType.player: "Id",
    EntityType.battles: "id",
    EntityType.event: "EventId"
}

class ApiHelper:
    base_uri = 'https://gameinfo{self.prefix}.albiononline.com/api/gameinfo/'
    prefix_map = {Realm.europe: "-ams", Realm.america: "", Realm.asia: "-sgp"}
    uri_template_map = {
        ApiType.BATTLES: ('battles?sort=recent&limit=50&offset={offset}', EntityType.battles),
        ApiType.EVENTS: ('events?sort=recent&limit=50&offset={offset}', EntityType.event),
        ApiType.BATTLE_EVENTS: ('events/battle/{id}?limit=50&offset={offset}', EntityType.event),
        ApiType.GUILD_MEMBERS: ('guilds/{id}/members', EntityType.player),
        ApiType.PLAYER: ('players/{id}', EntityType.player),
        ApiType.PLAYER_KILLS: ('players/{id}/kills', EntityType.event),
        ApiType.PLAYER_DEATHS: ('players/{id}/deaths', EntityType.event),
        ApiType.EVENT: ('events/{id}', EntityType.event),
        ApiType.GUILD: ('guilds/{id}', EntityType.guild)
    }
    events_suffix = 'events?limit=50&offset='

    def __init__(self, realm: Realm):
        self.prefix = self.prefix_map.get(realm)
        self.current = realm

    def apitype4api(self, api: ApiType) -> EntityType:
        return self.uri_template_map.get(api)[1]

    def get_uri(self, type: ApiType,  offset: int, id: str):
        # Эти параметры зашиты в строке шаблона f-string!
        offset = offset
        id = id
        template = self.base_uri + self.uri_template_map[type][0]
        retval = eval(f'f"""{template}"""')
        return retval