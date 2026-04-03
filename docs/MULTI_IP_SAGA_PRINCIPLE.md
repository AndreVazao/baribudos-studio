# Princípio Multi-IP / Multi-Saga

## Regra estrutural
O Baribudos Studio **não pode ficar preso à IP Baribudos**.

Baribudos é:
- uma **IP**
- uma **saga**
- um conjunto de histórias
- a primeira linha editorial mais desenvolvida

Mas a arquitetura do Studio e do Website deve continuar preparada para:
- criar **novas IPs**
- criar **novas sagas** dentro de cada IP, quando fizer sentido
- manter **visual sets**, **character locks**, **publish readiness** e **pipelines** por IP/saga
- evitar qualquer dependência estrutural onde o sistema assuma que "Baribudos" é a única marca, a única família principal ou o único fluxo editorial

## Consequências práticas
Sempre que uma funcionalidade nova for criada, validar se ela está:

1. **Genérica por IP/saga**
   - usar `saga_slug`, `ip slug`, `project.saga_slug`, `visualSetId`, etc.
   - evitar hardcodes específicos de Baribudos no domínio central

2. **Escalável para múltiplos universos**
   - novas famílias/personagens
   - novas regras visuais
   - novas estruturas de catálogo
   - novos bundles, produtos e páginas públicas

3. **Isolada por contexto editorial**
   - visual sets de uma saga não podem contaminar outra
   - character lock de uma saga não deve bloquear outra
   - publicação e prontidão devem respeitar o contexto da IP/saga do projeto

## Baribudos continua importante
Baribudos continua a ser a referência principal para:
- testar maturidade do sistema
- validar gates de qualidade
- consolidar cockpit e consistência visual

Mas deve ser tratado como:
- **primeira IP premium do sistema**
- **não como limite da plataforma**

## Regra de desenvolvimento
Ao adicionar features novas, preferir sempre:
- naming genérico
- estruturas orientadas a IP/saga
- fallback e runtime reutilizáveis
- cockpit preparado para múltiplas IPs

## Objetivo final
Ter um Studio e um Website onde:
- Baribudos funciona muito bem
- novas IPs entram sem refazer a base
- novas sagas podem herdar o fluxo e adaptar o seu próprio canon, visual set e pipeline
