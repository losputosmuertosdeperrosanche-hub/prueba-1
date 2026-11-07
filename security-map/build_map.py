#!/usr/bin/env python3
"""Genera index.html: mapa de empresas por sector con los datos descargados.

Entradas: raw/<código WZ>/*.json (fetch_companies.py), geocache.json (geocode.py),
contacts.json (contactos de OpenRegister), countries.geojson, relief.json (make_relief.py) y vendor/*.css.
La página usa además relief.jpg, relief-sat.jpg, basemap/*.json (basemap.py) y data/osm-*.json (osm_pois.py),
que se publican junto a ella.
"""
import argparse, datetime, glob, json, pathlib

import i18n_de

BASE = pathlib.Path(__file__).parent

ORDEN_OSM = ["osm-hosteleria", "osm-salud", "osm-inmobiliarias"]

SECTORES = {
    "80.01": {"label": "Seguridad privada", "short": "Seguridad", "title": "Sicherheit"},
    "82.30": {"label": "Organización de eventos, ferias y congresos", "short": "Eventos", "title": "Events"},
}


def main(lang="es"):
    de = lang == "de"
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
    sectors = {code: {**s, **(i18n_de.SECTORES_DE[code] if de else {}), "source": "openregister", "queries": consultas[code]}
               for code, s in SECTORES.items()}
    # Sectores de OpenStreetMap (osm_pois.py): la página descarga data/osm-<sector>.json en segundo plano
    cache = json.loads((BASE / "osm_lookup.json").read_text()) if de else {}
    for f in sorted((BASE / "data").glob("osm-*.meta.json"), key=lambda f: ORDEN_OSM.index(f.name.split(".")[0])):
        code = f.name.split(".")[0]
        meta = json.loads(f.read_text())
        if not de:
            sectors[code] = meta
            continue
        # versión alemana: filas traducidas en data-de/ (solo para el vídeo en alemán)
        filas = json.loads((BASE / "data" / f"{code}.json").read_text())["rows"]
        (BASE / "data-de").mkdir(exist_ok=True)
        traducidas = [i18n_de.fila_de(r, (cache.get(r[0]) or {}).get("tags")) for r in filas]
        (BASE / "data-de" / f"{code}.json").write_text(json.dumps({"rows": traducidas}, ensure_ascii=False, separators=(",", ":")))
        sectors[code] = i18n_de.meta_de(code, meta, f"data-de/{code}.json")
    meta = {"fetched": datetime.date.today().strftime("%d/%m/%Y"), "sectors": sectors,
            "relief": json.loads((BASE / "relief.json").read_text())["bounds"]}
    frontera = [f for f in json.loads((BASE / "countries.geojson").read_text())["features"] if f["properties"]["de"]]

    html = (BASE / "template.html").read_text()
    if de:
        html = i18n_de.traducir_plantilla(html)
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # Un único enlace: la página española y la alemana se publican juntas y se cambian con este botón
    enlace = ('<a class="lang" href="index.html" lang="es">Español</a>' if de
              else '<a class="lang" href="index-de.html" lang="de">Deutsch</a>')
    for marca, valor in [("<!--__IDIOMA__-->", enlace),
                         ("/*__LEAFLET_CSS__*/", (BASE / "vendor/leaflet-1.9.4.css").read_text()),
                         ("/*__CLUSTER_CSS__*/", (BASE / "vendor/markercluster-1.5.3.css").read_text()),
                         ("/*__META__*/null", dump(meta)),
                         ("/*__DATA__*/[]", dump(list(data.values()))),
                         ("/*__DEBORDER__*/null", dump({"type": "FeatureCollection", "features": frontera}))]:
        assert marca in html, marca
        html = html.replace(marca, valor)
    if de:  # index-de.html va como página propia del artefacto: necesita su propio esqueleto
        html = i18n_de.DOCUMENTO_INICIO + html + i18n_de.DOCUMENTO_FIN
    salida = BASE / ("index-de.html" if de else "index.html")
    salida.write_text(html)
    sin = sum(1 for d in data.values() if d["y"] is None)
    por_sector = {code: sum(1 for d in data.values() if code in d["s"]) for code in SECTORES}
    osm = {c: s["count"] for c, s in sectors.items() if s["source"] == "osm"}
    print(f"{salida.name}: {len(data)} empresas {por_sector}, {sin} sin coordenadas, {len(html) // 1024} KB; OpenStreetMap: {osm}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Genera index.html (español) o index-de.html (alemán, --lang de).")
    ap.add_argument("--lang", choices=["es", "de"], default="es")
    main(ap.parse_args().lang)
