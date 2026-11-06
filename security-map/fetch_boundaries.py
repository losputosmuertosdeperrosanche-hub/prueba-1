#!/usr/bin/env python3
"""Descarga el contorno simplificado de cada ciudad consultada desde Nominatim (OpenStreetMap)."""
import glob, json, pathlib, time, requests

BASE = pathlib.Path(__file__).parent
OUT = BASE / "cities.geojson"
HEADERS = {"User-Agent": "NexusLead-security-map/1.0"}


def main():
    fc = json.loads(OUT.read_text()) if OUT.exists() else {"type": "FeatureCollection", "features": []}
    hechas = {f["properties"]["name"] for f in fc["features"]}
    for f in sorted(glob.glob(str(BASE / "raw" / "*.json"))):
        ciudad = json.loads(pathlib.Path(f).read_text())["city"]
        if ciudad in hechas:
            continue
        for intento in range(6):
            time.sleep(2)
            r = requests.get("https://nominatim.openstreetmap.org/search", headers=HEADERS, timeout=60, params={
                "city": ciudad, "countrycodes": "de", "format": "geojson", "polygon_geojson": 1,
                "polygon_threshold": 0.002, "limit": 1, "featureType": "city"})
            if r.status_code != 429:
                break
            time.sleep(20 * (intento + 1))
        r.raise_for_status()
        feats = [x for x in r.json()["features"] if x["geometry"]["type"] in ("Polygon", "MultiPolygon")]
        if not feats:
            print(ciudad, "sin contorno"); continue
        g = feats[0]["geometry"]
        fc["features"].append({"type": "Feature", "properties": {"name": ciudad}, "geometry": g})
        OUT.write_text(json.dumps(fc, separators=(",", ":")))
        print(ciudad, g["type"], len(json.dumps(g)) // 1024, "KB")


if __name__ == "__main__":
    main()
