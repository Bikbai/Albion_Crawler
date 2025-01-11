#!/usr/bin/env bash
/opt/kafka/bin/kafka-topics.sh --create --topic guild-europe --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic guild-america --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic guild-asia --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic player-europe --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic player-america --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic player-asia --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic battles-europe --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic battles-america --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic battles-asia --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic event-europe --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic event-america --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic event-asia --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic test-europe --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic test-america --bootstrap-server kafka.lan:9092 --partitions 10
/opt/kafka/bin/kafka-topics.sh --create --topic test-asia --bootstrap-server kafka.lan:9092 --partitions 10