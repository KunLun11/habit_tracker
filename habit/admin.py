from django.contrib import admin
from unfold.admin import ModelAdmin

from habit.models.habits import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(ModelAdmin):
    list_display = ("user", "name", "target_streak", "is_active")
    list_filter = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(HabitLog)
class HabitLogAdmin(ModelAdmin):
    list_display = ("habit", "completed_at", "note")
    list_filter = ("habit",)
    readonly_fields = ("completed_at", "completed_date")
