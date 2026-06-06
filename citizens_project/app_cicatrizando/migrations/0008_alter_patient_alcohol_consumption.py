# Changed alcohol_consumption from CharField to JSONField
# First transforms existing VARCHAR data into valid JSON text, then
# lets Django's standard AlterField cast it to jsonb.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cicatrizando', '0007_alter_observation_image'),
    ]

    operations = [
        # Step 1: Transform existing VARCHAR data into valid JSON text (e.g. 'NONE' -> '["NONE"]')
        # This makes the subsequent ::jsonb cast succeed.
        migrations.RunSQL(
            sql="""
                UPDATE app_cicatrizando_patient
                SET alcohol_consumption = CASE
                    WHEN alcohol_consumption IS NULL OR alcohol_consumption = '' THEN '[]'
                    ELSE '["' || alcohol_consumption || '"]'
                END
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Step 2: Django generates: ALTER COLUMN ... TYPE jsonb USING "alcohol_consumption"::jsonb
        # Now that the data is valid JSON text, this cast succeeds.
        migrations.AlterField(
            model_name='patient',
            name='alcohol_consumption',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
