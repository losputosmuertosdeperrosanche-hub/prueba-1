#!/usr/bin/env python3
"""Monta la demo: vídeo original a 720 px de ancho y 30 fps (H.264) + narración alemana (AAC).

Uso: python demo_movil_mezclar.py <vídeo original> <carpeta de la narración> <salida.mp4>
"""
import subprocess, sys
import imageio_ffmpeg
from demo_movil_guion import DURACION, GUION

FF = imageio_ffmpeg.get_ffmpeg_exe()
original, narr, salida = sys.argv[1], sys.argv[2], sys.argv[3]
entradas = ["-i", original]
filtros, etiquetas = [], []
for i, (inicio, _) in enumerate(GUION):
    entradas += ["-i", f"{narr}/s{i:02d}.wav"]
    filtros.append(f"[{i + 1}:a]adelay={round(inicio * 1000)}:all=1,aresample=44100,"
                   f"aformat=channel_layouts=stereo,volume=0.9[a{i}]")
    etiquetas.append(f"[a{i}]")
filtros.append("".join(etiquetas) + f"amix=inputs={len(GUION)}:duration=longest:normalize=0,apad,"
               f"atrim=0:{DURACION},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
filtros.append("[0:v:0]fps=30,scale=720:-2:flags=lanczos,format=yuv420p[vout]")
cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *entradas,
       "-filter_complex", ";".join(filtros), "-map", "[vout]", "-map", "[aout]", "-t", str(DURACION),
       "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-profile:v", "high", "-level", "4.0", "-g", "60",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", salida]
subprocess.run(cmd, check=True)
print("demo generada:", salida)
