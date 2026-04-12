# Manual Builds

## Objetivo
Usar GitHub Actions só quando fizer sentido, sem gastar minutos à toa.

## Workflows disponíveis
- `Manual Build Windows EXE`
- `Manual Build Android Debug`

## Quando correr o Windows
Correr quando quiseres validar:
- abertura da app desktop
- navegação principal
- fluxo Studio para Website

## Quando correr o Android
Correr quando quiseres validar:
- APK debug instalável
- navegação base no telemóvel
- comportamento geral do frontend sincronizado

## Ordem recomendada
1. fechar alterações principais
2. garantir branch verde
3. correr Windows manual build
4. descarregar artefacto
5. correr Android manual build
6. descarregar APK debug

## Regra prática
Não correr estes workflows a cada pequena mudança. Guardar para marcos reais.
