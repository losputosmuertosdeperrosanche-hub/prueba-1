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
    "Für dein Unternehmen: eine Website für 100 Euro.",
    "Am selben Tag bekommst du sie. Bezahlen musst du erst danach.",
    "Frag nach unseren anderen Projekten und überzeug dich selbst.",
    "Teste uns mit einer Demo. Gefällt sie dir, machen wir weiter. Du verlierst nichts.",
    "KI heißt Zeit sparen: durch Automatisierung und optimierte Firmen.",
    "Dazu bieten wir weitere Dienste. Dank KI sind sie günstig.",
    "Für viele Programmierer ist das ein Weckruf.",
    "Willst du eine Website? Schreib uns, wir machen dir eine Demo.",
]
assert len(TEXTOS) == len(_TIEMPOS["inicios"]), "un texto por escena"
GUION = [(inicio + RETARDO, texto) for inicio, texto in zip(_TIEMPOS["inicios"], TEXTOS)]
