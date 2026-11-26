# Baribudos — Plano Mestre de Entrega do Studio e Website

**Versão:** 1.0  
**Data de referência:** 25 de novembro de 2026  
**Estado:** plano de execução vivo; atualizar em cada PR relevante  
**Âmbito:** `AndreVazao/baribudos-studio` e `AndreVazao/baribudos-studio-website`

Este documento é o plano de trabalho de referência para levar o Baribudos Studio e o Baribudos Website a um estado operacional, seguro, editorialmente correto e comercialmente utilizável. Deve permanecer versionado no repositório, ser atualizado através de PRs pequenos e ser revisto antes de cada ciclo de trabalho.

Não confundir código integrado com funcionalidade operacional: uma rota protegida não prova que o cliente usa corretamente sessões; um build READY não prova que a loja pública funciona; um pipeline de produção validado por smoke tests não prova que existe geração real por fornecedores; uma referência de ficheiro não prova que o binário está armazenado e acessível.

---

## 1. Objetivo final e definição de pronto

### 1.1 Studio

O Studio só será considerado pronto quando:

- autenticação segura, sessão opaca, expiração, revogação e recuperação estejam completas;
- PINs estejam armazenados apenas como hashes fortes e as credenciais legadas conhecidas tenham sido tratadas;
- o primeiro owner seja criado por bootstrap único e controlado, sem credenciais previsíveis;
- todas as rotas privadas tenham autorização server-side baseada no utilizador persistido, com matriz de papéis explícita;
- o frontend use Bearer tokens de forma consistente, restaure sessão com `/users/me`, faça logout e trate 401/403/503;
- operações editoriais, produção, publicação, distribuição, assets e controlos administrativos tenham permissões e auditoria adequadas;
- a geração narrativa e audiovisual real esteja ligada a fornecedores configurados, com estados honestos, retries, limites, custos e rastreabilidade;
- os cânones editoriais sejam aplicados no backend e na interface;
- os artefactos produzidos sejam reais, verificáveis, armazenados e recuperáveis;
- CI, testes negativos, segurança, build e validação de produção estejam verdes no commit exato candidato a merge.

### 1.2 Website

O Website só será considerado pronto quando:

- catálogo público, páginas de produto, variantes e assets sejam consistentes e navegáveis anonimamente;
- checkout, criação de encomenda, pagamento, captura, webhooks e reconciliação sejam idempotentes e seguros;
- nenhuma confirmação de pagamento seja inferida do frontend ou de dados não verificados no servidor;
- a integração PayPal esteja validada em Sandbox, incluindo falhas, duplicados, timeouts e estados desconhecidos;
- a gestão de publicação e disponibilidade esteja sincronizada com o Studio sem expor dados administrativos;
- políticas RLS, grants, constraints e migrações estejam documentados, testados e aplicados apenas por processo aprovado;
- emails, recibos, estados de encomenda, cancelamentos e reembolsos tenham comportamento definido e testado;
- experiência mobile, acessibilidade, SEO, desempenho, observabilidade e tratamento de erros estejam verificados;
- CI, Preview e smoke tests de fluxos públicos e comerciais estejam verdes.

### 1.3 Critério transversal

Não declarar o projeto concluído enquanto houver P0 aberto, fluxo crítico sem teste de ponta a ponta, dependência externa sem validação, estado comercial ambíguo ou discrepância entre o que a interface promete e o que o backend efetivamente executa.

---

## 2. Regras de execução e controlo de risco

1. Trabalhar em branches dedicadas, com PRs pequenos e focados.
2. Cada PR deve indicar objetivo, risco, ficheiros afetados, testes, limitações e dependências.
3. Não integrar PR com CI pendente ou vermelho.
4. Não fazer merge, deploy, migração de produção, alteração de secrets ou operação financeira sem autorização explícita.
5. Preferir validações read-only para auditorias de infraestrutura e dados.
6. Nunca imprimir, descodificar ou copiar secrets para logs, documentação, comentários ou testes.
7. Não enfraquecer autenticação para manter compatibilidade; migrar os clientes e contratos de forma explícita.
8. Separar ambientes local, CI, Preview, Sandbox e produção.
9. Cada correção de segurança deve incluir teste negativo (sem sessão, sessão expirada, papel insuficiente, utilizador inativo, recurso inexistente).
10. Nunca apresentar slideshow, animatic ou audiobook como minissérie animada produzida.
11. Atualizar este roadmap com estado real, commit/PR e evidência; não marcar tarefas como concluídas por inferência.

### Estados

- **TODO** — ainda não iniciado.
- **IN PROGRESS** — implementação em curso.
- **BLOCKED** — depende de decisão, fornecedor, infraestrutura ou credencial.
- **VERIFY** — implementação existe, falta evidência suficiente.
- **DONE** — implementação, testes e critérios de aceitação verificados.
- **ACCEPTED RISK** — risco explicitamente aceite pelo responsável, com justificação e prazo.

---

## 3. Studio — plano por fases

### ST-0 — Fundação de identidade e sessões

**Objetivo:** garantir identidade verificável no servidor.

- [x] ST-001 — armazenamento de sessões opacas, hash-only, expiração e revogação (PR #76, integrado segundo relatório de 25/11).
- [x] ST-002 — DTOs de Secret Vault com allowlist/masking e hardening de traversal (PR #78, integrado segundo relatório de 25/11).
- [ ] ST-003 — principal server-side e dependência de papéis (PR #79, Draft; CI a revalidar no stack final).
- [ ] ST-004 — inicialização SQLite concorrente e permissões de ficheiro (PR #80, Draft; integrada nas branches #84–#86; decidir integração sem duplicar commits).
- [ ] ST-005 — hashing PBKDF2-SHA256, migração de PIN legado no login e sessão no login (PR #81, Draft).
- [ ] ST-006 — bootstrap único do owner, sem owner previsível criado automaticamente (PR #82, Draft).
- [ ] ST-007 — endpoint `GET /api/users/me` com DTO seguro e revogação de sessão de conta inativa (PR #83, Draft).
- [ ] ST-008 — RBAC em gestão de utilizadores (PR #84, Draft).
- [ ] ST-009 — RBAC em operações editoriais e pipeline de produção (PR #85, Draft).
- [ ] ST-010 — RBAC em controlos administrativos, deployment, DB, vault e updater (PR #86, Draft).

**Aceitação:** testes de token inválido/expirado/revogado, user inexistente/inativo, papel insuficiente, falha do armazenamento e concorrência; segredo de bootstrap removível após uso; nenhuma rota protegida aceita identidade fornecida pelo cliente.

### ST-1 — Fecho de RBAC e superfície API

**Prioridade:** P0.

- [ ] ST-101 — inventariar todas as rotas FastAPI e classificá-las como públicas, autenticadas, editoriais, administrativas ou internas. (IN PROGRESS — auditoria confirmou rotas de produção ainda sem dependência server-side; ver registo de 25/11)
- [ ] ST-102 — proteger CRUD de projetos e operações de escrita; definir leitura por papel e isolamento por projeto quando aplicável. (IN PROGRESS — PR #87 protege list/create/update com principal server-side e ownership; falta inventário/coverage total)
- [ ] ST-103 — proteger publicação, despublicação, aprovação editorial e alterações de catálogo. (IN PROGRESS — PR #87 protege website-publisher; PR #89 cobre publishing e Distribution Hub V6; catálogo e restantes reconciliações ainda por auditar)
- [ ] ST-104 — proteger upload, substituição, eliminação, listagem privada e download de assets; validar ownership, MIME, tamanho e path. (IN PROGRESS — PR #87 exige papel autenticado owner/admin/editor nas rotas /assets; limites/MIME/ownership por objeto ainda por fechar)
- [ ] ST-105 — rever rotas de capas, vídeos, ebooks, audiobooks, vozes, previews e distribuição.
- [ ] ST-106 — proteger diagnósticos e rotas operacionais que revelem estado interno; manter apenas health/readiness estritamente públicos.
- [ ] ST-107 — aplicar autorização por objeto, não apenas por papel, onde existam projetos, assets ou encomendas pertencentes a diferentes utilizadores.
- [ ] ST-108 — acrescentar rate limiting/lockout progressivo a login e bootstrap; não permitir enumeração de utilizadores.
- [ ] ST-109 — adicionar auditoria de ações sensíveis (ator, ação, recurso, resultado, timestamp), sem tokens, PINs ou secrets.
- [ ] ST-110 — criar teste automatizado que percorra a lista de rotas e falhe perante novas rotas privadas sem política declarada.

**Aceitação:** matriz de permissões aprovada; testes 401/403/404; endpoints públicos documentados; nenhuma operação mutável ou dado sensível acessível anonimamente.

### ST-2 — Migração do frontend para sessões

**Prioridade:** P0.

- [ ] ST-201 — localizar todos os fluxos de login, estado de utilizador e chamadas API.
- [ ] ST-202 — guardar token opaco apenas em mecanismo adequado ao modelo de ameaça; nunca em URL, logs ou localStorage sem avaliação explícita.
- [ ] ST-203 — centralizar cliente HTTP e adicionar `Authorization: Bearer` às rotas privadas.
- [ ] ST-204 — restaurar sessão via `/api/users/me` ao iniciar/recarregar.
- [ ] ST-205 — tratar 401 (limpar sessão e pedir login), 403 (sem permissão) e 503 (indisponibilidade) sem loops.
- [ ] ST-206 — integrar logout e revogação no servidor.
- [ ] ST-207 — remover dependências de identidade/role vindas apenas do estado local ou payload do browser.
- [ ] ST-208 — testar navegação direta, refresh, múltiplos separadores, expiração e revogação.

**Aceitação:** todos os fluxos privados funcionam apenas com sessão válida; nenhuma UI concede permissões que o servidor não reconhece.

### ST-3 — Motor editorial e geração narrativa real

**Prioridade:** P0/P1 conforme dependências externas.

- [ ] ST-301 — separar claramente planeamento, geração textual, revisão, aprovação e produção.
- [ ] ST-302 — implementar validação server-side dos cânones editoriais e duração.
- [ ] ST-303 — uma obra = uma história canónica = uma minissérie individual.
- [ ] ST-304 — episódio individual com alvo de 5 minutos, mínimo de 4:30 e sem máximo rígido.
- [ ] ST-305 — volume com cinco livros aprovados da mesma IP/saga/idioma, cinco episódios e compilação real com durações e transições reais.
- [ ] ST-306 — sexto livro inicia novo volume.
- [ ] ST-307 — audiobook é produto separado; slideshow/animatic não é animação final.
- [ ] ST-308 — idades 4–5, 6–7 e 8–10; segurança emocional, autonomia e pensamento crítico; uma virtude principal, secundária opcional e três perguntas familiares.
- [ ] ST-309 — bloquear medo, vergonha, humilhação ou punição como resolução narrativa.
- [ ] ST-310 — consentimento explícito para vozes; proibir clonagem sem consentimento verificável.
- [ ] ST-311 — integrar fornecedores reais de texto/voz/imagem/vídeo, com credenciais por ambiente, timeouts, retries, limites e custos.
- [ ] ST-312 — mostrar estado real por etapa e impedir que mocks sejam apresentados como produção.
- [ ] ST-313 — manter BB-001 e BB-002 como drafts não aprovados até aprovação editorial formal.

**Aceitação:** geração ponta a ponta com fornecedor configurado em ambiente controlado; artefactos e durações verificáveis; falhas recuperáveis; sem simular sucesso.

### ST-4 — Assets e cadeia de produção

- [ ] ST-401 — decidir e documentar armazenamento privado/público, provider, lifecycle e retenção.
- [ ] ST-402 — eliminar referências de ficheiro sem objeto físico correspondente.
- [ ] ST-403 — upload assinado ou backend streaming, verificação de MIME/tamanho/hash e nomes não previsíveis.
- [ ] ST-404 — autorização por asset e URLs temporárias para conteúdos privados.
- [ ] ST-405 — transcodificação, thumbnails, validação de áudio/vídeo e retries.
- [ ] ST-406 — política de backup, restauração, retenção e eliminação.
- [ ] ST-407 — provar exportação e reprodução dos artefactos finais.

**Estado de referência 25/11:** auditoria anterior indicou Supabase Storage sem buckets/objetos e referências `PublicationAsset.fileUrl` sem prova de armazenamento binário próprio; issue #30 continua a exigir resolução. Confirmar novamente antes de decidir provider.

### ST-5 — Operação, qualidade e lançamento

- [ ] ST-501 — observabilidade estruturada e correlação por request/job.
- [ ] ST-502 — alertas para falhas de jobs, armazenamento, providers e sessões.
- [ ] ST-503 — backup/restore testado e runbooks de incidentes.
- [ ] ST-504 — testes de carga e limites de concorrência.
- [ ] ST-505 — hardening CORS, headers, cookies/tokens, CSP e configuração de produção.
- [ ] ST-506 — revisão de permissões de secrets e variáveis Vercel; nunca expor valores.
- [ ] ST-507 — staging/Preview E2E e checklist de release.
- [ ] ST-508 — revisão final de acessibilidade e UX.

---

## 4. Website — plano por fases

### WB-0 — Integridade de dados e catálogo

- [x] WB-001 — proteção RLS e grants de `system_metadata` (PR #51, integrado segundo relatório de 25/11).
- [x] WB-002 — unicidade de produto por variante de publicação (PR #53, integrado segundo relatório de 25/11).
- [ ] WB-003 — rever todas as tabelas, RLS, grants anon/authenticated/service role e funções SECURITY DEFINER.
- [ ] WB-004 — validar catálogo público anonimamente, sem sessão administrativa.
- [ ] WB-005 — validar variantes, disponibilidade, preço, idioma, idade, formatos e assets.
- [ ] WB-006 — garantir que dados internos, metadados, tokens e estados de fornecedor nunca são expostos ao público.

### WB-1 — Checkout e pagamentos

**Prioridade:** P0 comercial.

- [ ] WB-101 — fechar desenho de estados da encomenda e máquina de estados do pagamento.
- [ ] WB-102 — validar preço, moeda, variante, stock/disponibilidade e total exclusivamente no servidor.
- [ ] WB-103 — PayPal create order e capture server-side, com autorização e validação de ownership.
- [ ] WB-104 — idempotência por operação e proteção contra replay/duplicação.
- [ ] WB-105 — validar assinatura e origem dos webhooks; deduplicar eventos.
- [ ] WB-106 — reconciliar timeouts e resultados desconhecidos sem repetir captura cegamente.
- [ ] WB-107 — suportar falha, cancelamento, expiração, reembolso e disputa.
- [ ] WB-108 — concluir guest checkout de forma segura ou exigir conta; nunca confiar num identificador de browser.
- [ ] WB-109 — testar Sandbox com cenários positivos, negativos e concorrentes.
- [ ] WB-110 — manter produção sem transações reais até aprovação explícita e checklist de lançamento.

**Estado de referência 25/11:** PR #47 PayPal permanece Draft; não há confirmação de capturas Sandbox/produção, reconciliação de resultados desconhecidos nem conclusão do checkout legado guest. PR #26 está obsoleta/fechada sem merge. Confirmar estado antes de retomar.

### WB-2 — Publicação e sincronização com Studio

- [ ] WB-201 — definir contrato versionado Studio → Website.
- [ ] WB-202 — sincronização idempotente de produtos, variantes, assets e estados editoriais.
- [ ] WB-203 — impedir publicação de obra não aprovada ou artefacto inexistente.
- [ ] WB-204 — validar consistência entre catálogo, páginas e checkout.
- [ ] WB-205 — reconciliação periódica e fila de erros recuperáveis.
- [ ] WB-206 — garantir que despublicação/retirada não quebra encomendas existentes nem histórico.

### WB-3 — Experiência e confiança

- [ ] WB-301 — rever UX mobile e desktop de catálogo, produto, carrinho e checkout.
- [ ] WB-302 — acessibilidade WCAG, navegação por teclado e mensagens de erro.
- [ ] WB-303 — SEO, metadados, dados estruturados e indexação correta.
- [ ] WB-304 — páginas legais, privacidade, cookies, termos, entrega e reembolso.
- [ ] WB-305 — emails transacionais, recibos e notificações sem divulgar dados sensíveis.
- [ ] WB-306 — performance, imagens responsivas, caching e Core Web Vitals.

### WB-4 — Operação e lançamento

- [ ] WB-401 — monitorização de checkout, pagamentos, webhooks e erros de catálogo.
- [ ] WB-402 — backup/restore e retenção de encomendas.
- [ ] WB-403 — runbook de reconciliação manual e incidentes de pagamento.
- [ ] WB-404 — teste E2E anónimo do catálogo até checkout Sandbox.
- [ ] WB-405 — checklist de lançamento e aprovação explícita antes de ativar pagamentos reais.

---

## 5. Bloqueios e riscos conhecidos a revalidar

| ID | Risco/bloqueio | Prioridade | Evidência/ação necessária |
|---|---|---|---|
| R-01 | Stack de autenticação/RBAC ainda em PRs Draft | P0 | Integrar em ordem segura e testar cliente |
| R-02 | Rotas privadas ainda não classificadas/protegidas | P0 | Inventário total e teste automático |
| R-03 | PIN legado previsível em contas existentes | P0 | Identificar sem expor; forçar rotação/reset controlado |
| R-04 | Frontend pode ainda não usar Bearer sessions | P0 | Migração cliente e E2E |
| R-05 | Assets binários sem storage comprovado | P1 | Decidir provider e provar upload/download |
| R-06 | Providers de geração ainda não comprovados em produção | P1 | E2E com credenciais de ambiente controlado |
| R-07 | PayPal sem ciclo Sandbox/reconciliação completo | P0 comercial | Fechar PR #47 e testes |
| R-08 | Acesso anónimo à loja ainda por validar | P0 comercial | Teste anon de catálogo e checkout |
| R-09 | Secrets Vercel não auditáveis por leitura simples | P1 | Rever nomes/flags sem descodificar valores |
| R-10 | Storage e retenção/backup indefinidos | P1 | Decisão arquitetural e runbook |

Os riscos são hipóteses de trabalho baseadas no último relatório conhecido, não afirmações de estado atual. Revalidar antes de cada decisão.

---

## 6. Sequência recomendada de execução

A sequência é orientadora e pode ser ajustada quando CI ou dependências revelarem bloqueios:

1. **Fechar autenticação base:** PRs #79–#83 e dependências SQLite/PIN/bootstrap/sessão.
2. **Fechar autorização server-side:** PRs #84–#86, seguida de inventário total de rotas e proteção de projetos/publicação/assets.
3. **Migrar frontend do Studio:** token, `/me`, Bearer wrapper, logout e testes E2E.
4. **Resolver contas legadas e segurança operacional:** rotação de PINs previsíveis, rate limiting, auditoria e hardening.
5. **Fechar o Website comercial:** catálogo anónimo, PayPal Sandbox, idempotência, webhooks e reconciliação.
6. **Fechar produção editorial real:** providers, cânones, assets, estados honestos e outputs verificáveis.
7. **Fechar sincronização e experiência:** Studio → Website, UX, acessibilidade, SEO, emails e observabilidade.
8. **Auditoria de lançamento:** threat model, regressões, backup/restore, E2E e aprovação formal.

Não iniciar uma fase dependente enquanto a anterior tiver bloqueios P0 que comprometam a segurança ou integridade dos dados.

---

## 7. Política de PR e merge

Cada PR deve conter:

- [ ] escopo pequeno e único;
- [ ] ligação aos IDs deste plano;
- [ ] testes unitários e de integração;
- [ ] testes negativos de autorização quando aplicável;
- [ ] CI verde no SHA exato;
- [ ] análise de migrações e impacto de dados;
- [ ] notas de deploy/configuração sem valores secretos;
- [ ] riscos remanescentes e plano de rollback;
- [ ] documentação atualizada.

**Ordem de merge:** respeitar dependências reais do grafo de commits. Antes de cada merge, confirmar base/head SHA, conflitos, checks obrigatórios, estado Draft/Ready e efeito de incluir commits ancestrais. Nunca fazer merge automático apenas porque `mergeable=true`.

---

## 8. Cadência e atualização do plano

- Em cada sessão: escolher uma tarefa P0/P1, confirmar estado real, implementar, testar e atualizar este documento.
- Em cada PR: atualizar checkboxes apenas com evidência do commit e checks.
- No fim de cada ciclo: registar PR, SHA, workflows, resultados e bloqueios.
- Não apagar tarefas concluídas; preservar histórico de decisões e datas.
- Quando uma tarefa for bloqueada, documentar dependência, responsável/decisão necessária e alternativa segura.
- Reavaliar prioridades após cada integração e auditoria.

### Registo de execução

| Data UTC | Repositório | PR/Commit | Trabalho/evidência | Estado |
|---|---|---|---|---|
| 2026-11-25 | Studio | PR #84 — `a315955077231afeecd075ff40d928a7418bd1db` | RBAC user management; Studio CI, Distribution Hub V6 Smoke e Story Production Cloud Validation verdes | VERIFY — Draft |
| 2026-11-25 | Studio | PR #85 — `83a3caab1b13f68b14818036e6a901f6a80dfa5f` | RBAC editorial/production; três workflows verdes | VERIFY — Draft |
| 2026-11-25 | Studio | PR #86 — `c6eaa1178d32dde6ec5e897d60e9cbd693bc6ee6` | RBAC administrativo; três workflows verdes | VERIFY — Draft |
| 2026-11-25 | Studio | PR #84–#86 | Dependência `httpx==0.27.2` adicionada aos workflows de testes; correção de concorrência SQLite propagada | DONE — CI confirmado |
| 2026-11-25 | Studio | PR #86 | Inclusão deste plano mestre no branch de trabalho | IN PROGRESS — aguarda merge |
| 2026-11-25 | Studio | PR #87 — branch `security/project-assets-publisher-rbac-2026-11-25` | Projetos: identidade/owner derivado da sessão e isolamento de edição; assets e Website Publisher protegidos por RBAC; três workflows verdes no SHA exato `23ac545ff775abaaf226eb11795b1e90b0aaaee5` | VERIFY — Draft, não integrado |
| 2026-11-25 | Studio | PR #87 — `23ac545ff775abaaf226eb11795b1e90b0aaaee5` | Projetos, assets e Website Publisher protegidos; smoke test usa principal owner server-side; três workflows concluídos com sucesso no SHA exato | VERIFY — 3/3 CI verdes; Draft, não integrado |
| 2026-11-25 | Studio | PR #88 — `f8e1a5e638b05f05d0799c344870027c9131ef67` | project-commercial e exportações EPUB/audiobook/vídeo protegidos por sessão server-side e ownership; corrigido teste legado que invocava a rota de vídeo diretamente sem principal autenticado | VERIFY — 3/3 workflows verdes no SHA exato; Draft, não integrado |
| 2026-11-25 | Studio | PR #89 — `4a051c0af6541563566ccd4afda6b2824db6f641` | Publishing e Distribution Hub V6 exigem sessão server-side, ownership por projeto e autoria da publicação derivada da sessão; listagem editorial filtrada por projetos próprios | VERIFY — 3/3 workflows verdes no SHA exato; Draft, não integrado |
| 2026-11-25 | Studio | PR #90 — `f10686887bf68683e9046be45cf5a956fd800d76` | Corrige compatibilidade com o papel `creator` existente no modelo: criadores autenticados podem aceder aos próprios projetos; continuam impedidos de aceder a projetos alheios; RBAC atualizado nos routers de projeto/comercial/exportação/publicação/distribuição | VERIFY — 3/3 workflows verdes no SHA exato; Draft, não integrado |
| 2026-11-25 | Studio | PR #87 — `5474bd83ac8df0d7c8b955e2d33da1a478b5288f` | Projetos/assets/Website Publisher; Studio CI, Distribution Hub V6 Smoke e Story Production Cloud Validation verdes no SHA exato | VERIFY — 3/3 verdes; Draft |
| 2026-11-25 | Studio | PR #88 — `f8e1a5e638b05f05d0799c344870027c9131ef67` | project-commercial e exportações EPUB/audiobook/vídeo; três workflows verdes no SHA exato | VERIFY — 3/3 verdes; Draft |
| 2026-11-25 | Studio | PR #89 — `4a051c0af6541563566ccd4afda6b2824db6f641` | Publishing e Distribution Hub; três workflows verdes no SHA exato | VERIFY — 3/3 verdes; Draft |
| 2026-11-25 | Studio | PR #90 — `03b06f5fac38958636f91b3d4f0ab3a8c273723e` | Compatibilidade do papel creator; três workflows verdes no SHA exato | VERIFY — 3/3 verdes; Draft |
| 2026-11-25 | Studio | PR #91 — `c27cafe20d6806817ef662c218b0704fb7712540` | Voice Library/Preview/Profiles protegidos por papel server-side; Audio Cast, Editorial/Final Media e Illustration Pipeline/Provider com ownership por projeto; testes negativos e dependência reutilizável | VERIFY — Studio CI, Distribution Hub V6 Smoke e Story Production Cloud Validation verdes no SHA exato; Draft, não integrado |
| 2026-11-25 | Website | PR #47 — `263b46d302d838d7621af4a4fdded1caba4cfbfc` | Website CI e Repository Visibility passaram no SHA exato; PayPal capture capability/owner binding implementados | VERIFY — Draft; provider concurrency, adapter cookie tests, migration baseline e guest legacy pendentes |

---

## 9. Condições para declarar Baribudos pronto

A declaração final exige evidência de todos os pontos:

- [ ] Studio P0 de autenticação, RBAC e frontend fechado.
- [ ] Studio geração editorial real e cadeia de assets validadas.
- [ ] Studio outputs finais verificáveis, com estados e durações verdadeiros.
- [ ] Website catálogo público anónimo validado.
- [ ] Website pagamentos Sandbox e reconciliação validados.
- [ ] Website publicação/sincronização consistente com Studio.
- [ ] RLS, grants, secrets e rotas revistos.
- [ ] CI integral verde nos commits finais.
- [ ] E2E dos fluxos críticos verdes.
- [ ] Backup/restore, observabilidade e runbooks disponíveis.
- [ ] Nenhum P0 aberto ou risco crítico sem aceitação explícita.
- [ ] Aprovação humana explícita para deploy/ativação comercial.

**Princípio final:** avançar continuamente, mas só promover para DONE aquilo que foi implementado, testado e comprovado. O objetivo não é acumular commits; é entregar dois produtos seguros, coerentes e utilizáveis na realidade.


### Atualização de execução — 25/11/2026

- PR #87 integrada na `main`: `ca74a924c1a6698e6acf8bab6b5f1cc6e918b588` (base de autenticação, bootstrap, sessão atual e RBAC base).
- PRs empilhadas #88–#91 consolidadas na PR #92, integrada na `main`: `b89b5f0e15b3b097fc4af18a9d04a62890fd0854`. A nova PR passou Studio CI, Distribution Hub V6 Smoke e Story Production Cloud Validation no SHA `671874dc9056bec6ca9940e3790381a5fffe23eb`. PRs antigas #88–#91 fechadas como substituídas pela consolidação.
- Nova fase em curso na branch `security/studio-illustration-assets-ip-jobs-rbac-2026-11-25`: proteção por sessão e ownership de projeto nas rotas Illustration Assets e Illustration Generation; jobs globais limitados a owner/admin; atualização e import de jobs verificam projeto proprietário; uploads temporários removidos em `finally`.
- Testes novos cobrem 401 anónimo, 403 viewer, acesso a projeto próprio, bloqueio de projeto alheio e listagem global owner-only. CI pendente para a nova PR.
- Auditoria identificou como próximas superfícies: legacy Illustrations upload, Covers, Jobs globais, IP canons/characters/metadata/branding e Diagnostics. As rotas IP ainda confiam em identidade/role fornecidos por query/form/payload e em comparações por nome; não considerar esta área resolvida.
- Website: PR #47 continua Draft. PR #54 adiciona política comum e testes dos cookies de captura guest, empilhada sobre #47. Não resolve baseline de migrações, concorrência distribuída PayPal, guest legacy nem revogação de sessões JWT.


### Atualização de execução — 26/11/2026

- Studio PR #93 integrada na `main`: `acf32b2053af46f2ba248c6deb8da8c7fe187dc`. Illustration Assets e Illustration Generation passaram a validar sessão, papel e ownership de projeto; jobs globais limitados a owner/admin; importações limpam ficheiros temporários em `finally`. Os três workflows passaram no SHA exato antes do merge.
- Nova branch `security/legacy-ip-covers-jobs-diagnostics-rbac-2026-11-26` em execução: rotas antigas de ilustrações, capas, jobs, diagnostics, branding pack, factory, age badges e IP Creator passam a exigir principal de sessão e autorização por projeto/IP.
- Canons, personagens, metadados, branding e paletas deixam de confiar em `user_id`, `user_name` ou `user_role` enviados pelo cliente. O acesso privado a IP usa o ID autenticado, listas de editores autorizados e papéis permitidos; comparações por nome não são usadas como prova de identidade.
- Jobs passam a exigir projeto para editor/creator e listagem global apenas para owner/admin. Criação de jobs deriva `created_by` da sessão. Diagnostics passa a owner/admin.
- Testes negativos adicionados para impersonação por query, acesso anónimo, isolamento por projeto, diagnostics e criação de IP com owner forjado. PR ainda não aberta/CI não validada; não marcar como concluído até workflows verdes no SHA exato.
- Website PR #54: primeira validação encontrou dois testes de contrato obsoletos após a extração da política de cookies para helper. Foram ajustados para testar o resultado efetivo do helper (HttpOnly, Secure, SameSite, path e expiração), sem enfraquecer as garantias. Novo SHA `6be0dda339066b8ff6e8c86bd737a122028b3dbc`; CI pendente.
- Website PR #47 continua bloqueada por concorrência distribuída PayPal, recuperação de checkout órfão, baseline de migrações e reconciliação de checkouts guest antigos. Sem pagamentos Sandbox/produção ou migrações.


### Atualização de execução — 26/11/2026 (fase seguinte)

- Nova branch empilhada sobre a PR #94: `security/studio-private-admin-surfaces-2026-11-26`.
- Protegidos endpoints de settings, memória persistente AndreOS, diagnostics/smoke, instalação e gestão dos motores locais de IA/áudio, gestão de sagas, saga loader/runtime, visual sets e pairing administrativo.
- Endpoint público de health reduzido a liveness mínima; removidos host, porta, ambiente e caminhos locais.
- `saga-loader/{id}/can-edit/{user_role}` mantém compatibilidade do URL, mas ignora o papel enviado pelo cliente e calcula a autorização a partir da sessão e da política de IP.
- Pairing: listar/criar/revogar exige owner/admin; resolução mantém-se como capability pública com código aleatório e expiração de 72 horas para permitir o emparelhamento de dispositivos.
- Public asset manifests continuam públicos apenas para assets publicados e deixam de devolver `storage_path` interno.
- Testes negativos adicionados para anónimo, viewer, role spoofing, pairing, health e exposição de caminhos privados. CI ainda não validada.
- A auditoria total continua em curso; não declarar Studio fechado até analisar os manifests automáticos de autorização, as rotas restantes e os fluxos E2E.


### Atualização de execução — 26/11/2026 (rotas de produção e comercial)

- Nova branch `security/studio-project-production-routes-rbac-2026-11-26`, empilhada sobre a fase de superfícies administrativas.
- Story Layout, Story Source, Story Translation, Editorial Engine, Editorial Production, Product Credits, Project Integrity, Publication Package, Publish Readiness, V1 Readiness e distribuição legada passam a validar sessão e ownership do projeto.
- Foram removidas verificações de autorização baseadas em `user_name`/`user_role` enviados por query. A distribuição legada usa o principal autenticado; mutações de publicação ficam limitadas a owner/admin/creator.
- Commerce Groups e Sponsors ficam sob administração; Sponsorship Scopes separa leitura autenticada, mutação owner/admin e resolução com ownership de projeto.
- Website Bundles, Website Visual Sets, Website Contract e endpoints de reconciliação exigem papel apropriado; publicar bundles/visual sets e validar todos os contratos são operações owner/admin.
- Testes negativos cobrem anónimo, viewer, tentativa de spoofing por query, projeto próprio vs projeto alheio e mutações comerciais/publicação.
- CI pendente. A auditoria continua a tratar como P0 a montagem estática integral de `/storage`, migração completa dos clientes para bearer sessions e revisão final de todas as rotas e ficheiros servidos.


### Atualização de execução — 26/11/2026 (migração do cliente para Bearer)

- Nova branch `security/studio-client-bearer-session-2026-11-26`, PR #97 em preparação sobre `main`.
- O cliente centraliza o cabeçalho `Authorization: Bearer` em GET/POST/PUT/PATCH/DELETE; respostas 401 limpam a sessão local e notificam a aplicação.
- Login valida a presença do token opaco devolvido em `session.token`; foram removidos os valores predefinidos de utilizador e PIN.
- O arranque deixa de restaurar o perfil a partir de localStorage e valida a sessão com `GET /users/me`; logout chama `POST /users/logout` e limpa o estado local mesmo quando a rede falha.
- O perfil público fica apenas em memória; o token é mantido em memória durante a execução e persistido apenas nos cofres nativos: Android Keystore/iOS Keychain via Capacitor Secure Storage 7.1.6 e cofre de credenciais do sistema via Rust keyring no Tauri. O adaptador web não persiste token. O cliente revalida sempre com `GET /users/me` antes de restaurar o perfil.
- Testes Node nativos adicionados para bearer em GET/POST, ausência de perfil em localStorage e limpeza após 401; CI executa `npm run test:auth` antes do build.
- A resolução de media ainda constrói URLs diretas `/storage/`; a separação entre assets públicos e downloads privados autenticados permanece bloqueio P0.
- Não existe deploy, alteração de produção, instalação de plugin nativo ou migração de dados nesta fase.


#### Revisão adicional do transporte e identidade no cliente

- A pesquisa do código encontrou chamadas `fetch()` diretas fora do helper central, incluindo uploads multipart de assets, ilustrações, voz e branding. Todas passaram a usar `apiFetch()`, que injeta Bearer sem definir Content-Type manualmente para FormData.
- Removidos `user_id`, `user_name` e `user_role` dos módulos de API do cliente (projetos, IP e distribuição); o servidor é agora a única fonte de identidade/autorização.
- Pesquisa estática após alteração: 19 módulos API; a única chamada direta a `fetch()` é o próprio `apiFetch()` central. Nenhum campo de identidade cliente foi encontrado nesses módulos.
- A CI foi atualizada para correr os testes de contrato Node antes do build. O primeiro run completo na versão anterior passou; a revisão adicional aguarda validação no novo SHA.


#### Armazenamento nativo de sessão — implementação adicionada

- Capacitor: dependência `@aparajita/capacitor-secure-storage@^7.1.6`, compatível com a linha Capacitor 7 existente; usa Android Keystore e iOS Keychain, com acessibilidade iOS `whenUnlockedThisDeviceOnly`.
- Tauri desktop: comandos nativos `secure_session_get/set/clear` usam a crate Rust `keyring` para o cofre de credenciais do sistema operativo (Windows Credential Manager no target desktop atual).
- O token só é restaurado após ligação à API e é validado por `/users/me`; o perfil nunca é usado como prova de autenticação.
- O cliente web não persiste tokens. O armazenamento nativo só é chamado quando a runtime é Capacitor nativa ou Tauri; falhas do cofre bloqueiam a persistência e não provocam fallback para localStorage.
- Pendente: validação real de compilação/execução Android e Windows, incluindo instalação/sync Capacitor, cargo check/build e ensaio de logout/expiração/reinício em dispositivos. Até essa evidência, a persistência nativa está implementada mas ainda não certificada.


### Atualização de execução — 26/11/2026 (contenção da exposição de storage)

- Nova branch `security/studio-private-storage-serving-2026-11-26`, PR #98 em preparação sobre `main`.
- Removida a montagem estática da raiz privada em `/storage`. O inventário FastAPI e a CI passam agora a falhar se essa rota reaparecer.
- Criado `GET /api/projects/{project_id}/media?path=...`: exige sessão e ownership do projeto, só aceita ficheiros explicitamente referenciados nos campos de caminho do próprio projeto, rejeita traversal e extensões não permitidas, e devolve `private, no-store` + `nosniff`.
- Criado `GET /api/public/assets/{asset_id}/file`: só serve registos do asset registry em estado `published`; drafts/arquivados são 404. Manifestos públicos passam a usar este endpoint.
- Respostas da API de assets deixaram de devolver caminhos `/storage`; URLs de assets não publicados ficam vazias.
- Outputs do projeto passaram a ser descarregados/visualizados via fetch autenticado com Bearer; URLs `/storage` deixaram de ser convertidas em URLs diretas.
- CORS deixou de aceitar wildcard com credenciais: origins explícitas configuráveis por `BARIBUDOS_CORS_ORIGINS`, sem cookies, com Authorization/Content-Type e métodos limitados.
- Testes adicionados para acesso anónimo, ownership, paths não referenciados, traversal, extensões, assets published vs draft e CORS.
- Pendente: migrar os previews de voz/audio, updater e restantes consumidores de media para endpoints específicos autorizados; validação CI no SHA final. Nenhum ficheiro de produção foi alterado nem movido.


#### Media privado — previews de voz e updater

- Voice Preview passa a emitir um identificador UUID opaco e `file_url` em vez de expor `file_path`; o endpoint `GET /api/voice-preview/{preview_id}/file` exige sessão e papel owner/admin/editor/creator e só resolve o ficheiro com nome derivado do UUID.
- Audio Cast e Voice Cloning carregam o preview como blob autenticado, sem URL direta para storage.
- Updater deixa de devolver `file_path`/ `storage_url`; valida o basename e a extensão do instalador, devolve `file_url` e serve-o em `GET /api/updater/files/{file_name}`, limitado a owner/admin e a extensões de instalador permitidas.
- O cliente faz fetch same-origin com Bearer e rejeita destinos externos para impedir fuga do token.
- Testes acrescentados para preview autenticado, updater admin-only, traversal, media same-origin e rejeição de encaminhamento de Bearer para outro domínio.
- Continuam por auditar todos os restantes campos/consumidores de media e validar a compatibilidade de assets publicados em todos os ecrãs; CI final ainda pendente.


#### Assets privados e aprovação de publicação

- Assets com projecto/IP têm agora `GET /api/assets/{asset_id}/file`, Bearer obrigatório e autorização por ownership do projeto ou acesso de leitura à IP; assets globais ficam owner/admin-only.
- DTOs de assets incluem `file_url` autenticada e mantêm `url` pública apenas para assets já publicados.
- Upload e registo forçam estado `draft`, ignorando qualquer tentativa do cliente de definir `published`.
- Publicação, arquivo e rollback foram limitados a owner/admin. Só o endpoint de publicação explícita pode promover um asset para `published`.
- Testes cobrem tentativa de self-publish por editor e isolamento do ficheiro privado por projeto.


#### Isolamento de amostras de voz

- Upload de amostra associa `owner_user_id` à sessão autenticada.
- Listagem de editor/creator fica limitada às próprias amostras; owner/admin mantém visão administrativa.
- Consulta individual e geração de preview verificam a titularidade da amostra; amostras legadas sem owner ficam restritas a owner/admin até reconciliação/consentimento.
- Audio Cast preview aplica a mesma verificação; respostas públicas de voz deixam de incluir caminhos físicos.
- Testes cobrem isolamento entre utilizadores e bloqueio de preview de amostra alheia.


#### Fecho de superfícies estáticas e DTOs

- O mount `/public` também deixa de seguir symlinks para fora da raiz do projeto; apenas diretório físico dentro de `APP_CONFIG.project_root` pode ser montado.
- CORS rejeita explicitamente `*` em `BARIBUDOS_CORS_ORIGINS`, além de usar `allow_credentials=False`.
- DTOs privados de assets removem `storage_path`, `file_path`, `absolute_path` e `source_path`; o manifest sanitiza os mesmos campos recursivamente.
- Upload de assets não aceita estado de publicação vindo do cliente; a promoção pública continua reservada a owner/admin.


#### Ownership transversal da API de assets

- Listagem e consulta de assets filtram/verificam acesso ao projeto e à IP; assets globais são reservados a owner/admin.
- Upload e registo exigem autorização de edição do projeto e, quando indicado, também da IP. Não basta ter acesso a um projeto para escrever assets numa IP diferente.
- Downloads privados repetem a verificação de ownership, independentemente da autorização usada na listagem.
- Testes atualizados para exigir simultaneamente acesso ao projeto e à IP quando o asset está associado a ambos.


#### Isolamento do ficheiro de preview de voz

- Cada preview cria sidecar privado com owner_user_id e timestamp; o endpoint de download exige o mesmo utilizador (ou owner/admin) e aplica TTL de 15 minutos.
- O payload deixou de devolver `speaker_wav` ou caminhos físicos da amostra usada.
- Audio Cast propaga o principal autenticado para o serviço de preview; a titularidade é verificada antes de sintetizar e antes de descarregar.
