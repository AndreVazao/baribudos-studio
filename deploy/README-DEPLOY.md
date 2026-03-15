# Baribudos Studio - Deploy Final

## 1. Backend local
### Windows
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python deploy\check_runtime.py
python deploy\start-backend.py
