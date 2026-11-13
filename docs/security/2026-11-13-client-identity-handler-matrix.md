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
