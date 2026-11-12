# Baribudos Studio - Persistent Memory

O Baribudos Studio tem uma camada de memoria persistente operacional local em Markdown.

## Objetivo correto

Evitar perda de contexto operacional durante o uso do Studio no PC de casa.

Esta memoria local e para o programa instalado trabalhar melhor, continuar tarefas, lembrar progresso, manter historico de producao e alimentar o Obsidian local.

## Separacao obrigatoria

```text
Studio instalado no PC
└── Memoria operacional viva
    ├── progresso de trabalho
    ├── sessoes de producao
    ├── estado de projetos criativos
    ├── historico local
    └── ligacao ao Obsidian local

AndreVazao/andreos-memory
└── Memoria de programacao/contexto tecnico das repos
    ├── o que foi alterado no codigo
    ├── decisoes de arquitetura
    ├── auditorias
    ├── instrucoes para futuras mexidas
    └── contexto para ChatGPT/God Mode quando trabalhar nas repos
```

## Uso da memoria local do Studio

A memoria local do Studio e usada para:

- Guardar decisoes operacionais do Studio.
- Guardar historico de acoes locais.
- Guardar backlog local.
- Guardar arquitetura operacional do Studio.
- Gerar contexto compacto para IA local.
- Abrir notas no Obsidian.
- Manter a relacao Studio -> Website documentada.

## Local de armazenamento runtime

No PC de casa, a memoria deve apontar para o vault local do Obsidian.

Configurar uma destas variaveis:

```text
BARIBUDOS_MEMORY_ROOT=C:\\AndreOS
```

ou:

```text
BARIBUDOS_OBSIDIAN_VAULT_ROOT=C:\\Users\\Andre\\Documents\\AndreOS
```

Opcionalmente, o nome do vault Obsidian pode ser definido com:

```text
BARIBUDOS_OBSIDIAN_VAULT_NAME=AndreOS
```

Se nenhuma variavel for definida, o Studio usa por defeito:

```text
%USERPROFILE%\\AndreOS
```

O modo antigo `storage/memory/AndreOS/` so deve ser usado se for explicitamente ativado:

```text
BARIBUDOS_USE_LEGACY_STORAGE_MEMORY=1
```

Isto evita que a memoria operacional viva fique presa dentro da repo publica ou exposta pela montagem /storage.

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

## Relacao com AndreOS Memory

O repo AndreVazao/andreos-memory serve como memoria tecnica de programacao e auditoria das repos, distinta da memoria operacional viva do Studio.

**Verificacao de visibilidade em 2026-11-12:** o GitHub reportou atualmente este repositorio com visibilidade publica. Documentacao anterior chamava-lhe privado. Rever a visibilidade e o conteudo do repositorio antes de guardar informacao pessoal, operacional sensivel ou material que deva ser privado. Nunca guardar credenciais, tokens, chaves API, cookies, segredos ou dados sensiveis de clientes em Git.

## Snapshot de estado e continuidade

A fonte de verdade sobre o estado técnico global do Studio e o documento:

- docs/STUDIO_CURRENT_STATE_AND_COMPLETION_ROADMAP.md

Esse documento regista inventário, gaps, prioridades, idiomas configurados, critérios de conclusão e sequência de implementação. Atualizá-lo a cada marco relevante. Não assumir que uma funcionalidade está concluída apenas por existirem serviços, rotas, painéis ou CI verde.

## Regra principal

Nunca guardar credenciais, tokens, chaves API, cookies, segredos, dados sensiveis de clientes ou ficheiros privados de runtime em repos GitHub.
