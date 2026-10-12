#!/usr/bin/env python3
"""NexusLead - buscador simple por terminal sobre la API de OpenRegister.

Busca empresas del sector cosmética en Núremberg (Nürnberg) usando
POST https://api.openregister.de/v1/search/company.

Uso:
    export OPENREGISTER_API_KEY="tu_api_key"
    python nexuslead_search.py                      # cosmética en Nürnberg
    python nexuslead_search.py -q "Naturkosmetik"    # texto libre adicional
    python nexuslead_search.py --wz                  # filtrar por códigos WZ
    python nexuslead_search.py --todas --csv leads.csv
"""

import argparse
import csv
import os
import sys

import requests

API_URL = "https://api.openregister.de/v1/search/company"

# Palabras clave (en alemán) que se buscan en el objeto social ("purpose")
# registrado en el Handelsregister.
KEYWORDS_COSMETICA = [
    "Kosmetik",
    "kosmetisch",
    "Körperpflege",
    "Hautpflege",
    "Parfüm",
    "Duftstoffe",
    "Beauty",
]

# Códigos WZ 2025 relacionados con cosmética.
WZ_COSMETICA = {
    "20.42": "Herstellung von Körperpflegemitteln und Duftstoffen",
    "46.45": "Großhandel mit kosmetischen Erzeugnissen und Körperpflegemitteln",
    "47.75": "Einzelhandel mit kosmetischen Erzeugnissen und Körperpflegemitteln",
    "96.02": "Friseur- und Kosmetiksalons",
}


def construir_peticion(args):
    filtros = [{"field": "city", "value": args.ciudad}]
    if args.wz:
        filtros.append({"field": "industry_codes", "values": list(WZ_COSMETICA)})
    else:
        filtros.append({"field": "purpose", "keywords": KEYWORDS_COSMETICA})
    if not args.todas:
        filtros.append({"field": "active", "value": "true"})

    body = {
        "filters": filtros,
        "pagination": {"page": args.pagina, "per_page": args.por_pagina},
    }
    if args.query:
        body["query"] = {"value": args.query}
    return body


def buscar(api_key, body):
    try:
        resp = requests.post(
            API_URL,
            json=body,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        sys.exit(f"No se pudo conectar con OpenRegister: {exc}")
    if resp.status_code == 401:
        sys.exit("Error 401: API key inválida o ausente.")
    if not resp.ok:
        sys.exit(f"Error {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def a_fila(empresa):
    direccion = empresa.get("address") or {}
    return {
        "nombre": empresa.get("name", ""),
        "forma_juridica": empresa.get("legal_form", ""),
        "activa": "sí" if empresa.get("active") else "no",
        "direccion": direccion.get("formatted_value", ""),
        "registro": f'{empresa.get("register_type", "")} {empresa.get("register_number", "")}'.strip(),
        "juzgado": empresa.get("register_court", ""),
        "company_id": empresa.get("company_id", ""),
        "objeto_social": (empresa.get("purpose") or "").replace("\n", " "),
    }


def imprimir(filas, paginacion):
    total = paginacion.get("total_results", len(filas))
    pagina = paginacion.get("page", 1)
    paginas = paginacion.get("total_pages", 1)
    print(f"\n{total} empresas encontradas (página {pagina}/{paginas})\n")
    for i, f in enumerate(filas, 1):
        print(f"{i:>3}. {f['nombre']}  [{f['forma_juridica']}, activa: {f['activa']}]")
        if f["direccion"]:
            print(f"     📍 {f['direccion']}")
        print(f"     🏛  {f['registro']} - {f['juzgado']}  ({f['company_id']})")
        if f["objeto_social"]:
            objeto = f["objeto_social"]
            print(f"     📝 {objeto[:160]}{'…' if len(objeto) > 160 else ''}")
        print()


def guardar_csv(filas, ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(a_fila({}).keys()))
        writer.writeheader()
        writer.writerows(filas)
    print(f"Guardadas {len(filas)} empresas en {ruta}")


def main():
    parser = argparse.ArgumentParser(
        description="NexusLead: busca empresas de cosmética en Núremberg vía OpenRegister."
    )
    parser.add_argument("-q", "--query", help="texto libre adicional (nombre, marca...)")
    parser.add_argument("-c", "--ciudad", default="Nürnberg", help="ciudad (por defecto: Nürnberg)")
    parser.add_argument("--wz", action="store_true",
                        help="filtrar por códigos WZ de cosmética en vez de palabras clave del objeto social")
    parser.add_argument("--todas", action="store_true", help="incluir también empresas inactivas")
    parser.add_argument("-p", "--pagina", type=int, default=1, help="página de resultados")
    parser.add_argument("-n", "--por-pagina", type=int, default=20, help="resultados por página")
    parser.add_argument("--csv", metavar="RUTA", help="exportar los resultados a CSV")
    args = parser.parse_args()

    api_key = os.environ.get("OPENREGISTER_API_KEY")
    if not api_key:
        sys.exit("Define la variable de entorno OPENREGISTER_API_KEY con tu API key.")

    datos = buscar(api_key, construir_peticion(args))
    filas = [a_fila(e) for e in datos.get("results", [])]
    imprimir(filas, datos.get("pagination", {}))
    if args.csv:
        guardar_csv(filas, args.csv)


if __name__ == "__main__":
    main()
