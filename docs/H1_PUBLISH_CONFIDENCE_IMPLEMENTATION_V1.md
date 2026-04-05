# H1 PUBLISH CONFIDENCE IMPLEMENTATION V1

## Objective
Implement the first low-risk operational improvement block for Baribudos Studio focused on publish confidence and Website control feedback.

This block must improve operator trust without reopening architecture and without destabilizing already green paths.

---

## Scope
This implementation block covers:
- publish state model clarity
- receipt visibility after publish
- next recommended action after publish/control events
- distinction between sent / received / materialized
- operator-facing failure language
- consistent operator language across publish/control

This block does **not** cover:
- architecture redesign
- Website refactor
- new pipelines
- large backend changes
- broad dashboard redesign

---

## Implementation checklist

### H1.1 Publish state model clarity
- [ ] map current Studio/Website control evidence into canonical operator-facing states
- [ ] keep canonical state ladder explicit:
  - Pacote pronto para publicar
  - Publicação enviada
  - Website confirmou receção
  - Website materializado
  - Divergência detetada
- [ ] render one visible state block in the Website control/publish area
- [ ] show last update timestamp when available
- [ ] avoid collapsing different stages into one generic success badge

### H1.2 Receipt visibility after publish
- [ ] normalize successful publish acknowledgement into a receipt object in Studio UI state
- [ ] render a clear receipt card after successful Website acknowledgement
- [ ] show when available:
  - publication_id
  - variant_id
  - received_at
  - sync state label
  - next recommended action
- [ ] do not confuse receipt with full materialization

### H1.3 Next action after publish
- [ ] map the current publish/control state to one recommended next action
- [ ] show one visible block:
  - Próximo passo recomendado
  - Motivo
- [ ] ensure next action changes according to the actual current state
- [ ] reduce operator hesitation after publish

### H1.5 Sent vs received vs materialized distinction
- [ ] preserve the distinction between:
  - Studio sent
  - Website acknowledged receipt
  - Website materialized
- [ ] show progression without pretending later confirmation exists
- [ ] ensure materialization is only shown when control/status evidence supports it
- [ ] elevate divergence when reconcile/status proves mismatch or incomplete state

### H1.4 Failure language
- [ ] map common publish/control failures to operator-facing classes
- [ ] support at minimum:
  - Website indisponível
  - Autenticação do Website falhou
  - Publicação rejeitada pelo Website
  - Receção do Website não confirmada
  - Materialização no Website não confirmada
  - Divergência entre Studio e Website
- [ ] present operator meaning first
- [ ] keep technical detail secondary and optional

### H1.6 Operator language consistency
- [ ] use one canonical label set across state / receipt / failure / next-step blocks
- [ ] remove inconsistent wording for equivalent meanings
- [ ] keep language short, operational and trustworthy
- [ ] avoid primary backend-style labels in operator UI

---

## Main surfaces expected to change
Studio only, mainly:
- Website control area
- publish result feedback area
- control-state interpretation in Studio UI
- operator-facing labels/messages around publish/control

---

## Acceptance criteria
This H1 block is complete when:
- operator can distinguish package readiness, publish sent, Website receipt, Website materialization and divergence
- operator sees a strong receipt after Website acknowledgement
- operator sees one clear next recommended action
- operator does not confuse receipt with materialization
- failure states are explained in operator language first
- publish/control language feels coherent across the whole Studio surface

---

## Execution rule
Keep this implementation block:
- incremental
- reviewable
- low-risk
- Studio-side first
- aligned with Studio as source of truth

If a larger blocker appears, isolate it rather than expanding this block into a redesign.
