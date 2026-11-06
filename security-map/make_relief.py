#!/usr/bin/env python3
"""Recorta el relieve de Natural Earth (NE1_HR_LC_SR_W_DR, dominio público) alrededor de Alemania
y lo reproyecta a Web Mercator para usarlo como fondo tipo satélite en Leaflet.

Uso: python make_relief.py /ruta/NE1_HR_LC_SR_W_DR.tif
Genera relief.jpg (mapa físico), relief-sat.jpg (estilo satélite) y relief.json (límites para L.imageOverlay).
"""
import json, math, pathlib, sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
BASE = pathlib.Path(__file__).parent
W, S, E, N = 1.0, 44.5, 20.0, 57.5   # lon/lat del recorte
PX_DEG = 21600 / 360                  # resolución del original (60 px por grado)
ESCALA = 2                            # remuestreo bicúbico para suavizar


def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def satelite(a):
    """Recolorea el relieve con una paleta tipo foto de satélite (no es una imagen satelital real)."""
    f = a.astype(np.float32) / 255
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    agua = (b > r + 0.08) & (b > g - 0.02)
    lum = (0.3 * r + 0.59 * g + 0.11 * b)
    sombra = np.clip((lum - 0.45) / 0.5, 0, 1) ** 1.3          # conserva el sombreado del relieve
    verde = np.clip((g - r) * 4 + 0.5, 0, 1)                     # zonas boscosas del original
    oscuro = np.array([0.20, 0.26, 0.13]); claro = np.array([0.50, 0.53, 0.33])
    bosque = np.array([0.11, 0.21, 0.09])
    tierra = oscuro + (claro - oscuro) * sombra[..., None]
    tierra = tierra * (1 - 0.55 * verde[..., None]) + bosque * 0.55 * verde[..., None] + 0.05 * sombra[..., None]
    sat = f.max(axis=-1) - f.min(axis=-1)
    roca = (np.clip((lum - 0.7) / 0.2, 0, 1) * np.clip((0.12 - sat) / 0.08, 0, 1))[..., None]  # nieve/roca (Alpes)
    tierra = tierra * (1 - roca) + np.array([0.85, 0.85, 0.86]) * roca
    mar = np.array([0.05, 0.12, 0.22]) + (b[..., None] - 0.6) * np.array([0.05, 0.1, 0.15])
    out = np.where(agua[..., None], mar, tierra)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    x0, x1 = int((W + 180) * PX_DEG), int((E + 180) * PX_DEG)
    y0, y1 = int((90 - N) * PX_DEG), int((90 - S) * PX_DEG)
    a = np.asarray(src.crop((x0, y0, x1, y1)))
    h_eq = a.shape[0]
    # filas de salida espaciadas uniformemente en Mercator
    out_w = (x1 - x0) * ESCALA
    m_n, m_s = merc(N), merc(S)
    out_h = int(round(out_w * (m_n - m_s) / math.radians(E - W)))
    ys = np.linspace(0, 1, out_h)
    lats = np.degrees(2 * np.arctan(np.exp(m_n - ys * (m_n - m_s))) - math.pi / 2)
    filas = np.clip(((N - lats) * PX_DEG).round().astype(int), 0, h_eq - 1)
    img = Image.fromarray(a[filas]).resize((out_w, out_h), Image.BICUBIC)
    img.save(BASE / "relief.jpg", quality=80, optimize=True, progressive=True)
    satelite(np.asarray(img)).save(BASE / "relief-sat.jpg", quality=80, optimize=True, progressive=True)
    (BASE / "relief.json").write_text(json.dumps({"bounds": [[S, W], [N, E]]}))
    print(img.size, (BASE / "relief.jpg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
