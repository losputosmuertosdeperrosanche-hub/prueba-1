#!/usr/bin/env python3
"""Sintetiza cada frase de demo_movil_guion.py con Piper (voz de_DE-thorsten-high).

Uso: python demo_movil_narrar.py <carpeta de salida> <ruta al modelo .onnx>
Requisitos: pip install piper-tts, y el modelo con su .onnx.json (ver narrar_de.py).
Genera s00.wav ... s06.wav (22.050 Hz, mono) y muestra cuánto dura cada una.
"""
import pathlib, sys, wave
from piper import PiperVoice
from piper.config import SynthesisConfig
from demo_movil_guion import GUION

salida = pathlib.Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)
modelo = pathlib.Path(sys.argv[2])
voz = PiperVoice.load(str(modelo), config_path=str(modelo) + ".json")
for i, (inicio, texto) in enumerate(GUION):
    ruta = salida / f"s{i:02d}.wav"
    with wave.open(str(ruta), "wb") as wf:
        voz.synthesize_wav(texto, wf, syn_config=SynthesisConfig(length_scale=1.0))
    with wave.open(str(ruta), "rb") as wf:
        dur = wf.getnframes() / wf.getframerate()
    print(f"s{i:02d} inicio={inicio:6.2f}s duración={dur:5.2f}s fin={inicio + dur:6.2f}s  {texto}")
