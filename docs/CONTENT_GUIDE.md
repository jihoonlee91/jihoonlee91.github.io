# Content Guide — Adding & Editing Publications, PDFs, CV

## Adding or editing a publication

Edit the `papers` array in `papers.json`. Each entry:

```json
{
  "slug": "2018-sliding-mode-uav-carrier-landing",
  "category": "int-journal",
  "title": "Sliding mode guidance and control for UAV carrier landing",
  "title_en": null,
  "title_ko": null,
  "authors": "Seokwon Lee, Jihoon Lee, ...",
  "authors_ko": null,
  "venue": "IEEE Transactions on Aerospace and Electronic Systems, Vol. 55, No. 2, pp. 951-966",
  "venue_ko": null,
  "year": 2019,
  "citations": 79,
  "doi": "10.1109/TAES.2018.2867259",
  "abstract": "",
  "abstract_ko": "",
  "official_link": "https://ieeexplore.ieee.org/document/8447257/",
  "pdf": "papers/pdfs/2018-sliding-mode-uav-carrier-landing.pdf",
  "theme": "Autonomous Carrier Landing & Guidance"
}
```

- `category` must be one of: `int-journal`, `domestic-journal`,
  `int-conference`, `domestic-conference`, `thesis` — this drives which
  section of `publications.html` the entry lands in (see `CATEGORY_ORDER` in
  `generate.py`).
- `theme` must be one of the values in `THEME_ORDER` in `generate.py`
  (currently: Morphing-Wing Aircraft Control; Autonomous Carrier Landing &
  Guidance; Dynamic Soaring & Learning-Based Control; Target Tracking &
  Sensing; Path Planning for Search & Rescue; UAV Pitch-Hold Control for Mine
  Detection; Satellite & Lunar Orbiter GNC) — drives the Publications page's
  "By Research Theme" toggle view. See `docs/DESIGN.md` for why this isn't split along
  aerospace-vs-semiconductor-AI lines. Add a new theme (and add it to
  `THEME_ORDER`) if a paper genuinely doesn't fit any existing one.
- English is the primary language throughout the site, including visible
  publication data, citation metadata, and BibTeX exports. Korean is retained
  only as supporting information on a smaller secondary line or in a note.
- Publication cards and paper pages always display an English title first.
  For a Korean-language record, keep the official Korean title in `title` and
  put the verified English title in `title_en`; the Korean title then appears
  on the second line. For an English-language record that also has a Korean
  title (for example, the dissertation), keep the English title in `title`,
  leave `title_en` null, and put the Korean title in `title_ko`.
- Store the verified English abstract in `abstract`. When the publication also
  provides a Korean abstract, store it separately in `abstract_ko`; it appears
  below the English text as supporting information. Never generate or
  paraphrase an abstract from the title. Leave it blank when the source itself
  has no abstract.
- Keep `authors` and `venue` in English. Use optional `authors_ko` and
  `venue_ko` only when the source provides useful Korean metadata; the Korean
  values render as a secondary line.
- `slug` must be unique, lowercase, hyphenated — it's the filename for the
  paper's landing page (`papers/<slug>.html`) and BibTeX file
  (`bibtex/<slug>.bib`), and the expected filename for a self-hosted PDF.
- After editing, run `python generate.py` and confirm that publication
  source/Author-PDF coverage remains complete.

## Adding a self-hosted Author PDF

A paper can have **both** an `official_link` and a self-hosted PDF at the
same time — they show as two separate badges (green destination-labelled
publication source, amber `Author PDF`), not one replacing the other. This
matters because many source-of-record pages are paywalled: the final publisher
or proceedings link stays as the citable record, and the Author PDF gives
visitors something they can actually open without a
subscription.

For any paper — whether or not it already has an `official_link`:

1. Save the PDF as `papers/pdfs/<slug>.pdf` — the filename must exactly
   match the `slug` field.
2. Run `python generate.py` again. This automatically:
   - Adds an **Author PDF** badge (amber) on the paper's card and its own
     page, linking to the file.
   - Adds a `citation_pdf_url` meta tag to `papers/<slug>.html` so Google
     Scholar's crawler can index the PDF directly (see
     `docs/DESIGN.md` for why the badge is colored differently from
     the publication-source badge).
   - Removes the gray `No Public Link Yet` fallback for that entry.
3. Commit and push the PDF and any edited source data. Generated HTML is
   gitignored and must not be committed.

If a paper has copyright restrictions preventing self-hosting, put the
final publisher or proceedings URL in `official_link` and skip the PDF. Do not
store a DOI-resolver or discovery-page URL when a deeper destination exists.

## Finding a publication-source link for an existing paper

Use these sources for discovery, then store only the final destination defined
in `docs/DATA_SOURCES.md`:

1. ORCID public API — `https://pub.orcid.org/v3.0/0000-0001-5327-824X/works`
   (no auth, machine-readable JSON). Resolve any DOI through to the publisher.
2. Crossref search — `https://search.crossref.org`; again, retain the final
   publisher page rather than the DOI resolver.
3. Conference-specific archives — ICAS (`icas.org/ICAS_ARCHIVE`), EUCASS
   (`eucass.eu`), IEEE Xplore, AIAA ARC.
4. DBpia (`dbpia.co.kr`) for Korean domestic papers. Store the exact
   `articleDetail?nodeId=...` page only after confirming title, authors, venue,
   and year; do not stop at RISS or trust a search snippet alone.

## Editing CV content (Education / Experience / Awards / Skills / Projects)

These are plain arrays/objects in `papers.json` (`education`, `experience`,
`awards`, `skills`, `projects`), rendered on `cv.html` by the corresponding
render functions in `generate.py`. Project entries keep `title` (English),
`title_ko` (Korean), `sponsor`, `sponsor_ko`, and `period` as separate fields;
related output is linked with `related_papers` and/or `related_themes`. An item can carry an
optional `"url"` key to make its main title a link (used for the SNU
dissertation and the FDCL lab homepage).

Keep English names primary and store available official Korean names in the
matching `_ko` field: `organization_ko`, `school_ko`, `degree_ko`,
`title_ko`, or `sponsor_ko`. Renderers place those values immediately below or
beside the English name in smaller supporting text. Do not replace an English
primary name with Korean-only text.

**Before adding anything about employment, read `docs/CONTENT_POLICY.md`
first** — substantive employer-work descriptions do not belong on this
public site.

## Profile-level fields (Home page hero, not per-paper)

- `identity_tag` — the one-line hook under the name (e.g. "Aerospace GNC
  Researcher → AI & Software Engineer."). Keep it to one
  short sentence; `tagline` and `bio` are for anything longer.
- `collaborator_affiliations` — a `{"Full Name": "Affiliation string"}` map
  used only to annotate the CV page's "Frequent Collaborators" list (which
  computes the actual co-authorship *counts* from `papers.json` itself, not
  from this map). Add an entry here only for a name that already appears as
  a paper author; an unlisted collaborator still shows up, just without an
  affiliation line. See `docs/DESIGN.md` for the `min_count`/`top_n`
  thresholds that control who counts as "frequent."
- `education` / `experience` entries can carry an optional `"url"` key to
  make their first displayed field a link (used for the SNU dissertation
  and the FDCL lab homepage) — same mechanism for both arrays.

## Rebuilding after any papers.json change

```bash
python generate.py
```

Regenerates `index.html`, `publications.html`, `cv.html`, `life.html`, every
`papers/<slug>.html`, `bibtex/*.bib`, `sitemap.xml`, and `robots.txt`. It also
generates Wiki pages when `wiki.json` contains notes. Generated output is
gitignored; commit only maintained source files. `.github/workflows/build.yml`
runs `generate.py` on every push to `main` and deploys the fresh output.

## Adding a public Wiki note

Add a note object to `wiki.json` with a unique lowercase hyphenated `slug`,
title, summary, dates, tags, notice, structured sections, and verified public
sources. `generate.py` creates the Wiki index and `wiki/<slug>.html`; the Wiki
navigation item appears only when at least one note exists. The file is
currently empty, so no Wiki page is published.

Wiki notes are public and search-indexed. Do not include raw case evidence,
personal identifiers, compensation, employer-confidential systems, internal
metrics, process details, or unsupported legal conclusions. Current-employer
content remains subject to `docs/CONTENT_POLICY.md`.
