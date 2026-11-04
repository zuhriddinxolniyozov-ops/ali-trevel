from django.db import migrations

OLD = ('https://youtube.com/@alitravel_z?si=XcvxpVc1VFoS8JxV', 'https://youtube.com/@alitravel_z', '')
NEW = 'https://www.youtube.com/@Alitravel_uz'


def use_new_channel(apps, schema_editor):
    # the company's YouTube channel; a link the owner typed in by hand is left alone
    apps.get_model('api', 'SiteContent').objects.filter(youtube_url__in=OLD).update(youtube_url=NEW)


class Migration(migrations.Migration):
    dependencies = [('api', '0021_site_x_url')]
    operations = [migrations.RunPython(use_new_channel, migrations.RunPython.noop)]
