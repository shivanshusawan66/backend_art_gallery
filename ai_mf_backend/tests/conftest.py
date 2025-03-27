import os
import sys

import django

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)  # Use your project’s settings path

# Set up Django after setting environment variables
django.setup()
