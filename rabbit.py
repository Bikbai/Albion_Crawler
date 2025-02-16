import logging
import time

import pika
import json

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from constants import EntityType, Realm
from constants import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

topic_suffix_map = {
    EntityType.guild: 'guild',
    EntityType.player: 'player',
    EntityType.battles: 'battles',
    EntityType.event: 'event',
    EntityType.test:  'test',
    EntityType.battlebatch: 'battlebatch',
    EntityType.eventbatch: 'eventbatch',
    EntityType.item: 'item'
}

class Topic:
    topic_suffix_map = {
        EntityType.guild: 'guild',
        EntityType.player: 'player',
        EntityType.battles: 'battles',
        EntityType.event: 'event',
        EntityType.test: 'test',
        EntityType.battlebatch: 'battlebatch',
        EntityType.eventbatch: 'eventbatch',
        EntityType.item: 'item'
    }
    def get_topic_name(self, realm: Realm, entity: EntityType| str):
        if isinstance(entity, EntityType):
            suffix = topic_suffix_map.get(entity)
            if suffix is None:
                raise Exception(f'Requested topic for unknown entity {entity.name}')
            return f'{realm.name}-{suffix}'
        else:
            return f'{realm.name}-{entity}'


class RabbitMQClient(Topic):
    def __init__(self, realm: Realm, topic: EntityType | str, host='kafka.lan', port=5672, username='admin', password='qwerty'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = super(RabbitMQClient, self).get_topic_name(realm, topic)
        self.connection: BlockingConnection|None = None
        self.channel: BlockingChannel|None = None
        self.unacked_delivery_tags = []

    def ack(self):
        for dt in self.unacked_delivery_tags:
            self.channel.basic_ack(delivery_tag=dt)
            self.unacked_delivery_tags.pop()

    def connect(self):
        """Установка соединения с RabbitMQ"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def disconnect(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_open:
            self.connection.close()

    def send_message(self, message, headers: dict, queue=None):
        """Отправка сообщения в очередь"""
        if not self.connection or not self.connection.is_open:
            self.connect()

        queue_to_use = queue if queue else self.queue_name
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_to_use,
            body=json.dumps(message).encode(encoding='UTF-8'),
            properties=pika.BasicProperties(delivery_mode=2, headers=headers)  # делаем сообщение устойчивым
        )
        #print(f" [x] Sent {message}")

    def receive_messages(self, callback, queue=None):
        """Получение сообщений из очереди"""
        if not self.connection or not self.connection.is_open:
            self.connect()

        queue_to_use = queue if queue else self.queue_name

        def _callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                callback(data)
            except Exception as e:
                log.error(f"Error processing message: {e}")
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=queue_to_use, on_message_callback=_callback)
        self.channel.start_consuming()

    def get_one_message(self, queue=None, auto_ack=True):
        """Получить одно сообщение из очереди"""
        if not self.connection or not self.connection.is_open:
            self.connect()

        queue_to_use = queue if queue else self.queue_name
        method_frame: Basic.GetOk | None
        header_frame: BasicProperties | None
        body: bytes | None
        sleep_time = 0
        max_sleep_time = 60
        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=queue_to_use, auto_ack=auto_ack)
            if method_frame:
                self.unacked_delivery_tags.append(method_frame.delivery_tag)
                s = body.decode("UTF-8")
                return s
            else:
                sleep_time = sleep_time + 1 if sleep_time < max_sleep_time else max_sleep_time
                log.info(f"No message returned, sleeping for {sleep_time} s")
                time.sleep(sleep_time)
                continue

# Пример использования:

if __name__ == '__main__':
    rabbitmq_client = RabbitMQClient(host='kafka.lan', queue_name='test_queue')

    # Отправка сообщения
    rabbitmq_client.send_message({"key": "value"})
    def process_message(message):
        print(f"Received: {message}")

    rabbitmq_client.receive_messages(process_message)

    # Или получение одного сообщения
    message = rabbitmq_client.get_one_message()
    if message:
        print(f"Single message received: {message}")

    rabbitmq_client.disconnect()