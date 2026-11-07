"""Narración alemana de la demo para móvil (grabación de iPhone, 148 s).

Cada entrada es (segundo de inicio, texto en alemán). La lee demo_movil_narrar.py con Piper.
El orden sigue la grabación: intro, mapa, ficha de empresa, búsqueda y filtros, lista y cierre.
"""
DURACION = 148.345  # duración del vídeo original, en segundos

GUION = [
    (0.6, "Das ist eine Demo von NexusLead für Mobiltelefone. NexusLead zeigt dir echte Betriebe in ganz Deutschland, direkt auf einer Karte."),
    (9.0, "Oben siehst du die Anzahl: über 45.000 Betriebe. Mehr als 20.000 davon haben eine Telefonnummer oder eine E-Mail-Adresse."),
    (17.8, "Die Zahlen in den Kreisen zeigen, wie viele Betriebe dort liegen. Wenn du zoomst, werden daraus einzelne Punkte."),
    (25.0, "Die Karte auf dem Handy ist beim Zoomen noch nicht perfekt. Das lösen wir als Nächstes. Auf dem Computer hat sie schon mehr Qualität und funktioniert besser."),
    (34.0, "Ein Tipp auf einen Betrieb öffnet sein Datenblatt. Dort siehst du den Unternehmensgegenstand, also was die Firma macht, und den Eintrag im Handelsregister."),
    (43.0, "Mit dem Button Betrieb im Internet suchen öffnest du die Suche bei Google. Mit Google Maps siehst du die Adresse auf der Karte."),
    (51.0, "Die Karte bewegst du mit einem Finger. Mit zwei Fingern zoomst du hinein oder heraus."),
    (57.3, "Die Betriebe aktualisieren wir laufend. Wir hören damit nicht auf."),
    (62.0, "Sicherheit und Events kommen aus offiziellen Registern. Gastronomie, Gesundheit und Immobilien kommen aus OpenStreetMap, einer offenen Karte, die Freiwillige pflegen."),
    (73.0, "Oben kannst du nach einer Firma, einer Straße oder einer Postleitzahl suchen."),
    (78.0, "Die Treffer erscheinen sofort auf der Karte."),
    (82.0, "Mit der Stadtauswahl legst du den Ort fest. Hier wählen wir Düsseldorf."),
    (87.5, "Danach wählst du die Branche: Sicherheit, Events, Gastronomie, Gesundheit oder Immobilien."),
    (94.5, "Bei Events in Düsseldorf siehst du zum Beispiel fünf Betriebe."),
    (98.5, "Ein Tipp auf eine Firma zeigt dir auch hier die Adresse, das Handelsregister und den Unternehmensgegenstand."),
    (105.2, "Die Karte zeigt dir dann nur die Betriebe der Auswahl."),
    (109.7, "Mit dem Filter Mit Kontakt siehst du nur Betriebe mit Telefon oder E-Mail. Das ist ideal, wenn du gezielt anrufen oder schreiben willst."),
    (119.0, "Dann zeigt die Liste alle Betriebe der Auswahl, bis zu 300 auf einmal."),
    (124.5, "Die Liste kannst du durchscrollen und einen Betrieb antippen."),
    (129.0, "Bei Restaurants siehst du zusätzlich Küche, Öffnungszeiten und Telefonnummer."),
    (134.2, "Und wir hören nicht auf, die Betriebe zu aktualisieren. Das war die Demo für Mobiltelefone."),
    (140.4, "Die Karte für das Handy verbessern wir als Nächstes."),
    (144.6, "Danke fürs Zuschauen."),
]
