from django.db import migrations, models


def switch_on(apps, schema_editor):
    apps.get_model("api", "SiteContent").objects.update(booking_verification_enabled=True)


class Migration(migrations.Migration):
    dependencies = [("api", "0034_bookingrequest_verification_code_and_more")]

    operations = [
        migrations.AlterField(model_name="sitecontent", name="booking_verification_enabled", field=models.BooleanField(default=True)),
        migrations.RunPython(switch_on, migrations.RunPython.noop),
    ]
