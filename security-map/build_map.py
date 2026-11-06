#!/usr/bin/env python3
"""Genera index.html: mapa de empresas de seguridad con los datos descargados.

Entradas: raw/*.json (fetch_companies.py), geocache.json (geocode.py),
contacts.json (contactos de OpenRegister), countries.geojson y vendor/*.css.
"""
import datetime, glob, json, pathlib, statistics

BASE = pathlib.Path(__file__).parent


def main():
    geocache = json.loads((BASE / "geocache.json").read_text())
    contacts = json.loads((BASE / "contacts.json").read_text())
    data, consultas = [], []
    for f in sorted(glob.glob(str(BASE / "raw" / "*.json"))):
        raw = json.loads(pathlib.Path(f).read_text())
        empresas = [e for n in sorted(raw["pages"], key=int) for e in raw["pages"][n]]
        consultas.append({"name": raw["city"], "total": raw["total_results"], "loaded": len(empresas)})
        for e in empresas:
            a = e.get("address") or {}
            g = geocache.get(e["company_id"])
            k = contacts.get(e["company_id"])
            consultado = k is not None
            if k and "error" in k:
                k = None
            data.append({
                "i": e["company_id"], "n": e["name"], "f": e["legal_form"], "c": a.get("city") or raw["city"],
                "a": a.get("formatted_value", ""), "r": f'{e["register_type"]} {e["register_number"]}',
                "g": e["register_court"], "p": e.get("purpose") or "",
                "y": g["lat"] if g else None, "x": g["lon"] if g else None, "q": g["precision"] if g else None,
                "k": k, "kc": consultado,
            })
    # Ciudades según la dirección actual de cada empresa (puede diferir de la ciudad consultada)
    completas = {c["name"] for c in consultas if c["loaded"] == c["total"]}
    por_ciudad = {}
    for d in data:
        por_ciudad.setdefault(d["c"], []).append(d)
    cities = []
    for name, ds in por_ciudad.items():
        pts = [d for d in ds if d["q"] == "direccion"]
        cities.append({"name": name, "count": len(ds), "partial": name not in completas,
                       "label": any(c["name"] == name for c in consultas),
                       "lat": statistics.median(d["y"] for d in pts) if pts else None,
                       "lon": statistics.median(d["x"] for d in pts) if pts else None})
    cities.sort(key=lambda c: (-c["count"], c["name"]))
    meta = {"fetched": datetime.date.today().strftime("%d/%m/%Y"), "cities": cities, "queries": consultas}

    html = (BASE / "template.html").read_text()
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (html.replace("/*__LEAFLET_CSS__*/", (BASE / "vendor/leaflet-1.9.4.css").read_text())
                .replace("/*__CLUSTER_CSS__*/", (BASE / "vendor/markercluster-1.5.3.css").read_text())
                .replace("/*__META__*/null", dump(meta))
                .replace("/*__DATA__*/[]", dump(data))
                .replace("/*__GEO__*/null", (BASE / "countries.geojson").read_text())
                .replace("/*__CITIES__*/null", (BASE / "cities.geojson").read_text()))
    (BASE / "index.html").write_text(html)
    sin = sum(1 for d in data if d["y"] is None)
    print(f"index.html: {len(data)} empresas, {sin} sin coordenadas, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
