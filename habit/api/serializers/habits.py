from rest_framework import serializers

from account.api.account.serializers.my import CustomUserSerializer
from habit.models.habits import Habit, HabitLog
from habit.services.habits import HabitManager


class HabitListSerializer(serializers.ModelSerializer):
    included_serializers = {"user": CustomUserSerializer}
    is_completed_today = serializers.BooleanField(read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "name",
            "description",
            "target_streak",
            "current_streak",
            "best_streak",
            "total_completions",
            "is_active",
            "is_completed_today",
            "user",
        )

    class JSONAPIMeta:
        included_resources = ("user",)


class HabitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ("name", "description", "target_streak")

    def create(self, validated_data):
        user = self.context["request"].user
        return HabitManager.create_habit(user=user, **validated_data)


class HabitCheckinSerializer(serializers.Serializer):
    note = serializers.CharField(allow_blank=True, required=False, write_only=True)
    mood = serializers.CharField(allow_blank=True, required=False, write_only=True)
    id = serializers.IntegerField(read_only=True)
    habit_id = serializers.IntegerField(read_only=True)
    habit_name = serializers.CharField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    completed_date = serializers.DateField(read_only=True)
    streak_before = serializers.IntegerField(read_only=True)
    streak_after = serializers.IntegerField(read_only=True)
    is_milestone = serializers.BooleanField(read_only=True)
    milestone_type = serializers.CharField(allow_null=True, read_only=True)
    message = serializers.CharField(required=False, read_only=True)

    def create(self, validated_data):
        user = self.context["request"].user
        habit_id = self.context["view"].kwargs.get("pk")
        note = validated_data.get("note")
        mood = validated_data.get("mood")
        return HabitManager.checkin(
            habit_id=habit_id,
            user=user,
            note=note,
            mood=mood,
        )


class HabitLogSerializer(serializers.ModelSerializer):
    included_serializers = {"habit": HabitListSerializer}

    class Meta:
        model = HabitLog
        fields = ("id", "habit", "completed_at", "completed_date", "note", "mood")
