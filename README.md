# Baribudos Studio

Base monorepo do Baribudos Studio.

## Backend Python
Local: `studio_core`

### Instalar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# uvicorn studio_core.api.main:app --host 0.0.0.0 --port 8787 --reload
