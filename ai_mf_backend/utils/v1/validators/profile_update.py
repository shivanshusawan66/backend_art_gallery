import logging
from datetime import timedelta
from asgiref.sync import sync_to_async

from django.core.exceptions import ValidationError
from django.utils import timezone

from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.config.v1.api_config import api_config

logger = logging.getLogger(__name__)


# Updated validation function to consider both time and modification count
async def validate_profile_modification_time(instance):
    """
    Validator to restrict profile modification within a defined period and number of changes.
    Validates if the user has exceeded the allowed changes in a time zone window
    """
    
    
    max_changes = api_config.MAX_CHANGES_PER_WINDOW
    window_days = api_config.CHANGES_WINDOW
    restriction_period = timedelta(days=window_days)

    # Calculate the start time of the sliding window (now - window_days)
    start_time = timezone.now() - restriction_period

    # Count profile updates within the window
    change_count = await sync_to_async(
    UserLogs.objects.filter(
        user_id=instance.user_id,
        action="profile_update",
        last_access__gte=start_time
    ).count
    )()

    if change_count >= max_changes:
        oldest_log = await sync_to_async(
        UserLogs.objects.filter(
            user_id=instance.user_id,
            action="profile_update",
            last_access__gte=start_time
        ).order_by("last_access").first
        )()

        next_allowed_time = oldest_log.last_access + restriction_period
        next_time_formatted = next_allowed_time.strftime("%Y-%m-%d at %H:%M:%S")
        raise ValidationError(
            f"You have reached the maximum number of profile updates allowed within a "
            f"{window_days}-day period. Your next update will be permitted on {next_time_formatted}. "
            "Please try again after that time."
        )
    else:
        return True
