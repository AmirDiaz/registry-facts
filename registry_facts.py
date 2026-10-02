#!/usr/bin/env python3
"""registry-facts — verifiable dated facts from the Sourcey open registry,
formatted for paste-ready answers (Reddit / forums / citations).

Every fact carries its provenance: dataset URL, release digest, entity ids.
`--format reddit` emits a comment-shaped answer with the citation inline —
the exact shape bounty #130 ("answer live threads with a dated fact from an
open registry") asks for.

Usage:
  registry-facts.py company devin [--format reddit|json|table]
  registry-facts.py readiness cloudflare [--format reddit]
  registry-facts.py search "free tier" [--limit 5]
  registry-facts.py releases
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://sourcey.com"
DATASETS = {
    "companies": f"{BASE}/companies.json",
    "credits": f"{BASE}/startup-credits.json",
    "readiness": f"{BASE}/agent-readiness.json",
}
UA = "registry-facts/1.0 (+https://github.com/AmirDiaz/registry-facts)"


def fetch(name):
    req = urllib.request.Request(DATASETS[name], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def now_iso():
    return time.strftime("%Y-%m-%d", time.gmtime())


def short_digest(sha):
    return (sha or "").replace("sha256:", "")[:12]


def find_company(ds, term):
    term_l = term.lower()
    hits = []
    for c in ds.get("companies", []):
        if term_l in (c.get("slug") or "").lower() or term_l in (c.get("name") or "").lower():
            hits.append(c)
    return hits


def find_profiles(rd, term):
    term_l = term.lower()
    hits = []
    ent_names = {}
    # build entity name map from companies dataset lazily via company field
    for p in rd.get("profiles", []):
        prod = ((p.get("scope") or {}).get("product") or {})
        if term_l in (prod.get("name") or "").lower() or term_l in (prod.get("key") or "").lower():
            hits.append(p)
    return hits


def search_all(term, limit=5):
    out = []
    cds = fetch("companies")
    for c in find_company(cds, term)[:limit]:
        out.append(("company", cds, c))
    rds = fetch("readiness")
    for p in find_profiles(rds, term)[:limit]:
        out.append(("readiness", rds, p))
    return out


def fmt_reddit_company(c, ds):
    rel = short_digest(ds.get("release_id"))
    url = f"{BASE}/companies"
    summary = (c.get("summary") or "").split(".")[0].strip()
    lead = f"{summary}." if summary else f"{c.get('name')} is listed in the registry."
    return (
        f"{c.get('name')} — {lead} "
        f"Listed in the Sourcey open companies registry "
        f"(release `{rel}`; retrieved {now_iso()}). "
        f"Registry: {url}"
    )


def fmt_reddit_readiness(p, ds):
    scope = (p.get("scope") or {})
    prod = (scope.get("product") or {}).get("name", "?")
    grade = p.get("grade") or (p.get("assessment") or {}).get("grade", "?")
    rel = short_digest(ds.get("release_id"))
    url = f"{BASE}/agent-readiness"
    return (
        f"Per the Sourcey agent-readiness registry, **{prod}** currently holds grade "
        f"**{grade}** for agent onboarding (release `{rel}`; retrieved {now_iso()}). "
        f"Grades are published with evidence at {url}"
    )


def fmt_table(kind, rec, rel):
    if kind == "company":
        rows = [
            ("name", rec.get("name")),
            ("slug", rec.get("slug")),
            ("summary", (rec.get("summary") or "")[:100]),
            ("entity_id", rec.get("entity_id")),
            ("release", rel),
        ]
    else:
        scope = rec.get("scope") or {}
        rows = [
            ("product", (scope.get("product") or {}).get("name")),
            ("funnel", (scope.get("funnel") or {}).get("name")),
            ("grade", rec.get("grade") or (rec.get("assessment") or {}).get("grade")),
            ("lifecycle", rec.get("lifecycle")),
            ("release", rel),
        ]
    w = max(len(k) for k, _ in rows)
    return "\n".join(f"  {k.ljust(w)}  {v}" for k, v in rows)


def main():
    ap = argparse.ArgumentParser(prog="registry-facts",
                                 description="Dated, citable facts from the Sourcey open registry.")
    sub = ap.add_subparsers(dest="cmd")
    p_c = sub.add_parser("company", help="fact sheet for a company (slug or name)")
    p_c.add_argument("name")
    p_r = sub.add_parser("readiness", help="agent-readiness grades for a product")
    p_r.add_argument("name")
    p_s = sub.add_parser("search", help="search companies + readiness profiles")
    p_s.add_argument("query")
    p_s.add_argument("--limit", type=int, default=5)
    p_rel = sub.add_parser("releases", help="current release digests per dataset")
    for p in (p_c, p_r):
        p.add_argument("--format", default="table", choices=["table", "reddit", "json"])
    p_s.add_argument("--format", default="table", choices=["table", "reddit", "json"])
    args = ap.parse_args()

    if args.cmd == "releases":
        for name in DATASETS:
            d = fetch(name)
            print(f"{name:10s} release={short_digest(d.get('release_id'))} "
                  f"contract={d.get('dataset_contract')}")
        return 0

    if args.cmd == "company":
        ds = fetch("companies")
        hits = find_company(ds, args.name)
        if not hits:
            print(f"no company matches '{args.name}'", file=sys.stderr)
            return 1
        if args.format == "json":
            print(json.dumps({"release": ds.get("release_id"), "hits": hits[:3]}, indent=1, default=str))
        elif args.format == "reddit":
            for c in hits:
                print(fmt_reddit_company(c, ds))
        else:
            for c in hits:
                print(fmt_table("company", c, short_digest(ds.get("release_id"))))
                print()
        return 0

    if args.cmd == "readiness":
        ds = fetch("readiness")
        hits = find_profiles(ds, args.name)
        if not hits:
            print(f"no readiness profile matches '{args.name}'", file=sys.stderr)
            return 1
        if args.format == "json":
            print(json.dumps({"release": ds.get("release_id"), "hits": hits[:3]}, indent=1, default=str))
        elif args.format == "reddit":
            for p in hits:
                print(fmt_reddit_readiness(p, ds))
        else:
            for p in hits:
                print(fmt_table("readiness", p, short_digest(ds.get("release_id"))))
                print()
        return 0

    if args.cmd == "search":
        results = search_all(args.query, args.limit)
        if not results:
            print(f"nothing matches '{args.query}'", file=sys.stderr)
            return 1
        if args.format == "json":
            print(json.dumps([{"kind": k, "release": d.get("release_id"), "record": r}
                              for k, d, r in results], indent=1, default=str))
        elif args.format == "reddit":
            for k, d, r in results:
                print(fmt_reddit_company(r, d) if k == "company" else fmt_reddit_readiness(r, d))
        else:
            for k, d, r in results:
                print(f"[{k}] {fmt_table(k, r, short_digest(d.get('release_id')))}")
                print()
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
