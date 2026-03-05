import json
import logging
import uuid
from datetime import date, datetime

from kafka import KafkaProducer

logger = logging.getLogger("main")


class HabitProducer:
    def __init__(self):
        self.producer = None

    def send_habit_completed(
        self,
        user_id: int,
        habit_id: int,
        habit_name: str,
        completed_date: date,
        streak_before: int,
        streak_after: int,
        is_milestone: bool,
        milestone_type: str | None,
    ):
        if self.producer is None:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=["localhost:9092"],
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    retries=5,
                    linger_ms=10,
                    max_request_size=1048576,
                )
            except Exception as e:
                logger.error(f"Failed to create producer: {e}")
                raise
        producer = self.producer
        payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": "habit_complete",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "habit_id": habit_id,
            "habit_name": habit_name,
            "completed_date": completed_date.isoformat()
            if isinstance(completed_date, date)
            else completed_date,
            "streak_before": streak_before,
            "streak_after": streak_after,
            "is_milestone": is_milestone,
            "milestone_type": milestone_type,
        }
        producer.send("habit.completed", key=str(user_id), value=payload)
        producer.flush()


habit_producer = HabitProducer()
