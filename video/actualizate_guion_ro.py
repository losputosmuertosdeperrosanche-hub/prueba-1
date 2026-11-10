"""Narración en rumano del anuncio de actualizate IA (1080x1920, voz ro_RO-mihai-medium).

Cada frase empieza RETARDO segundos después del inicio de su escena, según actualizate_tiempos_ro.json,
el mismo fichero que lee stage_actualizate.html.
Uso: python3 demo_movil_narrar.py <carpeta de salida> <modelo .onnx> actualizate_guion_ro
"""
import json
import pathlib

_TIEMPOS = json.loads(pathlib.Path(__file__).with_name("actualizate_tiempos_ro.json").read_text(encoding="utf-8"))
DURACION = _TIEMPOS["duracion"]
RETARDO = 0.35

TEXTOS = [
    "Web designer sau agenție de inteligență artificială? Diferența este mare.",
    "Un web designer face totul manual. Durează zile.",
    "Noi lucrăm cu inteligență artificială.",
    "Un site poate fi gata în aproximativ zece minute.",
    "O persoană verifică totul. Calitatea nu scade.",
    "Pentru firma ta: un site web de 100 de euro.",
    "Îl primești în aceeași zi. Abia apoi plătești.",
    "Vezi alte lucrări ale noastre și judecă singur.",
    "Testează-ne cu o demonstrație. Dacă îți place, continuăm. Nu pierzi nimic.",
    "Inteligența artificială înseamnă timp câștigat prin automatizări.",
    "Avem și alte servicii, foarte ieftine.",
    "Pentru mulți programatori, este un semnal de trezire.",
    "Vrei un site web? Scrie-ne, îți facem o demonstrație.",
]
assert len(TEXTOS) == len(_TIEMPOS["inicios"]), "un texto por escena"
GUION = [(inicio + RETARDO, texto) for inicio, texto in zip(_TIEMPOS["inicios"], TEXTOS)]
