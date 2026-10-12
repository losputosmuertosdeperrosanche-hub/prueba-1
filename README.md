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
