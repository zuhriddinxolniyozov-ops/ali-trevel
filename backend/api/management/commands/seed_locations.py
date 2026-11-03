"""Exact locations of the places of the tours (slug -> latitude, longitude, note).

The coordinates come from Wikipedia / Wikidata and OpenStreetMap (both open data). Where only the town or the area is known the place gets
an "approximate location" note, so the page does not pretend to be exact. An admin can correct any of them in the tour editor.
"""
from api.management.commands.seed_translations import PHRASES

TOWN = "Approximate location: the town centre"
KHIVA = "Approximate location: inside Itchan Kala, Khiva"
PHRASES[TOWN] = ("Taxminiy joylashuv: shahar markazi", "Примерное местоположение: центр города", "", "", "")
PHRASES[KHIVA] = ("Taxminiy joylashuv: Xivadagi Ichan Qal'a ichida", "Примерное местоположение: внутри Ичан-Калы, Хива", "", "", "")

LOCATIONS = {
    # Samarkand
    "registan-square": (39.654722, 66.975556, ""), "gur-e-amir-mausoleum": (39.648333, 66.968889, ""), "bibi-khanym-mosque": (39.660556, 66.979167, ""),
    "siyob-bazaar": (39.662000, 66.980000, ""), "shah-i-zinda": (39.663056, 66.987778, ""), "silk-road-eternal-city": (39.653836, 67.061276, ""),
    "ulugh-beg-observatory": (39.675000, 67.005000, ""), "imam-al-bukhari-complex": (39.814999, 66.944485, ""),
    # Bukhara
    "ark-fortress": (39.777778, 64.410278, ""), "chor-minor": (39.774830, 64.427383, ""), "ismail-samani-mausoleum": (39.776944, 64.400556, ""),
    "lyabi-hauz": (39.773056, 64.420278, ""), "poi-kalon-complex": (39.775833, 64.414167, ""),
    # Fergana Valley
    "khudayar-khan-palace-kokand": (40.538611, 70.937778, ""), "rishton-ceramics": (40.356667, 71.284722, TOWN), "yodgorlik-silk-factory-margilan": (40.471111, 71.724722, TOWN),
    # Karakalpakstan
    "ayaz-kala-fortress": (42.009722, 61.027222, ""), "mizdakhan-necropolis": (42.400972, 59.388556, ""), "moynaq-ship-graveyard": (43.766667, 59.033333, ""),
    "savitsky-museum-nukus": (42.465806, 59.612333, ""), "toprak-kala": (41.927194, 60.822167, ""),
    # Kashkadarya
    "ak-saray-palace": (39.060833, 66.829167, ""), "amir-timur-birthplace-shahrisabz": (39.050000, 66.833333, TOWN), "dorut-tilovat-complex": (39.049720, 66.827240, ""),
    # Khiva
    "itchan-kala": (41.378333, 60.363889, ""), "juma-mosque-khiva": (41.377500, 60.359900, ""), "kalta-minor-minaret": (41.378300, 60.357970, ""),
    "tash-hauli-palace": (41.378200, 60.361500, ""), "islam-khoja-minaret-khiva": (41.377500, 60.365000, KHIVA), "kunya-ark-khiva": (41.378883, 60.358222, ""),
    "pahlavon-mahmud-mausoleum-khiva": (41.376984, 60.359365, ""),
    # on the road
    "gijduvan-ceramics": (40.103120, 64.677330, TOWN), "kok-gumbaz-mosque-qarshi": (38.863729, 65.791128, ""), "rabati-malik-caravanserai": (40.122778, 65.148056, ""),
    # Tashkent
    "amir-timur-square": (41.311389, 69.279722, ""), "chorsu-bazaar": (41.326667, 69.235000, ""), "khast-imam-complex": (41.314700, 69.263300, ""),
    "tashkent-metro": (41.305022, 69.265344, "Approximate location: Kosmonavtlar station"),
}
PHRASES["Approximate location: Kosmonavtlar station"] = ("Taxminiy joylashuv: Kosmonavtlar bekati", "Примерное местоположение: станция «Космонавтов»", "", "", "")
