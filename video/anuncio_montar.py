#!/usr/bin/env python3
"""Une los fotogramas del anuncio y su narración en un MP4 vertical 1080x1920, 30 fps, con audio AAC.

Uso: python anuncio_montar.py <carpeta fotogramas> <carpeta narración> <salida.mp4> [módulo del guion]
"""
import importlib
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
frames, narr, salida = sys.argv[1], sys.argv[2], sys.argv[3]
guion = importlib.import_module(sys.argv[4] if len(sys.argv) > 4 else "anuncio_guion_de")
GUION, DURACION = guion.GUION, guion.DURACION
entradas = ["-framerate", "30", "-i", f"{frames}/f%05d.jpg"]
filtros, etiquetas = [], []
for i, (inicio, _) in enumerate(GUION):
    entradas += ["-i", f"{narr}/s{i:02d}.wav"]
    filtros.append(f"[{i + 1}:a]adelay={round(inicio * 1000)}:all=1,aresample=44100,"
                   f"aformat=channel_layouts=stereo,volume=0.9[a{i}]")
    etiquetas.append(f"[a{i}]")
filtros.append("".join(etiquetas) + f"amix=inputs={len(GUION)}:duration=longest:normalize=0,apad,"
               f"atrim=0:{DURACION},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *entradas,
       "-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[aout]", "-t", str(DURACION),
       "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
       "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-profile:v", "high", "-level", "4.2", "-g", "60",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", salida]
subprocess.run(cmd, check=True)
print("anuncio generado:", salida)
