#!/usr/bin/env python3
"""Traducción al alemán de la página del mapa (build_map.py --lang de).

Se usa para el vídeo de TikTok en alemán: index-de.html y data-de/*.json. La página publicada sigue en español.
Cada texto de PLANTILLA es una cadena exacta de template.html; traducir_plantilla() comprueba que aparezca.
"""
import re

# (español, alemán): cadenas exactas de template.html (se reemplazan todas las apariciones)
PLANTILLA = [
    ("<title>NexusLead Sicherheit</title>", "<title>NexusLead Deutschland</title>"),
    ("Buscar empresa, calle o código postal", "Firma, Straße oder PLZ suchen"),
    ('<span class="sr">Ciudad</span>', '<span class="sr">Stadt</span>'),
    ('<span class="sr">Sector</span>', '<span class="sr">Branche</span>'),
    (" Con contacto</label>", " Mit Kontakt</label>"),
    (">Lista</button>", ">Liste</button>"),
    ('aria-label="Mapa de Alemania con empresas"', 'aria-label="Karte von Deutschland mit Betrieben"'),
    ('aria-label="Tipo de mapa"', 'aria-label="Kartenart"'),
    (">Mapa</button>", ">Karte</button>"),
    (">Satélite</button>", ">Satellit</button>"),
    ("Cargando calles…", "Straßen werden geladen…"),
    ('aria-label="Cerrar"', 'aria-label="Schließen"'),
    ('foreign:"Sociedad extranjera"', 'foreign:"Ausländische Gesellschaft"'),
    ("empresas reales · OpenRegister + OSM", "echte Betriebe · OpenRegister + OSM"),
    ("Todos los sectores · ${fmt(TOTAL)}", "Alle Branchen"),
    ("No se pudo cargar el mapa. Comprueba la conexión y recarga la página.",
     "Die Karte konnte nicht geladen werden. Prüfe die Verbindung und lade die Seite neu."),
    ("Empresas: <a href", "Betriebe: <a href"),
    (" y OpenStreetMap · Calles © ", " und OpenStreetMap · Straßen © "),
    ("· Relieve: Natural Earth", "· Relief: Natural Earth"),
    ("No se pudo cargar el mapa de carreteras", "Die Straßenkarte konnte nicht geladen werden"),
    ("Faltan librerías del mapa", "Kartenbibliotheken fehlen"),
    ("Cargando ${SECTORS[code].short.toLowerCase()}…", "Lade ${SECTORS[code].short.toLowerCase()}…"),
    ("No se pudo cargar ${SECTORS[code].short", "Laden fehlgeschlagen: ${SECTORS[code].short"),
    ("Toda Alemania · ${fmt(total)}", "Deutschland · ${fmt(total)}"),
    ("</b> emp. · <b>", "</b> Betr. · <b>"),
    (">Copiar</button>", ">Kopieren</button>"),
    ('toast("Copiado")', 'toast("Kopiert")'),
    ("Mantén pulsado el texto para copiarlo", "Text gedrückt halten zum Kopieren"),
    ("Buscar la empresa en internet", "Betrieb im Internet suchen"),
    ("OpenStreetMap no tiene teléfono, email ni web de este negocio.",
     "OpenStreetMap hat für diesen Betrieb kein Telefon, keine E-Mail und keine Website."),
    ('<div class="k">Teléfono</div>', '<div class="k">Telefon</div>'),
    (">Llamar</a>", ">Anrufen</a>"),
    ('<div class="k">Email</div>', '<div class="k">E-Mail</div>'),
    (">Escribir</a>", ">Schreiben</a>"),
    (">Abrir</a>", ">Öffnen</a>"),
    ("Contacto no consultado todavía: cada consulta de contacto en OpenRegister gasta 10 créditos.",
     "Kontaktdaten noch nicht abgefragt: Jede Abfrage bei OpenRegister kostet 10 Credits."),
    ("OpenRegister no tiene teléfono, email ni web de esta empresa.",
     "OpenRegister hat für diesen Betrieb kein Telefon, keine E-Mail und keine Website."),
    ('<div class="k">USt-IdNr. (IVA)</div>', '<div class="k">USt-IdNr.</div>'),
    ("Fuente del contacto:", "Quelle der Kontaktdaten:"),
    ('"Especialidad" : code === "osm-hosteleria" ? (e.sub === "Hotel" || e.sub === "Pensión" ? "Categoría" : "Cocina") : "Detalle"',
     '"Fachgebiet" : code === "osm-hosteleria" ? (e.sub === "Hotel" || e.sub === "Pension" ? "Kategorie" : "Küche") : "Details"'),
    ('<span class="chip">Fuente: OpenStreetMap</span>', '<span class="chip">Quelle: OpenStreetMap</span>'),
    ("<h3>Dirección</h3>", "<h3>Adresse</h3>"),
    ("Sin dirección en OpenStreetMap", "Keine Adresse in OpenStreetMap"),
    ("<h3>Horario</h3>", "<h3>Öffnungszeiten</h3>"),
    ("<h3>Origen de los datos</h3>", "<h3>Herkunft der Daten</h3>"),
    ("Negocio registrado en OpenStreetMap por la comunidad (© colaboradores de OpenStreetMap, ODbL). Puede haber datos desactualizados. ",
     "Von der Community in OpenStreetMap eingetragen (© OpenStreetMap-Mitwirkende, ODbL). Die Daten können veraltet sein. "),
    ("Ver ficha en OpenStreetMap", "Eintrag in OpenStreetMap ansehen"),
    ("Ubicación aproximada (código postal)", "Ungefähre Lage (Postleitzahl)"),
    ("Ubicación aproximada (ciudad)", "Ungefähre Lage (Stadt)"),
    ('<span class="chip ok">Activa</span>', '<span class="chip ok">Aktiv</span>'),
    ("<h3>Registro mercantil</h3>", "<h3>Handelsregister</h3>"),
    ("<dt>Registro</dt>", "<dt>Registernr.</dt>"),
    ("<dt>Juzgado</dt><dd>Amtsgericht ", "<dt>Gericht</dt><dd>Amtsgericht "),
    ("<h3>Objeto social</h3>", "<h3>Unternehmensgegenstand</h3>"),
    ("No consta.", "Keine Angabe."),
    ("<h3>Contacto</h3>", "<h3>Kontakt</h3>"),
    ("Con teléfono o email", "Mit Telefon oder E-Mail"),
    ("negocios de OpenStreetMap en ", "Betriebe aus OpenStreetMap in "),
    ("(área completa de cada ciudad); ", "(gesamtes Stadtgebiet); "),
    (" con teléfono o email.", " mit Telefon oder E-Mail."),
    ("${fmt(q[0].loaded)} de ${fmt(q[0].total)} empresas activas en Alemania (muestra).",
     "${fmt(q[0].loaded)} von ${fmt(q[0].total)} aktiven Betrieben in Deutschland (Stichprobe)."),
    ("completas ${esc(full.join", "vollständig ${esc(full.join"),
    ("Parciales: ${esc(part.join", "Teilweise: ${esc(part.join"),
    ("items.length)} empresas`", "items.length)} Betriebe`"),
    ("Se muestran 300. Busca o elige una ciudad para acotar.",
     "Es werden 300 angezeigt. Suche oder wähle eine Stadt zum Eingrenzen."),
    ("Ninguna empresa coincide. Prueba con otra búsqueda o quita filtros.",
     "Kein Betrieb passt. Versuche eine andere Suche oder entferne Filter."),
]

# index-de.html se publica como página propia dentro del artefacto: sin el esqueleto que la plataforma
# pone a index.html, así que lo lleva ella (mismo doctype, metas y estilos base que index.html).
DOCUMENTO_INICIO = (
    '<!doctype html><html lang="de"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    '<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
    'html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}'
    'img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>\n'
)
DOCUMENTO_FIN = "\n</body></html>\n"

# Nombres de sector (meta de la página) en alemán
SECTORES_DE = {
    "80.01": {"label": "Private Sicherheitsdienste", "short": "Sicherheit", "title": "Sicherheit"},
    "82.30": {"label": "Veranstaltungs-, Messe- und Kongressorganisation", "short": "Events", "title": "Events"},
    "osm-hosteleria": {"label": "Gastronomie (Restaurants, Bars, Cafés und Hotels)", "short": "Gastro", "title": "Gastro"},
    "osm-salud": {"label": "Gesundheitswesen (Arztpraxen, Zahnärzte und Kliniken)", "short": "Gesundheit", "title": "Gesundheit"},
    "osm-inmobiliarias": {"label": "Immobilien und Hausverwaltung", "short": "Immobilien", "title": "Immobilien"},
}

# Tipo de negocio (columna 2 de data/osm-*.json)
TIPO_DE = {
    "Restaurante": "Restaurant", "Cafetería": "Café", "Comida rápida": "Schnellimbiss", "Bar": "Bar",
    "Pub": "Pub", "Hotel": "Hotel", "Pensión": "Pension", "Consulta médica": "Arztpraxis",
    "Dentista": "Zahnarzt", "Clínica": "Klinik", "Terapeuta": "Therapeut", "Inmobiliaria": "Immobilienmakler",
    "Administración de fincas": "Hausverwaltung",
}

# Tipo de cocina (etiqueta OSM "cuisine", primer valor)
CULINARIA_DE = {
    "italian": "italienisch", "kebab": "Döner", "pizza": "Pizza", "asian": "asiatisch", "burger": "Burger",
    "coffee_shop": "Café", "vietnamese": "vietnamesisch", "german": "deutsch", "regional": "regional",
    "indian": "indisch", "greek": "griechisch", "turkish": "türkisch", "chinese": "chinesisch", "sushi": "Sushi",
    "japanese": "japanisch", "thai": "thailändisch", "ice_cream": "Eis", "international": "international",
    "korean": "koreanisch", "sandwich": "Sandwich", "mexican": "mexikanisch", "steak_house": "Steakhaus",
    "french": "französisch", "chicken": "Hähnchen", "bavarian": "bayerisch", "spanish": "spanisch",
    "arab": "arabisch", "mediterranean": "mediterran", "lebanese": "libanesisch", "seafood": "Meeresfrüchte",
    "bubble_tea": "Bubble Tea", "persian": "persisch", "cake": "Kuchen", "portuguese": "portugiesisch",
    "sausage": "Wurst", "african": "afrikanisch", "balkan": "Balkan", "breakfast": "Frühstück", "fish": "Fisch",
    "pastry": "Gebäck", "salad": "Salat", "bakery": "Bäckerei", "tapas": "Tapas", "pasta": "Pasta",
    "vegan": "vegan", "vegetarian": "vegetarisch", "ramen": "Ramen", "noodle": "Nudeln",
    # Valores OSM "cuisine" sin entrada arriba (la clave va en minúsculas; extra_de hace cu.lower())
    "american": "amerikanisch", "croatian": "kroatisch", "croatic": "kroatisch", "kroatian": "kroatisch", "croatia": "kroatisch",
    "barbecue": "Barbecue", "donut": "Donut", "oriental": "orientalisch", "orient": "orientalisch", "bistro": "Bistro",
    "austrian": "österreichisch", "georgian": "georgisch", "italian_pizza": "Pizza", "pizza_italian": "Pizza", "falafel": "Falafel",
    "afghan": "afghanisch", "fries": "Pommes", "french_fries": "Pommes", "pommes": "Pommes", "bagel": "Bagel", "friture": "Frittiertes",
    "fried_food": "Frittiertes", "syrian": "syrisch", "syrianarabic": "syrisch-arabisch", "ethiopian": "äthiopisch", "aethiopian": "äthiopisch",
    "crepe": "Crêpes", "crepes": "Crêpes", "crêpe": "Crêpes", "peruvian": "peruanisch", "waffle": "Waffeln", "waffles": "Waffeln",
    "bowl": "Bowls", "bowls": "Bowls", "juice": "Säfte", "sudanese": "sudanesisch", "argentinian": "argentinisch",
    "fine_dining": "Gehobene Küche", "casual_fine_dining": "Casual Fine Dining", "grill": "Grill", "russian": "russisch",
    "moroccan": "marokkanisch", "maroccan": "marokkanisch", "polish": "polnisch", "brazilian": "brasilianisch", "swabian": "schwäbisch",
    "tea": "Tee", "curry": "Curry", "brunch": "Brunch", "indonesian": "indonesisch", "nepalese": "nepalesisch", "soup": "Suppen",
    "swedish": "schwedisch", "coffee": "Kaffee", "ukrainian": "ukrainisch", "hot_dog": "Hot Dog", "latin_american": "lateinamerikanisch",
    "fish_and_chips": "Fish & Chips", "local": "regional", "lokal": "regional", "irish": "irisch", "poke": "Poké Bowl", "pokebowl": "Poké Bowl",
    "fast_food": "Fast Food", "shawarma": "Schawarma", "canteen": "Kantine", "israeli": "israelisch", "pakistani": "pakistanisch",
    "pakistan": "pakistanisch", "hawaiian": "hawaiisch", "steak": "Steak", "middle_eastern": "nahöstlich", "cafe": "Café",
    "coffe_shop": "Café", "cafeteria": "Cafeteria", "pancake": "Pfannkuchen", "european": "europäisch", "egyptian": "ägyptisch",
    "mongolian": "mongolisch", "bosnian": "bosnisch", "armenian": "armenisch", "eritrean": "eritreisch", "malaysian": "malaysisch",
    "romanian": "rumänisch", "rumanian": "rumänisch", "chocolate": "Schokolade", "uzbek": "usbekisch", "burrito": "Burrito",
    "tex-mex": "Tex-Mex", "dessert": "Dessert", "scandinavian": "skandinavisch", "smoothie": "Smoothies", "jewish": "jüdisch",
    "fusion": "Fusion", "wine": "Wein", "hungarian": "ungarisch", "caribbean": "karibisch", "gourmet": "Gourmet", "cuban": "kubanisch",
    "health_food": "Gesundheitskost", "healthy": "gesund", "taiwanese": "taiwanesisch", "venezuelan": "venezolanisch",
    "albanian": "albanisch", "uyghur": "uigurisch", "uyghurisch": "uigurisch", "noodles": "Nudeln", "deli": "Delikatessen",
    "croque": "Croque", "croques": "Croque", "sri_lankan": "sri-lankisch", "franconian": "fränkisch", "fränkische": "fränkisch",
    "tibetan": "tibetisch", "tibetian": "tibetisch", "tibet": "tibetisch", "snack": "Snacks", "snacks": "Snacks", "wrap": "Wraps",
    "wraps": "Wraps", "potato": "Kartoffel", "colombian": "kolumbianisch", "kurdish": "kurdisch", "cantonese": "kantonesisch",
    "baklava": "Baklava", "organic": "Bio", "dumplings": "Dumplings", "bulgarian": "bulgarisch", "czech": "tschechisch",
    "beef_bowl": "Beef Bowl", "pub": "Pub", "fried_chicken": "Brathähnchen", "australian": "australisch", "tacos": "Tacos",
    "buffet": "Buffet", "chilean": "chilenisch", "grilled_chicken": "Grillhähnchen", "californian": "kalifornisch", "british": "britisch",
    "wings": "Wings", "belgian": "belgisch", "diner": "Diner", "flammkuchen": "Flammkuchen", "iranian": "iranisch", "drinks": "Getränke",
    "lunch": "Mittagessen", "south_indian": "südindisch", "tarte_flambee": "Flammkuchen", "meat": "Fleisch", "dutch": "niederländisch",
    "lao": "laotisch", "hummus": "Hummus", "pretzel": "Brezel", "filipino": "philippinisch", "cookies": "Kekse", "bohemian": "böhmisch",
    "tunisian": "tunesisch", "alsatian": "elsässisch", "guatemalan": "guatemaltekisch", "bolivian": "bolivianisch", "levante": "levantinisch",
    "levantine": "levantinisch", "senegambische (whatever this will be)": "senegambisch", "black_forest": "Schwarzwälder",
    "panamerican": "panamerikanisch", "ghanaian": "ghanaisch", "cameroonian": "kamerunisch", "backwaren": "Backwaren", "kebap": "Kebab",
    "divers": "Verschiedenes", "bengal": "bengalisch", "bangladeshi": "bangladeschisch", "pinsa": "Pinsa",
    "japanese,peruvian": "japanisch-peruanisch", "western": "westlich", "gözleme": "Gözleme", "açaí": "Açaí", "swiss": "schweizerisch",
    "suisse": "schweizerisch", "senegal": "senegalesisch", "baguette": "Baguette", "frozen_yogurt": "Frozen Yogurt", "iraqi": "irakisch",
    "tyrolean": "tirolerisch", "jamaican": "jamaikanisch", "ayurvedic": "ayurvedisch", "central_asian": "zentralasiatisch",
    "bakery_with_café": "Bäckerei mit Café", "goulash": "Gulasch", "empanada": "Empanadas", "churro": "Churros", "hotpot": "Hotpot",
    "eastern_european": "osteuropäisch", "osteuropa": "osteuropäisch", "curry-sausage": "Currywurst", "kebab turkish": "türkischer Kebab",
    "asian fusion and sushi": "asiatische Fusion & Sushi", "soup, salad, panini": "Suppen, Salate, Panini", "antipasti": "Antipasti",
    "tajik": "tadschikisch", "cheesecake": "Cheesecake", "japanes fusion": "japanische Fusion", "italian,greek": "italienisch-griechisch",
    "cross-over": "Crossover", "crossover": "Crossover", "canadian": "kanadisch",
    "seasonal regional dishes & selected meals with indian touch": "saisonal-regional mit indischem Einschlag", "nigerian": "nigerianisch",
    "student_food": "Studentenessen", "soul_food": "Soul Food", "seasonal": "saisonal", "limited": "begrenztes Angebot",
    "italian_turkish": "italienisch-türkisch", "slovak": "slowakisch", "indochinese": "indochinesisch", "burger_and_beef": "Burger & Beef",
    "irish,franconian": "irisch-fränkisch", "street_food": "Street Food", "yemeni": "jemenitisch", "yeminitic": "jemenitisch",
    "yemenese": "jemenitisch", "creole": "kreolisch", "sinhalese": "singhalesisch", "danish": "dänisch", "avocado": "Avocado",
    "kumpir": "Kumpir", "kiosk": "Kiosk", "malagasy": "madagassisch", "sicilian": "sizilianisch", "libanese": "libanesisch",
    "bar_and_grill": "Bar & Grill", "fermented_vegetables": "fermentiertes Gemüse", "finnish": "finnisch", "gambian": "gambisch",
    "cambodian": "kambodschanisch", "gyros": "Gyros", "nouvelle_cuisine": "Nouvelle Cuisine", "palestinian": "palästinensisch",
    "kyrghyz": "kirgisisch", "kyrgyz": "kirgisisch", "yakiniku": "Yakiniku", "bread": "Brot", "burmese": "birmanisch", "arepa": "Arepa",
    "superfood": "Superfood", "fish_sandwich": "Fischsandwich", "bar": "Bar", "anatolian": "anatolisch", "majorca": "mallorquinisch",
    "çiğköfte": "Çiğköfte", "balkan,pizza,kebab": "Balkan, Pizza, Kebab", "teahouse": "Teehaus", "shisha": "Shisha", "hessian": "hessisch",
    "corn_dog": "Corn Dog", "michelin": "Sternerestaurant", "maultaschen": "Maultaschen", "toast": "Toast", "pommesbude": "Pommesbude",
    "sausage pomfrit": "Wurst & Pommes", "tarte": "Tarte", "pizzeria": "Pizzeria", "cocktails": "Cocktails", "cook&chill": "Cook & Chill",
    "crumble": "Crumble", "norwegian": "norwegisch", "insects": "Insekten", "no": "", "blind": "",
}

# Fachgebiet (etiqueta OSM "healthcare:speciality", primer valor)
ESPECIALIDAD_DE = {
    "general": "Allgemeinmedizin", "internal": "Innere Medizin", "gynaecology": "Gynäkologie",
    "ophthalmology": "Augenheilkunde", "paediatrics": "Kinderheilkunde", "orthopaedics": "Orthopädie",
    "otolaryngology": "HNO-Heilkunde", "dermatology": "Dermatologie", "orthodontics": "Kieferorthopädie",
    "urology": "Urologie", "psychiatry": "Psychiatrie", "radiology": "Radiologie", "dentist": "Zahnmedizin",
    "neurology": "Neurologie", "cardiology": "Kardiologie", "plastic_surgery": "Plastische Chirurgie",
    "child_psychiatry": "Kinderpsychiatrie", "surgery": "Chirurgie", "stomatology": "Stomatologie",
    "gastroenterology": "Gastroenterologie", "dental_oral_maxillo_facial_surgery": "Mund-Kiefer-Gesichtschirurgie",
    "nephrology": "Nephrologie", "pulmonology": "Pneumologie", "oncology": "Onkologie",
    "physiotherapy": "Physiotherapie", "psychotherapy": "Psychotherapie",
    # Valores OSM "healthcare:speciality" sin entrada arriba (clave en minúsculas)
    "implantology": "Implantologie", "implantology paradontologie oralchirurgie": "Implantologie, Parodontologie, Oralchirurgie",
    "paediatric_dentistry,implantology": "Kinderzahnheilkunde, Implantologie", "paediatric_dentistry": "Kinderzahnheilkunde",
    "acupuncture": "Akupunktur", "accupuncture": "Akupunktur", "endocrinology": "Endokrinologie", "osteopathy": "Osteopathie",
    "diabetology": "Diabetologie", "neurosurgery": "Neurochirurgie", "anaesthetics": "Anästhesie", "chiropractic": "Chiropraktik",
    "occupational": "Arbeitsmedizin", "endodontics": "Endodontie", "rheumatology": "Rheumatologie", "dentistry": "Zahnmedizin",
    "psychotherapist": "Psychotherapie", "homeopathy": "Homöopathie", "allergology": "Allergologie", "trauma": "Unfallchirurgie",
    "haematology": "Hämatologie", "biological_haematology": "Hämatologie", "emergency": "Notfallmedizin", "proctology": "Proktologie",
    "physiatry": "Physikalische Medizin", "naturopathy": "Naturheilkunde", "neuropsychiatry": "Neuropsychiatrie", "nuclear": "Nuklearmedizin",
    "traditional_chinese_medicine": "Traditionelle Chinesische Medizin", "podiatry": "Podologie", "infectious_diseases": "Infektiologie",
    "dermatovenereology": "Dermatovenerologie", "fertility": "Reproduktionsmedizin", "radiotherapy": "Strahlentherapie",
    "palliative": "Palliativmedizin", "oral_surgery": "Oralchirurgie", "oralchirurgie": "Oralchirurgie", "abortion": "Schwangerschaftsabbruch",
    "vaccination": "Impfungen", "otorhinolaryngology": "HNO-Heilkunde", "orolaryngology": "HNO-Heilkunde", "hno": "HNO-Heilkunde",
    "diagnostic_radiology": "Diagnostische Radiologie", "diagnostische_radiologie": "Diagnostische Radiologie", "radiologie": "Radiologie",
    "pathology": "Pathologie", "massage_therapy": "Massagetherapie", "phlebology": "Phlebologie", "depth": "Tiefenpsychologie",
    "psychotherapie": "Psychotherapie", "occupational_therapy": "Ergotherapie", "paediatric_surgery": "Kinderchirurgie", "angiology": "Angiologie",
    "systemic": "Systemische Therapie", "behavior": "Verhaltenstherapie", "verhaltenstherapie": "Verhaltenstherapie",
    "aesthetic_medicine": "Ästhetische Medizin", "psychology": "Psychologie", "vascular_surgery": "Gefäßchirurgie", "gefäßmedizin": "Gefäßmedizin",
    "body": "Körpertherapie", "humanistic": "Humanistische Psychotherapie", "hypnosis": "Hypnose", "optometry": "Optometrie",
    "family_medicine": "Familienmedizin", "general,internal": "Allgemein- und Innere Medizin", "addiction": "Suchtmedizin",
    "addiction_medicine": "Suchtmedizin", "periodontics": "Parodontologie", "parodontology": "Parodontologie", "periodontology": "Parodontologie",
    "somnology": "Schlafmedizin", "children": "Kindermedizin", "psychosomatic": "Psychosomatik", "psychosomatic_medicine": "Psychosomatische Medizin",
    "augen": "Augenheilkunde", "ophtalmology": "Augenheilkunde", "hand_surgery": "Handchirurgie", "mrt": "MRT",
    "pain_management": "Schmerztherapie", "pain": "Schmerztherapie", "hemostaseology": "Hämostaseologie", "verkehrsmedizin": "Verkehrsmedizin",
    "check-up": "Check-up", "sports_trauma": "Sporttraumatologie", "obstetric_ultrasonography": "Geburtshilfliche Sonographie",
    "travel_medicine": "Reisemedizin", "heilpraktiker_für_psychotherapie": "Heilpraktiker für Psychotherapie", "lerntherapie": "Lerntherapie",
    "osteologie": "Osteologie", "tropical": "Tropenmedizin", "zahnarzt": "Zahnarzt", "plastische_chirurgie": "Plastische Chirurgie",
    "neonatology": "Neonatologie", "covid19": "COVID-19", "oral_and_maxillofacial_surgery": "Mund-Kiefer-Gesichtschirurgie", "lasik": "LASIK",
    "prophylaxe": "Prophylaxe", "general_surgery": "Allgemeinchirurgie", "coaching": "Coaching", "osteoporosis": "Osteoporose",
    "gastroentology": "Gastroenterologie", "laser_coagulation": "Laserkoagulation", "sports": "Sportmedizin", "sport_medicine": "Sportmedizin",
    "botox": "Botox", "hairloss": "Haarausfall", "zahnheilkunde": "Zahnheilkunde", "ambulantes_op-zentrum": "Ambulantes OP-Zentrum",
    "physicalische_therapie": "Physikalische Therapie", "gastroenterological_surgery": "Gastroenterologische Chirurgie",
    "prenatal_medicine": "Pränatalmedizin", "mkg": "MKG-Chirurgie", "prothetik": "Prothetik", "specialist_pediatrician": "Kinderheilkunde",
    "rehabilitation": "Rehabilitation", "herbalism": "Phytotherapie", "mammography": "Mammographie", "dermaordinology": "Dermatologie",
    "alternative": "Alternativmedizin", "augenlasern": "Augenlasern", "nutrition": "Ernährungsmedizin", "spine_surgery": "Wirbelsäulenchirurgie",
    "geriatrics": "Geriatrie", "dialysis": "Dialyse", "yes": "", "biology": "", "ortologist": "Kieferorthopädie",
}

# Días y meses de la etiqueta opening_hours de OSM
DIAS_DE = {"Mo": "Mo", "Tu": "Di", "We": "Mi", "Th": "Do", "Fr": "Fr", "Sa": "Sa", "Su": "So", "PH": "Feiertag",
           "off": "geschlossen", "Jan": "Jan", "Feb": "Feb", "Mar": "Mär", "Apr": "Apr", "May": "Mai", "Jun": "Jun",
           "Jul": "Jul", "Aug": "Aug", "Sep": "Sep", "Oct": "Okt", "Nov": "Nov", "Dec": "Dez"}
DIAS_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(DIAS_DE) + r")(?![A-Za-z])")


def traducir_plantilla(html):
    """Aplica PLANTILLA a template.html. Falla si alguna cadena no aparece (la plantilla cambió)."""
    for es, de in PLANTILLA:
        if es not in html:
            raise SystemExit(f"Texto no encontrado en la plantilla: {es[:70]!r}")
        html = html.replace(es, de)
    return html


# Palabras clave de opening_hours que aparecen sueltas en inglés (fuera de comillas)
HORARIO_PALABRAS = {"open": "geöffnet", "closed": "geschlossen", "unknown": "unbekannt", "sunset": "Sonnenuntergang",
                    "sunrise": "Sonnenaufgang", "day": "Tag"}
HORARIO_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(HORARIO_PALABRAS) + r")(?![A-Za-z])", re.IGNORECASE)
# Comentarios de OSM entre comillas que son frases fijas (el resto de comentarios libres se deja como está)
HORARIO_FRASES = {"by appointment": "nach Vereinbarung", "please call us": "bitte anrufen", "call us": "anrufen",
                  "call for appointments": "Termine nach Absprache", "unknown": "unbekannt",
                  "opening soon": "Eröffnung in Kürze"}


def horario_de(s):
    """Horario OSM en alemán: 24/7, días y meses, palabras clave y frases fijas entre comillas."""
    partes = re.split(r'("[^"]*")', (s or "").replace("24/7", "rund um die Uhr"))
    for i, p in enumerate(partes):
        if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            frase = p[1:-1].strip()
            partes[i] = '"' + HORARIO_FRASES.get(frase.lower(), frase) + '"'
        else:
            partes[i] = HORARIO_RE.sub(lambda m: HORARIO_PALABRAS[m.group(1).lower()], p)
    return DIAS_RE.sub(lambda m: DIAS_DE[m.group(1)], "".join(partes))


def _primero(tags, clave):
    v = (tags.get(clave) or "").strip()
    return v.split(";")[0].strip() if v else ""


def estrellas_de(v):
    """Categoría hotelera de OSM: "4" -> "4 Sterne", "3S" -> "3 Sterne Superior"."""
    m = re.fullmatch(r"\s*([1-5])(S?)\s*", v or "")
    if not m:
        return ""
    return f"{m.group(1)} {'Stern' if m.group(1) == '1' else 'Sterne'}" + (" Superior" if m.group(2) else "")


def extra_de(tags):
    """Dato extra del negocio en alemán: cocina, especialidad o categoría del hotel."""
    cu = _primero(tags, "cuisine")
    if cu:
        return CULINARIA_DE.get(cu.lower(), cu.replace("_", " "))
    esp = _primero(tags, "healthcare:speciality")
    if esp:
        return ESPECIALIDAD_DE.get(esp.lower(), esp.replace("_", " "))
    return estrellas_de(tags.get("stars", ""))


def fila_de(fila, tags):
    """Convierte una fila de data/osm-*.json ([id, nombre, tipo, lat, lon, dirección, ciudad, tel, email, web, horario, extra])."""
    nueva = list(fila)
    nueva[2] = TIPO_DE.get(fila[2], fila[2])
    nueva[10] = horario_de(fila[10])
    nueva[11] = extra_de(tags or {})
    return nueva


def meta_de(code, meta, fichero):
    """Meta de un sector OSM en alemán; `fichero` es la ruta de sus filas (data-de/...)."""
    return {**meta, **SECTORES_DE[code], "file": fichero}
