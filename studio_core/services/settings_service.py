from studio_core.core.storage import read_json, write_json

SETTINGS_FILE = "data/settings.json"

DEFAULT_SETTINGS = {
    "default_language": "pt-PT",
    "output_languages": ["pt-PT", "pt-BR", "en", "es", "fr", "de", "it", "nl", "zh", "ja"],
    "author_default": "André Vazão",
    "produced_by": "Baribudos Studio",
    "youtube_publish": False,
    "marketplace_publish": False
}

def get_settings():
    data = read_json(SETTINGS_FILE, {})
    if not data:
        write_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    return data

def update_settings(payload):
    write_json(SETTINGS_FILE, payload)
    return payload
