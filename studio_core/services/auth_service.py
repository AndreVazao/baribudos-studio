from studio_core.core.storage import read_json

USERS_FILE = "data/users.json"

def login_user(name, pin):
    users = read_json(USERS_FILE, [])
    for u in users:
        if u["name"].lower() == name.lower() and u["pin"] == pin:
            return u
    return None
