from datetime import datetime

import kafka
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

import logging
from constants import LOGGER_NAME, Realm, EntityType
from utility import setup_logger, print_startup_message, timer

logging.basicConfig(level=logging.WARNING)  # Optional: Minimal configuration for the root logger

# Create and configure a named logger
log = setup_logger()

print_startup_message(log)

def convert_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt  # Можно вернуть объект datetime
        # Или вернуть строку: return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    except Exception as e:
        print(f"Ошибка при преобразовании даты '{ts_str}': {e}")
        return None

class EventBatchProcessor:
    def __init__(self, realm: Realm):
        self.realm = realm
        self.__create_client__()
        self.consumer = kafka.KafkaConsumer(realm=realm, topic=EntityType.eventbatch)
        self.producer = kafka.KafkaProducer(realm=realm, topic=f"{realm.name}-evt-reload")
    def do_process(self, batch_size):
        try:
            with timer(logger=log, descriptor="Batch consume: "):
                msg = self.consumer.consume(batch_size)
            with timer(logger=log, descriptor="Batch insert: "):
                self.insert_data(msg)
            self.consumer.commit()
        except Exception as ex:
            log.error(ex)

    def convert(self, row):
        converted = []
        for t in row:
            if t == 'None':
                converted.append(0)
            else:
                converted.append(int(t))
        return converted
    def _process_row(self, row):
        try:
            row['timestamp'] = convert_timestamp(row['timestamp'])
            row['killer_averageitempower'] = round(row['killer_averageitempower'])
            row['victim_averageitempower'] = round(row['victim_averageitempower'])
            row['killer_eq.type'] = self.convert(row['killer_eq.type'])
            row['victim_eq.type'] = self.convert(row['victim_eq.type'])
            row['killer_id'] = int(row['killer_id'])
            row['killer_guild_id'] = int(row['killer_guild_id'])
            row['victim_id'] = int(row['victim_id'])
            row['victim_guild_id'] = int(row['victim_guild_id'])
        except Exception as e:
            log.error(e)
            return row['eventid']
        return row

    def __create_client__(self):
        try:
            self.client = Client(
                host='dbserver.lan',
                port=9000,
                database='default'
            )
            log.info(f"ClickHouse connect done. Server: {self.client.connection.server_info}")
        except ClickHouseError as e:
            log.error(f"Ошибка при подключении к ClickHouse: {e}")

# Функция для массовой вставки данных

    def insert_data(self, data_to_insert):
        if not self.client:
            log.error(f"insert_data: Клиент не создан. Вставка невозможна.")
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
            processed_data = []
            bad_rows = []
            for row in data_to_insert:
                pr = self._process_row(row)
                if isinstance(pr, dict):
                    processed_data.append(pr)
                else:
                    bad_rows.append(pr)

            if len(bad_rows) > 0:
                self.producer.send_message(message=bad_rows, key="None")
            prepared_data = [
                (
                    self.realm.name,
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
            self.client.execute(query, prepared_data)
        except ClickHouseError as e:
            log.error(f"Ошибка при вставке данных: {e}")
            raise e
        except Exception as e:
            log.error(f"Неизвестная ошибка: {e}")
            raise e


worker = EventBatchProcessor(realm=Realm.asia)
worker.do_process(100000)

