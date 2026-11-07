#!/usr/bin/env python3
"""Monta una versión de la demo: vídeo original a 720 px y 30 fps, con una narración en otro idioma.

Cada frase empieza al principio de su tramo del vídeo (los mismos tramos que el guion).
Si una frase dura más que su tramo, el último fotograma se mantiene hasta que acaba la frase,
así una explicación nunca se pisa con la siguiente.

Uso: python demo_movil_montar.py <vídeo original> <carpeta de la narración> <salida.mp4> [módulo del guion]
"""
import importlib
import subprocess
import sys
import wave

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ANTES, DESPUES = 0.3, 0.5  # silencio antes y después de cada frase, en segundos

original, narr, salida = sys.argv[1], sys.argv[2], sys.argv[3]
guion = importlib.import_module(sys.argv[4] if len(sys.argv) > 4 else "demo_movil_guion")
GUION, DURACION = guion.GUION, guion.DURACION
N = len(GUION)


def duracion_wav(ruta):
    with wave.open(ruta, "rb") as wf:
        return wf.getnframes() / wf.getframerate()


tramos = []
for i, (inicio, _) in enumerate(GUION):
    a = 0.0 if i == 0 else inicio                      # tramo del vídeo original: [a, b)
    b = GUION[i + 1][0] if i + 1 < N else DURACION
    offset = max(ANTES, inicio - a)                    # cuándo empieza la frase dentro del tramo
    dur = duracion_wav(f"{narr}/s{i:02d}.wav")
    F = b - a
    O = max(F, offset + dur + DESPUES)                 # duración del tramo en la versión final
    tramos.append(dict(a=a, b=b, F=F, offset=offset, dur=dur, O=O))

t_salida = 0.0
for t in tramos:
    t["T"] = t_salida
    t_salida += t["O"]
TOTAL = t_salida

entradas = ["-i", original]
filtros = [f"[0:v:0]split={N}" + "".join(f"[s{i}]" for i in range(N))]
for i, t in enumerate(tramos):
    cadena = f"[s{i}]trim=start={t['a']:.3f}:end={t['b']:.3f},setpts=PTS-STARTPTS"
    if t["O"] - t["F"] > 0.01:
        cadena += f",tpad=stop_mode=clone:stop_duration={t['O'] - t['F']:.3f}"
    filtros.append(cadena + f"[v{i}]")
filtros.append("".join(f"[v{i}]" for i in range(N)) + f"concat=n={N}:v=1:a=0[vc];"
               "[vc]fps=30,scale=720:-2:flags=lanczos,format=yuv420p[vout]")
etiquetas = []
for i, t in enumerate(tramos):
    entradas += ["-i", f"{narr}/s{i:02d}.wav"]
    retardo = round((t["T"] + t["offset"]) * 1000)
    filtros.append(f"[{i + 1}:a]adelay={retardo}:all=1,aresample=44100,"
                   f"aformat=channel_layouts=stereo,volume=0.9[a{i}]")
    etiquetas.append(f"[a{i}]")
filtros.append("".join(etiquetas) + f"amix=inputs={N}:duration=longest:normalize=0,apad,"
               f"atrim=0:{TOTAL:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *entradas,
       "-filter_complex", ";".join(filtros), "-map", "[vout]", "-map", "[aout]", "-t", f"{TOTAL:.3f}",
       "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-profile:v", "high", "-level", "4.0", "-g", "60",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", salida]
subprocess.run(cmd, check=True)
congelado = 0.0
for i, t in enumerate(tramos):
    congelado += t["O"] - t["F"]
    print(f"tramo {i:02d}: vídeo {t['a']:6.2f}-{t['b']:6.2f} s, frase {t['dur']:4.1f} s, "
          f"congelado {t['O'] - t['F']:4.1f} s")
print(f"duración final {TOTAL:.1f} s (de ellos {congelado:.1f} s con la imagen congelada); demo: {salida}")
