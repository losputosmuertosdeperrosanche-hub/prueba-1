"""Narración en alemán del anuncio de la actualización: sectores Friseure y Autowerkstätten (42,5 s).

Cada entrada es (segundo de inicio, texto en alemán). La lee demo_movil_narrar.py con la voz de_DE-thorsten-high.
Los inicios siguen la animación de render_actualizacion.js: ciudad, sector, ficha de empresa, filtro y segundo sector.
"""
DURACION = 42.5  # duración del anuncio, en segundos

GUION = [
    (0.6, "Neu bei NexusLead: Friseure und Autowerkstätten."),
    (4.45, "Über 4.500 neue Betriebe in acht Großstädten."),
    (8.8, "Wähle zuerst die Stadt, zum Beispiel Berlin."),
    (12.6, "Dann die Branche: Friseure und Kosmetikstudios."),
    (18.9, "Ein Tipp auf einen Betrieb zeigt dir Adresse und Kontakt."),
    (24.4, "Filter Mit Kontakt: nur Betriebe mit Telefon oder E-Mail."),
    (29.2, "Jetzt die Autowerkstätten, auf derselben Karte."),
    (33.8, "Die Daten stammen aus OpenStreetMap."),
    (37.4, "Insgesamt über 50.000 Betriebe. Kommentiere UPDATE, und wir zeigen dir alles."),
]
