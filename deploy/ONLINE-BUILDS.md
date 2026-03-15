# Baribudos Studio - Builds Online Grátis

## Objetivo
Gerar online:
- APK Android
- EXE Windows

Sem hospedar a app.

## Requisitos
- Repo no GitHub
- Actions ativas
- Idealmente repo pública para evitar limites chatos de minutos

## Android APK
Workflow:
- `.github/workflows/android-apk.yml`

Como usar:
1. GitHub > Actions
2. Abrir "Android APK Build"
3. Run workflow
4. Esperar terminar
5. Abrir o job concluído
6. Descarregar artifact:
   - `baribudos-android-apk`

Ficheiro esperado:
- `app-debug.apk`

## Windows EXE
Workflow:
- `.github/workflows/windows-exe.yml`

Como usar:
1. GitHub > Actions
2. Abrir "Windows EXE Build"
3. Run workflow
4. Esperar terminar
5. Abrir o job concluído
6. Descarregar artifact:
   - `baribudos-windows-exe`

Ficheiros esperados:
- `.exe` direto
- ou instalador NSIS `.exe`

## Notas
- O APK debug pode pedir permissões normais do Android.
- O EXE Windows pode ser sinalizado pelo SmartScreen por não ter assinatura paga.
- Isto é normal em builds independentes.

## Fluxo recomendado
1. Fazer push da repo
2. Executar build Android
3. Executar build Windows
4. Descarregar os artefactos
5. Instalar no telemóvel e no PC
