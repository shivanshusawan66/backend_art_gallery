import os
import uuid

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4()}{ext}"