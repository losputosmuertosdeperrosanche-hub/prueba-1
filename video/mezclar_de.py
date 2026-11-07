#!/usr/bin/env python3
"""Une los fotogramas (render.js) y la narración (narrar_de.py) en un MP4 vertical 1080x1920, 30 fps, con audio AAC.

Uso: python mezclar_de.py <carpeta fotogramas> <carpeta narración> <salida.mp4>
"""
import subprocess, sys, pathlib
import imageio_ffmpeg
from guion_de import GUION, DURACION

FF = imageio_ffmpeg.get_ffmpeg_exe()
frames, narr, salida = sys.argv[1], sys.argv[2], sys.argv[3]
entradas = ["-framerate", "30", "-i", f"{frames}/f%05d.jpg"]
filtros, etiquetas = [], []
for i, (inicio, _) in enumerate(GUION):
    entradas += ["-i", f"{narr}/s{i:02d}.wav"]
    retardo = round(inicio * 1000)
    filtros.append(f"[{i + 1}:a]adelay={retardo}:all=1,aresample=44100,aformat=channel_layouts=stereo,volume=0.85[a{i}]")
    etiquetas.append(f"[a{i}]")
filtros.append("".join(etiquetas) + f"amix=inputs={len(GUION)}:duration=longest:normalize=0,apad,"
               f"atrim=0:{DURACION},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *entradas,
       "-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[aout]", "-t", str(DURACION),
       "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
       "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-level", "4.2", "-g", "60",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", salida]
subprocess.run(cmd, check=True)
print("vídeo generado:", salida)
