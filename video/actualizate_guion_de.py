"""Narración en alemán del anuncio de actualizate IA (1080x1920, voz de_DE-thorsten-high).

Cada frase empieza RETARDO segundos después del inicio de su escena, según actualizate_tiempos_de.json,
el mismo fichero que lee stage_actualizate.html.
Uso: python3 demo_movil_narrar.py <carpeta de salida> <modelo .onnx> actualizate_guion_de
"""
import json
import pathlib

_TIEMPOS = json.loads(pathlib.Path(__file__).with_name("actualizate_tiempos_de.json").read_text(encoding="utf-8"))
DURACION = _TIEMPOS["duracion"]
RETARDO = 0.35

TEXTOS = [
    "Webdesigner oder KI-Agentur? Der Unterschied ist groß.",
    "Ein Webdesigner baut alles von Hand. Das dauert Tage.",
    "Wir arbeiten mit künstlicher Intelligenz.",
    "Eine Website ist bei uns in etwa zehn Minuten fertig.",
    "Danach prüft ein Mensch alles. Die Qualität leidet nicht.",
    "Zuerst eine Demo, gratis. Gefällt sie dir, bauen wir die Website.",
    "Dann bekommst du deine Website für 100 Euro.",
    "Am selben Tag ist sie fertig. Bezahlen musst du erst danach.",
    "Frag nach unseren anderen Projekten und überzeug dich selbst.",
    "Für viele sind das Stunden. Für uns: Denken und Optimieren.",
    "Bestellungen abtippen? Ein Formular trägt sie automatisch ein.",
    "Immer dieselben Fragen? Die Antworten laufen automatisch.",
    "Rechnungen von Hand? Vorlagen versenden sich selbst.",
    "Wir analysieren dein Unternehmen gratis. Du brauchst nur den Firmennamen.",
    "Per E-Mail bekommst du eine komplette Diagnose.",
    "Die KI sieht, was Menschen übersehen. Wir prüfen von Hand. Du entscheidest, ob es stimmt.",
    "Wir haben weitere Dienste. Dank KI sind sie günstig.",
    "Für viele Programmierer ist das ein Weckruf.",
    "Willst du eine Website? Schreib uns. Die Demo kostet nichts.",
]
assert len(TEXTOS) == len(_TIEMPOS["inicios"]), "un texto por escena"
GUION = [(inicio + RETARDO, texto) for inicio, texto in zip(_TIEMPOS["inicios"], TEXTOS)]
