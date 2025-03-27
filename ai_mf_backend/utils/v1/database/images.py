from django.core.exceptions import ValidationError

def validate_image_size(file):
    max_size = 2 * 1024 * 1024  # 2 MB limit
    if file.size > max_size:
        raise ValidationError("The image size exceeds the maximum allowed limit of 2MB.")