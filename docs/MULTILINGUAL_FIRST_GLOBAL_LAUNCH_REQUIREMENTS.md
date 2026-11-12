# Multilingual-first production and simultaneous global launch

**Date:** 2026-11-12  
**Status:** Product requirement and acceptance specification  
**Scope:** Every IP managed by Baribudo Estúdio, including stories, books, audiobooks, miniseries, series and video distribution.

## 1. Strategic objective

Baribudo Estúdio must be designed for **multilingual production from the beginning**, with the ambition of launching each approved production across all previously selected target languages and markets in coordinated releases.

This is not a workflow where a Portuguese product is considered complete and translations are added later as optional extras. The production model must treat each target language as a first-class edition of the same underlying work.

The business objective is broad, coordinated international reach: publish to all selected language markets with consistent quality, timing, brand identity, editorial intent and discoverability.

This requirement applies to every IP, not only Baribudos.

## 2. One canonical work, multiple language editions

Each work must have a canonical source and a set of language editions connected to the same underlying work/version lineage.

The system must distinguish:
- canonical story/work and its editorial version;
- source language;
- target language edition;
- translated/adapted text and its review status;
- language-specific narration and character performances;
- localized images or text embedded in images, where required;
- audiobook edition;
- miniseries/episode edition;
- subtitles, captions, descriptions and metadata;
- publication package and release status for each market.

A language edition must retain stable references to the canonical work, IP, canon, characters, approved assets and source version. It must be possible to identify exactly which source version each translation or adaptation derives from.

Changing the canonical story must not silently overwrite already approved translations. It should mark affected editions as potentially outdated and create an explicit review/revision task.

## 3. Previously selected languages are the source of truth

The target language set must reuse the languages already defined in existing Studio configuration and documentation. This requirement does **not** authorize inventing a new language list or replacing previously approved locale choices.

Before implementation, inventory the existing language configuration and document:
- locale identifier (BCP 47 where appropriate, e.g. language plus regional variant);
- display name in the language itself;
- editorial owner/reviewer;
- spelling, punctuation and typography conventions;
- preferred regional vocabulary and accent;
- enabled/disabled status per IP and output format;
- voice/TTS provider capability and quality status;
- subtitle/caption conventions and reading-speed limits;
- publication channels and market metadata.

Do not collapse materially different locales into one generic language where regional vocabulary, pronunciation, spelling, cultural context or platform targeting matters.

The language catalogue should be centrally managed and reusable across IPs, with IP-specific glossaries, character-name rules and localization guidance.

## 4. Story creation, translation and localization

The production system must support:
1. writing or generating the canonical story;
2. editorial approval of the canonical source;
3. generating a separate edition for each enabled target locale;
4. applying the IP glossary, character canon, age group and pedagogical intent;
5. linguistic and cultural review;
6. approval and version freeze per language edition.

Translation must preserve meaning, narrative continuity, humor, emotional tone, character personality, pedagogical intent and age suitability. It must not be treated as literal word substitution.

The system should support both:
- faithful translation where the source wording and structure transfer naturally;
- controlled localization/adaptation where idioms, cultural references, rhymes, jokes or examples need an equivalent in the target market.

Every adapted passage must remain traceable to its source. Human review/approval must be available, and a generated translation must never be labelled approved solely because an AI provider returned text.

Maintain per-IP terminology, character names, pronunciation notes, recurring expressions and forbidden/inconsistent variants. Canonical character identity must not change when a character speaks another language.

## 5. Multilingual voices, clones and casting

Every target language edition must be able to generate its own narration and character dialogue.

A voice supplied by a person (the voice donor) must remain credited to that person when used in another language, including when:
- the voice is cloned from the original recording;
- a multilingual model synthesizes the person's voice in a language the person did not record;
- pronunciation, pitch, timbre, speed or other vocal properties are transformed;
- the voice is assigned to a different character or role in a localized edition.

**Language adaptation does not change voice provenance or authorship.**

Each generated performance must retain:
- original voice donor/person ID and credited name;
- original source voice profile and recording/model lineage;
- derived clone/model and variant IDs;
- target locale and accent;
- provider/model and synthesis configuration;
- character or narrator role;
- source script and localized script version;
- consent and permitted language/market/use scope;
- actual inclusion in the final edition.

The voice donor's name must appear in credits according to the approved credit-visibility policy, even if the performance is generated in a different language. Credits should distinguish voice donor/source from any separate voice actor, translator, director or adapter who contributed.

Do not assume a clone can convincingly speak every language. Before a voice/locale combination is used in a release, validate provider support, pronunciation, intelligibility, naturalness, emotional performance and consistency. If quality is insufficient, the edition must be marked blocked/needs review and the Studio should offer an authorized alternative voice or human dubbing path. Never silently substitute an unrelated voice while keeping the original donor credit.

Consent must explicitly cover cross-language synthesis and the relevant markets/channels. Existing consent for a voice in one language or IP must not automatically be interpreted as permission for every language, IP, market or commercial context. For minors, require appropriate parental/tutelar authorization and stronger controls; no child voice cloning or cross-language use is presumed permitted.

## 6. Audiobooks

For each approved language edition:
- generate or record the audiobook from that edition's approved text;
- use the selected authorized multilingual narrator and character cast;
- preserve donor attribution and per-role credits;
- validate audio integrity, duration, completeness, clipping, silence, pronunciation and language quality;
- synchronize chapter/section boundaries and metadata;
- retain the link to the exact text edition and voice assets used.

A successful provider response is not sufficient evidence of a valid audiobook. The audio artifact must pass technical and editorial validation before the edition can be marked complete.

## 7. Miniseries, series and YouTube distribution

Every miniseries/series derived from a work must support corresponding language editions. Localized video must use the approved localized script and the corresponding authorized voices, not simply reuse the source-language audio.

For each language edition, support:
- localized episode script and dialogue;
- voice casting, narration and character performances;
- timing, dubbing and audio/video synchronization;
- subtitles and closed captions, including accessibility review;
- localized title, description, tags/metadata and calls to action;
- localized end credits and sponsor disclosures;
- thumbnails and any text embedded in promotional artwork;
- age-appropriate editorial and platform-policy review.

The series/season/episode relationships must remain identical across language editions unless an explicitly approved cultural adaptation requires a documented difference. Each edition must identify its source edition and adaptation lineage.

YouTube and YouTube Kids are distribution contexts, not proof of child-safety compliance. Every video must pass the applicable platform audience designation, content, privacy, advertising and child-directed-content requirements. Do not assume that a video automatically appears in the YouTube Kids app merely because it is uploaded to YouTube or marked for children. Channel eligibility, platform decisions and applicable policies remain external constraints.

The Website must retain its own durable publication assets and language editions so that releases remain available when the private Studio is offline.

## 8. Coordinated global release management

A work may be released in multiple languages as one coordinated launch. The Studio should provide a release matrix with one row per target locale and output format, showing:
- source/canonical version;
- translation/localization status;
- text approval;
- image/artwork readiness;
- voice/cast/consent readiness;
- audiobook validation;
- episode/video validation;
- subtitles/captions;
- credits and sponsorship review;
- publication package readiness;
- scheduled/published status and channel receipts.

Support two release policies:
- **coordinated launch:** publish the selected language editions together only when all required markets/formats pass;
- **staggered launch:** release ready language editions independently when the owner explicitly chooses this strategy.

A failure in one locale must not corrupt or roll back already published editions in other locales. The owner must be able to see which markets are live, blocked, delayed or awaiting review.

All language variants must share campaign identity and release lineage while retaining locale-specific metadata, URLs, assets and analytics.

## 9. Credits and sponsorship in every language

Credits must be derived from actual contributors and assets used in each published edition. The donor of a source voice remains credited in every language where that voice lineage is used.

Localized credits must render contributor names exactly as approved. Role labels may be translated, but credited personal names must not be translated or altered without authorization.

Sponsors must be resolved using the existing Studio/IP/saga/product/campaign scopes and must be reviewed for each language and market. Sponsor copy, disclosures, logos and calls to action may require localization and legal/platform review. Sponsorship must remain visually and semantically separate from creative authorship.

## 10. Required technical model

The implementation should introduce or formalize:
- a central locale catalogue;
- canonical work/source-version records;
- localized edition records and source lineage;
- translation/localization jobs and review states;
- per-IP localization glossary and style guide;
- language-aware voice casting and consent scopes;
- voice synthesis provenance across languages;
- localized audiobook and episode artifacts;
- subtitles/captions and localized metadata;
- per-locale publication packages and channel receipts;
- coordinated/staggered release orchestration.

Use explicit per-stage states such as `pending`, `running`, `needs_review`, `blocked`, `succeeded` and `failed`. A whole production must not be marked complete while a required locale or artifact is missing under the selected release policy.

## 11. Acceptance criteria

- [ ] The Studio uses the already approved language/locale set; no new language list is invented.
- [ ] Every IP can enable or disable locales independently without hardcoded Baribudos assumptions.
- [ ] One canonical work can produce traceable localized editions.
- [ ] Source edits flag affected translations for review instead of silently overwriting them.
- [ ] Translation/localization preserves each IP's canon, pedagogical purpose and age suitability.
- [ ] Audiobooks can be produced for each enabled locale from the matching approved text.
- [ ] Voice casting can synthesize/record each locale and preserves the original donor attribution.
- [ ] Voice consent explicitly covers language, IP, market and commercial use as applicable.
- [ ] Inadequate voice/locale quality blocks release or triggers an authorized alternative; no silent substitution.
- [ ] Miniseries and series have localized scripts, audio, subtitles/captions, credits and metadata.
- [ ] Every locale edition has technical and editorial readiness checks.
- [ ] The owner can launch all selected locales together or deliberately stagger them.
- [ ] One locale's failure does not damage another locale's successful publication.
- [ ] Website editions and assets remain durable and available while the private Studio is offline.
- [ ] Credits and sponsor disclosures are correctly localized and separated.

## 12. Current evidence and implementation gap

The existing Studio documentation already establishes a text-first production flow, voice profiles with a language field, voice ownership/credits, multi-IP separation and production readiness concepts. The editorial pipeline audit dated 2026-11-12 found that the main story-generation path still uses Portuguese templates and does not perform real translation merely because a language code is supplied.

Therefore, multilingual output is a strategic requirement but **must not be represented as implemented**. The actual configured locale list still needs to be inventoried from the existing configuration before code changes. Multilingual voice synthesis, quality gates, localized video, subtitles and coordinated multi-market publication also require end-to-end verification.

This document records product requirements and acceptance criteria. It does not claim that multilingual production or global simultaneous distribution is currently operational.
