# CI Artifacts Guide

## Objetivo
Saber exatamente o que descarregar depois de correr os workflows manuais do Studio.

## Windows desktop
Workflow:
- `Manual Build Windows EXE`

Artefacto esperado:
- `baribudos-studio-windows-bundle`

Onde procurar dentro do artefacto:
- bundle NSIS `.exe`
- bundle MSI `.msi` quando existir
- executável desktop gerado pelo Tauri

## Android debug
Workflow:
- `Manual Build Android Debug`

Artefacto esperado:
- `baribudos-studio-android-debug-apk`

Onde procurar dentro do artefacto:
- `app-debug.apk`

## Ordem recomendada
1. correr Windows manual build
2. descarregar artefacto Windows
3. correr Android manual build
4. descarregar APK debug
5. validar fluxo real Studio → Website

## Regra prática
Primeiro validar que a app abre e navega. Só depois investir tempo em distribuição externa.
