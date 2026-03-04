import json
import logging
from datetime import date, datetime

import clickhouse_connect
from django.conf import settings
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


class HabitConsumer:
    def get_kafka_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id,
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT,
            )
            return consumer
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            raise

    def get_clickhouse_client(self):
        client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DATABASE,
            user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
        )
        return client

    def consume(self):
        logger.info("Starting Kafka consumer...")
        consumer: KafkaConsumer = self.get_kafka_consumer(
            topic="habit.completed",
            group_id="analytics_consumer_group",
        )
        logger.info("Kafka consumer created, connecting to ClickHouse...")
        client = self.get_clickhouse_client()
        logger.info("ClickHouse connected. Waiting for messages...")
        try:
            while True:
                for message in consumer:
                    logger.info(f"Received message: {message.value}")
                    event = message.value
                    if not isinstance(event, dict):
                        logger.error(f"Invalid type for event: {event}")
                        continue
                    try:
                        timestamp_str = event.get("timestamp").replace("T", " ").split(".")[0]
                        timestamp = datetime.fromisoformat(timestamp_str)
                        completed_date = date.fromisoformat(event.get("completed_date"))
                        data = [(
                            event.get("event_id"),
                            event.get("event_type"),
                            timestamp,
                            int(event.get("user_id")),
                            int(event.get("habit_id")),
                            event.get("habit_name"),
                            completed_date,
                            int(event.get("streak_before")),
                            int(event.get("streak_after")),
                            bool(event.get("is_milestone")),
                            event.get("milestone_type"),
                        )]
                        columns = [
                            "event_id", "event_type", "timestamp", "user_id", "habit_id",
                            "habit_name", "completed_date", "streak_before", "streak_after",
                            "is_milestone", "milestone_type"
                        ]
                        client.insert("habit_events", data, column_names=columns)
                        logger.info(f"Inserted event: {event.get('event_id')}")
                    except Exception as e:
                        logger.error(f"Error inserting: {type(e).__name__}: {e}")
                        continue
                    try:
                        consumer.commit()
                    except Exception as e:
                        logger.error(f"Commit failed: {e}")
        except KeyboardInterrupt:
            logger.info("Stopping consumer")
            consumer.close()
            client.close()


habit_consumer = HabitConsumer()
