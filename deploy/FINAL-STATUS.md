# Baribudos Studio — Estado Final Atual

## 1. O que já está pronto

### Build & distribuição
- Build online de APK Android via GitHub Actions
- Build online de EXE Windows via GitHub Actions
- Artifact download funcional

### Backend core
- FastAPI app operacional
- Bootstrap automático no arranque
- Diagnostics
- Health check
- Storage mount
- Public assets mount

### IP / Saga system
- IP registry
- Saga runtime engine
- Canon loading
- Metadata loading
- Palette loading
- Brand assets loading
- Character loading
- Runtime validation

### Editorial / produção
- Story engine canon-aware
- Factory engine central
- Production pipeline auto/manual
- Publication package
- Publish readiness
- Publish gate
- Project integrity audit
- Smoke test backend

### Outputs
- Cover real
- EPUB real
- Audiobook real
- Vídeo real
- Storyboard manifest
- Illustration pipeline por frame
- Upload manual por frame
- Import de imagens geradas por frame
- Integração de frames aprovados no EPUB
- Integração de frames aprovados no vídeo slideshow

### Frontend
- Dashboard base
- IP creator/editor panels
- Runtime panel
- Production pipeline panel
- Illustration pipeline panel
- Smoke panel
- Outputs panel

---

## 2. O que está funcional mas ainda não está premium

### Audiobook
- Funciona
- Usa TTS técnico
- Ainda não é narração premium humana

### Vídeo
- Funciona
- Já usa slideshow multi-frame
- Ainda não tem motion design premium
- Ainda não tem sincronização fina por página

### Ilustrações internas
- Pipeline pronta
- Upload/manual pronto
- Import externo pronto
- Aprovação pronta
- Geração automática interna do backend ainda não está ligada a provider real

### EXE / APK
- Build gera artefactos
- Ainda falta validar uso real em ambiente do teu PC e telemóvel

---

## 3. O que ainda falta mesmo para produção forte

### Visual AI real
- provider de geração de imagem ligado ao backend
- regeneração automática por frame
- variações por frame
- controlo de seed/consistência

### Motion / série
- zoom/pan por frame
- tempos por página com base em texto
- sincronização fina com áudio
- intro/outro
- música ambiente
- legendas

### Audio premium
- vozes melhores
- narração emocional
- música ambiente
- pausas melhores
- mix final

### Editorial premium
- front matter mais rica
- credits page
- toc mais rica
- back matter
- export print-ready PDF ainda não está fechado

### Desktop/mobile polish
- UX mais limpa
- fluxo mais guiado
- menos painéis técnicos expostos
- onboarding

---

## 4. Classificação honesta por módulo

### Verde
- IP runtime
- canon loading
- project structure
- publication package
- readiness
- publish gate
- smoke test
- cover
- epub base
- build APK
- build EXE

### Amarelo
- audiobook
- vídeo
- illustration pipeline
- production pipeline UI
- desktop/mobile UX

### Vermelho
- geração de imagem automática no backend
- PDF print-ready premium
- série com motion premium
- audio premium final
