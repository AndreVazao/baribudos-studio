# Baribudos Studio — Release V1

## Objetivo
Gerar a primeira release operacional do Studio com:
- build Windows
- build Android
- updater base funcional
- smoke test mínimo validado

---

## 1. Antes do build

Confirmar:
- `deploy/version.json`
- `deploy/release_manifest.json`
- `data/projects.json` com pelo menos 1 projeto real
- story layout pronta
- story aplicada
- pipeline de ilustração criada
- capa pronta ou builder pronto
- audiobook testado
- updater testado

---

## 2. Check técnico local

Executar:

```bash
python deploy/release_check.py
