# V6 Channel Actions Spec

## Objetivo
Definir as ações reais que o Distribution Hub deve suportar por destino.

## Ações mínimas por canal
- `prepare_payload`
- `mark_ready`
- `record_attempt`
- `mark_published`
- `mark_failed`
- `add_note`

## Regras por ação
### prepare_payload
Guarda ou atualiza o `payload_snapshot_json` do canal.

### mark_ready
Define `status=ready` e preenche `ready_at`.

### record_attempt
Incrementa `attempt_count` e atualiza `last_attempt_at`.

### mark_published
Define `status=published`, preenche `published_at` e limpa `last_error`.

### mark_failed
Define `status=failed` e atualiza `last_error`.

### add_note
Atualiza `notes` sem alterar o resto do estado.

## Regra de segurança
Falhas de um canal não devem alterar o estado dos outros canais do mesmo projeto.
