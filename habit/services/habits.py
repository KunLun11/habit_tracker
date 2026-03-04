# from habit.services.tasks.task_send_milestone import send_milestone_notification
import logging
from datetime import timedelta

from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from account.models.users import CustomUser
from analytics.kafka_producer import habit_producer
from habit.models.habits import Habit, HabitLog

logger = logging.getLogger(__name__)


class HabitManager:
    @staticmethod
    def _get_base_queryset(user: CustomUser):
        return Habit.objects.filter(user=user, is_active=True)

    @staticmethod
    def create_habit(
        user: CustomUser,
        name: str,
        description=None,
        **extra_fields,
    ):
        name = name.strip()
        if not name:
            raise ValidationError()
        if Habit.objects.filter(user=user, name__iexact=name, is_active=True).exists():
            raise ValidationError("Привычка с таким названием уже есть")
        if Habit.objects.filter(user=user, is_active=True).count() >= 20:
            raise ValidationError("Добавлено уже максимальное количество привычек")
        habit = Habit.objects.create(
            user=user,
            name=name,
            description=description,
            target_streak=extra_fields.get("target_streak", 21),
            is_active=True,
        )
        return habit

    @classmethod
    def list_user_habits(cls, user: CustomUser):
        today = timezone.now().date()
        return cls._get_base_queryset(user).annotate(
            is_completed_today=Exists(
                HabitLog.objects.filter(
                    habit=OuterRef("pk"),
                    completed_date=today,
                )
            )
        )

    @classmethod
    def checkin(
        cls,
        habit_id: int,
        user: CustomUser,
        note=None,
        mood=None,
    ):
        habit: Habit = Habit.objects.filter(id=habit_id).first()
        if habit.user != user:
            raise NotFound
        if not habit.is_active:
            raise ValidationError("Привычка не активна")
        today = timezone.now().date()
        if HabitLog.objects.filter(habit=habit, completed_date=today).exists():
            raise ValidationError("Уже отмечено сегодня")
        last_log: HabitLog = (
            HabitLog.objects.filter(habit=habit).order_by("-completed_date").first()
        )
        if not last_log:
            new_streak = 1
        elif last_log.completed_date == today - timedelta(days=1):
            new_streak = habit.current_streak + 1
        else:
            new_streak = 1
        habit_log = HabitLog.objects.create(
            habit=habit,
            completed_at=timezone.now(),
            completed_date=today,
            note=note or "",
            mood=mood or "",
        )
        streak_before = habit.current_streak
        habit.current_streak = new_streak
        habit.best_streak = max(habit.best_streak, new_streak)
        habit.total_completions += 1
        habit.save()
        milestone_type = None
        if new_streak == habit.target_streak:
            milestone_type = "target"
        elif new_streak == 7:
            milestone_type = "weekly"
        elif new_streak % 365 == 0:
            milestone_type = "yearly"
        else:
            None
        # if milestone_type:
        #     send_milestone_notification.delay(
        #         user.email,
        #         user.id,
        #         habit.id,
        #         habit.name,
        #         milestone_type,
        #         new_streak,
        #     )
        try:
            habit_producer.send_habit_completed(
                user_id=user.id,
                habit_id=habit.id,
                habit_name=habit.name,
                completed_date=today,
                streak_after=new_streak,
                streak_before=streak_before,
                is_milestone=milestone_type is not None,
                milestone_type=milestone_type,
            )
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}")

        message = None
        if milestone_type:
            message = f"Поздравляем! Вы достигли цели: {new_streak} дней подряд!"

        return {
            "id": habit_log.id,
            "habit_id": habit.id,
            "habit_name": habit.name,
            "completed_at": habit_log.completed_at,
            "completed_date": habit_log.completed_date,
            "streak_before": streak_before,
            "streak_after": new_streak,
            "is_milestone": milestone_type is not None,
            "milestone_type": milestone_type,
            "message": message,
        }
