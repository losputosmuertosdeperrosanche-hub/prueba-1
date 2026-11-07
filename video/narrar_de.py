#!/usr/bin/env python3
"""Sintetiza la narración alemana (guion_de.py) con Piper, voz de_DE-thorsten-high.

Requisitos: pip install piper-tts ; y el modelo de voz en esta carpeta:
  https://huggingface.co/rhasspy/piper-voices/tree/main/de/de_DE/thorsten/high
  (de_DE-thorsten-high.onnx y de_DE-thorsten-high.onnx.json)
Uso: python narrar_de.py <carpeta de salida>   -> s00.wav ... s11.wav (22.050 Hz, mono)
"""
import sys, wave, pathlib
from piper import PiperVoice
from piper.config import SynthesisConfig
from guion_de import GUION

AQUI = pathlib.Path(__file__).parent
salida = pathlib.Path(sys.argv[1]); salida.mkdir(parents=True, exist_ok=True)
voz = PiperVoice.load(str(AQUI / "de_DE-thorsten-high.onnx"), config_path=str(AQUI / "de_DE-thorsten-high.onnx.json"))
for i, (inicio, texto) in enumerate(GUION):
    with wave.open(str(salida / f"s{i:02d}.wav"), "wb") as wf:
        voz.synthesize_wav(texto, wf, syn_config=SynthesisConfig(length_scale=1.0))
    print(f"s{i:02d} inicio={inicio:5.2f} {texto}")
