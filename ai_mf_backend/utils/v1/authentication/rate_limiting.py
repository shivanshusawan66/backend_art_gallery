import time
from django.core.cache import cache

from ai_mf_backend.config.v1.api_config import api_config


def throttle_otp_requests(user_id):
    """
    Throttles OTP requests based on the number of requests within a time window.

    We have added this along with IP rate limiting since a user can request too many times from diff IPs also.
    """
    cache_key = f"otp_requests_{user_id}"
    request_timestamps = cache.get(cache_key, [])

    # Clean up old timestamps
    current_time = time.time()
    request_timestamps = [
        t
        for t in request_timestamps
        if current_time - t < api_config.THROTTLE_WINDOW_SECONDS
    ]

    if len(request_timestamps) >= api_config.MAX_OTP_REQUESTS:
        return (
            False,
            f"Too many OTP requests. Try again after {api_config.THROTTLE_WINDOW_SECONDS - int(current_time - request_timestamps[0])} seconds.",
        )

    # Add current timestamp and update the cache
    request_timestamps.append(current_time)
    cache.set(cache_key, request_timestamps, timeout=api_config.THROTTLE_WINDOW_SECONDS)

    return True, None
