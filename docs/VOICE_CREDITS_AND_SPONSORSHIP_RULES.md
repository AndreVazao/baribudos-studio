# Regras de vozes, créditos e patrocínios por escopo

## 1. Regra editorial base
A produção editorial da IP/Saga pode ser **exclusiva de uma pessoa** e, ao mesmo tempo, incluir **contribuidores**.

Exemplo atual:
- **IP Baribudos**: produção editorial exclusiva do André
- **Saga Baribudos**: produção editorial exclusiva do André
- **Produtos Baribudos**: produção editorial exclusiva do André

Isto **não impede** que existam contribuidores em:
- vozes
- narração
- clones de voz
- ilustração
- música/sons
- revisão
- apoio técnico

### Regra correta
- **ownership editorial** != **lista de contribuidores**
- o dono editorial mantém controlo de produção e publicação
- os contribuidores podem aparecer nos créditos finais e em material promocional quando aprovado

---

## 2. Fluxo de produção pretendido
Fluxo inicial assumido para livros, séries e audiobooks:

1. André cria o **texto base** noutra conversa/fluxo de escrita
2. o texto é colado/importado para o Studio
3. o Studio entra na fase de **produção**
   - imagens
   - ilustrações
   - capas
   - variantes
   - audiobook
   - série/vídeo quando aplicável
4. o Studio usa **vozes pré-definidas** por personagem/função narrativa
5. os créditos finais são montados automaticamente com base nas contribuições registadas

### Implicação estrutural
O Studio deve suportar uma pipeline **text-first**, onde a escrita vem primeiro e a produção multimédia acontece depois.

---

## 3. Regras de vozes e voice clones
## Tipos de voz a suportar
O sistema deve distinguir entre:
- **voz base humana gravada**
- **clone de voz**
- **voz narrativa/papel**
- **voz de personagem**
- **voz ambiente/efeitos vocais**

## Campos mínimos por voz/perfil vocal
Cada perfil vocal deve poder guardar:
- `voice_profile_id`
- `display_name`
- `owner_person_id`
- `credited_name`
- `voice_type` (`narrator`, `character`, `ambient`, `promo`, `system`)
- `source_type` (`recorded_human`, `cloned_voice`, `synthetic_hybrid`)
- `allowed_ips`
- `allowed_sagas`
- `allowed_roles`
- `consent_status`
- `credit_visibility`
- `notes`

## Regras de uso
- vozes da família só podem ser usadas se estiverem **marcadas como autorizadas**
- cada voz pode ser:
  - global no Studio
  - limitada a uma IP
  - limitada a uma saga
  - limitada a um conjunto de personagens/funções
- uma voz pode ser a **voz-padrão de um papel**

### Exemplo atual desejado
- voz do André = pai / narrador masculino / eventualmente outras funções aprovadas
- voz da esposa = mãe / narradora feminina / eventualmente outras funções aprovadas
- vozes dos filhos = personagens infantis / participações / promos aprovadas

---

## 4. Créditos finais e contribuições
## Regra de créditos
Os créditos devem ser independentes da propriedade editorial.

Ou seja:
- André continua dono editorial de Baribudos
- mas os créditos podem listar quem contribuiu

## Estrutura de créditos recomendada
Cada produto/publicação deve conseguir guardar blocos como:
- `created_by`
- `written_by`
- `produced_by`
- `voices_by`
- `narration_by`
- `character_voices_by`
- `sound_design_by`
- `music_by`
- `illustrations_by`
- `editing_by`
- `special_thanks`

## Regra de visibilidade
Cada crédito deve poder ser marcado como:
- `internal_only`
- `show_on_product`
- `show_on_website`
- `show_on_promo`

## Regra para Baribudos
Mesmo sendo exclusivo teu em produção editorial:
- os créditos de voz/narração/contribuição **podem e devem aparecer** quando tu aprovares
- isso não transfere ownership editorial

---

## 5. Regras de patrocínio
Patrocínios não devem ser tratados como um bloco único global.

## Escopos de patrocínio recomendados
Cada patrocínio deve ter um `scope_type` claro:

- `studio_global`
  - aparece no Studio inteiro / em promoções globais
- `ip`
  - aparece apenas numa IP específica
- `saga`
  - aparece apenas numa saga específica
- `product`
  - aparece apenas num produto/publicação específica
- `campaign`
  - aparece apenas numa campanha específica

## Campos mínimos por patrocínio
- `sponsor_id`
- `name`
- `scope_type`
- `scope_target_id`
- `scope_target_slug`
- `active`
- `start_at`
- `end_at`
- `credit_text`
- `logo_asset`
- `cta_text`
- `cta_url`
- `placement_rules`
- `exclusive`
- `priority`
- `internal_notes`

## Regras práticas de patrocínio
### Studio global
Usar só para:
- promoções gerais do Studio
- branding institucional
- parceiros permanentes da casa

### Por IP
Usar quando um patrocinador apoia um universo inteiro.
Exemplo:
- um patrocinador ligado a uma linha educativa específica

### Por saga
Usar quando o patrocínio é de uma saga concreta dentro de uma IP.
Exemplo:
- patrocínio só da Saga Baribudos
- sem contaminar outras sagas ou IPs

### Por produto
Usar quando:
- é uma edição concreta
- um audiobook concreto
- um volume específico
- uma série/vídeo específico

### Por campanha
Usar quando:
- a promoção é temporária
- Black Friday, lançamento, campanha sazonal, etc.

---

## 6. Regras de conflitos de patrocínio
Quando houver mais do que um patrocínio possível, aplicar esta ordem:

1. `product`
2. `campaign`
3. `saga`
4. `ip`
5. `studio_global`

### Regra de exclusividade
Se `exclusive = true`, o patrocinador bloqueia os patrocinadores de escopo mais amplo no mesmo contexto.

Exemplo:
- um patrocinador exclusivo da Saga Baribudos deve bloquear a exibição de um patrocinador global do Studio dentro de assets dessa saga, se essa for a política definida

---

## 7. Regra de promoções e créditos promocionais
As promoções devem conseguir puxar automaticamente:
- créditos de vozes
- contributors aprovados
- patrocinadores válidos para aquele escopo

### Exemplo desejado
Na promo de um audiobook Baribudos pode aparecer algo como:
- Vozes por: André Vazão, [Nome da esposa], [nomes aprovados]
- Narração por: André Vazão
- Com o apoio de: [patrocinador da saga ou do produto]

---

## 8. Regra de implementação prioritária
Na prática, o melhor é modelar isto em 3 camadas separadas:

### A. Ownership editorial
Quem manda editorialmente em:
- IP
- saga
- produto

### B. Contributors / credits
Quem contribuiu em:
- voz
- arte
- edição
- som
- apoio

### C. Sponsorship scope
Que patrocinador aparece em:
- Studio
- IP
- saga
- produto
- campanha

Estas 3 camadas **não devem ficar misturadas**.

---

## 9. Regra final para o caso Baribudos
Fica assim:

- Baribudos continua exclusivo de produção editorial do André
- pode ter contribuidores de voz e outros créditos
- pode usar vozes da família com consentimento e escopo definidos
- pode ter patrocinadores próprios da saga ou dos produtos Baribudos
- esses patrocinadores **não devem contaminar automaticamente** outras IPs ou sagas

---

## 10. Decisão recomendada
As melhores regras para deixar isto certo são:

1. **separar ownership editorial de contributors**
2. **separar contributors de perfis vocais**
3. **separar patrocínios por escopo**
4. **fazer promos e créditos puxarem dados por contexto**
5. **não tratar Baribudos como exceção técnica, só como IP premium exclusiva**

Isto permite:
- proteger a tua IP Baribudos
- creditar a tua família quando participa
- usar voice clones de forma organizada
- suportar novas IPs/sagas no futuro
- vender/patrocinar sem misturar universos
