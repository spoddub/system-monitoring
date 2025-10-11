from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_monitoring", "0001_initial"),
    ]
    operations = [
        migrations.RenameField(
            model_name="machine",
            old_name="is_ative",
            new_name="is_active",
        ),
    ]
