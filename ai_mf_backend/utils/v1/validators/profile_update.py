from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def validate_profile_modification_time(instance):
    """
    Validator to restrict profile modification within a defined period.
    Users can only modify their profile after a specified number of days
    have passed since the last update.
    """
    restriction_period = timedelta(days=10)

    if instance.update_date is None:
        return

    time_since_last_update = timezone.now() - instance.update_date

    if time_since_last_update < restriction_period:
        days_left = (restriction_period - time_since_last_update).days
        raise ValidationError(
            f"You can change your credentials after {days_left} days."
        )


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
