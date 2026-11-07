#!/usr/bin/env python3
"""Empresas de logística de OpenStreetMap en las ocho ciudades: sector "osm-logistica".

Nominatim busca cada palabra clave en cuatro cuadrantes de cada ciudad. Cada resultado trae la dirección y las
etiquetas de contacto en la misma respuesta. Se conservan los que tienen nombre de empresa, una ciudad de la
lista y un tipo de negocio, y se guardan en data/osm-logistica.json con el mismo formato que osm_pois.py.
Se descartan puntos de recogida, buzones, bancos, escuelas y organismos públicos.

Uso: python osm_logistica.py
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import re
import time

from osm_pois import CIUDADES, LOOKUP_CACHE, OUT, areas, nominatim, registro

PALABRAS = ["Spedition", "Logistik", "Logistics", "Kurier", "Paketdienst", "Transportunternehmen",
            "Fuhrunternehmen", "Frachtdienst", "Lagerei", "Lagerhaus", "Lagerhalle", "Transport",
            "DHL Zustellbasis", "DHL Paketzentrum", "DPD", "GLS", "Schenker", "Dachser"]
CATEGORIAS_DESCARTADAS = {"landuse", "information", "place", "boundary", "highway", "waterway", "natural",
                          "railway", "aeroway", "tourism", "leisure", "historic", "route", "emergency"}
EXCLUIR = re.compile(r"Shop|Kiosk|Bank|Deutsche Post|Service Point|Packstation|Paketbox|Paketshop|Paketannahme|"
                     r"Filiale|Partner|Automat|Schule|Oberstufenzentrum|Universit|Hochschule|Institut|Bundesamt|"
                     r"Kita|Kindergarten|Museum|Theater|Apotheke|Hotel|Restaurant|Café|Bäckerei", re.I)
GENERICOS = re.compile(r"^(DHL|Logistik|Lagerhaus( \d+)?|Transport|Spedition|Kurier|Paketdienst)$", re.I)
FORMA = re.compile(r"\b(GmbH|UG|KG|OHG|AG|SE|GbR|e\.\s?K\.|Co\.|Ltd|mbH)\b")


def tipo_de(nombre, categoria):
    """Tipo de negocio según el nombre (None si no parece una empresa de logística)."""
    if re.search(r"Spedit", nombre, re.I):
        return "Transitario (spedición)"
    if re.search(r"Kurier|Paket|Expressdienst|Zustellbasis|DHL|DPD|GLS|UPS|FedEx", nombre):
        return "Mensajería y paquetería"
    if re.search(r"Logistik|Logistics|Schenker|Dachser", nombre, re.I):
        return "Logística"
    if re.search(r"Lagerei|Lagerhaus|Lagerhalle", nombre, re.I):
        return "Almacén"
    if re.search(r"Transport|Fuhr|Fracht", nombre, re.I) and (FORMA.search(nombre) or categoria == "office"):
        return "Transporte de mercancías"
    return None


def main():
    zonas = areas()
    encontrados, consultas = {}, 0
    for ciudad in CIUDADES:
        a = zonas[ciudad]
        mit_lat, mit_lon = (a["s"] + a["n"]) / 2, (a["w"] + a["e"]) / 2
        cuadrantes = [(a["w"], a["n"], mit_lon, mit_lat), (mit_lon, a["n"], a["e"], mit_lat),
                      (a["w"], mit_lat, mit_lon, a["s"]), (mit_lon, mit_lat, a["e"], a["s"])]
        for palabra in PALABRAS:
            for w, n, e, s in cuadrantes:
                res = nominatim("search", {"q": palabra, "addressdetails": 1, "extratags": 1, "limit": 40,
                                           "countrycodes": "de", "viewbox": f"{w},{n},{e},{s}", "bounded": 1})
                consultas += 1
                for r in res:
                    encontrados.setdefault(f"{r['osm_type'][0].upper()}{r['osm_id']}", r)
        print(f"{ciudad}: {len(encontrados)} resultados acumulados en {consultas} consultas", flush=True)

    cache = json.loads(LOOKUP_CACHE.read_text()) if LOOKUP_CACHE.exists() else {}
    filas = []
    for clave, r in encontrados.items():
        nombre = (r.get("name") or "").strip()
        categoria = r.get("category", "")
        if (not nombre or categoria in CATEGORIAS_DESCARTADAS or EXCLUIR.search(nombre)
                or GENERICOS.match(nombre)):
            continue
        tipo = tipo_de(nombre, categoria)
        a = r.get("address", {})
        ciudad = a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or ""
        if not tipo or ciudad not in CIUDADES:
            continue
        info = {"name": nombre, "lat": float(r["lat"]), "lon": float(r["lon"]), "address": a,
                "tags": r.get("extratags") or {}}
        cache[clave] = info
        filas.append(registro(clave, {"tipo": tipo}, info))
    LOOKUP_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
    filas.sort(key=lambda f: (f[6], f[1]))
    (OUT / "osm-logistica.json").write_text(json.dumps({"rows": filas}, ensure_ascii=False, separators=(",", ":")))
    con = sum(1 for f in filas if f[7] or f[8])
    meta = {"label": "Logística (transitarios, mensajería, transporte y almacenes)", "short": "Logística",
            "title": "Logistik", "source": "osm", "file": "data/osm-logistica.json", "count": len(filas),
            "withContact": con, "cities": CIUDADES, "fetched": time.strftime("%d/%m/%Y")}
    (OUT / "osm-logistica.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"== logística: {len(filas)} empresas, {con} con teléfono o email", flush=True)


if __name__ == "__main__":
    main()
