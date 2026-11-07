#!/usr/bin/env python3
"""Sintetiza cada frase de un guion con Piper.

Uso: python demo_movil_narrar.py <carpeta de salida> <modelo .onnx> [módulo del guion]
Por defecto el guion es demo_movil_guion (alemán, voz de_DE-thorsten-high).
Para rumano: demo_movil_guion_ro con la voz ro_RO-mihai-medium.
Requisitos: pip install piper-tts, y el modelo con su .onnx.json (ver narrar_de.py).
Genera s00.wav ... sNN.wav (22.050 Hz, mono) y muestra cuánto dura cada una.
"""
import importlib
import pathlib
import sys
import wave

from piper import PiperVoice
from piper.config import SynthesisConfig

salida = pathlib.Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)
modelo = pathlib.Path(sys.argv[2])
guion = importlib.import_module(sys.argv[3] if len(sys.argv) > 3 else "demo_movil_guion")
voz = PiperVoice.load(str(modelo), config_path=str(modelo) + ".json")
for i, (inicio, texto) in enumerate(guion.GUION):
    ruta = salida / f"s{i:02d}.wav"
    with wave.open(str(ruta), "wb") as wf:
        voz.synthesize_wav(texto, wf, syn_config=SynthesisConfig(length_scale=1.0))
    with wave.open(str(ruta), "rb") as wf:
        dur = wf.getnframes() / wf.getframerate()
    print(f"s{i:02d} inicio={inicio:6.2f}s duración={dur:5.2f}s fin={inicio + dur:6.2f}s  {texto}")
