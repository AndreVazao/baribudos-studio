# H1 PANEL INTEGRATION FINAL STEP

## Objective
Close the first visible H1 slice by wiring the new publish-confidence components into the existing `WebsiteControlPanel.jsx`.

This is the final low-risk UI integration step that remains after the new helper and card were already added to the branch.

---

## Already implemented in branch
The following pieces already exist in the integration branch:
- `client/mobile-app/src/utils/websitePublishUiState.js`
- `client/mobile-app/src/components/WebsitePublishConfidenceCard.jsx`

These already cover:
- publish state interpretation
- receipt interpretation
- next recommended action
- sent vs received vs materialized distinction
- operator-facing failure mapping

---

## Remaining direct code step
Update:
- `client/mobile-app/src/components/WebsiteControlPanel.jsx`

### 1. Add import
```js
import WebsitePublishConfidenceCard from "./WebsitePublishConfidenceCard.jsx"
```

### 2. Render the card in the publish section
Recommended location:
- inside `Publicar e sincronizar Website`
- after the publication policy block
- before the action buttons

Suggested insertion:
```jsx
<WebsitePublishConfidenceCard
  selectedProject={selectedProject}
  publishStatus={publishStatus}
  publicationDetail={publicationDetail}
  divergence={divergence}
  lastError={lastError}
/>
```

### 3. Keep safe compatibility during first pass
Do not delete major existing blocks immediately unless visual duplication becomes excessive.

The first safe pass should:
- integrate the new card
- keep legacy data blocks available
- validate the new operator-facing layer visually

### 4. Simplify only after validation
After confirming the new card behaves correctly, simplify or reduce duplicated legacy messaging in:
- generic top-level Website error banner
- repetitive status explanation in current sync block
- scattered operator meaning across publish/divergence/publication detail areas

---

## Expected visible result
After this integration step, the Studio should visibly gain:
- canonical publish state ladder
- stronger receipt visibility
- recommended next action
- clearer distinction between sent / received / materialized
- clearer operator-facing failure language

---

## Acceptance criteria for this final H1 wiring step
- new publish-confidence card is visible in the Website publish/control section
- state ladder is visible to operator
- receipt is visible when Website acknowledgement exists
- next recommended action is visible
- receipt is not confused with materialization
- failure language is more operator-friendly than before
- no backend/API changes are required for this step

---

## Scope rule
This step must remain:
- UI-only
- low-risk
- Studio-side only
- compatible with green paths

Do not expand this final wiring step into a redesign of the Website control area.
