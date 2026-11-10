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
    "Un web designer face totul manual, iar asta durează zile.",
    "Noi lucrăm cu inteligență artificială.",
    "Un site web poate fi gata în aproximativ zece minute.",
    "O persoană verifică totul. Calitatea nu scade.",
    "Mai întâi îți facem o demonstrație gratuită.",
    "Apoi, un site web pentru firma ta costă 100 de euro.",
    "Îl primești în aceeași zi. Abia apoi plătești.",
    "Vezi alte lucrări ale noastre și judecă singur.",
    "Pentru mulți, ore pierdute. Pentru noi, a gândi și a optimiza.",
    "Comenzi copiate manual? Un formular le completează singur.",
    "Aceleași întrebări? Răspunsurile vin automat.",
    "Facturi și memento-uri făcute manual? Se trimit singure.",
    "Îți analizăm firma gratuit. Ai nevoie doar de numele firmei.",
    "Pe e-mail primești un diagnostic complet.",
    "Inteligența artificială vede ce nu vede un om. Tu decizi dacă e corect.",
    "Avem și alte servicii, foarte ieftine.",
    "Pentru programatori, este un semnal de trezire.",
    "Vrei un site web? Scrie-ne, demonstrația nu costă nimic.",
]
assert len(TEXTOS) == len(_TIEMPOS["inicios"]), "un texto por escena"
GUION = [(inicio + RETARDO, texto) for inicio, texto in zip(_TIEMPOS["inicios"], TEXTOS)]
