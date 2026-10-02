# registry-facts

Verifiable **dated facts** from the [Sourcey](https://sourcey.com) open registry,
formatted for paste-ready answers — Reddit comments, forum replies, citations.

Every fact carries its provenance: dataset URL, release digest, retrieval date.
No "as far as I know" — every line is checkable against a specific registry release.

```bash
$ python3 registry_facts.py readiness cloudflare --format reddit
Per the Sourcey agent-readiness registry, **Cloudflare 1.1.1.1 Public DNS** currently
holds grade **A+** for agent onboarding (release `8094c042ec14`; retrieved 2026-10-02).
Grades are published with evidence at https://sourcey.com/agent-readiness

$ python3 registry_facts.py company devin --format reddit
Devin — Devin is an AI software engineer that handles pull requests, bug fixes,
refactors, and migrations through a web workspace, a CLI, and a desktop app.
Listed in the Sourcey open companies registry (release `8094c042ec14`;
retrieved 2026-10-02). Registry: https://sourcey.com/companies
```

(Live output, 2026-10-02 — all three datasets resolve to release `8094c042…`.)

## Why

Answering a live thread with a *dated* fact is different from answering from memory:
memory has no release digest, no retrieval date, and no way for the reader to check
whether the answer is stale. Open registries publish exactly that — versioned,
citable state. This tool turns their current release into paste-shaped sentences.

The output format is deliberately claim-shaped:

> (what) — (one-line summary). Listed in the (registry) registry
> (release `digest12`; retrieved YYYY-MM-DD). Registry: (URL)

Anyone can verify the claim by fetching the registry at that release and checking
the digest — no trust in the commenter required.

## Usage

```
registry_facts.py company <name>    [--format table|reddit|json]
registry_facts.py readiness <name> [--format table|reddit|json]
registry_facts.py search <query>   [--limit N] [--format ...]
registry_facts.py releases
```

- `company` — fact sheet for a company by slug/name (543 companies)
- `readiness` — agent-readiness grades by product name (25 profiles, per-product scope)
- `search` — one term across both datasets, Reddit-format ready
- `releases` — current release digest per dataset (companies / credits / readiness)

## Design

- Python 3 stdlib only, single file — same discipline as
  [sourcey-tracker](https://github.com/AmirDiaz/sourcey-tracker),
  [sourcey-registry-cli](https://github.com/AmirDiaz/sourcey-registry-cli),
  [readiness-badges](https://github.com/AmirDiaz/readiness-badges),
  [x402-balance](https://github.com/AmirDiaz/x402-balance) and
  [franticls](https://github.com/AmirDiaz/franticls).
- Facts cite the **release digest, not a timestamp** — digests are content-addressed,
  timestamps are just when you looked.
- `--format json` includes full records + release ids for programmatic use.

## License

MIT — see `LICENSE`.
