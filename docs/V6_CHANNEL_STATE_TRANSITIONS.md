# V6 Channel State Transitions

## Objetivo
Fixar as transições válidas de estado por canal no Distribution Hub.

## Estados
- `draft`
- `planned`
- `queued`
- `ready`
- `published`
- `failed`

## Transições válidas
- `draft -> planned`
- `planned -> queued`
- `queued -> ready`
- `ready -> published`
- `ready -> failed`
- `failed -> planned`
- `failed -> ready`
- `published -> planned` somente se houver nova versão ou revisão

## Regra
Não saltar diretamente de `draft` para `published` sem passar pelo menos por uma fase de preparação.

## Uso prático
O backend deve validar estas transições para evitar estados incoerentes por canal.
