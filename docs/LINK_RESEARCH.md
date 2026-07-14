# Link Research Runbook

How official links for `papers.json` entries were found, and how to run
another round for the papers that still don't have one. Written after
finding links for 28/43 papers via ~15 parallel research agents across
several rounds — this records what worked, what didn't, and the exact
verification rule to keep following.

## The rule (non-negotiable)

**Never fabricate a URL.** A link only goes into `official_link` after an
agent actually fetched the page (or resolved a DOI) and confirmed the
title + author list + year match. A WebSearch result snippet is a lead, not
a confirmation — several early agents caught themselves about to report a
plausible-but-wrong nodeId/URL this way and correctly discarded it. If an
agent can't verify, it must return `null`, not a guess.

## Source reliability, ranked by what actually worked

1. **ORCID public API** — `https://pub.orcid.org/v3.0/{orcid-id}/works`
   (`Accept: application/json`, no auth). Gave 13 confirmed DOIs in a
   single fetch for this site's international papers. Always try this
   first for any author with an ORCID iD before spawning search agents.
2. **CrossRef** (`search.crossref.org`) — good for a DOI ORCID didn't have
   (found the 2024 Korean journal article's DOI this way).
3. **Conference-specific archives** — ICAS (`icas.org/ICAS_ARCHIVE/...`) and
   EUCASS (`eucass.eu`) both have browsable proceedings archives with
   direct PDF links; worth checking by conference name + year even when a
   DOI search comes up empty.
4. **RISS** (`riss.kr`) — Korean thesis/dissertation and conference-paper
   aggregator. Worked well for several domestic KSAS conference papers when
   DBpia failed; server-rendered enough for `WebFetch` to read directly.
5. **The author's own PhD lab site** (for this project: `fdcl.snu.ac.kr`,
   Flight Dynamics and Control Lab) — some labs publish a dedicated page per
   paper under `/publication/`. Worth checking directly for any co-author
   who has an active lab site, especially for domestic papers that don't
   show up elsewhere.
6. **Direct plain-title WebSearch (no `site:` restriction)** — surfaced a
   direct PDF on a conference's own site once (`ipnt.or.kr`), and pointed at
   working DBpia nodeIds a `site:dbpia.co.kr` search missed.
7. **DBpia** (`dbpia.co.kr`) — the single biggest source of Korean articles,
   but also the least reliable to automate: author pages and
   table-of-contents listings are JavaScript-rendered, so `WebFetch` mostly
   sees an empty shell. Success rate here was low (roughly 6 of ~24
   domestic-paper attempts across multiple rounds) and every hit required
   actually fetching the specific `articleDetail?nodeId=...` URL and
   confirming the visible title/author text — a `site:dbpia.co.kr <title>`
   search alone never confirmed anything by itself.
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

## How to run another round

For the remaining papers (`python generate.py`'s "still have no official
link / PDF" output lists them), fan out one Agent per 3-4 papers rather
than one agent for everything — parallel batches finish faster and a
narrower prompt keeps each agent focused. A prompt template that worked:

```
Find official public links for these Korean-language conference papers
co-authored by 이지훈 (Jihoon Lee), a Seoul National University aerospace
engineering researcher (advisor Prof. Youdan Kim), published in
한국항공우주학회 (KSAS) conference proceedings.

Strategy — try all of these:
1. Plain WebSearch with the exact Korean title (no site: restriction).
2. Check koreascience.kr and kiss.kstudy.com (often more WebFetch-friendly
   than DBpia).
3. Check RISS (riss.kr) — try both a title search and an author search.
4. If you land on a DBpia URL, check <title>/og:title meta tags even if
   the body is empty — this can still confirm a match.

Only report a URL you've actually fetched and confirmed (title + authors +
year match). Never fabricate. Use null if not found.

[... list of papers ...]

Return ONLY a JSON object: {"slug_key": "https://... or null", ...}
```

After the agent(s) return, apply confirmed links with a small Python
script against `papers.json` (see git history for the exact pattern used
each round), then `python generate.py` to verify the "still missing" count
went down, then commit.

## When no link is findable

Fall back to a self-hosted preprint PDF (`docs/CONTENT_GUIDE.md`) if the
site owner has a copy and the venue's copyright policy allows it. If
neither exists, leave the "Coming Soon" badge as-is rather than linking to
something unverified — see the rule at the top of this doc.
