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
    "Web designer sau agenție de inteligență artificială?",
    "Un web designer face totul manual. Durează zile.",
    "Noi lucrăm cu inteligență artificială.",
    "Un site poate fi gata în aproximativ zece minute.",
    "O persoană verifică totul. Calitatea nu scade.",
    "Pentru firma ta: un site web de 100 de euro.",
    "Îl primești în aceeași zi. Abia apoi plătești.",
    "Vezi alte lucrări și judecă singur.",
    "Testează-ne cu o demonstrație.",
    "Pentru mulți sunt ore pierdute. Pentru noi: a gândi și a optimiza.",
    "Comenzi copiate manual? Un formular le completează singur.",
    "Aceleași întrebări? Răspunsurile vin automat.",
    "Facturi și memento-uri manuale? Se trimit singure.",
    "Îți analizăm firma gratuit. Ai nevoie doar de numele firmei.",
    "Pe e-mail primești un diagnostic complet: cu șanse și pierderi pe care nu le observi.",
    "Inteligența artificială vede ce nu vede omul. Tu decizi dacă e corect.",
    "Avem și alte servicii, foarte ieftine.",
    "Pentru programatori, un semnal de trezire.",
    "Vrei un site web? Scrie-ne.",
]
assert len(TEXTOS) == len(_TIEMPOS["inicios"]), "un texto por escena"
GUION = [(inicio + RETARDO, texto) for inicio, texto in zip(_TIEMPOS["inicios"], TEXTOS)]
