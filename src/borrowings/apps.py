import os
import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.timezone import now


class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        """Executed when the application is ready."""
        import borrowings.signals  # Import signals to ensure they are registered

        # Connects the create_periodic_task method to the post_migrate signal
        # This ensures that the task is created only after database migrations
        post_migrate.connect(self.create_periodic_task, sender=self)

    def create_periodic_task(self, **kwargs):
        """Creates or retrieves a periodic task for checking overdue borrowings."""
        from django_celery_beat.models import PeriodicTask, IntervalSchedule

        # Create or get an interval schedule that runs every day
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )

        # Create or get a periodic task that runs the check_and_update_overdue_borrowings task daily
        PeriodicTask.objects.get_or_create(
            name="Check and update overdue borrowings",
            task="borrowings.tasks.check_overdue_borrowings",
            interval=schedule,
            start_time=now(),
        )
