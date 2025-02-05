from datetime import datetime

from dateutil import parser

from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

def convert_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt  # Можно вернуть объект datetime
        # Или вернуть строку: return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    except Exception as e:
        print(f"Ошибка при преобразовании даты '{ts_str}': {e}")
        return None

def process_row(row):
    row['timestamp'] = convert_timestamp(row['timestamp'])
    row['killer_averageitempower'] = round(row['killer_averageitempower'])
    row['victim_averageitempower'] = round(row['victim_averageitempower'])
    row['killer_eq.type'] = [int(value) for value in row['victim_eq.type']]
    row['victim_eq.type'] = [int(value) for value in row['victim_eq.type']]
    row['killer_id'] = int(row['killer_id'])
    row['killer_guild_id'] = int(row['killer_guild_id'])
    row['victim_id'] = int(row['victim_id'])
    row['victim_guild_id'] = int(row['victim_guild_id'])
    return row

# Создание клиента ClickHouse
def create_client():
    try:
        client = Client(
            host='dbserver.lan',
            port=9000,
            database='default'
        )
        print("Успешное подключение к ClickHouse")
        return client
    except ClickHouseError as e:
        print(f"Ошибка при подключении к ClickHouse: {e}")
        return None

# Функция для массовой вставки данных
def insert_data(client, data_to_insert):
    if not client:
        print("Клиент не создан. Вставка невозможна.")
        return

    # SQL-запрос для вставки данных
    query = """
    INSERT INTO events (
        realm, groupmembercount, numberofparticipants, eventid, 
        timestamp,
        killer_averageitempower, killer_eq.kind, killer_eq.type, killer_eq.qty, killer_id, killer_guild_id, killer_deathfame, killer_killfame,
        victim_averageitempower, victim_eq.kind, victim_eq.type, victim_eq.qty, victim_inventory, victim_id, victim_guild_id, victim_deathfame, victim_killfame
    ) VALUES
    """

    try:
        # Преобразование данных в формат, подходящий для вставки
        processed_data = [process_row(row) for row in data_to_insert]

        prepared_data = [
            (
                'america',
                row['groupmembercount'],
                row['numberofparticipants'],
                row['eventid'],
                row['timestamp'],
                row['killer_averageitempower'],
                row['killer_eq.kind'],
                row['killer_eq.type'],
                row['killer_eq.qty'],
                row['killer_id'],
                row['killer_guild_id'],
                row['killer_deathfame'],
                row['killer_killfame'],
                row['victim_averageitempower'],
                row['victim_eq.kind'],
                row['victim_eq.type'],
                row['victim_eq.qty'],
                row['victim_inventory'],
                row['victim_id'],
                row['victim_guild_id'],
                row['victim_deathfame'],
                row['victim_killfame']
            )
            for row in processed_data
        ]

        # Выполнение массовой вставки
        client.execute(query, prepared_data)
        print("Данные успешно вставлены!")
    except ClickHouseError as e:
        print(f"Ошибка при вставке данных: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")

# Данные для вставки (массив записей)
data_to_insert = [
    {
        "groupmembercount": 2,
        "numberofparticipants": 3,
        "eventid": 1151813917,
        "timestamp": "2025-01-26T17:24:11.730405200Z",
        "killer_averageitempower": 1591.07043,
        "killer_eq.kind": [
            "MainHand",
            "Head",
            "Armor",
            "Shoes",
            "Bag",
            "Cape",
            "Mount",
            "Potion"
        ],
        "killer_eq.type": [
            "3287",
            "403",
            "683",
            "1355",
            "107",
            "52",
            "65",
            "69"
        ],
        "killer_eq.qty": [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2
        ],
        "killer_id": "25749",
        "killer_guild_id": "2339",
        "killer_deathfame": 0,
        "killer_killfame": 93472,
        "victim_averageitempower": 1405.38672,
        "victim_eq.kind": [
            "MainHand",
            "OffHand",
            "Head",
            "Armor",
            "Shoes",
            "Bag",
            "Cape",
            "Mount"
        ],
        "victim_eq.type": [
            "1848",
            "1466",
            "572",
            "2315",
            "3289",
            "553",
            "237",
            "814"
        ],
        "victim_eq.qty": [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1
        ],
        "victim_inventory": [
            {
                "114": 10
            },
            {
                "1287": 1
            },
            {
                "176": 1
            },
            {
                "240": 1
            }
        ],
        "victim_id": "1471",
        "victim_guild_id": "483",
        "victim_deathfame": 186944,
        "victim_killfame": 0,
        "Group": {
            "7695": {
                "averageitempower": 0,
                "eq.kind": [],
                "eq.type": [],
                "eq.qty": [],
                "id": "7695",
                "guild_id": "1",
                "damagedone": 6056,
                "supporthealingdone": 0
            },
            "25749": {
                "averageitempower": 1591.07043,
                "eq.kind": [
                    "MainHand",
                    "Head",
                    "Armor",
                    "Shoes",
                    "Bag",
                    "Cape",
                    "Mount",
                    "Potion"
                ],
                "eq.type": [
                    "3287",
                    "403",
                    "683",
                    "1355",
                    "107",
                    "52",
                    "65",
                    "69"
                ],
                "eq.qty": [
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2
                ],
                "id": "25749",
                "guild_id": "2339",
                "damagedone": 5627,
                "supporthealingdone": 0
            },
            "25750": {
                "averageitempower": 1475.58752,
                "eq.kind": [
                    "MainHand",
                    "Head",
                    "Armor",
                    "Shoes",
                    "Bag",
                    "Cape",
                    "Mount",
                    "Potion",
                    "Food"
                ],
                "eq.type": [
                    "10167",
                    "572",
                    "2855",
                    "1355",
                    "558",
                    "237",
                    "240",
                    "219",
                    "3785"
                ],
                "eq.qty": [
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    1
                ],
                "id": "25750",
                "guild_id": "2339",
                "damagedone": 0,
                "supporthealingdone": 1516
            }
        }
    }
]


client = create_client()

if client:
    # Массовая вставка данных
    insert_data(client, data_to_insert)
