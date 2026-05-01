# Baribudos Studio - Persistent Memory

O Baribudos Studio tem agora uma camada de memoria persistente local em Markdown.

## Objetivo

Evitar perda de contexto entre sessoes, execucoes, alteracoes e decisoes do Studio.

A memoria e usada para:

- Guardar decisoes importantes.
- Guardar historico de acoes.
- Guardar backlog.
- Guardar arquitetura.
- Gerar contexto compacto para IA.
- Abrir notas no Obsidian.
- Manter a relacao Studio -> Website documentada.

## Local de armazenamento runtime

Por defeito, a memoria runtime fica em:

```text
storage/memory/AndreOS/
```

Esta pasta esta ignorada no Git por seguranca.

## Projetos iniciais

A inicializacao cria automaticamente:

```text
BARIBUDOS_STUDIO
BARIBUDOS_STUDIO_WEBSITE
```

Cada projeto contem:

```text
MEMORIA_MESTRE.md
DECISOES.md
ARQUITETURA.md
BACKLOG.md
HISTORICO.md
PROMPTS.md
ERROS.md
ULTIMA_SESSAO.md
```

## Endpoints principais

```text
POST /api/persistent-memory/initialize
GET  /api/persistent-memory/projects
POST /api/persistent-memory/projects
GET  /api/persistent-memory/projects/{project_name}
POST /api/persistent-memory/decisions
POST /api/persistent-memory/history
POST /api/persistent-memory/backlog
POST /api/persistent-memory/last-session
POST /api/persistent-memory/context
GET  /api/persistent-memory/obsidian-uri/{project_name}/{file_name}
```

## Protecao contra segredos

A memoria bloqueia conteudos com palavras sensiveis como:

```text
password
senha
token
api_key
secret
private_key
github_pat
cookie
authorization
bearer
```

Se uma dessas palavras for detectada numa escrita, a gravacao e bloqueada.

## Relacao com AndreOS Memory privado

O repo privado `AndreVazao/andreos-memory` e a memoria externa oficial para IA e Obsidian.

O Studio guarda memoria runtime local. O AndreOS Memory guarda memoria longa, versionada e consultavel por IA.

Fluxo recomendado:

```text
Baribudos Studio runtime memory
↓
Resumo/decisoes importantes
↓
AndreVazao/andreos-memory
↓
ChatGPT / Obsidian / God Mode
```

## Regra principal

Nunca guardar credenciais, tokens, chaves API, cookies ou segredos na memoria.
