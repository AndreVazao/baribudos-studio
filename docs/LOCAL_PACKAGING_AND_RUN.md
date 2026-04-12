# Local Packaging and Run Guide

## Objetivo
Este guia fecha o caminho mais curto para usar o Baribudos Studio como produto real no dia a dia, primeiro no PC e depois no Android.

## Regra de arquitetura
- O Studio é o centro de comando.
- O Website é um destino próprio.
- Amazon, YouTube e outros canais serão destinos futuros controlados pelo Studio.

## Frontend do Studio
Local: `client/mobile-app/`

Scripts já disponíveis:
- `npm run dev` → desenvolvimento web rápido
- `npm run build` → build web do frontend
- `npm run tauri:dev` → desktop app em modo dev
- `npm run tauri:build` → build desktop
- `npm run android:sync` → sincroniza frontend para Android
- `npm run android:build` → build web + sync Android

## Caminho mais rápido no PC
### Desktop
1. entrar em `client/mobile-app`
2. instalar dependências com `npm install`
3. usar `npm run tauri:dev` para validar a app desktop
4. usar `npm run tauri:build` para gerar o instalador desktop

### Android
1. entrar em `client/mobile-app`
2. correr `npm install`
3. correr `npm run android:build`
4. abrir Android Studio via `npm run android:open`
5. gerar APK a partir do projeto Android sincronizado

## Caminho mais rápido sem PC forte
### Windows EXE
Usar o workflow manual de build Windows no GitHub Actions e descarregar o artefacto gerado.

### Android APK
Usar o workflow manual de build Android APK no GitHub Actions e descarregar o artefacto gerado.

## Ordem de uso recomendada
1. abrir Studio
2. criar ou escolher projeto
3. preparar teaser e estado público
4. publicar para Website
5. validar homepage e páginas públicas
6. só depois avançar para destinos externos

## Checklist antes de empacotar
- frontend verde
- backend verde
- teaser com headline, subtitle e CTA
- cover definido
- galeria mínima pronta
- trailer definido quando existir
- estado público coerente

## Meta da próxima fase
A próxima camada deve transformar este guia em operações mais automáticas:
- Distribution Hub persistido
- estado por destino guardado em dados
- fila de publicação
- preparação real para Amazon / YouTube / audiobook
