# Link Research Runbook

How publication-source links for `papers.json` entries were found and how to
audit a future or changed record. The current baseline is complete: 38 papers
have a verified final source link and the other 5 have a verified Author PDF,
for 43/43 public access coverage. This is a historical runbook for maintaining
that standard, not a list of currently missing links.

## The rule (non-negotiable)

**Never fabricate a URL.** A link goes into `official_link` only after the
final publisher, proceedings, scholarly-database, or full-text repository
destination has been opened and its title + author list + year confirmed. DOI
resolvers, RISS hand-off pages, lab pages, Scholar, ResearchGate, and search
results are discovery sources, not final destinations. A search snippet is a
lead, not confirmation. If a final link cannot be verified, return `null`, not
a guess.

## Source reliability, ranked by what actually worked

1. **ORCID public API** — `https://pub.orcid.org/v3.0/{orcid-id}/works`
   (`Accept: application/json`, no auth). Gave 13 confirmed DOIs in a
   single fetch for this site's international papers. Always try this
   first for any author with an ORCID iD before spawning search agents.
2. **Crossref** (`search.crossref.org`) — good for a DOI ORCID didn't have
   (found the 2024 Korean journal article's DOI this way). Resolve the DOI and
   store the final publisher page, not `doi.org`.
3. **Conference-specific archives** — ICAS (`icas.org/ICAS_ARCHIVE/...`) and
   EUCASS (`eucass.eu`) both have browsable proceedings archives with
   direct PDF links; worth checking by conference name + year even when a
   DOI search comes up empty.
4. **RISS** (`riss.kr`) — useful Korean discovery and hand-off index. Follow
   `원문보기` through to DBpia or another final provider; do not store the RISS
   detail page when it only points onward.
5. **The author's own PhD lab site** (for this project: `fdcl.snu.ac.kr`,
   Flight Dynamics and Control Lab) — useful for discovery, but a lab index is
   not the final publication source. Follow its references to the publisher or
   proceedings record.
6. **Direct plain-title WebSearch (no `site:` restriction)** — surfaced a
   direct PDF on a conference's own site once (`ipnt.or.kr`), and pointed at
   working DBpia nodeIds a `site:dbpia.co.kr` search missed.
7. **DBpia** (`dbpia.co.kr`) — the largest current source group (18 records).
   Author pages and table-of-contents listings can still be difficult to
   automate, so every hit requires opening the exact
   `articleDetail?nodeId=...` page and confirming title, authors, venue, and
   year. A `site:dbpia.co.kr <title>` result alone never confirms a record.
8. **Semantic Scholar** (`semanticscholar.org` / its Graph API) — occasional
   hits for conference papers with no DOI; the public search API is rate
   limited (429s came back fast when queried programmatically in a tight
   loop), so prefer letting an agent use it once per paper via WebSearch/
   WebFetch rather than scripting many rapid calls.
9. **ResearchGate** — blocked entirely during this project (HTTP 403 on
   every fetch attempt, profile page and individual publication pages
   alike). Don't rely on it without an authenticated browser session.
10. **Playwright/browser automation** — mostly reported locked/unavailable
   ("Browser is already in use") in early rounds, but when it *was*
   available, it solved DBpia cleanly: using DBpia's own site search (not
   Google) with the exact Korean title through a real Playwright session
   confirmed 4/4 papers in one batch, reading title/authors/venue/year
   straight off the rendered results page. If Playwright is available,
   prefer it over WebFetch for any DBpia lookup — it was the single biggest
   swing in hit rate observed across this whole project.

## How to audit a future or changed paper

If a future record has neither a final source link nor an Author PDF,
`python generate.py` reports it. For a batch, fan out one agent per 3–4 papers
rather than one agent for everything. A prompt template that worked:

```
Find final publication-source links for these Korean-language conference papers
co-authored by 이지훈 (Jihoon Lee), a Seoul National University aerospace
engineering researcher (advisor Prof. Youdan Kim), published in
한국항공우주학회 (KSAS) conference proceedings.

Strategy — try all of these:
1. Plain WebSearch with the exact Korean title (no site: restriction).
2. Check koreascience.kr and kiss.kstudy.com (often more WebFetch-friendly
   than DBpia).
3. Check RISS (riss.kr) for discovery, then follow through to the final
   publisher/proceedings page.
4. If you land on a DBpia URL, check <title>/og:title meta tags even if
   the body is empty — this can still confirm a match.

Only report a URL you've actually fetched and confirmed (title + authors +
year match). Never fabricate. Use null if not found.

[... list of papers ...]

Return ONLY a JSON object: {"slug_key": "https://... or null", ...}
```

After the agent(s) return, add only confirmed final links to `papers.json`, then
run `python generate.py` and confirm coverage. Review the diff before commit.

## When no link is findable

Fall back to a self-hosted Author PDF (`docs/CONTENT_GUIDE.md`) if the
site owner has a copy and the venue's copyright policy allows it. If
neither exists, leave the `No Public Link Yet` fallback rather than linking to
something unverified. No current paper is in this state.
