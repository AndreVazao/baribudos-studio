# Studio — revisão alargada de superfícies API e política RBAC

**Data:** 13-11-2026  
**Base de código:** `main` em `517e4d6b552b41eeceb9b743ef1952152caa86ed`  
**Branch de documentação:** `docs/studio-identity-handler-matrix-2026-11-13`  
**Estado:** análise estática e proposta de implementação; não altera runtime.

## 1. Âmbito e nível de confiança

O inventário CI identifica **78 módulos Python de rotas, 233 handlers, 29 handlers que referenciam identidade fornecida pelo cliente e 97 superfícies sensíveis/operacionais**. A revisão estática anterior seguiu os 29 handlers e os helpers/serviços diretamente relevantes. Nesta passagem foi feita uma segunda leitura alargada dos restantes módulos, do registo da aplicação e dos contratos dos clientes.

Esta leitura é uma **classificação de risco por superfície**, não uma prova dinâmica de exploração nem uma auditoria transitiva completa de cada uma das 233 operações. Os números do inventário são os do artefacto CI; não foram recalculados por testes HTTP.

### Evidência transversal confirmada em `studio_core/api/main.py`

- Não está registado middleware global de autenticação nem dependência global de autenticação nos `include_router` inspecionados.
- CORS permite origins, métodos e headers wildcard com credenciais ativadas.
- A raiz de storage é montada integralmente em `/storage` com `StaticFiles`, sem allowlist de ficheiros.
- `public/` é montada separadamente em `/public`; os conteúdos têm de ser classificados antes de se assumir que são publicáveis.
- Os routers são registados diretamente; não há uma fronteira central de autenticação visível que compense handlers sem dependências locais.

### Evidência transversal confirmada nos clientes/modelos

- `User` ainda contém `pin: str`; `UserCreate` aceita PIN em texto simples.
- `ensure_default_owner()` cria automaticamente André/owner com PIN `1234` quando a lista de utilizadores está vazia.
- O login atual compara credencial contra o registo persistido e o handler devolve o registo do utilizador.
- O cliente React comum a Tauri/Capacitor guarda o utilizador completo em `localStorage`, não envia bearer token e restaura o utilizador sem validação de sessão.
- O login UI contém nome/PIN predefinidos. A migração tem de alterar o contrato de ponta a ponta; middleware isolado não chega.

## 2. Classificação de superfícies além dos 29 handlers

A classificação abaixo agrupa routers por efeito e dados envolvidos. **P0** significa que a operação deve ficar indisponível a anónimos e a utilizadores sem permissão antes de qualquer rollout público/rede; **P1** significa acesso privado ou controlado, a fechar na mesma migração. A ausência de uma dependência local é evidência estática, não prova de acesso remoto em execução.

| Domínio / routers | Exemplos de operações observadas | Risco | Política requerida |
|---|---|---:|---|
| Contas e credenciais — `users` | listar/criar/alterar utilizadores, PIN e login | P0 crítico | Login público limitado; gestão apenas owner; nunca devolver segredo/hash |
| Segredos e configuração — `secret_control`, `settings` | vault CRUD/export/reveal, leitura e escrita de settings | P0 crítico | Owner apenas; reveal/export com reautenticação e auditoria |
| Projetos/editorial — `projects`, `story_source`, `story_layout`, `editorial_engine`, `editorial_production`, `production_pipeline`, `factory` | ler/escrever texto, paginação, gerar história/ilustrações, correr pipeline | P0 | permissões por projeto; criança só em fluxo supervisionado e limitado |
| Media e uploads — `assets`, `illustrations`, `illustration_assets`, `illustration_generation`, `illustration_pipeline`, `voice_library`, `voice_profiles`, `audio_cast` | upload, import, fila de geração, edição de jobs, perfis e amostras de voz | P0 | upload/generation por projeto/IP; consentimento de voz; quotas e validação de ficheiros |
| IP, canon e saga — `ip_creator`, `ip_branding`, `ip_canons`, `ip_characters`, `ip_metadata`, `ip_palette`, `sagas`, `saga_runtime`, `saga_visual_sets`, `saga_loader` | criar IP, ACL, canon, personagens, branding, paleta, idiomas e assets visuais | P0 | ACL por IP; canon só editável por editor/owner autorizado |
| Publicação e distribuição — `publishing`, `publication_package`, `publish_readiness`, `distribution_hub`, `distribution_hub_v6`, `website_publisher`, `website_bundles`, `website_visual_sets` | freeze, readiness, publicar/despublicar, canais e sincronização | P0 crítico | aprovação editorial + permissão de publicação; integração Website M2M separada |
| Comercial e patrocínios — `project_commercial`, `commerce_groups`, `storefront`, `sponsors`, `sponsorship_scopes`, `website_admin` | preços, bundles, produtos, patrocinadores, visibilidade e campanhas | P0 | owner/admin comercial; nenhuma criança ou voice-recorder |
| Voz e créditos — `product_credits`, `voice_library`, `voice_profiles`, `voice_preview`, `audio_cast_preview` | créditos, amostras, preview e perfis | P0/P1 | acesso por projeto/IP; consentimento e lineage de doador; preview limitado |
| Operação local — `local_ai_installer`, `local_audio_installer`, `local_engine_manager`, `local_audio_engine_manager`, `updater`, `pairing` | instalar, selecionar provider, iniciar/parar engines, descarregar update, pairing | P0 | owner/admin de dispositivo; nunca expor a rede local sem autenticação |
| Operações e diagnóstico — `diagnostics`, `db_control`, `deploy_control`, `website_control`, `persistent_memory`, `system_smoke`, `system_smoke_v1`, `jobs`, `v1_readiness` | estado interno, caminhos, memória, jobs, smoke e deployments | P1 privado; algumas mutações P0 | owner/admin ou operador com capacidade explícita; resposta minimizada |
| Leitura potencialmente pública — `health`, `storefront`, `public_assets`, `branding_pack`, `marketplace_visuals` | health, catálogo, manifestos e adaptações de imagem | P1 até classificação | só allowlist pública, dados publicados e DTOs públicos; health sem paths/host/ambiente |

### Bloqueios imediatos de arquitetura

1. A raiz `/storage` não pode continuar montada como conteúdo estático. Separar storage privado e diretório público de assets aprovados.
2. Nenhuma rota de mutação pode ser considerada segura por não aceitar `user_role`: precisa de principal autenticado e autorização explícita.
3. Routers de leitura podem expor dados familiares, projetos, IPs, vozes, memória, paths ou configuração; não são públicos por serem GET.
4. Rotas de operação local (instaladores, processos, updater e pairing) são particularmente sensíveis se o backend estiver ligado a `0.0.0.0`.
5. Website Publisher é uma ação privilegiada Studio→Website; deve exigir utilizador com permissão `publication.publish` e credencial M2M do Website guardada apenas no servidor. Não criar endpoint Website→Studio implicitamente.

## 3. Matriz RBAC proposta

Usar permissões nomeadas e verificadas por recurso. Os nomes abaixo são uma proposta inicial para implementação e têm de ser versionados.

| Capacidade | Owner | Admin | Creator | Editor | Voice recorder | Child | Viewer |
|---|---:|---:|---:|---:|---:|---:|---:|
| `users.manage`, `users.credentials.reset`, `sessions.revoke_all` | ✓ | — | — | — | — | — | — |
| `settings.manage`, `secrets.manage`, `ops.deploy`, `ops.database.manage` | ✓ | — | — | — | — | — | — |
| `ops.read`, `jobs.read`, `diagnostics.read` | ✓ | ✓ | — | — | — | — | — |
| `projects.create`, `projects.read`, `projects.edit` (scope atribuído) | ✓ | ✓ | ✓ | ✓ | — | — | read scope |
| `editorial.generate`, `editorial.edit` (scope atribuído) | ✓ | ✓ | ✓ | ✓ | — | request supervisionado | — |
| `editorial.review`, `editorial.approve`, `publication.freeze` | ✓ | ✓ | — | ✓* | — | — | — |
| `publication.publish`, `publication.unpublish` | ✓ | ✓* | — | — | — | — | — |
| `distribution.manage`, `commercial.manage`, `sponsors.manage` | ✓ | ✓* | — | — | — | — | — |
| `ip.read`, `canon.read` (scope atribuído) | ✓ | ✓ | ✓ | ✓ | — | read guiado | — |
| `ip.edit`, `canon.edit`, `characters.edit` | ✓ | ✓ | ✓* | ✓* | — | — | — |
| `media.upload`, `media.generate` (scope atribuído) | ✓ | ✓ | ✓ | ✓ | ✓* | upload/record guiado | — |
| `voice.consent.manage`, `voice.profile.manage` | ✓ | ✓* | — | — | — | — | — |
| `credits.edit` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `website.publish`, `website.catalog.manage` | ✓ | ✓* | — | — | — | — | — |

* Requer concessão adicional explícita, âmbito atribuído e, quando aplicável, segunda aprovação. Não é automaticamente herdado do papel.

**Regras obrigatórias:**
- Role não é identidade. O servidor resolve `user_id`, role e estado da conta a partir da sessão.
- ACL de projeto/IP vive no servidor, com associação por IDs estáveis; nomes de pessoa, `created_by`, `requested_by`, `owner_id` ou `user_role` enviados pelo cliente nunca concedem acesso.
- A criança não tem permissões de publicação, preço, gestão, integração, segredo, deploy, apagamento ou administração. A ação infantil é um endpoint de intenção supervisionada, com limites próprios.
- `creator` e `editor` são papéis globais; o acesso real exige membership/grant no projeto/IP.
- `admin` não recebe automaticamente acesso a vaults, credenciais ou recuperação do owner.
- Operações críticas (publicar, alterar preço, revelar/exportar segredos, resetar credenciais) geram evento de auditoria com actor, sessão, recurso, ação, decisão e timestamp.

## 4. Contrato de sessão server-side

### Modelo mínimo

`users`:
- `id`, `name`, `role`, `is_active`, `password_hash`, `must_change_password`, `credential_version`, `created_at`, `updated_at`.
- Não persistir PIN/password em claro; não devolver hash, token ou dados internos.
- A migração de `users.json` deve ser idempotente, backup privado e validada. O owner inicial existente deve ser migrado para hash e obrigado a alterar a credencial; eliminar a criação silenciosa de um owner universal `André/1234`.

`auth_sessions`:
- `id`, `token_hash`, `user_id`, `credential_version`, `created_at`, `last_seen_at`, `expires_at`, `revoked_at`, `device_label`.
- Token opaco de 256 bits gerado com CSPRNG. Entregar uma única vez; persistir apenas SHA-256 do token aleatório.
- Validar em cada pedido: token, sessão não expirada/revogada, utilizador ativo e versão de credencial.
- Expiração por inatividade e absoluta configuráveis; rotação de token e revogação por dispositivo.
- Password hash com Argon2id e parâmetros versionados. Login genérico, rate limit e atraso progressivo; sem revelar se o utilizador existe.
- Alteração/reset de credencial incrementa `credential_version` e revoga todas as sessões anteriores.

### Store local

Usar SQLite local (biblioteca standard Python) para as tabelas de autenticação, sessões e auditoria, com transações, constraints e WAL; manter o ficheiro fora de `public/` e de qualquer static mount, permissões do sistema operativo restritas. A store de sessões em JSON não é aceitável sem lock interprocesso, escrita atómica e prova de concorrência. Esta decisão não requer serviço cloud pago nem migração imediata dos restantes dados editoriais.

### Principal e autorização

- `get_current_principal()` produz objeto imutável com `user_id`, `role`, `permissions`, `session_id` e estado de credencial, apenas depois de validar a sessão.
- `require_permission("...")` verifica capacidade global.
- `authorize_project(project_id, permission)` e `authorize_ip(ip_slug, permission)` verificam existência, membership/ACL e capacidade em cada operação.
- A camada de serviço recebe principal/contexto autorizado ou IDs de actor atribuídos pelo servidor; não recebe role/name arbitrários do payload.
- Default deny: toda a rota não classificada e não explicitamente pública exige autenticação.
- Não confiar em CORS, hostname local ou origem Tauri/Capacitor como autenticação.

## 5. Migração dos clientes sem quebrar Studio

1. **Contrato API paralelo:** introduzir login com resposta DTO mínima + token; `GET /auth/me`, `POST /auth/logout`, `POST /auth/change-password`, `GET /auth/sessions`, `DELETE /auth/sessions/{id}`. Não alterar rotas de negócio ainda.
2. **Adaptadores seguros:** confirmar plugin compatível de Keychain/Keystore para Capacitor e keyring Windows/macOS/Linux para Tauri. Não usar `localStorage` como fallback de token. Token em memória durante execução e secure storage nativo para persistência.
3. **Cliente HTTP central:** todas as chamadas API passam pelo mesmo wrapper com bearer token, tratamento 401, retry limitado e logout. Não enviar identidade/role para autorização.
4. **Bootstrap:** substituir `getSavedUser()` por validação `/auth/me`; sessão offline não é autorização indefinida. Cache local pode manter UI em modo leitura offline, mas ações ficam bloqueadas até revalidar.
5. **Rotas por domínio:** converter em lotes pequenos, começando users/settings/secrets, projects/IP, editorial/media, publication/commercial, operations e leitura privada.
6. **Storage:** media pública só por URL pública de registry; ficheiro privado por endpoint autenticado com autorização por projeto/IP, canonicalização do path e validação de tipo/tamanho.
7. **Desativação legacy:** só depois de desktop e mobile atualizados e testados. Não manter fallback que aceite `user_id`, `user_name` ou `user_role` enviados pelo cliente.
8. **Rollout reversível:** feature flag local para autenticação nova, métricas sem segredos, backup validado e procedimento de recuperação owner. Não expor temporariamente API privada para suportar clientes antigos.

## 6. Testes de aceitação — obrigatórios em CI

### AuthN
- Anónimo em qualquer rota privada → 401.
- Token inválido, expirado, revogado, sessão apagada, utilizador inativo ou `credential_version` desatualizada → 401.
- Credencial inicial obriga alteração antes de qualquer operação de negócio.
- Login falhado tem resposta indistinguível para utilizador inexistente e credencial errada.
- Rate limit por conta e origem, com proteção contra lockout abusivo.
- Token, hash e credencial nunca aparecem em respostas, logs ou telemetria.

### AuthZ
- Autenticado sem capacidade → 403.
- Falsificar `user_id`, `owner_id`, `user_name`, `user_role`, `created_by` ou `requested_by` não aumenta privilégios.
- User A não lê nem altera projeto/IP de User B; testar GET, PATCH, POST, upload, download e jobs.
- Criança tenta preço, publicar, delete, users, settings, segredos, deploy, DB e pairing → 403.
- Creator sem membership não edita projeto/IP; editor sem grant não aprova/publica.
- Publicação exige pacote congelado, readiness válida, aprovação e permissão server-side.
- Website M2M inválido/revogado/checksum inválido → rejeição; segredo não exposto a clientes.

### Storage / transporte
- `/storage/data/users.json`, projetos, logs, backups, vaults e ficheiros privados → 404/403, nunca conteúdo.
- `/public` contém apenas assets aprovados; manifestos não expõem paths locais.
- Path traversal, symlink escape e cross-IP access bloqueados.
- CORS permite apenas origins definidos por ambiente; OPTIONS e credentials testados.
- Upload verifica bytes, MIME real, extensão, tamanho, dimensão/duração quando aplicável e destino; rollback não deixa órfãos.
- Endpoints locais de installer/process/updater/pairing exigem autenticação e permissão de dispositivo.

### Clientes
- Tauri e Capacitor: login, reinício, revalidação, expiração, logout, revogação remota e rotação de credencial.
- Secure storage indisponível → login não persiste token; nunca fallback para localStorage.
- 401 limpa perfil/token e abre login; 403 mostra acesso negado sem apagar sessão.
- Modo offline mantém apenas cache local explicitamente permitido; não executa mutações protegidas.

## 7. Plano de execução em PRs pequenos

| Ordem | PR/entrega | Conteúdo | Gate |
|---|---|---|---|
| 0 | Inventário | classificação endpoint a endpoint, router público/M2M/privado e dono da permissão | nenhum handler sem classificação |
| 1 | Auth core | SQLite auth store, hash, login, sessão, revogação, DTO, auditoria | unit tests + concorrência |
| 2 | RBAC core | principal, permissions, project/IP scope, default deny em routers novos | tests 401/403 e spoof |
| 3 | Client adapters | secure storage Tauri/Capacitor, bearer wrapper, bootstrap/logout | testes nativos em Windows/Android |
| 4 | P0 data/editorial | users, settings, secrets, projects, IP/canon, editorial, media | regressão e negative HTTP tests |
| 5 | Publication/commercial | readiness, freeze, publishing, distribution, Website, prices/sponsors | approval + audit + M2M tests |
| 6 | Operations/storage | diagnostics, DB/deploy/updater/pairing, StaticFiles e downloads | storage exposure tests |
| 7 | Legacy removal | remover PIN/plaintext, campos de identidade, defaults e compatibilidade antiga | teste end-to-end e rollback ensaiado |

## 8. Decisões e limites

- Esta proposta não instala plugins, cria serviços externos, altera Supabase, Website, CORS, dados, credenciais ou infraestrutura.
- A escolha de plugin secure storage depende de teste real no bundle Tauri e Android; não adicionar dependência antes dessa validação.
- SQLite é recomendado apenas para autenticação/sessões/auditoria local; não implica migrar agora todos os JSON editoriais.
- A integração atual é Studio→Website. Não abrir Website→Studio sem desenho M2M independente e autorização explícita.
- A classificação de cada endpoint deve ser transformada em manifest testável (método, path, público/M2M/role, permissão, scope, side effect) e validada automaticamente contra o OpenAPI em CI.
- A auditoria transitiva e os testes HTTP ainda não foram executados. **Não declarar o Studio seguro nem remover o bloqueio P0 com base neste documento.**
