#!/usr/bin/env python3
"""Descarga empresas de seguridad (WZ 2025: 80.01) activas por ciudad desde OpenRegister.

Cada búsqueda cuesta 10 créditos y devuelve como máximo 30 empresas.
Uso: OPENREGISTER_API_KEY=... python fetch_companies.py "Nürnberg" [max_paginas]
Guarda raw/<ciudad>.json con todas las páginas descargadas.
"""
import json, os, sys, time, pathlib, requests

API = "https://api.openregister.de/v1/search/company"
WZ_SEGURIDAD = "80.01"
OUT = pathlib.Path(__file__).parent / "raw"

def pagina(api_key, ciudad, n):
    body = {"filters": [{"field": "industry_codes", "values": [WZ_SEGURIDAD]},
                        {"field": "city", "value": ciudad},
                        {"field": "active", "value": "true"}],
            "pagination": {"page": n, "per_page": 30}}
    r = requests.post(API, json=body, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    key = os.environ["OPENREGISTER_API_KEY"]
    ciudad = sys.argv[1]
    max_paginas = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    OUT.mkdir(exist_ok=True)
    f = OUT / f"{ciudad}.json"
    datos = json.loads(f.read_text()) if f.exists() else {"city": ciudad, "pages": {}}
    total_pages = datos.get("total_pages")
    for n in range(1, max_paginas + 1):
        if str(n) in datos["pages"]:
            continue
        if total_pages is not None and n > total_pages:
            break
        d = pagina(key, ciudad, n)
        datos["pages"][str(n)] = d["results"]
        datos["total_pages"] = total_pages = d["pagination"]["total_pages"]
        datos["total_results"] = d["pagination"]["total_results"]
        f.write_text(json.dumps(datos, ensure_ascii=False, indent=1))
        time.sleep(0.3)
    print(f"{ciudad}: {datos.get('total_results')} empresas, {datos.get('total_pages')} páginas, descargadas {len(datos['pages'])}")

if __name__ == "__main__":
    main()
