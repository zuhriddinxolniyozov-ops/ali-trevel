from urllib.parse import quote

from django.core.management.base import BaseCommand

from api import models
from api.market import GLOBAL, LOCAL, use


def commons(name):
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(name)}?width=1280"


# The first bonus, added to the 2-day Samarkand tour on both sites. Texts keep to well-documented facts: the monument near the
# Registan, the house nearby where Islam Karimov was born and grew up, and the memorial at the Hazrati Khizr complex where he rests.
KARIMOV = {
    "title": "In memory of Islam Karimov, the first President",
    "text": "Samarkand is the hometown of Islam Karimov, the first President of Uzbekistan. Your guide takes you to his monument on the avenue by the Registan, "
            "past the house nearby where he was born and grew up, and to the memorial at the Hazrati Khizr complex, where he rests above the old city. "
            "A quiet hour with stories of his life and of the independent Uzbekistan he led.",
    "duration": "About 1 hour",
    "tag": "exclusive",
    "image": commons("Мечеть Хазрет-Хызр.jpg"),
    "gallery": [commons("Mosque Hazrat-Hyzr (1).JPG")],
    "i18n": {
        "uz": {"title": "Birinchi Prezident Islom Karimov xotirasi",
               "text": "Samarqand — O'zbekistonning Birinchi Prezidenti Islom Karimovning ona shahri. Gid sizni Registon yonidagi xiyobondagi haykali yoniga, "
                       "u tug'ilib o'sgan uy yonidan va eski shahar uzra joylashgan, u abadiy qo'nim topgan Hazrati Xizr majmuasidagi yodgorlikka olib boradi. "
                       "Uning hayoti va u boshqargan mustaqil O'zbekiston haqidagi hikoyalar bilan sokin bir soat.",
               "duration": "Taxminan 1 soat"},
        "ru": {"title": "Память Ислама Каримова, первого Президента",
               "text": "Самарканд — родной город Ислама Каримова, первого Президента Узбекистана. Гид проведёт вас к его памятнику на проспекте у Регистана, "
                       "мимо дома, где он родился и вырос, и к мемориалу в комплексе Хазрати Хизр, где он покоится над старым городом. "
                       "Спокойный час с рассказами о его жизни и о независимом Узбекистане.",
               "duration": "Около 1 часа"},
        "fr": {"title": "En mémoire d'Islam Karimov, premier Président",
               "text": "Samarcande est la ville natale d'Islam Karimov, premier Président de l'Ouzbékistan. Votre guide vous mène à son monument près du Régistan, "
                       "devant la maison où il est né et a grandi, puis au mémorial du complexe Hazrati Khizr, où il repose au-dessus de la vieille ville.",
               "duration": "Environ 1 heure"},
        "de": {"title": "Zum Gedenken an Islam Karimow, den ersten Präsidenten",
               "text": "Samarkand ist die Heimatstadt von Islam Karimow, dem ersten Präsidenten Usbekistans. Ihr Guide führt Sie zu seinem Denkmal beim Registan, "
                       "vorbei an dem Haus, in dem er geboren wurde und aufwuchs, und zur Gedenkstätte im Hazrati-Khizr-Komplex, wo er über der Altstadt ruht.",
               "duration": "Etwa 1 Stunde"},
        "es": {"title": "En memoria de Islam Karimov, primer Presidente",
               "text": "Samarcanda es la ciudad natal de Islam Karimov, primer Presidente de Uzbekistán. Su guía le lleva a su monumento junto al Registán, "
                       "pasando por la casa donde nació y creció, y al memorial del complejo Hazrati Khizr, donde descansa sobre la ciudad vieja.",
               "duration": "Aproximadamente 1 hora"},
    },
}


class Command(BaseCommand):
    help = "Add the first special bonus (in memory of Islam Karimov) to the 2-day Samarkand tour on both sites, if it is not there yet."

    def handle(self, *args, **options):
        for market in (GLOBAL, LOCAL):
            with use(market):
                tour = models.Tour.objects.filter(slug="samarkand-city-tour").first()
                if not tour:
                    continue
                if any(b.get("title") == KARIMOV["title"] for b in tour.bonuses or []):
                    self.stdout.write(f"{market}: already there")
                    continue
                tour.bonuses = [*(tour.bonuses or []), KARIMOV]
                tour.save(update_fields=["bonuses"])
                self.stdout.write(f"{market}: bonus added")
