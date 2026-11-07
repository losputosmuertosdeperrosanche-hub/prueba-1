#!/usr/bin/env python3
"""Traducción al alemán de la página del mapa (build_map.py --lang de).

Se usa para el vídeo de TikTok en alemán: index-de.html y data-de/*.json. La página publicada sigue en español.
Cada texto de PLANTILLA es una cadena exacta de template.html; traducir_plantilla() comprueba que aparezca.
"""
import re

# (español, alemán): cadenas exactas de template.html (se reemplazan todas las apariciones)
PLANTILLA = [
    ("<title>NexusLead Sicherheit</title>", '<html lang="de">\n<title>NexusLead Deutschland</title>'),
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


def horario_de(s):
    return DIAS_RE.sub(lambda m: DIAS_DE[m.group(1)], (s or "").replace("24/7", "rund um die Uhr"))


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
        return CULINARIA_DE.get(cu, cu.replace("_", " "))
    esp = _primero(tags, "healthcare:speciality")
    if esp:
        return ESPECIALIDAD_DE.get(esp, esp.replace("_", " "))
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
