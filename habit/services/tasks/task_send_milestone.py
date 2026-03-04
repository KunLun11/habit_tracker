from django.conf import settings
from django.core.mail import send_mail

from config.celery import celery_app


@celery_app.task(queue="main")
def send_milestone_notification(
    email: str,
    user_id: int,
    habit_id: int,
    habit_name: str,
    milestone_type: str,
    new_streak: int,
):
    if milestone_type == "weekly":
        subject = f"Недельная серия: {new_streak} дней"
    elif milestone_type == "target":
        subject = f"Цель достигнута: {new_streak} дней"
    elif milestone_type == "yearly":
        subject = f"Годовая серия: {new_streak} дней"
    else:
        subject = f"{new_streak} дней подряд"
    message = f"{new_streak} дней вы выполняете'{habit_name}'"
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
