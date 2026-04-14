# Studio V7 Execution Backlog

## Objetivo

Transformar o Studio no centro operacional real para:
- produzir ebooks e audiobooks
- publicar no Website de forma consistente
- preparar expansão operacional para Amazon KDP e canais de áudio
- operar tudo de forma viável mesmo quando o operador está só no telemóvel

## Resultado esperado da V7

1. O Studio deixa de ser maioritariamente painel e passa a executar fluxos completos.
2. Cada projeto passa por estados claros: produção, package freeze, publicação, venda.
3. O Website recebe conteúdo válido e vendável sem passos manuais soltos.
4. O Distribution Hub passa a ser a consola real de operação por canal.

## Blocos da V7

### V7.1 - Production Readiness Engine
- Validar se um projeto está realmente pronto para sair da produção
- Fechar checks mínimos para ebook, audiobook e website
- Expor readiness operacional por projeto
- Bloquear publish quando faltar base crítica

### V7.2 - Publication Package Operational Freeze
- Tornar o freeze do publication package mais explícito e auditável
- Guardar metadata operacional do freeze
- Garantir que publish usa sempre package congelado e coerente

### V7.3 - Website Selling Surface
- Endurecer payload comercial vindo do Studio
- Garantir título, copy, cover, CTA, pricing e estado público coerentes
- Preparar o Website para vender de forma consistente

### V7.4 - Channel Operations Console
- Operar Website a partir do Studio como canal real
- Preparar ações honestas para Amazon KDP, YouTube e áudio
- Dar estado por canal, histórico, falhas e retries

### V7.5 - Ebook and Audiobook Commercial Outputs
- Fechar saída comercial para ebook
- Fechar saída comercial para audiobook
- Preparar manifests e metadados mínimos para plataformas externas

### V7.6 - Mobile Operator Mode
- Permitir ao operador validar estado, artefactos e ações pelo GitHub Actions
- Criar workflows úteis para operação sem PC local

## Ordem recomendada

1. Production Readiness Engine
2. Publication Package Operational Freeze
3. Website Selling Surface
4. Channel Operations Console
5. Ebook and Audiobook Commercial Outputs
6. Mobile Operator Mode polishing

## Primeira entrega concreta da V7

A primeira entrega deve fechar:
- readiness operacional real
- freeze auditável
- publish para Website só quando o projeto estiver mesmo pronto

## Critério de sucesso

- Um projeto consegue sair de draft para produção pronta
- O Studio consegue congelar package
- O Studio consegue publicar no Website com estado consistente
- O Distribution Hub mostra operação real
- O operador consegue validar tudo pelo telemóvel
