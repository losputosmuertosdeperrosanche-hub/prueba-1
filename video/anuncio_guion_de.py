"""Narración en alemán del anuncio de la actualización: sector Logística (42 s).

Cada entrada es (segundo de inicio, texto en alemán). La lee demo_movil_narrar.py con la voz de_DE-thorsten-high.
Los inicios siguen la animación de render_anuncio.js: ciudad, sector, ficha de empresa y filtro.
"""
DURACION = 42.5  # duración del anuncio, en segundos

GUION = [
    (0.6, "Neu bei NexusLead: die Branche Logistik."),
    (4.2, "172 Logistikbetriebe in acht Großstädten."),
    (8.8, "Wähle zuerst die Stadt, zum Beispiel Berlin."),
    (12.6, "Dann wählst du die Branche Logistik."),
    (15.0, "Dort findest du Speditionen, Kurierdienste, Lager und Transportunternehmen."),
    (20.0, "Ein Tipp auf einen Betrieb zeigt dir Adresse und Kontakt."),
    (24.0, "Mit dem Filter Mit Kontakt siehst du nur Betriebe mit Telefon oder E-Mail."),
    (29.0, "Die Daten stammen aus OpenStreetMap und werden laufend aktualisiert."),
    (33.6, "172 Betriebe, 28 mit Kontakt."),
    (38.5, "Kommentiere Logistik, und wir zeigen dir alles."),
]
