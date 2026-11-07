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

## Mapa de empresas (demo): seguridad y eventos

En `security-map/` está el mapa interactivo de empresas activas de Alemania con datos reales
del Handelsregister vía OpenRegister:

- **Seguridad privada** (código WZ 2025 **80.01**): Nürnberg, München, Köln, Düsseldorf y Stuttgart completas;
  Berlin, Hamburg y Frankfurt parciales.
- **Eventos, ferias y congresos** (WZ **82.30**): muestra de toda Alemania.
- **Hostelería, Salud e Inmobiliarias**: negocios reales de **OpenStreetMap** con su teléfono, email,
  web y horario cuando la comunidad los ha registrado, en el área completa de Berlin, Hamburg, München,
  Köln, Frankfurt am Main, Stuttgart, Düsseldorf y Nürnberg (`osm_pois.py`).

Pasos para regenerarlo:

```bash
cd security-map
export OPENREGISTER_API_KEY="tu_api_key"
python fetch_companies.py 80.01 "Nürnberg" 3   # sector, ciudad ("" = toda Alemania), páginas (30 empresas y 10 créditos por página)
python fetch_companies.py 82.30 "" 6
python geocode.py                              # coordenadas con OpenStreetMap (Photon)
python make_relief.py NE1_HR_LC_SR_W_DR.tif    # relieve de Natural Earth -> relief.jpg / relief-sat.jpg
python basemap.py                              # calles, edificios y agua de OpenStreetMap (OpenFreeMap) -> basemap/
python osm_pois.py hosteleria salud inmobiliarias  # negocios de OpenStreetMap + contacto (Nominatim) -> data/
python build_map.py                            # genera index.html
```

La página `index.html` necesita a su lado `relief.jpg`, `relief-sat.jpg` y las carpetas `basemap/` y `data/`.

- `raw/<código WZ>/`: respuestas de la API por ciudad.
- `contacts.json`: teléfono, email, web y USt-IdNr. obtenidos con `GET /v0/company/{id}/contact` (10 créditos por empresa).
- `geocache.json`: coordenadas y precisión (`direccion`, `codigo_postal` o `ciudad`).
- `countries.geojson`: fronteras (Natural Earth, vía `world-atlas`).
- `basemap/` (no se sube al repositorio, ~90 MB): se genera con `basemap.py`.

## Vídeo para TikTok (español y alemán)

- `video/nexuslead-tiktok-de.mp4`: vídeo vertical de 41 s (1080×1920, 30 fps, H.264 + AAC) en **alemán**:
  textos en pantalla, la propia app en alemán (`index-de.html`) y una **narración en alemán**.
- `video/guion-de.txt`: el texto de la narración con los segundos de inicio y lo que sale en pantalla.
- `video/nexuslead-tiktok.mp4`: versión anterior, en español y sin voz.

Regenerar la versión alemana:

```bash
cd security-map
python build_map.py --lang de                  # index-de.html y data-de/ (textos y datos en alemán)
cd ../video
APP_INDEX=index-de.html LANG_VIDEO=de PW=<ruta a playwright> node render.js ../security-map <node_modules con leaflet> <node_modules con @fontsource-variable> stage.html frames/
pip install piper-tts                           # voz de la narración (modelo de_DE-thorsten-high, licencia CC0)
python narrar_de.py narracion/                  # descargar antes de_DE-thorsten-high.onnx(.json) en esta carpeta
python mezclar_de.py frames/ narracion/ nexuslead-tiktok-de.mp4
```

Los textos de cada escena están en `render.js` (diccionario `TXT`; `LANG_VIDEO=es` reproduce la versión en español)
y el diseño del escenario en `stage.html`. La duración y los segundos de la narración están en `guion_de.py`.
