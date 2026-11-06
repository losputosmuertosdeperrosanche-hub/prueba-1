#!/usr/bin/env python3
"""Descarga empresas activas de un sector (código WZ 2025) desde OpenRegister.

Cada búsqueda cuesta 10 créditos y devuelve como máximo 30 empresas.
Uso:
    OPENREGISTER_API_KEY=... python fetch_companies.py 80.01 "Nürnberg" [max_paginas]
    OPENREGISTER_API_KEY=... python fetch_companies.py 82.30 "" [max_paginas]   # toda Alemania
Guarda raw/<codigo>/<ciudad o Deutschland>.json con todas las páginas descargadas.
"""
import json, os, sys, time, pathlib, requests

API = "https://api.openregister.de/v1/search/company"
OUT = pathlib.Path(__file__).parent / "raw"


def pagina(api_key, wz, ciudad, n):
    filtros = [{"field": "industry_codes", "values": [wz]}, {"field": "active", "value": "true"}]
    if ciudad:
        filtros.append({"field": "city", "value": ciudad})
    body = {"filters": filtros, "pagination": {"page": n, "per_page": 30}}
    r = requests.post(API, json=body, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    key = os.environ["OPENREGISTER_API_KEY"]
    wz, ciudad = sys.argv[1], sys.argv[2]
    max_paginas = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    carpeta = OUT / wz
    carpeta.mkdir(parents=True, exist_ok=True)
    f = carpeta / f"{ciudad or 'Deutschland'}.json"
    datos = json.loads(f.read_text()) if f.exists() else {"sector": wz, "city": ciudad, "pages": {}}
    total_pages = datos.get("total_pages")
    for n in range(1, max_paginas + 1):
        if str(n) in datos["pages"]:
            continue
        if total_pages is not None and n > total_pages:
            break
        d = pagina(key, wz, ciudad, n)
        datos["pages"][str(n)] = d["results"]
        datos["total_pages"] = total_pages = d["pagination"]["total_pages"]
        datos["total_results"] = d["pagination"]["total_results"]
        f.write_text(json.dumps(datos, ensure_ascii=False, indent=1))
        time.sleep(0.3)
    print(f"{wz} {ciudad or 'Deutschland'}: {datos.get('total_results')} empresas, "
          f"{datos.get('total_pages')} páginas, descargadas {len(datos['pages'])}")


if __name__ == "__main__":
    main()
