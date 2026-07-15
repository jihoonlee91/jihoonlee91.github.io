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

The JSON field remains named `official_link` for compatibility, but the site
labels each link by its actual source. A DOI or publisher page is preferred;
for Korean conference papers, use a verified DBpia article page before RISS.
RISS is retained only as a fallback index when no deeper publisher or DBpia
record has been confirmed. Lab pages and institutional repositories are valid
publication sources, while discovery-only services such as Semantic Scholar
should not be presented as official publisher links.

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
As of the two most recent research passes (see git log), it's down to 8
domestic-conference/2015-2018-era papers with no confirmed public link at
all — both passes independently confirmed DBpia/RISS genuinely have no
page for these, not a fetch/JS-rendering artifact. Further automated
attempts are unlikely to find these; a self-uploaded preprint PDF from the
owner (see `CONTENT_GUIDE.md`) is the realistic path forward.

## Abstracts

- 18 of 43 papers have a verified abstract in `papers.json` as of the two
  research passes referenced above (see git log for "abstracts" commits).
  Sources used, roughly in the order tried: the paper's own `official_link`
  page, CrossRef (`api.crossref.org/works/{doi}`, sometimes JATS-XML
  abstracts), Semantic Scholar Graph API
  (`api.semanticscholar.org/graph/v1/paper/DOI:...` or a title search),
  downloading the PDF (ICAS/EUCASS archive, IPNT conference) and extracting
  the first-page abstract text, DOAJ's article API, and RISS
  (`riss.kr`) for a Korean MS/PhD dissertation.
- A handful of Korean-language domestic papers have a Korean abstract only
  (used as-published, not translated) — some, like the 2024 domestic
  journal article, have both a Korean and an English abstract in the
  source; both are kept, joined by a blank line in the `abstract` field so
  `generate.py`'s `_abstract_paragraphs()` renders them as two separate
  paragraphs instead of one run-on block.
- **The other 25 are confirmed genuinely unavailable, not just
  "couldn't fetch"**: ~20 DBpia/RISS-linked Korean conference/journal
  papers whose detail pages render server-side but literally say "no
  abstract on file" (checked directly, not inferred from a blocked
  fetch); 2 AIAA ARC papers that return a bot-challenge page to every
  fetch method tried (WebFetch, curl with a browser UA, via the DOI
  redirect); and the 8 papers with no `official_link` at all, where a
  CrossRef/Semantic Scholar title search found no matching record.
- **Never fabricate or paraphrase-from-title an abstract** — same "wrong is
  worse than missing" policy as `official_link`. A blank `abstract` field
  is a legitimate, intentional state for a paper that's been checked and
  came back empty, not an oversight to "fix" with a guess.

## arXiv preprints / code repositories

Checked for all 43 papers (3 parallel research passes, one per ~15-paper
batch) against the arXiv API (`export.arxiv.org/api/query?search_query=ti:...`)
and Semantic Scholar's `externalIds`, plus a GitHub search per paper title +
"Jihoon Lee"/"SNU FDCL". **Result: zero arXiv preprints, zero paper-specific
code repos, for any of the 43.** This is expected for the field — GNC/aerospace
controls venues (AIAA, IEEE TAES, KSAS domestic conferences, EUCASS) don't
have arXiv-mirroring culture the way ML/CS does, and this is theory/simulation
work without a natural "release the code" artifact per paper. Not worth
re-running without new information (e.g. the owner confirming a specific
paper does have a preprint somewhere non-obvious).

One research pass did find the owner's own public GitHub repos
(`gtm-lpv-control`, `gtm-morphing-sim`, `morphing-hinf-control-learning`,
`morphing-dl-gain-scheduler`, `argos-vtol-model`, `morphing-flight-control-doc`)
that are topically related to the morphing-aircraft-control papers but whose
READMEs don't explicitly cite any specific paper — so none were added as a
per-paper `code` link (would violate the no-fabrication rule). Whether any of
these are worth surfacing as their own item (e.g. under Side Projects, or a
general "code" note) is an owner call, not automated — see
`docs/ACTION_ITEMS.md`.

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
