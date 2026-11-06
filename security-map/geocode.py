#!/usr/bin/env python3
"""Geocodifica las direcciones de raw/*.json con OpenStreetMap.

Usa Photon (photon.komoot.io). Las primeras ~100 se hicieron con Nominatim (consulta estructurada
con calle + código postal); ambos usan datos de OpenStreetMap.
Solo se marca precisión "direccion" si el resultado es una casa/calle con el mismo código postal;
si no, se usa el centro del código postal ("codigo_postal") o de la ciudad ("ciudad").
Guarda los resultados en geocache.json para no repetir consultas.
"""
import glob, json, pathlib, threading, time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = pathlib.Path(__file__).parent
CACHE = BASE / "geocache.json"
HEADERS = {"User-Agent": "NexusLead-security-map/1.0"}
PHOTON = "https://photon.komoot.io/api/"


def photon(q, plz=None, tipos=None):
    for intento in range(5):
        time.sleep(0.6)
        r = requests.get(PHOTON, params={"q": q, "limit": 5, "lang": "de"}, headers=HEADERS, timeout=60)
        if r.status_code not in (429, 502, 503, 504):
            break
        time.sleep(15 * (intento + 1))
    r.raise_for_status()
    for f in r.json().get("features", []):
        pr = f["properties"]
        if pr.get("countrycode") != "DE":
            continue
        if plz and pr.get("postcode") and pr["postcode"] != plz:
            continue
        if tipos and pr.get("type") not in tipos:
            continue
        lon, lat = f["geometry"]["coordinates"]
        return lat, lon
    return None


def geocodificar(a):
    plz, city, street = a.get("postal_code", ""), a.get("city", ""), a.get("street", "")
    if street:
        p = photon(f"{street}, {plz} {city}", plz, {"house", "street"})
        if p:
            return p, "direccion"
    if plz:
        p = photon(f"{plz} {city}", plz)
        if p:
            return p, "codigo_postal"
    if city:
        p = photon(f"{city}, Deutschland", None, {"city", "district", "locality"})
        if p:
            return p, "ciudad"
    return None, None


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    empresas = [e for f in sorted(glob.glob(str(BASE / "raw" / "*.json")))
                for p in json.load(open(f))["pages"].values() for e in p]
    pendientes = [e for e in empresas if e["company_id"] not in cache]
    lock = threading.Lock()

    def tarea(e):
        punto, precision = geocodificar(e.get("address") or {})
        with lock:
            cache[e["company_id"]] = {"lat": punto[0], "lon": punto[1], "precision": precision} if punto else None
            CACHE.write_text(json.dumps(cache))
            print(f"{len(cache)}/{len(empresas)} {precision or 'SIN RESULTADO'}", flush=True)

    # 4 consultas simultáneas como máximo para no sobrecargar Photon
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(tarea, pendientes))
    sin = sum(1 for v in cache.values() if not v)
    print(f"Hecho: {len(cache)} geocodificadas, {sin} sin coordenadas")


if __name__ == "__main__":
    main()
