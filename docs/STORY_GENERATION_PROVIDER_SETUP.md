# Story generation provider — Studio

## Purpose

The Studio story engine supports a provider-backed narrative generation path. It is intentionally disabled until an operator configures a provider. With no provider configured, the legacy deterministic template remains available only as a clearly labelled prototype; it is not represented as a finished original story.

## Environment configuration

Configure these variables in the backend runtime secret/environment manager. Never commit credentials to Git or place them in project JSON:

| Variable | Required | Meaning |
|---|---:|---|
| `BARIBUDOS_STORY_PROVIDER` | Yes | `openai` or `openai_compatible` |
| `BARIBUDOS_STORY_API_KEY` or `OPENAI_API_KEY` | Yes | Provider API credential |
| `BARIBUDOS_STORY_MODEL` | Yes | Exact model identifier enabled for the account |
| `BARIBUDOS_STORY_BASE_URL` | No | OpenAI-compatible API base; defaults to `https://api.openai.com/v1` |
| `BARIBUDOS_STORY_TIMEOUT_SECONDS` | No | Request timeout, clamped to 10–180 seconds; default 90 |
| `BARIBUDOS_STORY_RETRIES` | No | Bounded retries, clamped to 0–2; default 1 |

No provider is enabled by default and no API call is made by CI. The deployment operator must choose the provider/model and configure the secret deliberately.

## Studio entry points

- Factory capabilities expose whether provider-backed generation is configured, without exposing credentials.
- The factory accepts a creative brief when a provider is configured; otherwise it requires the existing locked text-first source.
- The production pipeline passes the creative brief, age range, protagonist and value theme into the story engine.
- The provider receives only the selected IP runtime and that IP's canons, not another IP's project context.

## Output contract

The provider must return a JSON object containing synopsis, title, target age, value theme, characters, protagonist, support character, ordered scenes, illustrated pages, raw text and final phrase. The service rejects missing required fields, missing pages/scenes, page text exceeding five non-empty lines, characters outside the loaded IP canon and values outside the approved pedagogical list.

Provider/model and token-usage metadata are attached to the generated version. A provider result is always marked `generated_needs_review`, `editorial_status=draft` and `approved=false`. A provider error fails closed; it does not silently fall back to the deterministic template.

## Editorial and media gates

Generation and production are separate stages. EPUB, audiobook, cover, miniseries and parent-guide builders are not called until every requested language variant has an explicit approval signal (`approved=true`, `editorial_status=approved` or `approval_state=approved`). Otherwise the run is `story_ready` and the generated text remains available for adult review.

Unsupported translation targets fail without writing copied source text under a different locale. Real translation/localization requires a separate provider-backed workflow and review gate.

## Operational limitations

- Provider integration is implemented, but a live provider is not configured or tested by this change.
- No final animation is implied by an MP4/animatic output.
- Human approval must be performed by an authorized Studio user; provider output can never approve itself.
- Before enabling provider calls in production, validate credentials/model access, provider data-retention terms, usage/cost limits, privacy and the Studio's private-family authorization boundary.
