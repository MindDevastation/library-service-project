from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.timezone import now

class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        import borrowings.signals

        post_migrate.connect(self.create_periodic_task, sender=self)

    def create_periodic_task(self):

        from borrowings.tasks import check_and_update_overdue_borrowings

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )

        PeriodicTask.objects.get_or_create(
            name="Check and update overdue borrowings",
            task="borrowings.tasks.check_and_update_overdue_borrowings",
            interval=schedule,
            start_time=now(),
        )
