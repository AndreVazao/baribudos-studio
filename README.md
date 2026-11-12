# Baribudos Studio

Monorepo base do Baribudos Studio.

## Documentação de referência

- [Estado atual, auditoria inicial e plano de conclusão](docs/STUDIO_CURRENT_STATE_AND_COMPLETION_ROADMAP.md)
- [Visão de produto e critérios de aceitação](docs/BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md)
- [Auditoria de segurança](docs/security/2026-11-09-authentication-and-storage-exposure-audit.md)
- [Auditoria da pipeline editorial](docs/2026-11-12-editorial-pipeline-gap-audit.md)
- [Requisitos de produção multilingue](docs/MULTILINGUAL_FIRST_GLOBAL_LAUNCH_REQUIREMENTS.md)

A documentação distingue explicitamente código existente de funcionalidades validadas em operação. Consultar o estado atual antes de assumir que um subsistema está concluído.

## Estrutura
- `studio_core/` → backend Python FastAPI
- `client/mobile-app/` → frontend React/Vite, Tauri e Capacitor
- `public/brand/` → logos e assets de marca
- `scripts/` → automação local

## Backend
### Instalar
```bash
python -m venv .venv
