# V6 Implementation Sequence

## Objetivo
Fechar a ordem certa para transformar o Distribution Hub em backend real sem partir o que já está verde.

## Sequência
1. criar entidade persistida por canal
2. criar endpoints mínimos de leitura e escrita
3. ligar painel do Studio a dados persistidos
4. guardar tentativa, erro e published por canal
5. só depois ligar integrações externas reais

## Regra
O Studio continua a ser o único centro de comando. O Website continua a ser o canal próprio principal.

## Saída esperada
No fim da V6 o Studio já deve conseguir:
- mostrar estado persistido por canal
- mostrar histórico básico por canal
- atualizar estado por canal
- guardar payload snapshot por canal
