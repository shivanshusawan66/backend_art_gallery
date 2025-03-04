import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from ai_mf_backend.config.v1.api_config import api_config

logger = logging.getLogger(__name__)


# Updated validation function to consider both time and modification count
def validate_profile_modification_time(instance):
    """
    Validator to restrict profile modification within a defined period and number of changes.
    Validates if the user has exceeded the allowed changes in a sliding window.
    """
    from ai_mf_backend.models.v1.database.user_authentication import UserLogs
    
    max_changes = api_config.MAX_CHANGES_PER_WINDOW
    window_days = api_config.CHANGES_WINDOW
    restriction_period = timedelta(days=window_days)

    # Safety check
    if not instance.pk:
        return

    # Calculate the start time of the sliding window (now - window_days)
    start_time = timezone.now() - restriction_period

    # Count profile updates within the window
    change_count = UserLogs.objects.filter(
        user=instance.user,
        action="profile_update",
        last_access__gte=start_time
    ).count()

    if change_count >= max_changes:
        # Find the oldest entry in the current window
        oldest_log = UserLogs.objects.filter(
            user=instance.user,
            action="profile_update",
            last_access__gte=start_time
        ).order_by("last_access").first() 

        if oldest_log:
            # Calculate when the next change is allowed
            next_allowed_time = oldest_log.last_access + restriction_period
            time_remaining = next_allowed_time - timezone.now()
            days_remaining = max(1, time_remaining.days + 1)  # Ceiling to whole days
            raise ValidationError(
                f"You can only change your profile {max_changes} times in a {window_days}-day window. "
                f"Try again in {days_remaining} days."
            )
        else:
            raise ValidationError("Maximum changes reached.")


def track_changes(old_instance, new_instance, fields_to_track):
    """
    Compare specified fields in the old and new instance to track changes.
    Returns a dictionary of changed fields with old and new values.
    """
    changed_fields = {}
    for field in fields_to_track:
        old_value = getattr(old_instance, field)
        new_value = getattr(new_instance, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
    return changed_fields
