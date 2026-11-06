# NexusLead – buscador de empresas de cosmética en Núremberg

Buscador por terminal que consulta la API de [OpenRegister](https://openregister.de)
(`POST /v1/search/company`) para encontrar empresas del sector cosmética en Nürnberg.

## Instalación

```bash
pip install -r requirements.txt
export OPENREGISTER_API_KEY="tu_api_key"
```

## Uso

```bash
python nexuslead_search.py                       # cosmética en Nürnberg (empresas activas)
python nexuslead_search.py -q "Naturkosmetik"     # añade texto libre
python nexuslead_search.py --wz                   # filtra por códigos WZ (20.42, 46.45, 47.75, 96.02)
python nexuslead_search.py -p 2 -n 50             # paginación
python nexuslead_search.py --todas --csv leads.csv  # incluye inactivas y exporta a CSV
python nexuslead_search.py -c "Fürth"             # otra ciudad
```

Por defecto filtra por ciudad y por palabras clave en el objeto social
(Kosmetik, Körperpflege, Parfüm, Beauty…). Con `--wz` usa los códigos de actividad WZ 2025.

## Versión en Go (SDK oficial `openregister-go`)

En `nexuslead-go/` está el mismo buscador escrito en Go con el SDK oficial
[`github.com/oregister/openregister-go`](https://github.com/oregister/openregister-go).
Requiere Go 1.22 o superior.

```bash
cd nexuslead-go
export OPENREGISTER_API_KEY="tu_api_key"
go run .                              # cosmética en Nürnberg
go run . -q "Naturkosmetik" -n 50     # texto libre, 50 resultados
go run . -wz -todas -csv leads.csv    # códigos WZ, incluye inactivas, exporta a CSV
go build -o nexuslead . && ./nexuslead -h   # compilar un ejecutable
```

## Mapa de empresas de seguridad (demo)

En `security-map/` está el mapa interactivo de empresas de seguridad privada
(código de actividad WZ 2025 **80.01**) con datos reales del Handelsregister vía OpenRegister.

Pasos para regenerarlo:

```bash
cd security-map
export OPENREGISTER_API_KEY="tu_api_key"
python fetch_companies.py "Nürnberg" 3   # descarga hasta 3 páginas (30 empresas/página, 10 créditos/página)
python geocode.py                        # coordenadas con OpenStreetMap (Photon)
python build_map.py                      # genera index.html con todo embebido
```

- `raw/`: respuestas de la API por ciudad.
- `contacts.json`: teléfono, email, web y USt-IdNr. obtenidos con `GET /v0/company/{id}/contact` (10 créditos por empresa).
- `geocache.json`: coordenadas y precisión (`direccion`, `codigo_postal` o `ciudad`).
- `countries.geojson`: fronteras de Alemania y vecinos (Natural Earth, vía `world-atlas`).
