#!/usr/bin/env python3
"""Genera index.html: mapa de empresas por sector con los datos descargados.

Entradas: raw/<código WZ>/*.json (fetch_companies.py), geocache.json (geocode.py),
contacts.json (contactos de OpenRegister), countries.geojson, relief.json (make_relief.py) y vendor/*.css.
La página usa además relief.jpg, relief-sat.jpg y basemap/*.json (basemap.py), que se publican junto a ella.
"""
import datetime, glob, json, pathlib

BASE = pathlib.Path(__file__).parent

SECTORES = {
    "80.01": {"label": "Seguridad privada", "short": "Seguridad", "title": "Sicherheit"},
    "82.30": {"label": "Organización de eventos, ferias y congresos", "short": "Eventos", "title": "Events"},
}


def main():
    geocache = json.loads((BASE / "geocache.json").read_text())
    contacts = json.loads((BASE / "contacts.json").read_text())
    data, consultas = {}, {code: [] for code in SECTORES}
    for f in sorted(glob.glob(str(BASE / "raw" / "*" / "*.json"))):
        raw = json.loads(pathlib.Path(f).read_text())
        code = raw["sector"]
        empresas = [e for n in sorted(raw["pages"], key=int) for e in raw["pages"][n]]
        consultas[code].append({"name": raw["city"], "total": raw["total_results"], "loaded": len(empresas)})
        for e in empresas:
            if e["company_id"] in data:          # la misma empresa en dos consultas o sectores
                d = data[e["company_id"]]
                if code not in d["s"]:
                    d["s"].append(code)
                continue
            a = e.get("address") or {}
            g = geocache.get(e["company_id"])
            k = contacts.get(e["company_id"])
            consultado = k is not None
            if k and "error" in k:
                k = None
            data[e["company_id"]] = {
                "i": e["company_id"], "n": e["name"], "f": e["legal_form"], "s": [code],
                "c": a.get("city") or raw["city"] or "",
                "a": a.get("formatted_value", ""), "r": f'{e["register_type"]} {e["register_number"]}',
                "g": e["register_court"], "p": e.get("purpose") or "",
                "y": g["lat"] if g else None, "x": g["lon"] if g else None, "q": g["precision"] if g else None,
                "k": k, "kc": consultado,
            }
    for qs in consultas.values():
        qs.sort(key=lambda c: -c["total"])
    meta = {"fetched": datetime.date.today().strftime("%d/%m/%Y"),
            "sectors": {code: {**s, "queries": consultas[code]} for code, s in SECTORES.items()},
            "relief": json.loads((BASE / "relief.json").read_text())["bounds"]}
    de = [f for f in json.loads((BASE / "countries.geojson").read_text())["features"] if f["properties"]["de"]]

    html = (BASE / "template.html").read_text()
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for marca, valor in [("/*__LEAFLET_CSS__*/", (BASE / "vendor/leaflet-1.9.4.css").read_text()),
                         ("/*__CLUSTER_CSS__*/", (BASE / "vendor/markercluster-1.5.3.css").read_text()),
                         ("/*__META__*/null", dump(meta)),
                         ("/*__DATA__*/[]", dump(list(data.values()))),
                         ("/*__DEBORDER__*/null", dump({"type": "FeatureCollection", "features": de}))]:
        assert marca in html, marca
        html = html.replace(marca, valor)
    (BASE / "index.html").write_text(html)
    sin = sum(1 for d in data.values() if d["y"] is None)
    por_sector = {code: sum(1 for d in data.values() if code in d["s"]) for code in SECTORES}
    print(f"index.html: {len(data)} empresas {por_sector}, {sin} sin coordenadas, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
