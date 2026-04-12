# Distribution State Model

## Objetivo
Fixar um modelo simples de estados para a distribuição por projeto.

## Estados
- `draft` → ainda sem base suficiente
- `planned` → direção definida, mas ainda sem base total
- `queued` → quase pronto, à espera de decisão final
- `ready` → pronto para seguir para o destino
- `published` → já publicado no destino

## Regra prática
Nem todos os destinos precisam de avançar ao mesmo tempo.

A ordem recomendada continua a ser:
1. Website próprio
2. validação de primeiras vendas
3. expansão para destinos externos

## Uso no Studio
O Studio deve usar estes estados para ajudar os administradores a decidir:
- se um projeto já pode vender
- se já pode sair para outro canal
- se ainda precisa de mais trabalho comercial ou editorial
