from django.db import models
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database import SoftDeleteModel


class UserLogs(SoftDeleteModel):
    user = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_details = models.JSONField(null=True, blank=True)
    device_type = models.CharField(max_length=100, null=True, blank=True)
    last_access = models.DateTimeField()
    ACTION_CHOICES = [
        ("login", "Logged In"),
        ("logged_out", "Logged Out"),
        ("signup", "Signed Up"),
        ("profile_update", "Profile Updated"),
        ("invalid", "invalid_action"),
    ]
    action = models.CharField(
        max_length=15,
        choices=ACTION_CHOICES,
        default="invalid",  # Set default to 'invalid'
    )

    class Meta:
        db_table = "user_logs"
        indexes = [
            models.Index(fields=["user"]),
        ]
        verbose_name = "User Logs"
        verbose_name_plural = "User Logs"

    def __str__(self):
        return str(self.user)
