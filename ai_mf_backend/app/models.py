from django.db import models

class UserLogs(models.Model):
    """
    Model for the ``user_logs`` table. This class will be used to maintain user entry logs.
    """

    # initial
    name = models.CharField(max_length=255)
    email_id = models.EmailField(max_length=255, db_index=True)

    # ip details sent by front end
    ip_details = models.JSONField()  # To handle dynamic IP details similar to Mongo's DynamicField
    device_type = models.CharField(max_length=100)

    # time of the query response
    last_access = models.DateTimeField()
    ACTION_CHOICES = [
        ('logged_in', 'Logged In'),
        ('logged_out', 'Logged Out'),
        ('invalid', 'invalid_action'),
    ]
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        default='invalid',  # Set default to 'invalid'
    )

    class Meta:
        db_table = 'user_logs'  # Equivalent to Mongo's collection
        indexes = [
            models.Index(fields=['email_id']),
        ]

    def __str__(self):
        return self.email_id

from django.utils import timezone

class UserManagement(models.Model):
    """
    Model for the ``user_management`` table. This class will be used to maintain users.
    """

    # initial
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=255)

    # time of the query response
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_access = models.DateTimeField(null=True, blank=True)

    # At the time of account creation
    otp = models.IntegerField(null=True, blank=True)
    otp_valid_till = models.DateTimeField(null=True, blank=True)

    # When a user is verified
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_management'  # Equivalent to Mongo's collection
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email
