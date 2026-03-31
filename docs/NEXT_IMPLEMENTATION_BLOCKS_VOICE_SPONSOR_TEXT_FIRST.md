# Próximos blocos de implementação — text-first, vozes/créditos e patrocínios por escopo

## Objetivo
Transformar as regras já formalizadas em peças implementáveis dentro do Studio.

Este documento existe para garantir que requisitos falados noutras conversas não dependem da memória do chat e ficam presos ao repositório como próximos blocos concretos.

---

## Bloco A — produção text-first
### Objetivo
O fluxo editorial deve começar por texto e só depois entrar na fase multimédia.

### Regra operacional
1. texto é criado fora ou dentro do ecossistema de escrita
2. texto é colado/importado no Studio
3. Studio cria/atualiza projeto
4. só depois arrancam:
   - ilustração
   - capas
   - audiobook
   - vídeo/série
   - variantes comerciais

### Entidades recomendadas
- `story_source`
- `story_source_type` (`pasted_text`, `imported_text`, `external_chat_origin`)
- `story_source_notes`
- `text_locked`
- `production_started_at`

### Endpoints recomendados
- `POST /api/projects/{project_id}/story-source`
- `GET /api/projects/{project_id}/story-source`
- `POST /api/projects/{project_id}/lock-text`

---

## Bloco B — voice profiles / clones de voz
### Objetivo
Modelar vozes da família com consentimento, escopo e créditos.

### Entidade recomendada: `voice_profile`
Campos mínimos:
- `id`
- `display_name`
- `owner_person_id`
- `credited_name`
- `voice_type`
- `source_type`
- `consent_status`
- `allowed_ips`
- `allowed_sagas`
- `allowed_roles`
- `default_for_roles`
- `credit_visibility`
- `notes`
- `active`

### Endpoints recomendados
- `GET /api/voice-profiles`
- `POST /api/voice-profiles`
- `PATCH /api/voice-profiles/{voice_profile_id}`
- `POST /api/voice-profiles/{voice_profile_id}/samples`
- `POST /api/voice-profiles/{voice_profile_id}/clone-status`

### Cockpit recomendado
Painel com:
- lista de perfis vocais
- voz de quem é
- nome creditado
- escopo permitido
- estado do consentimento
- se está pronta para uso em produção

---

## Bloco C — casting vocal por projeto/saga/personagem
### Objetivo
Poder definir rapidamente quem dá voz a quê.

### Entidade recomendada: `voice_casting`
Campos mínimos:
- `id`
- `project_id`
- `ip_slug`
- `saga_slug`
- `target_type` (`narrator`, `character`, `ambient`, `promo`)
- `target_id`
- `voice_profile_id`
- `credit_override`
- `approved`

### Endpoints recomendados
- `GET /api/voice-casting/{project_id}`
- `POST /api/voice-casting/{project_id}`
- `PATCH /api/voice-casting/{project_id}/{casting_id}`

### Regra desejada
Exemplo Baribudos:
- narrador masculino = voz André
- mãe = voz esposa
- crianças = vozes aprovadas dos filhos ou perfis apropriados

---

## Bloco D — créditos finais por produto
### Objetivo
Montar créditos automaticamente sem misturar com ownership editorial.

### Entidade recomendada: `product_credits`
Campos mínimos:
- `project_id`
- `product_context`
- `created_by`
- `written_by`
- `produced_by`
- `voices_by`
- `narration_by`
- `character_voices_by`
- `sound_design_by`
- `illustrations_by`
- `editing_by`
- `special_thanks`

### Endpoints recomendados
- `GET /api/product-credits/{project_id}`
- `POST /api/product-credits/{project_id}/rebuild`
- `PATCH /api/product-credits/{project_id}`

### Regra
- ownership editorial continua separado
- créditos puxam contributors aprovados
- promos e produto final podem usar variantes dos mesmos créditos

---

## Bloco E — patrocínios por escopo
### Objetivo
Permitir patrocínio global, por IP, por saga, por produto ou por campanha.

### Entidade recomendada: `sponsorship_scope`
Campos mínimos:
- `id`
- `sponsor_id`
- `scope_type`
- `scope_target_id`
- `scope_target_slug`
- `active`
- `exclusive`
- `priority`
- `credit_text`
- `cta_text`
- `cta_url`
- `logo_asset`
- `start_at`
- `end_at`
- `placement_rules`
- `internal_notes`

### Endpoints recomendados
- `GET /api/sponsorships`
- `POST /api/sponsorships`
- `PATCH /api/sponsorships/{id}`
- `GET /api/sponsorships/resolve?project_id=...`

### Ordem de resolução
1. `product`
2. `campaign`
3. `saga`
4. `ip`
5. `studio_global`

---

## Bloco F — promo resolver
### Objetivo
Permitir que as promos puxem automaticamente:
- credits válidos
- vozes válidas
- patrocinadores válidos

### Entidade/serviço recomendado
- `promo_context_resolver`

### Output esperado
- `credits_for_promo`
- `voices_for_promo`
- `sponsors_for_promo`
- `blocked_items`

---

## Ordem recomendada de implementação
### 1
`voice_profile`

### 2
`voice_casting`

### 3
`product_credits`

### 4
`sponsorship_scope`

### 5
`promo_context_resolver`

### 6
`story_source` + lock text / text-first gates

---

## Regra final
Tudo isto deve respeitar simultaneamente:
- Studio privado da família
- ownership editorial por IP/saga
- Baribudos como IP premium exclusiva do André
- contributors e vozes sem transferência de ownership
- patrocínios por contexto sem contaminar outros universos
