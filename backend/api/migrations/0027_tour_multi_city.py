from django.db import migrations, models

# Tours that visit several cities start in the "Multi-city" list; the team ticks or unticks any other tour in the admin.
MULTI = ["silk-road-7-day-journey", "silk-road-11-day-journey"]


def mark(apps, schema_editor):
    Tour = apps.get_model("api", "Tour")
    Tour.objects.filter(category="Multi-city").update(multi_city=True)
    Tour.objects.filter(slug__in=MULTI).update(multi_city=True)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0026_tour_destination_gallery"),
    ]

    operations = [
        migrations.AddField(model_name="tour", name="multi_city", field=models.BooleanField(default=False)),
        migrations.RunPython(mark, migrations.RunPython.noop),
    ]
