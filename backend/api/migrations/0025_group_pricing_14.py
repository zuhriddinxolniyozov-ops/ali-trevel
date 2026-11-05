from django.db import migrations

# The owner's prices by group size (4 November 2026): for the 2-day Samarkand tour ($209) 14 or more travelers pay $209,
# 11-13 pay $249, 7-10 pay $267, 3-6 pay $289 and 1-2 pay $294; every other tour follows the same proportions.
TIERS = [{"min": 14, "percent": 100}, {"min": 11, "percent": 119.138756}, {"min": 7, "percent": 127.751196},
         {"min": 3, "percent": 138.277512}, {"min": 1, "percent": 140.669856}]


def use_new_table(apps, schema_editor):
    apps.get_model("api", "SiteContent").objects.update(group_pricing_tiers=TIERS)


class Migration(migrations.Migration):
    dependencies = [("api", "0024_route_names_translated")]
    operations = [migrations.RunPython(use_new_table, migrations.RunPython.noop)]
