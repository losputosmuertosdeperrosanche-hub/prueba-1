#!/usr/bin/env python3
"""Fondo de mapa a partir de teselas vectoriales de OpenStreetMap (OpenFreeMap, esquema OpenMapTiles).

Descarga las teselas necesarias, las simplifica y las guarda en formato compacto
(enteros a 1e-5 grados con diferencias; ver codificar()) agrupadas en paquetes:
  basemap/pais.json        z8 para toda Alemania: autopistas, carreteras principales, ríos, lagos, ciudades
  basemap/zona-<x>_<y>.json     una por cada tesela z11 (~20 km): carreteras, agua, bosques, zonas urbanas, barrios
  basemap/detalle-<x>_<y>.json  una por cada tesela z12 (~5 km) con datos z14 alrededor de las empresas
                                y negocios con contacto: calles, edificios, agua, parques
La página carga las zonas al acercarse (zoom 10,5) y los bloques de detalle al acercarse más (zoom 13,5).

Uso: python basemap.py
Datos © colaboradores de OpenStreetMap (ODbL), teselas de OpenFreeMap (OpenMapTiles).
"""
import gzip, json, math, pathlib, time
from concurrent.futures import ThreadPoolExecutor

import mapbox_vector_tile as mvt
import requests
from shapely.geometry import MultiPolygon, shape

MIN_EDIFICIO_M2 = 100    # se descartan casetas, garajes y anexos pequeños
MIN_AREA_PAIS_M2 = 1e7   # bosques/zonas urbanas de la capa país: solo manchas de más de 10 km²
TOLERANCIA_M = {8: 60, 11: 6, 14: 1.5}   # simplificación de contornos, en metros, según el zoom

BASE = pathlib.Path(__file__).parent
CACHE = BASE / ".tilecache"          # .pbf descargados (no se suben al repositorio)
OUT = BASE / "basemap"
TILEJSON = "https://tiles.openfreemap.org/planet"
HEADERS = {"User-Agent": "NexusLead-security-map/1.0"}
DE = (5.8, 47.2, 15.1, 55.1)         # oeste, sur, este, norte

# Qué capas y clases se guardan en cada nivel (None = todas las clases)
CAPAS = {
    8: {"water": None, "waterway": {"river", "canal"}, "place": {"city", "town"},
        "landcover": {"wood"}, "landuse": {"residential", "suburb"},
        "transportation": {"motorway", "trunk", "primary"}},
    11: {"water": None, "waterway": {"river", "canal"}, "landcover": {"wood", "grass"},
         "landuse": {"residential", "suburb", "neighbourhood", "industrial", "commercial", "retail"},
         "park": None, "place": {"city", "town", "village", "suburb"},
         "transportation": {"motorway", "trunk", "primary", "secondary", "tertiary", "rail"}},
    14: {"water": None, "waterway": {"river", "canal", "stream"}, "landcover": {"wood", "grass"},
         "landuse": {"residential", "industrial", "commercial", "retail", "railway", "cemetery"},
         "park": None, "building": None, "place": {"suburb", "quarter", "neighbourhood", "village", "hamlet"},
         "transportation": {"motorway", "trunk", "primary", "secondary", "tertiary", "minor", "rail",
                            "motorway_link", "trunk_link", "primary_link"}},
}


def tile_of(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def parent(x, y, z, pz):
    f = 2 ** (z - pz)
    return x // f, y // f


def lonlat(z, x, y, px, py, extent):
    n = 2 ** z
    lon = (x + px / extent) / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + py / extent) / n))))
    return round(lon, 5), round(lat, 5)


def descargar(url_tpl, z, x, y):
    f = CACHE / f"{z}/{x}/{y}.pbf"
    if f.exists():
        return f.read_bytes()
    for intento in range(5):
        r = requests.get(url_tpl.format(z=z, x=x, y=y), headers=HEADERS, timeout=60)
        if r.status_code == 200:
            break
        time.sleep(3 * (intento + 1))
    r.raise_for_status()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(r.content)
    return r.content


def convertir(z, x, y, data):
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    capas = mvt.decode(data, default_options={"y_coord_down": True})
    feats = []
    for nombre, filtro in CAPAS[z].items():
        capa = capas.get(nombre)
        if not capa:
            continue
        ext = capa.get("extent", 4096)
        metros = 40075016 * math.cos(math.radians(lonlat(z, x, y, 0, ext / 2, ext)[1])) / 2 ** z / ext
        for f in capa["features"]:
            p = f["properties"]
            cls = "building" if nombre == "building" else p.get("class")
            if filtro is not None and cls not in filtro:
                continue
            g = f["geometry"]
            if g["type"] == "Point":
                nom = p.get("name:de") or p.get("name")
                if nombre == "place" and nom:
                    feats.append([nombre, cls, z, "P", list(q(lonlat(z, x, y, *g["coordinates"], ext))), nom])
                continue
            if g["type"] == "MultiPoint":
                continue
            geom = shape(g)
            if nombre == "building" and geom.area * metros ** 2 < MIN_EDIFICIO_M2:
                continue
            tol = TOLERANCIA_M[z]
            if z == 8 and nombre in ("landcover", "landuse"):
                # a escala de país solo bosques y núcleos urbanos grandes, para que la carga inicial sea ligera
                partes = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
                partes = [g for g in partes if g.geom_type == "Polygon" and g.area * metros ** 2 >= MIN_AREA_PAIS_M2]
                if not partes:
                    continue
                geom = MultiPolygon(partes)
                tol = 250
            geom = geom.simplify(tol / metros, preserve_topology=True)
            if geom.is_empty:
                continue
            feats.append([nombre, cls, z, *codificar(geom, lambda px, py: q(lonlat(z, x, y, px, py, ext)))])
    return feats


def q(ll):
    """Cuantiza lon/lat a 1e-5 grados (~1 m) como enteros."""
    return round(ll[0] * 1e5), round(ll[1] * 1e5)


def delta(coords, proyectar):
    """Anillo o línea como lista plana de enteros con diferencias: [x0, y0, dx1, dy1, ...]."""
    out, px, py = [], 0, 0
    for c in coords:
        x, y = proyectar(c[0], c[1])
        if out and x == px and y == py:
            continue
        out += [x - px, y - py]
        px, py = x, y
    return out


def codificar(geom, proyectar):
    """Devuelve [tipo, partes]: L = líneas, A = polígonos (cada polígono es una lista de anillos)."""
    t = geom.geom_type
    if t in ("LineString", "MultiLineString"):
        lineas = [geom] if t == "LineString" else list(geom.geoms)
        return ["L", [delta(l.coords, proyectar) for l in lineas]]
    polis = [geom] if t == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    return ["A", [[delta(p.exterior.coords, proyectar)] + [delta(r.coords, proyectar) for r in p.interiors] for p in polis]]


def main():
    url_tpl = requests.get(TILEJSON, headers=HEADERS, timeout=60).json()["tiles"][0]
    puntos = [v for v in json.loads((BASE / "geocache.json").read_text()).values() if v]
    # Teselas a descargar
    pedidos = {8: set(), 11: set(), 14: set()}
    x0, y0 = tile_of(DE[3], DE[0], 8)
    x1, y1 = tile_of(DE[1], DE[2], 8)
    pedidos[8] = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    for p in puntos:
        pedidos[11].add(tile_of(p["lat"], p["lon"], 11))
        pedidos[14].add(tile_of(p["lat"], p["lon"], 14))
    # Negocios de OpenStreetMap (osm_pois.py): calles a escala de ciudad en toda el área de cada ciudad
    # y detalle (calles y edificios) alrededor de cada negocio con teléfono o email
    import osm_pois
    if osm_pois.AREAS_CACHE.exists():
        for a in osm_pois.areas().values():
            ax0, ay0 = tile_of(a["n"], a["w"], 11)
            ax1, ay1 = tile_of(a["s"], a["e"], 11)
            pedidos[11] |= {(x, y) for x in range(ax0, ax1 + 1) for y in range(ay0, ay1 + 1)}
    for f in sorted((BASE / "data").glob("osm-*.json")):
        if f.name.endswith(".meta.json"):
            continue
        for r in json.loads(f.read_text())["rows"]:
            if r[7] or r[8]:
                pedidos[14].add(tile_of(r[3], r[4], 14))
                pedidos[11].add(tile_of(r[3], r[4], 11))
    print({z: len(t) for z, t in pedidos.items()})

    trabajos = [(z, x, y) for z, ts in pedidos.items() for x, y in sorted(ts)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        datos = list(pool.map(lambda t: (t, descargar(url_tpl, *t)), trabajos))

    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.json"):
        f.unlink()
    paquetes = {}
    for (z, x, y), data in datos:
        if z == 8:
            clave = "pais"
        else:
            px, py = parent(x, y, z, 11)
            clave = f"zona-{px}_{py}" if z == 11 else "detalle-{}_{}".format(*parent(x, y, z, 12))
        paquetes.setdefault(clave, []).extend(convertir(z, x, y, data))
    orden = ["landcover", "landuse", "park", "water", "waterway", "building", "transportation", "place"]
    indice = []
    for clave, feats in paquetes.items():
        # formato compacto: [capa, clase, zoom_origen, tipo, geometría o punto, nombre?]
        feats.sort(key=lambda f: (orden.index(f[0]), f[2]))
        (OUT / f"{clave}.json").write_text(json.dumps({"f": feats}, ensure_ascii=False, separators=(",", ":")))
        if clave != "pais":
            indice.append((clave.split("-")[0], [int(v) for v in clave.split("-")[1].split("_")]))
    (OUT / "index.json").write_text(json.dumps({
        "zoom": 11, "zonas": sorted(xy for t, xy in indice if t == "zona"),
        "detalle_zoom": 12, "detalles": sorted(xy for t, xy in indice if t == "detalle")}))
    total = sum(f.stat().st_size for f in OUT.glob("*.json"))
    print(f"{len(paquetes)} paquetes, {total // 1024 // 1024} MB en total")


if __name__ == "__main__":
    main()
