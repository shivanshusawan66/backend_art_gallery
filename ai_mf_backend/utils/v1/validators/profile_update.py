from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import models
import logging

logger = logging.getLogger(__name__)

# Updated validation function to consider both time and modification count
def validate_profile_modification_time(instance):
    """
    Validator to restrict profile modification within a defined period and number of changes.
    Users can only modify their profile a limited number of times in a 7-day window.
    """
    max_changes_per_window = 3  # Maximum allowed changes in 7 days
    restriction_period = timedelta(days=7)  # 7-day window

    # Ensure the instance has an `update_date` and `modification_count`
    if not instance.pk or not instance.modification_count :
        return

    # Calculate the time since the last update
    time_since_last_update = timezone.now() - instance.update_date

    # Check if the time since the last update is within the 7-day window
    if time_since_last_update < restriction_period:
        if instance.modification_count >= max_changes_per_window:
            days_left = (restriction_period - time_since_last_update).days
            raise ValidationError(
                f"You can only change your profile {max_changes_per_window} times in a 7-day window. "
                f"You have used up your {max_changes_per_window} changes, please try again after {days_left} days."
            )
    else:
        instance.modification_count = 0  # Reset modification count after the 7-day window


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