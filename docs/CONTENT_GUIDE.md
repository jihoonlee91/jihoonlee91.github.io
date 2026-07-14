# Content Guide — Adding & Editing Publications, PDFs, CV

## Adding or editing a publication

Edit the `papers` array in `papers.json`. Each entry:

```json
{
  "slug": "2018-sliding-mode-uav-carrier-landing",
  "category": "int-journal",
  "title": "Sliding mode guidance and control for UAV carrier landing",
  "title_en": null,
  "authors": "Seokwon Lee, Jihoon Lee, ...",
  "venue": "IEEE Transactions on Aerospace and Electronic Systems, Vol. 55, No. 2, pp. 951-966",
  "year": 2018,
  "citations": 79,
  "doi": "10.1109/TAES.2018.2867259",
  "abstract": "",
  "official_link": "https://doi.org/10.1109/TAES.2018.2867259",
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
  Guidance; Target Tracking & Sensing; Path Planning for Search & Rescue;
  UAV Pitch-Hold Control for Mine Detection; Satellite & Lunar Orbiter
  GNC) — drives the Publications page's "By Research Theme" toggle
  view. See `docs/DESIGN.md` for why this isn't split along
  aerospace-vs-semiconductor-AI lines. Add a new theme (and add it to
  `THEME_ORDER`) if a paper genuinely doesn't fit any existing one.
- `title_en` is only for entries whose `title` is in Korean — an English
  translation shown in italics under the title. Leave `null` for
  English-titled papers.
- `slug` must be unique, lowercase, hyphenated — it's the filename for the
  paper's landing page (`papers/<slug>.html`) and BibTeX file
  (`bibtex/<slug>.bib`), and the expected filename for a self-hosted PDF.
- After editing, run `python generate.py` and check its console output for
  which papers are still missing a link.

## Adding a self-hosted (preprint) PDF

A paper can have **both** an `official_link` and a self-hosted PDF at the
same time — they show as two separate badges (green "Official Link", amber
"Preprint PDF"), not one replacing the other. This matters because many
`official_link`s are paywalled (IEEE Xplore, journal publisher pages,
DBpia): the official link stays as the citable source of record, and the
preprint PDF gives visitors something they can actually open without a
subscription.

For any paper — whether or not it already has an `official_link`:

1. Save the PDF as `papers/pdfs/<slug>.pdf` — the filename must exactly
   match the `slug` field.
2. Run `python generate.py` again. This automatically:
   - Adds a **Preprint PDF** badge (amber) on the paper's card and its own
     page, linking to the file.
   - Adds a `citation_pdf_url` meta tag to `papers/<slug>.html` so Google
     Scholar's crawler can index the PDF directly (see
     `docs/DESIGN.md` for why the badge is colored differently from
     "Official Link").
   - Removes the gray "Coming Soon" badge for that entry.
3. Commit and push both the PDF and the regenerated HTML.

If a paper has copyright restrictions preventing self-hosting, put the
publisher/DOI link in `official_link` instead and skip the PDF.

## Finding an official link for an existing paper

Preference order (most to least reliable, per `docs/DATA_SOURCES.md`):

1. ORCID public API — `https://pub.orcid.org/v3.0/0000-0001-5327-824X/works`
   (no auth, machine-readable JSON, has DOIs for most international pubs).
2. CrossRef search — `https://search.crossref.org`.
3. Conference-specific archives — ICAS (`icas.org/ICAS_ARCHIVE`), EUCASS
   (`eucass.eu`), IEEE Xplore, AIAA ARC.
4. DBpia (`dbpia.co.kr`) for Korean domestic papers — expect a low hit rate;
   its listings are JS-rendered and not reliably fetchable headlessly. Only
   add a link after actually visiting the page and confirming title +
   authors + year match — do not trust a search snippet alone.

## Editing CV content (Education / Experience / Awards / Skills / Projects)

These are plain arrays/objects in `papers.json` (`education`, `experience`,
`awards`, `skills`, `projects`), rendered on `cv.html` by
`render_list_section()` / `render_awards_section()` /
`render_skills_section()` in `generate.py`. An item can carry an optional
`"url"` key to make its first field a link (used for the SNU dissertation
and the FDCL lab homepage).

**Before adding anything about current employer work, read
`docs/CONTENT_POLICY.md` first** — it's a hard gate, not a suggestion.

## Profile-level fields (Home page hero, not per-paper)

- `identity_tag` — the one-line hook under the name (e.g. "Aerospace GNC
  Researcher → Industrial AI Engineer, Samsung. Seoul."). Keep it to one
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

Regenerates `index.html`, `publications.html`, `cv.html`, every
`papers/<slug>.html`, `bibtex/*.bib`, `sitemap.xml`, `robots.txt`. Then
commit and push — `.github/workflows/build.yml` also runs `generate.py` on
every push to `main` as a safety net (so even a hand-edited `papers.json`
pushed without a local regen still gets built).
