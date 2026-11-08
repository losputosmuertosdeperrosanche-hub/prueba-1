"""Narración en alemán del vídeo de los sectores (52 s): todas las branches de NexusLead.

Cada entrada es (segundo de inicio, texto en alemán). La lee demo_movil_narrar.py con la voz de_DE-thorsten-high.
Los inicios siguen la animación de render_sektoren.js: cifra total, seis grupos de branches (5 s cada uno a partir
de los 7,6 s), contactos, tres pasos, fuentes y cierre.
"""
DURACION = 52.0  # duración del vídeo, en segundos

GUION = [
    (0.6, "Über 100.000 Betriebe in acht Großstädten."),
    (4.3, "35 Branchen auf einer Karte."),
    (7.6, "Essen und Einkauf: Gastronomie, Supermärkte, Bäckereien."),
    (12.6, "Gesundheit und Schönheit: Ärzte, Friseure, Apotheken."),
    (17.6, "Mode und Handel: Kleidung, Möbel, Juweliere, Blumen."),
    (22.6, "Firmen und Dienste: Unternehmen, Anwälte, Banken."),
    (27.6, "Autos und Räder: Werkstätten, Autohäuser, Fahrräder."),
    (32.6, "Freizeit und Familie: Sport, Kitas, Sicherheit."),
    (37.8, "Rund 40.000 Betriebe haben Telefon oder E-Mail."),
    (41.8, "Stadt wählen, Branche wählen, Betrieb antippen."),
    (45.6, "Quellen: OpenRegister und OpenStreetMap."),
    (48.8, "Kommentiere SEKTOREN für den Link."),
]
