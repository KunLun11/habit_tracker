from django.core.management.base import BaseCommand

from analytics.kafka_consumer import habit_consumer


class Command(BaseCommand):
    help = "Запуск Kafka consumer для сохранения событий в ClickHouse"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск Kafka consumer..."))
        habit_consumer.consume()
