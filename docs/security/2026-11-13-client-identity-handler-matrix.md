# Studio — matriz de handlers com identidade fornecida pelo cliente

**Base:** `main` em `517e4d6b552b41eeceb9b743ef1952152caa86ed` (13-11-2026).
**Fonte:** artefacto `studio-route-authorization-inventory` do workflow Studio CI, commit `dc4a0bfadb4c553bc5f45eb12471e7d87787f11e`.
**Estado:** inventário estático inicial; nenhuma das entradas abaixo está ainda aprovada como segura. A presença dos parâmetros não prova que concedem permissões; a revisão deve seguir o fluxo até ao serviço e verificar a origem real da autorização.

## Resumo

- 29 handlers referenciam parâmetros/atributos `user_id`, `user_name` ou `user_role`.
- O analisador é heurístico e não resolve dependências transitivas, middleware, closures nem verificações em serviços.
- Estado de revisão nesta matriz: **pendente** para todos os handlers; não usar este documento como autorização para ativar ou remover controlos.

## Ordem de revisão

1. **P0 imediato:** `users.py`, `projects.py`, `publishing.py`, `publication_package.py`, `publish_readiness.py`, `project_commercial.py`, `project_integrity.py`.
2. **P0 operacional/distribuição:** `distribution_hub.py`, `distribution_hub_v6.py`, `saga_loader.py`.
3. **P1 — IP/canon:** `ip_creator.py`, `ip_branding.py`, `ip_canons.py`, `ip_characters.py`, `ip_metadata.py`, `ip_palette.py`.
4. Para cada handler: seguir chamadas locais/importadas, identificar leituras/escritas/efeitos externos, definir principal server-side e permissão, criar testes 401/403 e tentativa de falsificação.

## Matriz de handlers

| Módulo:linha | Método e rota | Handler | Campos cliente | Revisão |
|---|---|---|---|---|
| `distribution_hub.py:151` | `PATCH /projects/{project_id}/channels/{channel_id}` | `patch_distribution_channel` | `user_name, user_role` | Pendente |
| `distribution_hub.py:188` | `POST /projects/{project_id}/channels/{channel_id}/attempts` | `record_distribution_attempt` | `user_name, user_role` | Pendente |
| `distribution_hub.py:219` | `POST /projects/{project_id}/channels/{channel_id}/publish-success` | `mark_distribution_publish_success` | `user_name, user_role` | Pendente |
| `distribution_hub.py:251` | `POST /projects/{project_id}/channels/{channel_id}/publish-failed` | `mark_distribution_publish_failed` | `user_name, user_role` | Pendente |
| `distribution_hub_v6.py:39` | `POST /{project_id}/refresh` | `refresh_distribution_hub_endpoint` | `user_name, user_role` | Pendente |
| `distribution_hub_v6.py:56` | `PATCH /{project_id}` | `patch_distribution_hub_endpoint` | `user_name, user_role` | Pendente |
| `ip_branding.py:37` | `GET /{slug}` | `get_ip_branding` | `user_id, user_name, user_role` | Pendente |
| `ip_branding.py:85` | `POST /{slug}/upload` | `upload_ip_brand_asset` | `user_id, user_name, user_role` | Pendente |
| `ip_canons.py:41` | `GET /{slug}/{canon_type}` | `get_ip_canon` | `user_id, user_name, user_role` | Pendente |
| `ip_characters.py:101` | `GET /{slug}` | `get_characters` | `user_id, user_name, user_role` | Pendente |
| `ip_characters.py:118` | `GET /{slug}/consistency-summary` | `get_characters_consistency_summary` | `user_id, user_name, user_role` | Pendente |
| `ip_characters.py:131` | `GET /{slug}/character-lock-status` | `get_character_lock_status` | `user_id, user_name, user_role` | Pendente |
| `ip_creator.py:41` | `GET (raiz do router)` | `ips` | `user_id, user_name, user_role` | Pendente |
| `ip_creator.py:53` | `GET /{slug}` | `ip_by_slug` | `user_id, user_name, user_role` | Pendente |
| `ip_creator.py:103` | `GET /{slug}/permissions` | `ip_permissions` | `user_id, user_name, user_role` | Pendente |
| `ip_metadata.py:20` | `GET /{slug}` | `get_metadata` | `user_id, user_name, user_role` | Pendente |
| `ip_palette.py:20` | `GET /{slug}` | `get_palette` | `user_id, user_name, user_role` | Pendente |
| `project_commercial.py:51` | `PATCH /{project_id}` | `patch_project_commercial` | `user_name, user_role` | Pendente |
| `project_integrity.py:43` | `POST /{project_id}/repair` | `repair_project` | `user_name, user_role` | Pendente |
| `projects.py:55` | `GET (raiz do router)` | `list_projects` | `user_id, user_name, user_role` | Pendente |
| `projects.py:121` | `PATCH /{project_id}` | `patch_project` | `user_name, user_role` | Pendente |
| `publication_package.py:66` | `POST /{project_id}/freeze` | `freeze_publication_package` | `user_name, user_role` | Pendente |
| `publish_readiness.py:162` | `POST /{project_id}/sync` | `sync_publish_readiness` | `user_name, user_role` | Pendente |
| `publish_readiness.py:183` | `POST /{project_id}/mark-ready` | `mark_ready` | `user_name, user_role` | Pendente |
| `publish_readiness.py:234` | `POST /{project_id}/unmark-ready` | `unmark_ready` | `user_name, user_role` | Pendente |
| `publishing.py:42` | `POST /publish` | `publish_project` | `user_name, user_role` | Pendente |
| `saga_loader.py:44` | `GET /{saga_id}/can-edit/{user_role}` | `can_edit_saga` | `user_role` | Pendente |
| `users.py:52` | `PATCH /{user_id}` | `patch_user` | `user_id` | Pendente |
| `users.py:81` | `PATCH /{user_id}/pin` | `patch_user_pin` | `user_id` | Pendente |

## Evidência exigida para fechar cada linha

- [ ] Dependências FastAPI efetivas identificadas (handler, router e aplicação).
- [ ] Serviços chamados e funções transitivas relevantes identificados.
- [ ] Dados lidos/escritos e side effects classificados.
- [ ] Papel/identidade do cliente não é usado como prova de autorização.
- [ ] Principal obtido exclusivamente de sessão/credencial validada no servidor.
- [ ] Permissão e âmbito (projeto/IP/recurso) documentados.
- [ ] Testes anónimos, papel insuficiente, identidade falsificada e utilizador desativado passam.

## Limite e próxima etapa

Esta matriz é uma lista de trabalho derivada do inventário CI, não a revisão manual concluída pedida na issue #43. O passo seguinte é seguir os handlers P0 e atualizar cada linha com referências concretas a serviços e testes. A migração de sessão/RBAC deve esperar pela conclusão dessa análise e pelo plano de compatibilidade desktop/mobile.


## Primeira revisão manual — superfícies P0

Revisão estática dos sete módulos prioritários em `main` (13-11-2026). Esta secção regista apenas comportamento diretamente visível nos handlers e helpers locais; ainda não substitui testes HTTP nem o rastreio completo de serviços.

| Módulo | Evidência observada | Conclusão estática |
|---|---|---|
| `users.py` | `GET /users`, `POST /users`, `PATCH /users/{user_id}`, `PATCH /users/{user_id}/pin` não recebem principal nem dependência de autorização. Login compara PIN em texto simples e devolve o registo completo do utilizador. | **P0 confirmado no código da rota:** gestão de utilizadores e PIN sem gate de autorização visível; exposição de registo e credencial na resposta. |
| `projects.py` | `GET /projects` usa `user_id`/`user_name` do pedido para filtrar visibilidade. `PATCH /projects/{project_id}` chama `_can_edit_or_publish(user_role, user_name)`; o helper aceita roles declaradas `owner/creator/admin` ou nomes fixos. | **P0 confirmado no código da rota:** autorização/visibilidade baseada em valores fornecidos pelo cliente. `POST /projects` também aceita `created_by` e `created_by_name` do payload. |
| `publishing.py` | `POST /publishing/publish` autoriza com `user_role`/`user_name` do pedido; `requested_by` pode ser fornecido no payload. | **P0 confirmado no código da rota:** a decisão local de publicar é forjável pelo cliente. |
| `publication_package.py` | `POST /publication-package/{project_id}/freeze` chama helper local que aceita `owner/creator/admin` ou nomes fixos vindos dos parâmetros; encaminha os mesmos valores ao serviço de freeze. | **P0 confirmado no gate da rota:** identidade/função do cliente controla o freeze; falta rastrear as verificações internas do serviço, sem assumir que são seguras. |
| `publish_readiness.py` | `POST sync`, `mark-ready` e `unmark-ready` usam helper local baseado em `user_role`/`user_name` do pedido. | **P0 confirmado no gate da rota:** cliente pode declarar role/nome aceite pelo helper para alterar estado de prontidão. |
| `project_commercial.py` | `PATCH /{project_id}` autoriza por `user_role`/`user_name` fornecidos pelo pedido; roles `owner/creator/admin` ou nomes `andre/andré/esposa`. | **P0 confirmado no gate da rota:** alterações comerciais aceitam identidade declarada pelo cliente. |
| `project_integrity.py` | `POST /{project_id}/repair` usa o mesmo padrão de autorização por role/nome do pedido antes de alterar o projeto. | **P0 confirmado no gate da rota:** operação de reparação aceita identidade declarada pelo cliente. |

### Decisão técnica

- Não corrigir estes módulos individualmente com comparações adicionais dos mesmos campos: isso preservaria a falsificação.
- O principal autenticado tem de ser derivado de sessão/credencial verificada no servidor e injetado por dependência central.
- Rotas de leitura que hoje aceitam acesso sem principal (por exemplo, listagens de publicação, pacote, prontidão e integridade) também precisam de classificação explícita: público, familiar autenticado ou editorial/admin. Não as tornar públicas por omissão.
- `requested_by`, `created_by` e `created_by_name` devem ser atribuídos pelo servidor após autenticação, não usados como prova de identidade quando enviados pelo cliente.
- Antes da implementação: mapear dependências do serviço `freeze_publication_package_operationally`, `publish_package`, `validate_project_publishability`, `sync_ready_for_publish_with_readiness`, `repair_project_structure` e helpers de storage; depois escrever testes HTTP negativos e de regressão.

### Estado desta revisão

- [x] Inspeção estática dos sete módulos P0 acima.
- [ ] Inspeção transitiva dos serviços e middleware da aplicação.
- [ ] Testes HTTP 401/403 e falsificação de identidade.
- [ ] Plano de migração de sessão/RBAC e compatibilidade desktop/mobile.
- [ ] Prova dinâmica de que ficheiros internos não são servidos por HTTP.
