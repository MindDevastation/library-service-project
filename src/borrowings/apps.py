from django.apps import AppConfig
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.timezone import now
from borrowings.tasks import check_overdue_borrowings

class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        import borrowings.signals

        self.create_periodic_task()

    def create_periodic_task(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )

        PeriodicTask.objects.get_or_create(
            name="Check overdue borrowings",
            task="borrowings.tasks.check_overdue_borrowings",
            interval=schedule,
            start_time=now(),
        )