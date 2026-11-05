from django.db import migrations, models


class Migration(migrations.Migration):
    """Tours and destinations get more photos after the cover, like hotels."""

    dependencies = [
        ("api", "0025_group_pricing_14"),
    ]

    operations = [
        migrations.AddField(model_name="destination", name="gallery", field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name="tour", name="gallery", field=models.JSONField(blank=True, default=list)),
    ]
