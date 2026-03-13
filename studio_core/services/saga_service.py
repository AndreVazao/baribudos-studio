from studio_core.core.storage import read_json, write_json

SAGAS_FILE = "data/sagas.json"

DEFAULT_SAGA = {
    "slug": "baribudos",
    "name": "Os Baribudos",
    "exclusive_owner": "andre",
    "colors": {
        "primary": "#2F5E2E",
        "secondary": "#6FA86A",
        "gold": "#D4A73C",
        "cream": "#F5EED6",
        "brown": "#8B5E3C"
    },
    "characters_locked": True,
    "sponsors": []
}

def list_sagas():
    sagas = read_json(SAGAS_FILE, [])
    if not sagas:
        write_json(SAGAS_FILE, [DEFAULT_SAGA])
        return [DEFAULT_SAGA]
    return sagas

def create_saga(data):
    sagas = list_sagas()
    sagas.append(data)
    write_json(SAGAS_FILE, sagas)
    return data
