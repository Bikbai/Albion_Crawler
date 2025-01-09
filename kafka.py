
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from confluent_kafka.serialization import StringSerializer
from constants import Realm, EntityType, LOGGER_NAME

import logging
log = logging.getLogger(LOGGER_NAME)

config = {
    'bootstrap.servers': 'kafka.lan:9092'
}

consumer_config = config.copy()
consumer_config.update({"group.id":"main.processor"})

class KafkaProducer:
    def __init__(self, realm: Realm, entity: EntityType):
        log.info("Kafka producer init started")
        self.__producer = Producer(config)
        self.__topic = f'{entity.name}-{realm.name}'
        self.string_serializer = StringSerializer('utf_8')
        log.info("Kafka producer init done")

    def __del__(self):
        self.__producer.flush()

    def info(self):
        return f'topic: {self.__topic}'

    def send_message(self, message, key):
        self.__producer.produce(
            self.__topic,
            value=self.string_serializer(str(message)),
            key=self.string_serializer(str(key)))
        self.__producer.flush()


class KafkaConsumer:
    def __init__(self, realm: Realm, entity: EntityType):
        log.info("Kafka producer init started")
        self.__consumer = Consumer(consumer_config)
        self.__topic = f'{entity.name}-{realm.name}'
        self.string_serializer = StringSerializer('utf_8')
        self.__consumer.subscribe([self.__topic])
        log.info("Kafka producer init done")

    def __del__(self):
        self.__consumer.close()

    def get(self):
        msg = self.__consumer.poll(timeout=1.0)
        if msg is None:
            return None
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                log.error(f'{msg.topic()}: {msg.partition()} reached end at offset {msg.offset()}')
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            return msg.value().decode('utf-8')


def gen_topics():
    for e in EntityType:
        for r in Realm:
            print(f'/opt/kafka/bin/kafka-topics.sh --create --topic {e.name}-{r.name} --bootstrap-server kafka.lan:9092')
