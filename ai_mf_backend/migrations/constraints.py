from django.db import connection, migrations


def create_update_date_triggers(apps, schema_editor):
    # Dynamically retrieve all model names
    models = apps.get_models()
    for model in models:
        table_name = model._meta.db_table  # Get table name for each model
        fields = [f.name for f in model._meta.fields]
        if "update_date" in fields:
            schema_editor.execute(
                f"""
                CREATE OR REPLACE FUNCTION update_timestamp() 
                RETURNS TRIGGER AS $$
                BEGIN
                   NEW.update_date = NOW();
                   RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_update_date
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW EXECUTE FUNCTION update_timestamp();
            """
            )


def set_marital_status_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        # Fetch tables that have a marital_status column
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name = 'marital_status'
              AND table_schema = 'public'
            GROUP BY table_name;
        """
        )
        tables = cursor.fetchall()

        # Regular expression pattern to allow only alphabetic characters and spaces
        # pattern = r"^[A-Za-z\s]+$"

        # Iterate over tables to apply CHECK constraint
        for (table,) in tables:
            try:
                # Check if the marital_status column exists in the current table
                cursor.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table}' 
                      AND column_name = 'marital_status';
                """
                )
                columns = {col[0] for col in cursor.fetchall()}

                # Apply the CHECK constraint only if the marital_status column is found
                if "marital_status" in columns:
                    cursor.execute(
                        f"""
                        ALTER TABLE {table}
                        ADD CONSTRAINT {table}_marital_status_check
                        CHECK (marital_status ~ '^[A-Za-z\\s]+$' AND marital_status IS NOT NULL AND TRIM(marital_status) <> '');
                    """
                    )
            except Exception as e:
                # Rollback transaction to continue with the next table if an error occurs
                connection.rollback()
                print(f"Skipping {table} due to error: {e}")


def set_default_dates_deleted(apps, schema_editor):
    with connection.cursor() as cursor:
        # Fetch tables that have relevant columns
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name IN ('add_date', 'update_date', 'deleted')
              AND table_schema = 'public'
            GROUP BY table_name;
        """
        )
        tables = cursor.fetchall()

        # Iterate over tables
        for (table,) in tables:
            try:
                # Check if each column exists in the current table before altering it
                cursor.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table}' 
                      AND column_name IN ('add_date', 'update_date', 'deleted');
                """
                )
                columns = {col[0] for col in cursor.fetchall()}

                # Prepare ALTER statements based on existing columns
                alter_statements = []
                if "add_date" in columns:
                    alter_statements.append("ALTER COLUMN add_date SET DEFAULT NOW()")
                if "update_date" in columns:
                    alter_statements.append(
                        "ALTER COLUMN update_date SET DEFAULT NOW()"
                    )
                if "deleted" in columns:
                    alter_statements.append("ALTER COLUMN deleted SET DEFAULT FALSE")

                # If there are statements to execute, proceed with ALTER
                if alter_statements:
                    cursor.execute(
                        f"ALTER TABLE {table} {', '.join(alter_statements)};"
                    )
            except Exception as e:
                # Rollback transaction to continue with next table
                connection.rollback()
                print(f"Skipping {table} due to error: {e}")


def set_user_personal_details_constraints(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # Date constraints to prevent future dates
            cursor.execute(
                """
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_dob_not_future
                CHECK (date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE);
            """
            )
            cursor.execute(
                """
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_add_date_not_future
                CHECK (add_date IS NULL OR add_date <= CURRENT_TIMESTAMP);
            """
            )
            cursor.execute(
                """
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_update_date_not_future
                CHECK (update_date IS NULL OR update_date <= CURRENT_TIMESTAMP);
            """
            )

            # Constraint to ensure `name` is not null or empty
            cursor.execute(
                """
                ALTER TABLE user_personal_details
                ADD CONSTRAINT user_personal_details_name_not_empty
                CHECK (name IS NOT NULL AND TRIM(name) <> '');
            """
            )

        except Exception as e:
            connection.rollback()
            print(f"Error applying constraints: {e}")


def set_gender_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        # Fetch tables that have a gender column
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name = 'gender'
              AND table_schema = 'public'
            GROUP BY table_name;
        """
        )
        tables = cursor.fetchall()

        # Iterate over tables to apply CHECK constraint
        for (table,) in tables:
            try:
                # Check if the gender column exists in the current table
                cursor.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table}' 
                      AND column_name = 'gender';
                """
                )
                columns = {col[0] for col in cursor.fetchall()}

                # Apply the CHECK constraint only if the gender column is found
                if "gender" in columns:
                    cursor.execute(
                        f"""
                        ALTER TABLE {table}
                        ADD CONSTRAINT {table}_gender_check
                        CHECK (gender ~ '^[A-Za-z\\s]+$' AND gender IS NOT NULL AND TRIM(gender) <> '');
                    """
                    )
            except Exception as e:
                # Rollback transaction to continue with the next table if an error occurs
                connection.rollback()
                print(f"Skipping {table} due to error: {e}")


def add_case_insensitive_unique_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        # Adding a unique index with a case-insensitive function
        cursor.execute(
            """
            CREATE UNIQUE INDEX gender_name_unique_ci 
            ON gender (UPPER(gender));
        """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX occupation_unique_ci 
            ON occupation (UPPER(occupation));
        """
        )


def set_income_category_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        # Fetch tables that have a marital_status column
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name = 'income_category'
              AND table_schema = 'public'
            GROUP BY table_name;
        """
        )
        tables = cursor.fetchall()

        # Regular expression pattern to allow only alphabetic characters and spaces
        # pattern = r"^\d+\s*-\s*\d+$"

        # Iterate over tables to apply CHECK constraint
        for (table,) in tables:
            try:
                # Check if the marital_status column exists in the current table
                cursor.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table}' 
                      AND column_name = 'income_category';
                """
                )
                columns = {col[0] for col in cursor.fetchall()}

                # Apply the CHECK constraint only if the marital_status column is found
                if "income_category" in columns:
                    cursor.execute(
                        f"""
                        ALTER TABLE {table}
                        ADD CONSTRAINT {table}_income_category_check
                        CHECK (income_category ~ '^\d+\s*-\s*\d+$' AND income_category IS NOT NULL AND TRIM(income_category) <> '');
                    """
                    )
            except Exception as e:
                # Rollback transaction to continue with the next table if an error occurs
                connection.rollback()
                print(f"Skipping {table} due to error: {e}")


def set_occupation_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        # Fetch tables that have a marital_status column
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name = 'occupation'
              AND table_schema = 'public'
            GROUP BY table_name;
        """
        )
        tables = cursor.fetchall()

        # Regular expression pattern to allow only alphabetic characters and spaces
        # pattern = r"^[A-Za-z\s]+$"

        # Iterate over tables to apply CHECK constraint
        for (table,) in tables:
            try:
                # Check if the marital_status column exists in the current table
                cursor.execute(
                    f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table}' 
                      AND column_name = 'occupation';
                """
                )
                columns = {col[0] for col in cursor.fetchall()}

                # Apply the CHECK constraint only if the marital_status column is found
                if "occupation" in columns:
                    cursor.execute(
                        f"""
                        ALTER TABLE {table}
                        ADD CONSTRAINT {table}_occupation_check
                        CHECK (occupation ~ '^[A-Za-z\\s]+$' AND occupation IS NOT NULL AND TRIM(occupation) <> '');
                    """
                    )
            except Exception as e:
                # Rollback transaction to continue with the next table if an error occurs
                connection.rollback()
                print(f"Skipping {table} due to error: {e}")


def set_user_personal_details_saving_category_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # Alphanumeric constraint for `saving_category`
            cursor.execute(
                """
                ALTER TABLE monthly_saving_capacity
                ADD CONSTRAINT user_personal_details_saving_category_number_dash_number
                CHECK (saving_category ~ '^(\\d+\\s*-\\s*\\d+)$');
            """
            )
        except Exception as e:
            connection.rollback()
            print(f"Error applying saving_category constraint: {e}")


def set_otp_valid_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # New constraint to prevent expired OTPs from being stored
            cursor.execute(
                """
                ALTER TABLE otp_logs
                ADD CONSTRAINT otp_valid_not_past
                CHECK (otp_valid >= CURRENT_TIMESTAMP);
                """
            )
            print("OTP validity constraint applied successfully.")
        except Exception as e:
            connection.rollback()
            print(f"Error applying OTP validity constraint: {e}")


def set_user_contact_info_constraints(apps, schema_editor):
    with connection.cursor() as cursor:
        try:
            # Email format validation (still allows NULL)
            cursor.execute(
                """
                ALTER TABLE user_contact_info
                ADD CONSTRAINT user_contact_info_email_format_check
                CHECK (
                    email IS NULL OR 
                    email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$'
                );
                """
            )

            # Mobile number validation: Must be in +91XXXXXXXXXX format
            cursor.execute(
                """
                ALTER TABLE user_contact_info
                ADD CONSTRAINT user_contact_info_mobile_number_check
                CHECK (
                    mobile_number IS NULL OR 
                    mobile_number ~ '^\\+91[0-9]{10}$'
                );
                """
            )

            # Ensure at least one of email, mobile_number, or password is not NULL
            cursor.execute(
                """
                ALTER TABLE user_contact_info
                ADD CONSTRAINT user_contact_info_at_least_one_field_check
                CHECK (
                    email IS NOT NULL OR 
                    mobile_number IS NOT NULL OR 
                    password IS NOT NULL
                );
                """
            )

            # Ensure email or mobile_number must be provided with password (if one is provided)
            cursor.execute(
                """
                ALTER TABLE user_contact_info
                ADD CONSTRAINT user_contact_info_email_or_mobile_with_password
                CHECK (
                    (email IS NOT NULL AND mobile_number IS NULL AND password IS NOT NULL) OR
                    (mobile_number IS NOT NULL AND email IS NULL AND password IS NOT NULL) OR
                    (email IS NOT NULL AND mobile_number IS NULL AND password IS NULL) OR
                    (mobile_number IS NOT NULL AND email IS NULL AND password IS NULL) OR
                    (email IS NULL AND mobile_number IS NULL AND password IS NULL)
                );
                """
            )

            # Add indexes for performance (on mobile_number and email)
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_contact_info_mobile_number 
                ON user_contact_info (mobile_number);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_contact_info_email 
                ON user_contact_info (email);
                """
            )

        except Exception as e:
            connection.rollback()
            print(f"Error applying UserContactInfo constraints: {e}")


class Migration(migrations.Migration):
    dependencies = [
        # Add the migration file on which this depends
        # Example: ('myapp', '0001_initial'),
        ("ai_mf_backend", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_marital_status_constraint),
        migrations.RunPython(set_default_dates_deleted),
        migrations.RunPython(set_user_personal_details_constraints),
        migrations.RunPython(add_case_insensitive_unique_constraint),
        migrations.RunPython(set_gender_constraint),
        migrations.RunPython(create_update_date_triggers),
        migrations.RunPython(set_income_category_constraint),
        migrations.RunPython(set_occupation_constraint),
        migrations.RunPython(set_user_personal_details_saving_category_constraint),
        migrations.RunPython(set_otp_valid_constraint),
        migrations.RunPython(set_user_contact_info_constraints),
    ]
