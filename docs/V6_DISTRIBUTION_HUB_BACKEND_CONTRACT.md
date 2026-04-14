# V6 Distribution Hub Backend Contract

## Objetivo
Definir a camada real de backend do Distribution Hub para sair do modo apenas visual e passar a operação persistida por destino.

## Entidade principal
`distribution_channel_state`

## Campos mínimos
- `id`
- `project_id`
- `channel_id`
- `status`
- `attempt_count`
- `last_attempt_at`
- `last_error`
- `ready_at`
- `published_at`
- `notes`
- `payload_snapshot_json`
- `created_at`
- `updated_at`

## channel_id esperados
- `website`
- `amazon_kdp`
- `youtube`
- `audio`

## status esperados
- `draft`
- `planned`
- `queued`
- `ready`
- `published`
- `failed`

## Regras
- um projeto pode ter vários estados, um por canal
- Website continua a ser o primeiro canal próprio
- falhas por canal não devem contaminar os outros canais
- payload snapshot deve guardar o que foi preparado para aquele canal naquele momento

## Endpoints mínimos
### listar por projeto
- `GET /distribution/projects/{project_id}/channels`

### detalhe de um canal
- `GET /distribution/projects/{project_id}/channels/{channel_id}`

### atualizar estado
- `PATCH /distribution/projects/{project_id}/channels/{channel_id}`

### registar tentativa
- `POST /distribution/projects/{project_id}/channels/{channel_id}/attempts`

### marcar published
- `POST /distribution/projects/{project_id}/channels/{channel_id}/publish-success`

### marcar failed
- `POST /distribution/projects/{project_id}/channels/{channel_id}/publish-failed`

## Meta da V6
Deixar o backend do Studio preparado para suportar ações reais por destino, histórico básico e futura integração com Amazon, YouTube e áudio.
