# V6 Failure and Retry Rules

## Objetivo
Definir como o Distribution Hub deve comportar-se quando um canal falha.

## Regras básicas
- uma falha afeta apenas o canal em causa
- o projeto não deve ser considerado falhado em todos os canais por causa de uma falha isolada
- `attempt_count` deve aumentar a cada tentativa real
- `last_error` deve guardar apenas o erro mais recente do canal

## Retry
- `failed -> planned` quando o payload precisar de correção
- `failed -> ready` quando a correção já estiver feita e o canal puder tentar de novo

## Notas
`notes` deve ser usado para guardar contexto humano útil, por exemplo:
- erro de metadata
- asset em falta
- thumbnail inválida
- capa ainda não final

## Meta
O histórico deve ajudar a perceber rapidamente por que um canal falhou e o que falta corrigir antes da próxima tentativa.
