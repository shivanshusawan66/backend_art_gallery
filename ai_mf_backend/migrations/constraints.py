from django.db import connection, migrations
from django.utils import timezone

def set_user_personal_details_constraints(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # Date constraints to prevent future dates
            cursor.execute("""
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_dob_not_future
                CHECK (date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE);
            """)
            cursor.execute("""
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_add_date_not_future
                CHECK (add_date IS NULL OR add_date <= CURRENT_TIMESTAMP);
            """)
            cursor.execute("""
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_update_date_not_future
                CHECK (update_date IS NULL OR update_date <= CURRENT_TIMESTAMP);
            """)

            # Constraint to ensure `name` is not null or empty
            cursor.execute("""
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_name_not_empty
                CHECK (name IS NOT NULL AND TRIM(name) <> '');
            """)

        except Exception as e:
            connection.rollback()
            print(f"Error applying constraints: {e}")

class Migration(migrations.Migration):
    dependencies = [
        # Add the migration file on which this depends
        # Example: ('myapp', '0001_initial'),
        ('ai_mf_backend', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(set_user_personal_details_constraints),
    ]
