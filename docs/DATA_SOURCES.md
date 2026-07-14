# Data Sources & Known Limitations

`papers.json` was assembled from several sources. This records provenance and
what's still unverified, so future edits don't accidentally overwrite a
verified field with a guess.

## Publication list

- **Base list**: Google Scholar profile
  (`https://scholar.google.co.kr/citations?user=vNY8rPEAAAAJ`), paginated
  fetch, 43 entries total (including Korean-language domestic conference
  papers Scholar indexes with garbled/OCR'd titles in naive scrapes — do not
  trust an LLM's summary of a Scholar page for Korean titles without
  cross-checking).
- **Ground truth for titles/authors/venues**: the site owner's own
  `publication.html` page on his prior personal site
  (`https://jihoon-lee.weebly.com/publication.html`), which lists precise
  English titles, full author names, and Journal / International Conference
  / Domestic Conference categories. This is the source of truth used to
  correct Scholar's noisy scrape — **43 total matched exactly** (41 on
  weebly + 1 Korean 2024 journal article + 1 PhD dissertation not listed on
  weebly).
- **CV** (pasted directly by the site owner) confirmed the dissertation is a
  **Ph.D.**, not M.S. as Scholar's "서울대학교 대학원" entry ambiguously
  suggested — always prefer the owner's direct statement over an inferred
  Scholar label.

## Official links (DOI / publisher / repository)

- **ORCID public API** (`https://pub.orcid.org/v3.0/{orcid}/works`, no auth
  needed) — reliable, machine-readable, gave 13 confirmed DOIs in one fetch.
  Prefer this over scraping publisher sites directly.
- **ICAS Congress archive** (`icas.org/ICAS_ARCHIVE/...`) and **EUCASS**
  (`eucass.eu`) — both have browsable/searchable proceedings archives;
  confirmed 3 more links this way (see git history / `papers.json` for
  which slugs).
- **CrossRef** (`search.crossref.org`) — useful for finding a DOI when ORCID
  doesn't have it (used for the 2024 Korean journal article,
  `10.5139/jksas.2024.52.4.297`).
- **DBpia** (Korean article database) — attempted for ~20 domestic
  conference papers via parallel research agents. **Mostly failed**: DBpia's
  author pages and table-of-contents listings are JavaScript-rendered, so
  `WebFetch` only sees the page shell, never the actual article list. Of ~24
  domestic-conference/journal lookups attempted, only 2 were confirmed by
  actually visiting a matching `articleDetail?nodeId=...` page. **Do not
  trust a WebSearch snippet alone as confirmation** — several agents caught
  and discarded plausible-looking but wrong DBpia nodeIds this way (verify
  by fetching the page and checking title+authors+year).
- **ResearchGate** — blocked entirely (HTTP 403 on every fetch attempt,
  including via the profile page and individual publication pages). Has not
  yielded any data; don't rely on it as a link source without an
  authenticated browser session.
- **FDCL lab site** (`fdcl.snu.ac.kr/publication/...`) — the owner's PhD lab
  (Flight Dynamics and Control Lab) publishes some domestic-conference
  papers directly on its own site with a dedicated page per paper. Found 2
  links this way after DBpia/RISS attempts failed for the same papers —
  worth checking directly (`fdcl.snu.ac.kr/publication/`) for any remaining
  unlinked domestic paper by a lab member before trying other sources.
- **SNU dissertation link**: found directly on the owner's own weebly
  `about.html` page, which linked both a library catalog record
  (`snu-primo.hosted.exlibrisgroup.com`) and the full-text repository
  (`dcollection.snu.ac.kr/common/orgView/000000176713`) — used the
  dCollection one as `official_link` since it's the full text, not just a
  catalog entry.

## Still unresolved (as of last generation)

Run `python generate.py` and read its "papers still have no official
link / PDF" output for the current list — it changes as links get added.
Roughly 24 domestic-conference papers from the 2015–2018 era have no
confirmed public link; they either need a manually-verified DBpia URL or a
self-uploaded preprint PDF (see `CONTENT_GUIDE.md`).

## Profile / CV data

- Name, affiliation, tagline, bio, experience, education, awards, skills,
  email, location: all provided directly by the site owner (pasted CV text
  and follow-up corrections), not scraped. Treat these as authoritative
  unless the owner says otherwise.
- Photo: downloaded from the owner's prior weebly site
  (`/uploads/.../1_orig.jpg`) — small (142×189); a higher-res replacement
  would be an easy upgrade (`assets/profile.jpg`).
- Social links (GitHub, LinkedIn, ORCID, ResearchGate, Instagram, Facebook):
  all provided directly by the owner in conversation.
