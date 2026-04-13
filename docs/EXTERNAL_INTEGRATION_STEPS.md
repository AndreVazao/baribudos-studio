# External Integration Steps

## Objetivo
Deixar uma sequência clara para chegar a integrações externas reais sem saltar etapas.

## Sequência recomendada
1. persistir estado por destino no Distribution Hub
2. guardar payload por canal
3. validar outputs mínimos por canal
4. criar ações manuais por destino
5. só depois automatizar publicação real

## Amazon KDP
Passos:
- preparar metadados
- preparar capa
- preparar ficheiro editorial
- guardar estado `ready`
- futura ação manual ou automatizada de submissão

## YouTube / YouTube Kids
Passos:
- preparar vídeo
- preparar título e descrição
- guardar estado `ready`
- futura ação manual ou automatizada de upload

## Audiobook / outras plataformas
Passos:
- preparar áudio
- preparar capa e copy
- guardar estado `ready`
- futura ação manual ou automatizada

## Regra prática
Primeiro deixar o Distribution Hub capaz de guardar e mostrar operação por destino. Só depois acoplar integrações reais.
