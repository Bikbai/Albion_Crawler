from unittest import TestCase
from kafka import KafkaProducer, KafkaConsumer, TX_Scope, gen_topics, Topic
from constants import Realm, EntityType, LOGGER_NAME
import json
import logging

log = logging.getLogger(LOGGER_NAME)
log.setLevel(level=logging.DEBUG)

class TestKafkaProducer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = KafkaProducer(realm=Realm.europe, entity=EntityType.test)
        cls.consumer = KafkaConsumer(realm=Realm.europe, entity=EntityType.test)

    def test_topic(self):
        s = Topic(Realm.europe, EntityType.test)
        self.assertEqual(str(s), 'test-europe')

    def test_send_consume(self):
        i = 0
        j = json.loads(f'{{"key": "value", "key2": {i}}}')
        self.producer.send_message(message=j, key=i, tx_scope=TX_Scope.TX_INTERNAL_COMMIT)
        nj = self.consumer.get()
        self.assertEqual(str(j), str(nj))

    def test_produce(self):
        i = 0
        for i in range(0, 9):
            j = json.loads(f'{{"key": "value", "key2": {i}}}')
            self.producer.send_message(message=j, key=i, tx_scope=TX_Scope.TX_INTERNAL_COMMIT)
        j = 0
        nj = 0
        self.assertEqual(str(j), str(nj))

    def test_single_consume(self):
        nj = self.consumer.get()
        print(nj["key2"])
        self.assertTrue(False)


    def test_multiple_consume(self):
        i = 0
        while True:
            nj = self.consumer.get()
            if nj is None:
                break
            self.consumer.commit()
            print(nj)
            i += 1
        print(i)

    def test_gen_script(self):
        gen_topics()
        self.assertTrue(True)