# Baribudos Studio - Persistent Memory

O Baribudos Studio tem uma camada de memoria persistente local em Markdown.

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

O repo privado `AndreVazao/andreos-memory` nao deve ser tratado como memoria operacional viva do Studio.

Ele serve como memoria tecnica de programacao e auditoria das repos, para quando ChatGPT/God Mode forem mexer no codigo e precisarem saber:

- O que foi feito.
- Porque foi feito.
- Que decisoes tecnicas existem.
- Que riscos foram detetados.
- Que proximas alteracoes devem respeitar.

Fluxo correto:

```text
Uso diario do Studio no PC
↓
Memoria local + Obsidian local

Trabalho de programacao nas repos
↓
AndreVazao/andreos-memory
↓
ChatGPT / God Mode / GitHub
```

## Regra principal

Nunca guardar credenciais, tokens, chaves API, cookies, segredos, dados sensiveis de clientes ou ficheiros privados de runtime em repos GitHub.
