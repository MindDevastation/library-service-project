from django.contrib.auth import get_user_model
from django.db import models


class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10)
    message = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    request_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.message[:50]}"


class ActionLog(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} (ID: {self.object_id}) at {self.timestamp}"
