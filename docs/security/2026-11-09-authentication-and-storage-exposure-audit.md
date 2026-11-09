# Baribudos Studio — audit de autenticação, autorização e exposição de ficheiros

**Data da auditoria:** 2026-11-09  
**Base analisada:** `main`  
**Objetivo:** preparar uma migração de segurança integral sem quebrar o Studio desktop, a aplicação móvel ou a integração com o Website.

## Resultado executivo

A revisão estática confirmou riscos críticos na fronteira HTTP do Studio. Não é seguro resolver isto apenas escondendo o PIN ou acrescentando uma verificação a algumas rotas: a autenticação atual não cria uma sessão de servidor e várias decisões de autorização confiam em identidade/função fornecidas pelo cliente.

**Prioridade P0 — exposição potencial de dados internos por ficheiros estáticos.** Em `studio_core/api/main.py`, a aplicação monta `StaticFiles` sobre a raiz completa devolvida por `resolve_storage_path()`, no prefixo `/storage`. Em `studio_core/core/storage.py`, os dados operacionais são guardados dentro dessa mesma raiz, incluindo `data/users.json`, `data/projects.json`, `data/settings.json`, `data/publications.json` e `data/jobs.json`. Consequentemente, paths como `/storage/data/users.json` ficam potencialmente servidos pela rota estática enquanto esses ficheiros existirem. A confirmação por pedido HTTP ainda tem de ser feita num ambiente de teste, mas a configuração estática já demonstra a exposição estrutural. A raiz de storage não pode continuar a ser publicada integralmente.

**Prioridade P0 — credenciais e identidade.** O proprietário inicial é criado com PIN `1234`; os PINs são guardados em texto simples no modelo e no JSON; os endpoints de utilizadores devolvem os registos completos, incluindo o PIN; o ecrã de login também preenche inicialmente André/`1234`. O cliente guarda o objeto de utilizador em `localStorage` e restaura-o no arranque sem revalidar uma sessão no servidor.

**Prioridade P0 — autorização forjável.** Rotas de projetos, publicação, operações comerciais e gestão de IP aceitam `user_name`, `user_role` e/ou `user_id` em query, formulário ou payload. Estes valores são dados controlados pelo cliente, não prova de identidade. Um pedido HTTP pode construir esses campos sem passar pelo login.

**Prioridade P0 — superfície HTTP.** A aplicação não apresenta middleware global de autenticação. O CORS está configurado com `allow_origins=["*"]` e `allow_credentials=True`. O host predefinido é `0.0.0.0`, permitindo escuta em todas as interfaces de rede; isto pode ser necessário para o cliente móvel na LAN, mas exige uma fronteira de acesso explícita e não deve ser confundido com exposição pública segura.

Não foi feita qualquer alteração funcional de autenticação nesta auditoria. Isso é intencional: uma correção parcial poderia deixar endpoints administrativos abertos ou impedir o login do desktop/móvel.

## Evidência verificada

| Área | Ficheiros / comportamento observado | Risco |
|---|---|---|
| Montagem estática | `studio_core/api/main.py`: `StaticFiles(directory=str(storage_dir))` montado em `/storage` | A raiz contém ficheiros JSON internos; exposição potencial direta |
| Persistência | `studio_core/core/storage.py`: `DEFAULT_JSON_FILES` inclui utilizadores, projetos, settings, publicações e jobs em `data/*.json` | Dados operacionais dentro da raiz estática |
| PIN inicial | `studio_core/api/routes/users.py`: `ensure_default_owner()` cria owner com PIN `1234` | Credencial previsível e conhecida |
| Modelo de utilizador | `studio_core/core/models.py`: `User.pin`, `UserCreate.pin`, `UserPinPatch.pin` | Segredo em texto simples |
| Respostas de utilizadores | `GET /api/users`, criação, alteração de PIN e login devolvem objetos/registos sem remover `pin` | Exposição de credenciais pela API |
| Cliente móvel | `client/mobile-app/src/components/LoginPanel.jsx`: defaults André/`1234` | Credenciais predefinidas na interface |
| Sessão cliente | `client/mobile-app/src/api/core.js`: guarda o utilizador JSON em `localStorage`; `App.jsx` restaura-o no arranque | Não existe sessão assinada/revalidada no servidor |
| Pedidos API | Helpers `get/post/put/patch/del` em `client/mobile-app/src/api/core.js` não acrescentam credencial de sessão | O cliente não está integrado com uma sessão server-side |
| Autorização de projetos | `projects.py`, `project_commercial.py`, `project_integrity.py`, `publish_readiness.py`, `publishing.py` | Regras baseadas em `user_name`/`user_role` enviados pelo cliente |
| Autorização de IP | `ip_creator.py`, `ip_branding.py`, `ip_canons.py`, `ip_characters.py`, `ip_metadata.py`, `ip_palette.py` | Identidade/função fornecidas por query, formulário ou payload |
| Superfície administrativa | `secret_control.py`, `db_control.py`, `deploy_control.py`, `website_admin.py`, `website_bundles.py`, `website_visual_sets.py`, `updater.py` | Handlers sem dependência central de sessão visível; requer auditoria de cada serviço chamado |
| Gestão de assets | `assets.py`: upload, registo, publicação, arquivo e rollback | Operações mutáveis sem dependência central de sessão visível |
| CORS e rede | `main.py` e `core/config.py` | Origem wildcard com credenciais e bind em todas as interfaces |

### Superfície de rotas

Foram identificados **75 módulos de rotas** registados por `studio_core/api/main.py`. A revisão estática cobriu os módulos de utilizadores, projetos, comercial/publicação, IP/personagens/canons/branding, assets, produção editorial, ilustração, áudio/vídeo, Website, operações locais, memória, segredos, administração e diagnóstico.

Módulos registados (inventário para a migração): `age_badges`, `assets`, `audio_cast`, `audio_cast_preview`, `audiobooks`, `branding_pack`, `commerce_groups`, `covers`, `db_control`, `deploy_control`, `distribution_hub_v6`, `diagnostics`, `editorial_engine`, `editorial_media_pipeline`, `editorial_production`, `ebooks`, `factory`, `final_media_render`, `health`, `illustration_assets`, `illustration_generation`, `illustration_pipeline`, `illustration_provider`, `illustrations`, `ip_branding`, `ip_canons`, `ip_characters`, `ip_creator`, `ip_metadata`, `ip_palette`, `jobs`, `local_ai_installer`, `local_audio_engine_manager`, `local_audio_installer`, `local_engine_manager`, `marketplace_visuals`, `pairing`, `persistent_memory`, `product_credits`, `production_pipeline`, `project_commercial`, `project_integrity`, `projects`, `public_assets`, `publication_package`, `publish_readiness`, `publishing`, `saga_loader`, `saga_runtime`, `saga_visual_sets`, `sagas`, `secret_control`, `settings`, `sponsors`, `sponsorship_scopes`, `storefront`, `story_layout`, `story_source`, `story_translation`, `system_smoke`, `system_smoke_v1`, `updater`, `v1_readiness`, `videos`, `voice_library`, `voice_preview`, `voice_profiles`, `website_admin`, `website_bundle_reconcile`, `website_bundles`, `website_contract`, `website_control`, `website_publisher`, `website_visual_set_reconcile`, `website_visual_sets`.

**Limite da auditoria:** esta é uma análise estática dos routers e dos serviços diretamente observados, não um teste dinâmico de todos os caminhos HTTP. A ausência de uma dependência de autenticação no router não prova, por si só, que nenhum serviço interno aplique uma proteção adicional. Essa verificação é uma tarefa explícita da fase seguinte.

## Arquitetura-alvo

1. **Identidade autenticada no servidor:** login valida PIN/credencial contra hash forte (Argon2id ou alternativa aprovada e suportada); o servidor emite sessão assinada, com expiração, revogação e associação ao utilizador ativo.
2. **Sem identidade declarada pelo cliente:** rotas obtêm `user_id` e `role` apenas do principal autenticado. Campos antigos `user_name`, `user_role` e `user_id` deixam de conceder permissões; durante a transição podem existir apenas para compatibilidade de leitura, nunca como autoridade.
3. **RBAC central:** matriz explícita de permissões para owner/admin, creator/editor, voice-recorder, child e viewer, com regras por recurso/projeto e testes de negação por defeito.
4. **Rotas públicas explícitas:** health/readiness e assets efetivamente publicados são allowlist. Todas as restantes rotas são privadas por defeito, incluindo gestão de segredos, ficheiros, operações locais, publicação e gestão comercial.
5. **Storage privado por defeito:** retirar a montagem da raiz de storage. Servir apenas assets publicados através de uma pasta/handler dedicado que valida estado, caminho e tipo; nunca servir `data/`, exports internos, vaults, backups, logs ou ficheiros de configuração.
6. **CORS restrito e rede local controlada:** origins exatas para desktop/móvel e Website; manter acesso LAN apenas quando necessário, com configuração explícita, sem wildcard com credenciais. Não expor o Studio doméstico diretamente à Internet.
7. **Migração compatível:** atualizar API, desktop, aplicação móvel e chamadas de sincronização Website na mesma sequência controlada. Credenciais antigas devem ser migradas/forçadas a redefinição; remover defaults de login. Não deixar um modo legado que continue a aceitar funções fornecidas pelo cliente.
8. **Auditoria e observabilidade:** registar login, falhas, expiração, revogação e ações administrativas sem escrever PINs, tokens ou segredos nos logs.

## Sequência segura de implementação

### Fase 0 — contenção e prova
- Criar ambiente de teste isolado e verificar por HTTP se `/storage/data/users.json`, `/storage/data/projects.json` e outros caminhos internos são servidos.
- Inventariar todos os usos legítimos de `/storage/*` nos clientes e separar media pública de dados privados.
- Mapear cada handler e cada serviço chamado, classificando: público, utilizador autenticado, editor, administrador, operação local.
- Identificar como o desktop autentica hoje e como a app móvel chega ao host LAN.

### Fase 1 — núcleo de autenticação
- Introduzir serviço único de credenciais, hash com salt e comparação segura.
- Definir sessão assinada/expirada/revogável e endpoint de sessão atual/logout.
- Definir migração de utilizadores existentes sem devolver hashes nem PINs.
- Remover credenciais por defeito da UI e do bootstrap; exigir configuração inicial segura.

### Fase 2 — proteção integral
- Aplicar dependências de autenticação e autorização a todas as rotas privadas.
- Remover confiança nos campos de identidade/função do cliente.
- Proteger explicitamente secret vault, DB/deploy controls, updater, assets, memória, publicação e comércio.
- Separar handlers públicos de manifests/assets aprovados.

### Fase 3 — clientes e integração
- Migrar desktop e móvel para a nova sessão, com tratamento de expiração e logout.
- Garantir que o Website continua a aceitar apenas a credencial de integração dedicada, independente da sessão de utilizador do Studio.
- Preservar sincronização outbound, versionada e auditável; não abrir o Studio à Internet.

### Fase 4 — testes obrigatórios e rollout
- 401 sem sessão, 403 por papel insuficiente, 401/403 após sessão expirada/revogada e utilizador desativado.
- Token adulterado, sessão de outro utilizador e tentativa de elevar role por query/body/form.
- CORS de origin permitido e não permitido, preflight e credenciais.
- Acesso HTTP negado a JSON interno, vaults, logs, backups e exports privados; assets publicados continuam acessíveis.
- Login/logout desktop e móvel, reconexão LAN, expiração durante uso e recuperação de sessão.
- Testes de regressão a publicação, edição, upload, produção e sincronização Website.
- Backup, migração e rollback ensaiados em dados de teste antes de qualquer migração real.

## Critério de conclusão

A migração só pode ser considerada concluída quando **todas** as rotas estiverem classificadas e protegidas, nenhum segredo/dado interno estiver acessível por HTTP público, nenhum cliente puder atribuir a si próprio um papel, e os testes positivos/negativos de desktop, móvel e Website passarem. Não declarar segurança concluída com base apenas em login funcional ou CI verde.

## Próxima frente

Começar pela prova de exposição de `/storage` em ambiente de teste e pela separação de assets públicos. Em paralelo, produzir a matriz rota → permissão → dependências de serviço. Só depois implementar a sessão central e migrar os clientes numa PR dedicada.
