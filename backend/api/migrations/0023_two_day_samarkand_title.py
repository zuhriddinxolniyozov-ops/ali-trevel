from django.db import migrations

# The Samarkand City Tour lasts two days: its name says so in every language (a name the owner changed by hand is left alone).
OLD = {'en': 'Samarkand City Tour', 'uz': 'Samarqand shahar turi', 'ru': 'Обзорный тур по Самарканду', 'fr': 'Visite de la ville de Samarcande',
       'de': 'Stadtrundfahrt Samarkand', 'es': 'Tour por la ciudad de Samarcanda'}
NEW = {'en': '2-Day Samarkand City Tour', 'uz': '2 kunlik Samarqand shahar turi', 'ru': '2-дневный обзорный тур по Самарканду',
       'fr': 'Visite de Samarcande en 2 jours', 'de': '2-tägige Stadtrundfahrt Samarkand', 'es': 'Tour de 2 días por Samarcanda'}


def rename(apps, schema_editor):
    for tour in apps.get_model('api', 'Tour').objects.filter(slug='samarkand-city-tour'):
        if tour.title == OLD['en']:
            tour.title = NEW['en']
        i18n = tour.i18n if isinstance(tour.i18n, dict) else {}
        for lang in ('uz', 'ru', 'fr', 'de', 'es'):
            entry = i18n.get(lang)
            if isinstance(entry, dict) and entry.get('title') == OLD[lang]:
                entry['title'] = NEW[lang]
        tour.i18n = i18n
        tour.save(update_fields=['title', 'i18n'])


class Migration(migrations.Migration):
    dependencies = [('api', '0022_youtube_link')]
    operations = [migrations.RunPython(rename, migrations.RunPython.noop)]
