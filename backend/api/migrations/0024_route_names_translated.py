from django.db import migrations

# Three stops of the 7- and 11-day journeys kept their English names in every language of the route list.
NAMES = {
    "Kok-Gumbaz Mosque (Qarshi)": {"uz": "Ko'k Gumbaz masjidi (Qarshi)", "ru": "Мечеть Кок-Гумбаз (Карши)", "fr": "Mosquée Kok-Goumbaz (Karchi)",
                                   "de": "Kok-Gumbaz-Moschee (Karschi)", "es": "Mezquita Kok-Gumbaz (Karshi)"},
    "Gijduvan Ceramics Workshop": {"uz": "G'ijduvon kulolchilik ustaxonasi", "ru": "Гиждуванская керамическая мастерская", "fr": "Atelier de céramique de Gijduvan",
                                   "de": "Keramikwerkstatt in Gijduvan", "es": "Taller de cerámica de Gijduvan"},
    "Rabat-i-Malik Caravanserai": {"uz": "Rabati Malik karvonsaroyi", "ru": "Караван-сарай Рабат-и-Малик", "fr": "Caravansérail Rabat-i-Malik",
                                   "de": "Karawanserei Rabat-i-Malik", "es": "Caravasar Rabat-i-Malik"},
}


def translate(apps, schema_editor):
    for tour in apps.get_model("api", "Tour").objects.all():
        i18n = tour.i18n if isinstance(tour.i18n, dict) else {}
        changed = False
        for lang, entry in i18n.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("route"), list):
                continue
            lines = []
            for line in entry["route"]:
                name, bar, fee = str(line).partition("|")
                local = NAMES.get(name.strip(), {}).get(lang)
                if local:
                    line = f"{local} |{fee}" if bar else local
                    changed = True
                lines.append(line)
            entry["route"] = lines
        if changed:
            tour.i18n = i18n
            tour.save(update_fields=["i18n"])


class Migration(migrations.Migration):
    dependencies = [("api", "0023_two_day_samarkand_title")]
    operations = [migrations.RunPython(translate, migrations.RunPython.noop)]
