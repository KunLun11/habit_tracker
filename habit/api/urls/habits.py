from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habit.api.views.habits import HabitLogViewSet, HabitViewSet

router = DefaultRouter()
router.register("", HabitViewSet, basename="habit")
router.register("habit-log", HabitLogViewSet, basename="habit_log")

habit_urlpatterns = [
    path("", include((router.urls, "habit"))),
]
