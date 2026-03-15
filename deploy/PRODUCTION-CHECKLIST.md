# Baribudos Studio - Checklist Técnico Final

## Backend
- `python -m venv .venv`
- instalar `requirements.txt`
- validar `python deploy/check_runtime.py`
- arrancar `python deploy/start-backend.py`
- abrir:
  - `/api/health`
  - `/api/diagnostics`
  - `/docs`

## Dependências que devem estar OK
- Python
- FFmpeg
- FFprobe
- eSpeak ou eSpeak-NG
- Node
- npm

## Dados base
- existe pelo menos 1 utilizador editorial
- existe pelo menos 1 IP
- existe pelo menos 1 projeto
- o projeto tem `illustration_path`
- branding principal carregado
- canons da saga presentes

## Pipeline por projeto
1. Criar / abrir projeto
2. Confirmar `illustration_path`
3. Executar Factory
4. Confirmar outputs:
   - cover
   - epub
   - audiobook
   - video
5. Preencher comercial
6. Validar readiness
7. Validar integrity
8. Congelar publication package
9. Marcar ready for publish
10. Executar smoke test
11. Publicar

## Frontend
- `cd client/mobile-app`
- `npm install`
- `npm run dev`
- validar login
- validar dashboard
- validar IP creator
- validar saga runtime panel
- validar factory
- validar outputs
- validar smoke test panel

## Android
- `npm run android:build`
- `npx cap open android`
- build APK no Android Studio
- validar API base para o IP local do PC

## Critérios de aprovação
- backend sem stacktrace
- diagnostics coerente
- project integrity sem missing files
- readiness pelo menos yellow
- smoke test OK
- publish gate funcional
