# registry-facts — verification report

Date: 2026-10-02 · Author: AmirDiaz · Tool: `registry_facts.py` v1.0.0

## Claim

The current release of an open registry can be rendered as dated, citable facts —
each sentence carrying dataset URL, release digest, and retrieval date — with a
zero-dependency CLI, in formats ready to paste into live threads.

## Method

Fetch the three Sourcey public JSON datasets, look up entities by slug/name (or
search across them), then render each record through a provenance template:
`(what) — (summary). Listed in (registry) (release digest; retrieved date).
Registry: URL`. Digests are shortened to 12 hex chars for readability; `releases`
shows each dataset's full release id.

## Results (all executed live, 2026-10-02 UTC)

| # | Command | Expected | Observed | Pass |
|---|---------|----------|----------|------|
| 1 | `company devin` | table with name/slug/summary/entity/release | all fields rendered, release `8094c042ec14` | ✅ |
| 2 | `readiness cloudflare --format reddit` | per-product grades | Developer Platform **C+**, 1.1.1.1 Public DNS **A+**, both with release + date | ✅ |
| 3 | `search AI --format reddit --limit 2` | mixed company+readiness facts | CollieAi, ActiveCampaign, OpenAI API (B), Resend (B) | ✅ |
| 4 | `releases` | digest per dataset | all three resolve to `8094c042ec14` (same release) | ✅ |
| 5 | empty-summary edge case | clean sentence | "ActiveCampaign is listed in the registry." fallback (fixed during test) | ✅ |

## Notable observations

- All three datasets shared release `sha256:8094c042…` at test time — consistent
  with a single coordinated registry release, which strengthens the citation
  (one digest covers the whole fact set).
- The readiness dataset is **per-product scoped**: one entity (Cloudflare) carries
  different grades per product surface (C+ Developer Platform vs A+ Public DNS).
  The tool renders each scoped profile separately rather than collapsing them.
- An entity with an empty `summary` field initially produced a malformed sentence
  ("— . Listed…"); fixed with a fallback lead and re-verified.

## Scope

Read-only against public HTTPS JSON. No auth, no writes, no scraping of gated
content. Provenance always points back to the registry's own URLs.
