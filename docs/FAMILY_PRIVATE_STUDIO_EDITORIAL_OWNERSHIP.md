# Studio privado da família + propriedade editorial por IP/Saga

## Regra-base
O **Baribudos Studio** é um **Studio privado e exclusivo da família**.

Utilizadores previstos do Studio:
- André
- esposa
- filhos
- eventualmente alguns familiares próximos autorizados

Isto significa que o Studio pode ser multiutilizador **dentro do contexto privado familiar**, sem se tornar um marketplace público de criação.

## Separação correta entre Studio e propriedade editorial
O facto de o Studio ser usado pela família **não significa** que todas as IPs, sagas e produtos sejam de produção partilhada.

A regra correta é:
- o **Studio** é a infraestrutura privada comum
- cada **IP** pode ter um dono editorial específico
- cada **saga** pode herdar ou especializar essa propriedade
- cada **produto** deve respeitar a propriedade editorial da IP/saga de origem

## Caso Baribudos
A tua regra editorial fica explícita:

- **IP Baribudos**: exclusiva de produção do André
- **Saga Baribudos**: exclusiva de produção do André
- **Produtos Baribudos**: exclusivos de produção do André

Mesmo que outros familiares usem o Studio, **não devem poder produzir nem publicar conteúdo Baribudos** sem autorização explícita do dono editorial.

## Outras IPs e sagas
Ao mesmo tempo, o Studio deve continuar preparado para que:
- outros membros da família criem as suas próprias **IPs**
- esses membros criem as suas próprias **sagas**
- o André crie outras IPs e outras sagas além de Baribudos
- cada universo tenha regras editoriais, visuais e comerciais próprias

## Regra de modelagem
A arquitetura deve continuar orientada a:

- `owner_id`
- `owner_name`
- permissões por IP
- permissões por saga
- permissões por publish
- separação entre `can_edit`, `can_publish` e `editorial owner`

## Regra operacional
Sempre que existir conflito entre:
- acesso ao Studio
- e propriedade editorial da IP/saga

vence a **propriedade editorial da IP/saga**.

Ou seja:
- alguém pode entrar no Studio
- mas não ganhar automaticamente direitos de produção sobre IPs exclusivas de outro membro da família

## Efeito prático esperado
O sistema deve conseguir suportar cenários como:

1. **Baribudos**
   - só André produz
   - só André publica
   - familiares podem consultar ou operar partes permitidas, mas não assumir produção editorial

2. **Nova IP da esposa**
   - esposa é dona editorial
   - esposa define personagens, saga, produtos e publish
   - André pode ter papel técnico/admin sem tomar posse editorial automática

3. **Nova IP de um filho**
   - IP fica associada ao dono editorial definido
   - regras e permissões seguem esse contexto

## Princípio final
O Studio deve ser:
- **privado da família**
- **multi-IP**
- **multi-saga**
- **com propriedade editorial separada por contexto**

Baribudos continua a ser a tua IP premium exclusiva,
mas a plataforma não pode assumir que:
- tudo é Baribudos
- ou que tudo é produção partilhada só por ser um Studio familiar.
