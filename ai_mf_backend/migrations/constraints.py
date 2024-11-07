from django.db import connection, migrations


def set_user_personal_details_saving_category_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # Alphanumeric constraint for `saving_category`
            cursor.execute("""
                ALTER TABLE monthly_saving_capacity
                ADD CONSTRAINT user_personal_details_saving_category_alphanumeric
                CHECK (saving_category ~ '^[A-Za-z0-9\\s]+$');
            """)
        except Exception as e:
            connection.rollback()
            print(f"Error applying saving_category constraint: {e}")

class Migration(migrations.Migration):
    dependencies = [
        # Add the migration file on which this depends
        # Example: ('myapp', '0001_initial'),
        ('ai_mf_backend', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(set_user_personal_details_saving_category_constraint),
    ]
