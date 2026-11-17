# Studio — registo de política-alvo para rotas FastAPI

**Snapshot:** `main` em `0bf7157cf9c976ed84acb53a965051f944f06f35` (16-11-2026).  
**Evidência CI:** [Studio CI #506](https://github.com/AndreVazao/baribudos-studio/actions/runs/43858283148); [artefacto de inventário](https://github.com/AndreVazao/baribudos-studio/actions/runs/43858283148/artifacts/14222401162).  
**Estado:** proposta conservadora de política; não altera runtime e não comprova proteção efetiva.

## Evidência runtime observada

- 219 `APIRoute` registadas e 0 duplicados por método/path.
- 0 dependências globais e 0 middleware de autenticação/autorização. A única middleware observada é CORS.
- CORS permite origins/métodos/headers `*` com `allow_credentials=true`.
- 219/219 rotas permanecem `UNCLASSIFIED`; principal/permissão vazios e `runtime_protection_verified=false`.
- `DENY_BY_DEFAULT` no manifesto é apenas a política-alvo do exportador, não uma proteção aplicada.
- 6 superfícies não-API: `/docs`, `/docs/oauth2-redirect`, `/openapi.json`, `/redoc`, `/public`, `/storage`.
- `/public` e `/storage` são `StaticFiles` mounts sem autorização verificada. `/storage` monta a raiz privada se existir; `/public` exige allowlist de assets aprovados.
- Inventário AST complementar: 233 handlers/78 módulos; 29 referenciam identidade do cliente; 97 sinalizados sensíveis/operacionais. É heurístico, não prova de exposição.

## Regra transversal

- Única rota API pública proposta: `GET /api/health`, apenas liveness/readiness minimizada.
- Única rota API anónima proposta: `POST /api/users/login`, com rate limit, resposta genérica e sem devolver registo completo/hash.
- Todas as restantes 217 rotas API são privadas; GET não significa público.
- Identidade, role, owner, membership e permissões são resolvidos no servidor. Campos do cliente nunca concedem acesso.
- Publicação exige aprovação/readiness, permissão específica e scope; Website Publisher é ação privilegiada Studio→Website.
- Crianças só podem usar endpoints de intenção/voz supervisionados; não têm permissões de gestão, preço, publicação, segredos ou operações. Nenhuma rota infantil específica foi identificada neste snapshot.

## Classificação por tag FastAPI

As contagens abaixo cobrem todas as 219 rotas registadas. O método/path define `read` versus mutação e as exceções indicadas na regra transversal. Permissões são nomes-alvo propostos; não estão implementadas.

| Tag | Rotas | Política-alvo / principal / permissão |
|---|---:|---|
| `age-badges` | 1 | authenticated · editorial.generate; projeto resolvido no servidor |
| `assets` | 7 | authenticated · assets.read/upload/publish; scope do asset + projeto/IP |
| `audio-cast` | 2 | authenticated · media.read/edit; projeto |
| `audio-cast-preview` | 1 | authenticated · media.preview; projeto e consentimento |
| `audiobooks` | 1 | authenticated · media.export; projeto |
| `branding-pack` | 2 | authenticated · catalog.preview.read; superfície interna, não pública |
| `covers` | 1 | authenticated · media.cover.build; projeto |
| `db-control` | 2 | owner · ops.database.read |
| `deploy-control` | 2 | owner · ops.deploy.read |
| `diagnostics` | 1 | owner · ops.diagnostics.read |
| `distribution-hub` | 3 | authenticated · distribution.read/manage; projeto/canal obrigatórios |
| `ebooks` | 1 | authenticated · media.export; projeto |
| `editorial-engine` | 5 | authenticated · editorial.read/edit; projeto |
| `editorial-media` | 2 | authenticated · media.generate; projeto |
| `editorial-production` | 3 | authenticated · editorial.generate; projeto |
| `factory` | 2 | authenticated · production.execute; projeto |
| `final-media` | 2 | authenticated · media.export/render; projeto |
| `illustration-assets` | 2 | authenticated · media.read/upload; projeto |
| `illustration-generation` | 5 | authenticated · media.generate/manage; projeto/job |
| `illustration-pipeline` | 4 | authenticated · media.read/edit; projeto |
| `illustration-provider` | 1 | authenticated · media.generate; projeto |
| `illustrations` | 1 | authenticated · media.upload; projeto |
| `ip-branding` | 3 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `ip-canons` | 2 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `ip-characters` | 4 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `ip-creator` | 9 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `ip-metadata` | 2 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `ip-palette` | 2 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `jobs` | 2 | authenticated · jobs.read/execute; actor e projeto resolvidos no servidor |
| `local-ai` | 3 | owner · device.engines.manage |
| `local-audio` | 3 | owner · device.engines.manage |
| `local-audio-engine-manager` | 4 | owner · device.engines.manage |
| `local-engine-manager` | 4 | owner · device.engines.manage |
| `marketplace-visuals` | 4 | authenticated · catalog.preview.read; superfície interna, não pública |
| `pairing` | 4 | owner · device.pairing.manage |
| `persistent-memory` | 10 | authenticated owner/member · memory.read/write, scope privado |
| `product-credits` | 3 | authenticated · credits.read/edit; projeto e consentimentos |
| `production-pipeline` | 2 | authenticated · production.read/execute; projeto |
| `project-commercial` | 2 | owner/commercial-admin · commercial.read/manage; projeto |
| `project-integrity` | 2 | authenticated · projects.integrity.read/repair; projeto |
| `projects` | 3 | authenticated · projects.read/create/edit; membership por ID |
| `publication-package` | 3 | authenticated · publication.read/freeze; projeto obrigatório |
| `publish-readiness` | 4 | authenticated · publication.read/review; projeto obrigatório |
| `publishing` | 2 | authenticated · publication.read/publish; aprovação e projeto obrigatórios |
| `saga-loader` | 5 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `saga-runtime` | 1 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `saga-visual-sets` | 3 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `sagas` | 3 | authenticated · ip.read/manage; membership por ID/slug validado no servidor |
| `secret-control` | 6 | owner · secrets.read/manage/export |
| `settings` | 2 | owner · settings.read/manage |
| `sponsors` | 2 | owner/commercial-admin · sponsors.read/manage |
| `sponsorship-scopes` | 4 | owner/commercial-admin · sponsorship.read/manage; âmbito IP/saga/produto |
| `storefront` | 4 | authenticated · catalog.preview.read; superfície interna, não pública |
| `story-layout` | 9 | authenticated · editorial.read/edit; projeto |
| `story-source` | 4 | authenticated · editorial.read/edit/lock; projeto |
| `story-translation` | 2 | authenticated · editorial.translation.read/generate; projeto |
| `system-smoke` | 2 | owner/operator · ops.smoke.read/execute |
| `system-smoke-v1` | 1 | owner/operator · ops.smoke.read |
| `untagged` | 1 | PUBLIC_LIVENESS · anonymous · health.readiness (única exceção GET /api/health) |
| `updater` | 3 | owner · device.updates.manage |
| `users` | 5 | owner · users.manage (exceto login) |
| `v1-readiness` | 1 | authenticated · publication.readiness.read; projeto |
| `videos` | 1 | authenticated · media.export; projeto |
| `voice-library` | 3 | authenticated · voice.read/record/manage; IP/projeto + lineage/consentimento |
| `voice-preview` | 1 | authenticated · voice.read/record/manage; IP/projeto + lineage/consentimento |
| `voice-profiles` | 4 | authenticated · voice.read/record/manage; IP/projeto + lineage/consentimento |
| `website-admin` | 2 | owner/commercial-admin · commercial.manage; produto |
| `website-bundles` | 2 | authenticated · publication.read/publish; grupo/edição obrigatórios |
| `website-bundles-reconcile` | 1 | owner/operator · ops.reconcile.read |
| `website-contract` | 2 | authenticated · website.contract.read; interno |
| `website-control` | 6 | owner/operator · website.ops.read |
| `website-publisher` | 5 | authenticated · publication.read/publish/unpublish; projeto obrigatório |
| `website-visual-sets` | 5 | authenticated · publication.read/publish; IP/edição obrigatórios |
| `website-visual-sets-reconcile` | 1 | owner/operator · ops.reconcile.read |

## Handlers AST não registados no snapshot ASGI

Estes 14 handlers não aparecem nas 219 rotas ativas. Confirmar se são código legado, routers deliberadamente desativados ou omissões de registo antes de os remover/reativar.

| Método | Path | Handler | Módulo | Linha |
|---|---|---|---|---:|
| GET | `/commerce-groups` | `commerce_groups_list` | `commerce_groups.py` | 52 |
| POST | `/commerce-groups` | `commerce_groups_create` | `commerce_groups.py` | 57 |
| PATCH | `/commerce-groups/{group_id}` | `commerce_groups_patch` | `commerce_groups.py` | 68 |
| DELETE | `/commerce-groups/{group_id}` | `commerce_groups_delete` | `commerce_groups.py` | 79 |
| GET | `/distribution/projects/{project_id}/channels` | `list_distribution_channels` | `distribution_hub.py` | 116 |
| GET | `/distribution/projects/{project_id}/channels/{channel_id}` | `get_distribution_channel` | `distribution_hub.py` | 137 |
| PATCH | `/distribution/projects/{project_id}/channels/{channel_id}` | `patch_distribution_channel` | `distribution_hub.py` | 151 |
| POST | `/distribution/projects/{project_id}/channels/{channel_id}/attempts` | `record_distribution_attempt` | `distribution_hub.py` | 188 |
| POST | `/distribution/projects/{project_id}/channels/{channel_id}/publish-success` | `mark_distribution_publish_success` | `distribution_hub.py` | 219 |
| POST | `/distribution/projects/{project_id}/channels/{channel_id}/publish-failed` | `mark_distribution_publish_failed` | `distribution_hub.py` | 251 |
| GET | `/public/ip/{ip_slug}/assets` | `ip_assets` | `public_assets.py` | 19 |
| GET | `/public/assets` | `assets_by_context` | `public_assets.py` | 28 |
| GET | `/public/project/{project_id}/assets` | `project_assets` | `public_assets.py` | 43 |
| GET | `/public/raw` | `raw_assets` | `public_assets.py` | 52 |

## Limites e trabalho restante

- A matriz por tag não substitui o rastreio handler→serviço→persistência/side effect. Esse rastreio continua pendente para os 219 handlers; não foi inferido a partir do nome da rota.
- Rever e aprovar cada permissão/scope com base no código e no modelo de dados; transformar esta proposta num manifesto testável contra OpenAPI.
- Testar 401/403, utilizador inativo, sessão expirada/revogada, token adulterado, role forgery, isolamento de projeto/IP, uploads/downloads, CORS e storage.
- Migrar primeiro desktop/mobile e contratos de media; só depois remover `/storage`. Não ativar middleware global antes da migração coordenada.
- Restringir `/docs` e `/openapi.json` em produção e rever a necessidade de `/redoc`.

**Conclusão:** o snapshot permite classificar provisoriamente todas as rotas ativas por domínio e identificar 14 handlers não registados. O P0 continua aberto: não há autenticação central, RBAC nem proteção de storage verificados. Nenhuma alteração a runtime, CORS, dados, credenciais, storage ou infraestrutura foi feita.
