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
    "sponsors": [],
    "typography": {
        "font_family": "Georgia",
        "preview_text": "Os Baribudos na floresta encantada",
        "scope": "saga"
    }
}

def list_sagas():
    sagas = read_json(SAGAS_FILE, [])
    if not sagas:
        write_json(SAGAS_FILE, [DEFAULT_SAGA])
        return [DEFAULT_SAGA]
    return sagas

def create_saga(data):
    sagas = list_sagas()
    payload = {
        **data,
        "typography": {
            **DEFAULT_SAGA.get("typography", {}),
            **(data.get("typography", {}) if isinstance(data.get("typography", {}), dict) else {}),
        },
    }
    sagas.append(payload)
    write_json(SAGAS_FILE, sagas)
    return payload


def update_saga(slug, payload):
    sagas = list_sagas()
    updated = None
    next_items = []
    for item in sagas:
        if str(item.get("slug", "")).strip() != str(slug).strip():
            next_items.append(item)
            continue
        merged = {
            **item,
            **payload,
            "colors": {
                **(item.get("colors", {}) if isinstance(item.get("colors", {}), dict) else {}),
                **(payload.get("colors", {}) if isinstance(payload.get("colors", {}), dict) else {}),
            },
            "typography": {
                **(item.get("typography", {}) if isinstance(item.get("typography", {}), dict) else {}),
                **(payload.get("typography", {}) if isinstance(payload.get("typography", {}), dict) else {}),
            },
        }
        next_items.append(merged)
        updated = merged
    if not updated:
        raise ValueError("saga_not_found")
    write_json(SAGAS_FILE, next_items)
    return updated
