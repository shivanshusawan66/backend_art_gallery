import os
import sys
import django
import random
from django.db import connection, transaction

# Setup Django environment - update this path to your project settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skti_system_backend.config.v1.django_settings")

django.setup()

from skti_system_backend.models.v1.database.gallery import Tag, Category, Artwork

def reset_and_populate(model_class, data_list, field_name):
    with transaction.atomic():
        model_class.objects.all().delete()
        print(f"Cleared existing {model_class.__name__} entries.")

        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {model_class._meta.db_table} AUTO_INCREMENT = 1;")
            print(f"Auto-increment reset for {model_class._meta.db_table}.")

        for item in data_list:
            model_class.objects.create(**{field_name: item})

    print(f"{model_class.__name__} table populated successfully.")

def populate_tags():
    tags = [
        'Abstract', 'Modern', 'Classic', 'Monochrome', 'Landscape', 'Portrait', 'Impressionism',
        'Sculpture', 'Surrealism', 'Expressionism', 'Cubism', 'Minimalism', 'Pop Art', 'Street Art',
        'Digital', 'Photorealism', 'Nature', 'Animals', 'Urban', 'Fantasy', 'Mythology', 'Black & White',
        'Colorful', 'Watercolor', 'Oil Painting', 'Acrylic', 'Ink', 'Mixed Media', 'Collage', 'Figurative'
    ]
    reset_and_populate(Tag, tags, field_name="name")

def populate_categories():
    categories = [
        'Painting', 'Sculpture', 'Photography', 'Digital Art', 'Printmaking', 'Ceramics',
        'Textile', 'Installation', 'Drawing', 'Mixed Media', 'Performance Art', 'Graffiti',
        'Glass Art', 'Conceptual Art', 'Street Photography', 'Film', 'Video Art'
    ]
    reset_and_populate(Category, categories, field_name="name")

def populate_artworks():
    with transaction.atomic():
        Artwork.objects.all().delete()
        print("Cleared existing Artwork entries.")

        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {Artwork._meta.db_table} AUTO_INCREMENT = 1;")
            print(f"Auto-increment reset for {Artwork._meta.db_table}.")

    tags_qs = list(Tag.objects.all())
    categories_qs = list(Category.objects.all())

    base_titles = [
        "Sunset Over the Hills", "Whispers of the Forest", "Urban Chaos", "Silent Reflections",
        "Faces of Time", "Metallic Dreams", "Waves of Color", "Forgotten Ruins",
        "Celestial Dance", "The Lonely Tree", "Burst of Life", "Vintage Streets",
        "Mystic Mountains", "Refraction", "The Wanderer", "Golden Horizon",
        "Dreamscape", "Neon Nights", "Serene Waters", "Flicker of Light",
        "Echoes of the Past", "Crimson Sky", "Silver Lining", "Lost in Time",
        "Dancing Shadows", "Frozen Moment", "Radiant Bloom", "Glass Maze",
        "Beyond the Veil", "Twilight Whisper"
    ]

    base_descriptions = [
        "A vivid depiction of natural beauty and light.",
        "Capturing the calm and peaceful moments in nature.",
        "Expressive and dynamic artwork inspired by city life.",
        "Reflective and serene landscape at dawn.",
        "Deep emotions portrayed through a series of faces.",
        "Modern sculpture with metal and light.",
        "Digital waves flowing in colorful harmony.",
        "Ancient ruins surrounded by nature's reclaim.",
        "Surreal cosmic bodies in movement.",
        "Minimalist representation of solitude.",
        "Vibrant burst of color and energy.",
        "Black and white classic city scenes.",
        "Misty mountains with magical ambiance.",
        "Light refraction through delicate glass art.",
        "Spirit of adventure caught in sculpture.",
        "Golden sun setting beyond the horizon.",
        "Dream-like scenes filled with imagination.",
        "City nights glowing in neon lights.",
        "Tranquil waters reflecting skies.",
        "Subtle flickers of light in darkness.",
        "Historical echoes and forgotten tales.",
        "Bright crimson sky at sunset.",
        "Optimistic silver clouds and light.",
        "Time lost in the sands of history.",
        "Shadows dancing with mystery.",
        "A frozen instant in the passage of time.",
        "Blooming flowers radiant with life.",
        "Maze of glass reflecting reality.",
        "Mystical veil hiding secrets.",
        "Soft whispers at twilight."
    ]

    for i in range(30):
        art = {
            'title': base_titles[i],
            'description': base_descriptions[i],
            'category': random.choice(categories_qs),
            'tags': random.sample(tags_qs, k=random.randint(1, 5)),
            'image_path': f'artworks/img{i+1}.jpeg',
        }
        artwork = Artwork.objects.create(
            title=art['title'],
            description=art['description'],
            category=art['category'],
            is_deleted=False,
        )
        # Assign image path string to image field name property
        artwork.image.name = art['image_path']
        artwork.tags.set(art['tags'])
        artwork.save()

    print("Artwork table populated successfully with 30 items.")

if __name__ == "__main__":
    # First delete artworks (child)
    Artwork.objects.all().delete()
    print("Deleted all artworks.")

    # Then delete tags and categories (parents)
    Tag.objects.all().delete()
    Category.objects.all().delete()
    print("Deleted all tags and categories.")

    # Reset auto-increment for all three tables
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {Artwork._meta.db_table} AUTO_INCREMENT = 1;")
        cursor.execute(f"ALTER TABLE {Tag._meta.db_table} AUTO_INCREMENT = 1;")
        cursor.execute(f"ALTER TABLE {Category._meta.db_table} AUTO_INCREMENT = 1;")
        print("Reset auto-increment keys for Artwork, Tag, and Category.")

    # Now repopulate
    populate_tags()
    populate_categories()
    populate_artworks()
