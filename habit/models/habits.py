from django.db import models

from base.models.bases import BaseModelID, BaseModelIDTime


class Habit(BaseModelIDTime):
    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    user = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits",
    )
    name = models.CharField("Название", max_length=125)
    description = models.TextField("Описание", blank=True)
    target_streak = models.PositiveSmallIntegerField("Цель(дней)", default=21)
    current_streak = models.PositiveSmallIntegerField("Текущая серия", default=0)
    best_streak = models.PositiveSmallIntegerField("Лучшая серия", default=0)
    total_completions = models.PositiveSmallIntegerField("Всего выполнений", default=0)
    is_active = models.BooleanField("Активна", default=True)

    def __str__(self):
        return self.name


class HabitLog(BaseModelID):
    class Meta:
        verbose_name = "Выполнение"
        verbose_name_plural = "Выполнения"

    habit = models.ForeignKey(
        "habit.Habit",
        on_delete=models.CASCADE,
        verbose_name="Привычка",
        related_name="habit_logs",
    )
    completed_at = models.DateTimeField("Отмечено в")
    completed_date = models.DateField("Дата отметки", db_index=True)
    note = models.TextField("Заметка", blank=True)
    mood = models.CharField("Самочувствие", blank=True)
