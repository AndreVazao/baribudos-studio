# Voice Profile — especificação implementável

## Objetivo
Criar a primeira camada técnica real para gerir:
- vozes da família
- clones de voz
- créditos de voz
- escopos de uso por IP/saga/papel
- consentimento

Esta camada é a base para:
- audiobook
- narração
- personagens
- promos
- créditos finais

---

## 1. Entidade principal: `voice_profile`
## Campos mínimos recomendados
- `id`
- `display_name`
- `owner_person_id`
- `owner_person_name`
- `credited_name`
- `voice_type`
- `source_type`
- `clone_provider`
- `language`
- `accent`
- `gender_hint`
- `age_hint`
- `consent_status`
- `credit_visibility`
- `allowed_ips`
- `allowed_sagas`
- `allowed_roles`
- `default_for_roles`
- `sample_audio_paths`
- `reference_text`
- `notes`
- `active`
- `created_at`
- `updated_at`

## Enumerações recomendadas
### `voice_type`
- `narrator`
- `character`
- `ambient`
- `promo`
- `system`

### `source_type`
- `recorded_human`
- `cloned_voice`
- `synthetic_hybrid`

### `consent_status`
- `pending`
- `approved`
- `restricted`
- `revoked`

### `credit_visibility`
- `internal_only`
- `product_only`
- `product_and_website`
- `all_promotional`

---

## 2. Regras de negócio
## Regra 1 — consentimento obrigatório
Nenhum perfil vocal da família deve ser usado se:
- `consent_status != approved`

## Regra 2 — escopo obrigatório
Cada voz deve poder ficar:
- global no Studio
- limitada a certas IPs
- limitada a certas sagas
- limitada a certos papéis/personagens

## Regra 3 — ownership editorial separado
A voz pode ser de outra pessoa,
mas isso não muda a propriedade editorial do produto/IP/saga.

## Regra 4 — créditos independentes
`credited_name` e `credit_visibility` decidem como essa voz aparece nos créditos,
não o ownership do produto.

---

## 3. Armazenamento recomendado inicial
### Ficheiro JSON inicial
- `data/voice_profiles.json`

### Estrutura esperada
```json
[
  {
    "id": "voice-andre-narrator",
    "display_name": "André Narrador",
    "owner_person_id": "andre-vazao",
    "owner_person_name": "André Vazão",
    "credited_name": "André Vazão",
    "voice_type": "narrator",
    "source_type": "cloned_voice",
    "clone_provider": "xtts",
    "language": "pt-PT",
    "accent": "pt-PT",
    "gender_hint": "male",
    "age_hint": "adult",
    "consent_status": "approved",
    "credit_visibility": "product_and_website",
    "allowed_ips": ["baribudos"],
    "allowed_sagas": ["baribudos"],
    "allowed_roles": ["narrator", "father"],
    "default_for_roles": ["narrator"],
    "sample_audio_paths": [],
    "reference_text": "",
    "notes": "Voz principal do pai/narrador para Baribudos.",
    "active": true
  }
]
```

---

## 4. Endpoints mínimos recomendados
### Listar perfis vocais
- `GET /api/voice-profiles`

### Criar perfil vocal
- `POST /api/voice-profiles`

### Atualizar perfil vocal
- `PATCH /api/voice-profiles/{voice_profile_id}`

### Ativar/desativar perfil vocal
- `PATCH /api/voice-profiles/{voice_profile_id}/status`

### Validar uso de um perfil vocal num contexto
- `GET /api/voice-profiles/{voice_profile_id}/validate?ip_slug=...&saga_slug=...&role=...`

---

## 5. Painel recomendado no cockpit
### Painel: `VoiceProfilesPanel`
Deve mostrar:
- nome do perfil
- nome creditado
- dono da voz
- tipo de voz
- provider de clone
- consentimento
- visibilidade de créditos
- IPs/sagas permitidas
- roles permitidos
- ativo / inativo

### Ações mínimas
- criar perfil
- editar perfil
- definir escopo
- ativar/desativar
- ver se está pronto para produção

---

## 6. Regras iniciais para a família
### André
Perfis iniciais possíveis:
- narrador
- pai
- promo masculina

### esposa
Perfis iniciais possíveis:
- mãe
- narradora feminina
- promo feminina

### filhos
Perfis iniciais possíveis:
- criança 1
- criança 2
- criança 3
- participações promocionais aprovadas

---

## 7. Integração futura
Depois de `voice_profile`, a sequência natural é:

1. `voice_casting`
2. `product_credits`
3. `audio_cast` usar `voice_profile` em vez de depender só de `voice_sample`
4. `promo_context_resolver`

---

## 8. Regra final
A implementação real deve assegurar simultaneamente:
- Studio privado da família
- Baribudos exclusivo do André editorialmente
- vozes da família com consentimento e créditos
- escopos por IP/saga/papel
- automação forte sem perder controlo humano
