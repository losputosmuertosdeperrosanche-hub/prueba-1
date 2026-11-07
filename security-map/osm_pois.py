#!/usr/bin/env python3
"""Negocios reales de OpenStreetMap por sector, con su contacto público (teléfono, email, web).

1. Área de cada ciudad (Nominatim).
2. Teselas z14 de OpenFreeMap que cubren esa área: capa "poi" (nombre, tipo, posición, id OSM).
3. Nominatim /lookup (50 negocios por petición, 1 petición por segundo) con extratags y dirección.
4. Guarda data/osm-<sector>.json en formato compacto para la página.

Uso: python osm_pois.py hosteleria salud inmobiliarias
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import gzip, json, math, pathlib, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import mapbox_vector_tile as mvt
import requests

import basemap

BASE = pathlib.Path(__file__).parent
OUT = BASE / "data"
LOOKUP_CACHE = BASE / "osm_lookup.json"
AREAS_CACHE = BASE / "osm_areas.json"
HEADERS = {"User-Agent": "NexusLead-security-map/1.0"}
NOMINATIM = "https://nominatim.openstreetmap.org"

CIUDADES = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main", "Stuttgart", "Düsseldorf", "Nürnberg"]

# (clase, subclase) de la capa poi de OpenMapTiles -> tipo de negocio
SECTORES = {
    "hosteleria": {
        "label": "Hostelería (restaurantes, bares, cafeterías y hoteles)", "short": "Hostelería", "title": "Gastro",
        "tipos": {("restaurant", "restaurant"): "Restaurante", ("cafe", "cafe"): "Cafetería",
                  ("fast_food", "fast_food"): "Comida rápida", ("bar", "bar"): "Bar", ("beer", "pub"): "Pub",
                  ("lodging", "hotel"): "Hotel", ("lodging", "guest_house"): "Pensión"}},
    "salud": {
        "label": "Salud (consultas médicas, dentistas y clínicas)", "short": "Salud", "title": "Gesundheit",
        "tipos": {("doctors", "doctors"): "Consulta médica", ("office", "physician"): "Consulta médica",
                  ("dentist", "dentist"): "Dentista", ("hospital", "clinic"): "Clínica",
                  ("office", "therapist"): "Terapeuta"}},
    "inmobiliarias": {
        "label": "Inmobiliarias y administración de fincas", "short": "Inmobiliarias", "title": "Immobilien",
        "tipos": {("office", "estate_agent"): "Inmobiliaria", ("shop", "estate_agent"): "Inmobiliaria",
                  ("office", "property_management"): "Administración de fincas"}},
    "peluqueria": {
        "label": "Peluquerías y centros de estética", "short": "Peluquería", "title": "Friseur & Kosmetik",
        "tipos": {("shop", "beauty"): "Peluquería o estética"}},
}
TIPO_OSM = {1: "N", 2: "W", 3: "R"}       # último dígito del id de OpenMapTiles


def nominatim(path, params):
    for intento in range(8):
        time.sleep(1.1)
        r = requests.get(f"{NOMINATIM}/{path}", params={**params, "format": "jsonv2"}, headers=HEADERS, timeout=90)
        if r.status_code == 200:
            return r.json()
        print(f"  Nominatim HTTP {r.status_code}, reintento", flush=True)
        time.sleep(15 * (intento + 1))
    r.raise_for_status()


# El recuadro de Hamburg incluye las islas de Neuwerk/Scharhörn en el mar del Norte: se limita al área urbana
AJUSTES_AREA = {"Hamburg": {"w": 9.72}}


def areas():
    cache = json.loads(AREAS_CACHE.read_text()) if AREAS_CACHE.exists() else {}
    for c in CIUDADES:
        if c not in cache:
            res = nominatim("search", {"city": c, "countrycodes": "de", "limit": 1, "featureType": "city"})
            s, n, w, e = map(float, res[0]["boundingbox"])
            cache[c] = {"s": s, "n": n, "w": w, "e": e}
            AREAS_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    return {c: {**cache[c], **AJUSTES_AREA.get(c, {})} for c in CIUDADES}


def pois_de_teselas(url_tpl, area, tipos):
    x0, y0 = basemap.tile_of(area["n"], area["w"], 14)
    x1, y1 = basemap.tile_of(area["s"], area["e"], 14)
    teselas = [(14, x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        datos = list(pool.map(lambda t: (t, basemap.descargar(url_tpl, *t)), teselas))
    encontrados = {}
    for (z, x, y), data in datos:
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        capa = mvt.decode(data, default_options={"y_coord_down": True}).get("poi")
        if not capa:
            continue
        ext = capa.get("extent", 4096)
        for f in capa["features"]:
            p = f["properties"]
            tipo = tipos.get((p.get("class"), p.get("subclass")))
            osm_t = TIPO_OSM.get(f.get("id", 0) % 10)
            if not tipo or not osm_t or not p.get("name") or f["geometry"]["type"] != "Point":
                continue
            px, py = f["geometry"]["coordinates"]
            if not (0 <= px < ext and 0 <= py < ext):     # el margen de la tesela se repite en la vecina
                continue
            lon, lat = basemap.lonlat(z, x, y, px, py, ext)
            encontrados[f"{osm_t}{f['id'] // 10}"] = {"tipo": tipo, "lat": lat, "lon": lon}
    return encontrados, len(teselas)


def lookup(ids):
    cache = json.loads(LOOKUP_CACHE.read_text()) if LOOKUP_CACHE.exists() else {}
    pendientes = [i for i in ids if i not in cache]
    print(f"  Nominatim: {len(pendientes)} negocios por consultar ({len(ids) - len(pendientes)} ya en caché)", flush=True)
    for k in range(0, len(pendientes), 50):
        lote = pendientes[k:k + 50]
        res = nominatim("lookup", {"osm_ids": ",".join(lote), "extratags": 1, "addressdetails": 1, "accept-language": "de"})
        vistos = set()
        for r in res:
            clave = f"{r['osm_type'][0].upper()}{r['osm_id']}"
            vistos.add(clave)
            cache[clave] = {"name": r.get("name") or "", "lat": float(r["lat"]), "lon": float(r["lon"]),
                            "address": r.get("address", {}), "tags": r.get("extratags") or {}}
        for clave in lote:                       # borrados de OSM desde que se generaron las teselas
            cache.setdefault(clave, None)
        if (k // 50) % 10 == 0 or k + 50 >= len(pendientes):
            LOOKUP_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
            print(f"  {min(k + 50, len(pendientes))}/{len(pendientes)}", flush=True)
    LOOKUP_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
    return cache


def primero(tags, *claves):
    for c in claves:
        v = (tags.get(c) or "").strip()
        if v:
            return v.split(";")[0].strip()
    return ""


def estrellas(v):
    """Categoría hotelera de OSM: "4", "3S" (Superior en la clasificación alemana)."""
    m = re.fullmatch(r"\s*(\d)(S?)\s*", v or "")
    if not m:
        return ""
    return f"{m.group(1)} {'estrella' if m.group(1) == '1' else 'estrellas'}" + (" Superior" if m.group(2) else "")


def registro(clave, info, r):
    """Fila compacta: [id, nombre, tipo, lat, lon, dirección, ciudad, teléfono, email, web, horario, extra]."""
    a, t = r["address"], r["tags"]
    calle = " ".join(v for v in [a.get("road") or a.get("pedestrian") or a.get("square") or "", a.get("house_number", "")] if v)
    ciudad = a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or ""
    direccion = ", ".join(v for v in [calle, " ".join(v for v in [a.get("postcode", ""), ciudad] if v)] if v)
    extra = primero(t, "cuisine") or primero(t, "healthcare:speciality") or estrellas(t.get("stars", ""))
    return [clave, r["name"], info["tipo"], round(r["lat"], 6), round(r["lon"], 6), direccion, ciudad,
            primero(t, "phone", "contact:phone", "contact:mobile", "mobile"),
            primero(t, "email", "contact:email"),
            primero(t, "website", "contact:website", "url"),
            primero(t, "opening_hours"), extra.replace("_", " ")]


def main():
    sectores = sys.argv[1:] or list(SECTORES)
    url_tpl = requests.get(basemap.TILEJSON, headers=HEADERS, timeout=60).json()["tiles"][0]
    zonas = areas()
    OUT.mkdir(exist_ok=True)
    for s in sectores:
        cfg = SECTORES[s]
        candidatos, cobertura = {}, []
        for c in CIUDADES:
            encontrados, n = pois_de_teselas(url_tpl, zonas[c], cfg["tipos"])
            print(f"{s} · {c}: {len(encontrados)} negocios en {n} teselas", flush=True)
            candidatos.update(encontrados)
            cobertura.append(c)
        cache = lookup(sorted(candidatos))
        filas = [registro(k, v, cache[k]) for k, v in candidatos.items() if cache.get(k) and cache[k]["name"]]
        # solo negocios cuya dirección está en una de las ciudades cubiertas (el recuadro incluye pueblos vecinos)
        filas = [f for f in filas if f[6] in CIUDADES]
        filas.sort(key=lambda f: (f[6], f[1]))
        (OUT / f"osm-{s}.json").write_text(json.dumps({"rows": filas}, ensure_ascii=False, separators=(",", ":")))
        con = sum(1 for f in filas if f[7] or f[8])
        meta = {"label": cfg["label"], "short": cfg["short"], "title": cfg["title"], "source": "osm",
                "file": f"data/osm-{s}.json", "count": len(filas), "withContact": con, "cities": cobertura,
                "fetched": time.strftime("%d/%m/%Y")}
        (OUT / f"osm-{s}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        print(f"== {s}: {len(filas)} negocios, {con} con teléfono o email", flush=True)


if __name__ == "__main__":
    main()
