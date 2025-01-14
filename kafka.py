import json
import uuid
from enum import Enum

from confluent_kafka import Producer, Consumer, KafkaError, KafkaException, Message, TopicPartition
from confluent_kafka.admin import TopicMetadata
from confluent_kafka.serialization import StringSerializer, StringDeserializer
from constants import Realm, EntityType, LOGGER_NAME
from utility import timer_decorator

import logging
log = logging.getLogger(LOGGER_NAME)

base_config = {
    'bootstrap.servers': 'kafka.lan:9092'
}

producer_config = base_config.copy()

producer_config.update(
    {
        'enable.idempotence': str(True),
        'transaction.timeout.ms': '600000'
     }
)

consumer_config = base_config.copy()
consumer_config.update(
    {"group.id": "main.processor.v4",
     'auto.offset.reset': 'earliest',
     'session.timeout.ms': 6000,
     'enable.auto.offset.store': False}) #коммит руками

class TX_Scope(Enum):
    TX_INTERNAL_ROLLBACK = 0,
    TX_INTERNAL_COMMIT = 1,
    TX_EXTERNAL = 2


class KafkaProducer:
    def delivery_callback(self, err: KafkaError, msg: Message):
        if err:
            if err.code() == err._PURGE_QUEUE:
                log.info(f'Message {msg.key()} rolled back from topic {msg.topic()}')
            else:
                log.error(f'Message {msg.key()} delivery failed to topic {msg.topic()}')
        else:
            log.debug('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))

    def __init__(self, realm: Realm, entity: EntityType):
        message_id = uuid.uuid4()
        self.partition_id = 0
        producer_config.update({'transactional.id': f'tx-{int(uuid.uuid4())}'})
        self.__producer = Producer(producer_config)
        self.__producer.init_transactions()
        self.__topic = f'{entity.name}-{realm.name}'
        self.__max_partitions = 1
        #log.info(f"Kafka producer init started, generating test message with {message_id}")
        #tmp_consumer = Consumer(consumer_config)
        #tm: TopicMetadata = tmp_consumer.list_topics(topic=self.__topic).topics.get(self.__topic)
        #self.__max_partitions = len(tm.partitions)
        #self.send_message("test data", message_id, TX_Scope.TX_INTERNAL_ROLLBACK)
        #tmp_consumer.close()
        log.info("Kafka producer init done, test message rolled back")

    def begin_tran(self):
        self.__producer.begin_transaction()

    def commit_tran(self):
        self.__producer.commit_transaction()

    def rollback_tran(self):
        self.__producer.abort_transaction()

    def _get_next_partition_id(self):
        self.partition_id += 1
        if self.partition_id > self.__max_partitions - 1:
            self.partition_id = 0
        return self.partition_id

    def __del__(self):
        self.__producer.flush()

    def info(self):
        return f'topic: {self.__topic}'

    @timer_decorator(logger=log)
    def send_message(self, message, key, tx_scope: TX_Scope = TX_Scope.TX_INTERNAL_ROLLBACK):
        if isinstance(message, dict):
            payload = json.dumps(message).encode('utf-8')
        elif isinstance(message, str):
            payload = message.encode('utf-8')
        else:
            msg = f"Not supported type {type(message)} of payload: {message}"
            log.error(msg)
            raise NotImplementedError(msg)
        if tx_scope != tx_scope.TX_EXTERNAL:
            self.__producer.begin_transaction()
        self.__producer.produce(
            self.__topic,
            value=payload,
            key=str(key),
            callback=self.delivery_callback,
            partition=self._get_next_partition_id())
        if tx_scope == tx_scope.TX_INTERNAL_ROLLBACK:
            self.__producer.abort_transaction()
        elif tx_scope == tx_scope.TX_INTERNAL_COMMIT:
            self.__producer.commit_transaction()
        self.__producer.flush()


class KafkaConsumer:
    def __init__(self, realm: Realm, entity: EntityType):
        log.info("Kafka consumer init started")
        self.__consumer = Consumer(consumer_config)
        self.__topic = f'{entity.name}-{realm.name}'
        self.__consumer.subscribe([self.__topic])
        self.__tp = TopicPartition(topic=self.__topic)
        self.__consumer.memberid()
        log.info("Kafka producer init done")

    def get_topic(self):
        return self.__topic

    def __del__(self):
        self.__consumer.close()

    @timer_decorator(logger=log)
    def get(self):
        msg = self.__consumer.poll()
        if msg is None:
            return None
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                log.error(f'{msg.topic()}: {msg.partition()} reached end at offset {msg.offset()}')
                return None
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            self.__tp.offset = msg.offset()
            self.__tp.partition = msg.partition()
            j = json.loads(msg.value().decode('utf-8'))
            self.__consumer.store_offsets(msg)
            return j

    def commit(self):
        self.__consumer.commit(offsets=[self.__tp])

def gen_topics():
    for e in EntityType:
        for r in Realm:
            str = f'/opt/kafka/bin/kafka-topics.sh \
--create \
--topic {e.name}-{r.name} \
--bootstrap-server kafka.lan:9092 \
--partitions {10}'
            print(str)
