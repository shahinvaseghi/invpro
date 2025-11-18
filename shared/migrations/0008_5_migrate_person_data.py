# Custom migration to migrate Person data from shared to production
# This should run BEFORE 0009_remove_personassignment_company_and_more

from django.db import migrations


def migrate_person_data(apps, schema_editor):
    """
    Migrate Person and PersonAssignment data from shared to production.
    This function copies all data from shared_person to production_person
    and shared_person_assignment to production_person_assignment.
    """
    db_alias = schema_editor.connection.alias
    
    # Check if shared_person table exists
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'shared_person'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Table doesn't exist, nothing to migrate
            return
        
        # Check if there's any data to migrate
        cursor.execute("SELECT COUNT(*) FROM shared_person;")
        person_count = cursor.fetchone()[0]
        
        if person_count == 0:
            # No data to migrate
            return
        
        # Migrate Person data
        cursor.execute("""
            INSERT INTO production_person (
                id, company_id, company_code, public_code, username,
                first_name, last_name, first_name_en, last_name_en,
                national_id, personnel_code, email, phone_number, mobile_number,
                description, notes, user_id, sort_order, is_enabled,
                metadata, created_at, created_by_id, edited_at, edited_by_id,
                enabled_at, enabled_by_id, disabled_at, disabled_by_id
            )
            SELECT 
                id, company_id, company_code, public_code, username,
                first_name, last_name, first_name_en, last_name_en,
                national_id, personnel_code, email, phone_number, mobile_number,
                description, notes, user_id, sort_order, is_enabled,
                metadata, created_at, created_by_id, edited_at, edited_by_id,
                enabled_at, enabled_by_id, disabled_at, disabled_by_id
            FROM shared_person
            ON CONFLICT (id) DO NOTHING;
        """)
        
        # Migrate PersonAssignment data
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'shared_person_assignment'
            );
        """)
        assignment_table_exists = cursor.fetchone()[0]
        
        if assignment_table_exists:
            cursor.execute("SELECT COUNT(*) FROM shared_person_assignment;")
            assignment_count = cursor.fetchone()[0]
            
            if assignment_count > 0:
                cursor.execute("""
                    INSERT INTO production_person_assignment (
                        id, company_id, company_code, person_id,
                        work_center_id, work_center_type, is_primary,
                        assignment_start, assignment_end, notes,
                        is_enabled, metadata, created_at, created_by_id,
                        edited_at, edited_by_id, enabled_at, enabled_by_id,
                        disabled_at, disabled_by_id
                    )
                    SELECT 
                        id, company_id, company_code, person_id,
                        work_center_id, work_center_type, is_primary,
                        assignment_start, assignment_end, notes,
                        is_enabled, metadata, created_at, created_by_id,
                        edited_at, edited_by_id, enabled_at, enabled_by_id,
                        disabled_at, disabled_by_id
                    FROM shared_person_assignment
                    ON CONFLICT (id) DO NOTHING;
                """)
        
        # Migrate Many-to-Many relationships (person_company_units)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'shared_person_company_units'
            );
        """)
        m2m_table_exists = cursor.fetchone()[0]
        
        if m2m_table_exists:
            cursor.execute("SELECT COUNT(*) FROM shared_person_company_units;")
            m2m_count = cursor.fetchone()[0]
            
            if m2m_count > 0:
                cursor.execute("""
                    INSERT INTO production_person_company_units (
                        person_id, companyunit_id
                    )
                    SELECT person_id, companyunit_id
                    FROM shared_person_company_units
                    ON CONFLICT DO NOTHING;
                """)


def reverse_migrate_person_data(apps, schema_editor):
    """
    Reverse migration - copy data back from production to shared.
    This is for rollback purposes only.
    """
    # This is a one-way migration, so reverse is a no-op
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0005_person_processstep_machine_code_personassignment_and_more'),
        ('shared', '0008_remove_accesslevel_updated_at_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_person_data, reverse_migrate_person_data),
    ]

