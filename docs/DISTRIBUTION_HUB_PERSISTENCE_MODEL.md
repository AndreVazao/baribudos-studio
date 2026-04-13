# Distribution Hub Persistence Model

## Objetivo
Preparar a camada v4 em que o Distribution Hub deixa de ser só leitura e passa a ter estado persistido por destino.

## Unidade principal
Cada projeto pode ter vários destinos de distribuição.

Exemplos:
- Website
- Amazon KDP
- YouTube
- Audiobook / outras plataformas

## Campos mínimos por destino
- `channel_id`
- `project_id`
- `status`
- `ready_at`
- `published_at`
- `last_error`
- `last_attempt_at`
- `notes`
- `payload_snapshot`

## Estados recomendados
- `draft`
- `planned`
- `queued`
- `ready`
- `published`
- `failed`

## Regras
- o Website continua a ser o primeiro destino real
- os outros destinos podem ficar persistidos mesmo antes de terem integração automática
- o Studio deve mostrar estado por destino sem depender do Website

## Meta da v4
Deixar o sistema pronto para evoluir de painel de readiness para painel de operação real por destino.
