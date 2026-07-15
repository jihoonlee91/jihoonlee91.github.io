# Design System

Static site, no build tooling beyond Python + plain CSS. Everything below is
implemented in `style.css` (tokens, layout, components) and `viz.py` (chart
SVG generation).

## Theme: light default, dark opt-in

- `:root` in `style.css` defines the **light** palette.
- `:root[data-theme="dark"]` overrides every token for dark mode.
- `generate.py`'s `THEME_INIT_SCRIPT` runs in `<head>` on every page, before
  paint, reading `localStorage.theme` and setting `data-theme` on `<html>` —
  this avoids a flash of the wrong theme.
- `THEME_TOGGLE_SCRIPT` (loaded once near `</body>`) defines
  `window.toggleTheme()`, wired to the nav bar's toggle button
  (`render_nav()` in `generate.py`), which flips `data-theme` and persists it
  to `localStorage`.
- **When adding new UI, always use CSS custom properties** (`var(--fg)`,
  `var(--accent)`, etc.) — never a hardcoded hex — so it reacts to both
  themes automatically.

## Layout

- Content width: `max-width: 1200px` on `.container`, `.nav-inner`, and
  `footer.site-footer` — reduced from 1600px after a wide-desktop review to
  improve line length while retaining multi-column layouts.
- `.bio` has no `max-width`/`ch` cap — an earlier 70ch limit made the intro
  paragraph wrap narrower than the actual container width, which looked
  broken on a wide screen. Any new free-text block should default to
  filling its flex/grid cell rather than adding an arbitrary ch cap.
- Single mobile breakpoint at `640px` — nav/hero/stats stack and center.
- Sticky top nav (`.site-nav`) with `Home / Publications / CV` links on the
  left/center and the theme toggle **in its own flex slot pinned to the far
  right edge** — it was originally inline with the nav links and moved out
  on request, so keep it separate from `.nav-links` if the nav is ever
  restructured.

## Typography

One font stack everywhere — `-apple-system, "Segoe UI", "Malgun Gothic",
Arial, sans-serif` — declared once on `body` and inherited by every element.
Do not introduce a second `font-family` declaration anywhere in the CSS; if a
new component seems to need a different typeface, that's a sign to reuse an
existing text class instead (`.paper-meta`, `.paper-venue`, `.tagline`, etc.
already cover the type scale in use: sizes range 0.8rem–2.1rem, weights
400/600/700 only).

## Color roles (non-chart)

| Token | Role |
|---|---|
| `--fg` / `--muted` | primary / secondary text |
| `--accent` | links, active nav, hover states |
| `--border` | hairline dividers |
| `--bg` / `--bg-soft` | page background / card-like surfaces |
| `--official` / `--official-bg` | "Official Link" badge (green) |
| `--preprint` / `--preprint-bg` | "Full Text (PDF)" badge (amber) |
| `--pending` | "No Public Link Yet" badge (gray) |
| `--tag-bg` | interest chips |

## Chart color palette (viz.py)

The Publications page renders three static SVG charts (publications-by-year
stacked bar, citations-by-year bar, keyword word cloud) via `viz.py`,
following the dataviz skill's procedure: pick the form → assign color by
job → **validate the palette with the skill's script** → apply mark specs
→ provide a legend/table fallback.

The 5-slot categorical palette (one slot per publication category) and the
single sequential blue hue are the skill's documented reference palette
(`references/palette.md`), re-validated against this site's own surfaces
(not the skill's defaults) before use:

```
node scripts/validate_palette.js "#2a78d6,#1baf7a,#eda100,#008300,#4a3aa7" --mode light --surface "#ffffff"
node scripts/validate_palette.js "#3987e5,#199e70,#c98500,#008300,#9085e9" --mode dark  --surface "#0d1117"
```

Both passed all four checks (lightness band, chroma floor, CVD separation,
contrast), with the contrast/CVD results at the floor band — which is why
every chart also ships a legend, direct value labels on segments/bars, and a
`<details>` table-view fallback rather than relying on color alone.

**If you ever change `--bg` (the dark surface) or the light surface, re-run
the validator against the new surface before reusing this palette** — the
contrast checks are surface-relative.

## Badges (Official Link / Full Text (PDF) / No Public Link Yet)

Every publication, on both the Publications list and its own paper page,
shows a small badge row from `link_badges()` in `generate.py`:

- **Official Link** (green) — `official_link` is set (a DOI or publisher/
  DBpia/library URL). Label shows the DOI value directly (not just a
  "(DOI)" marker) when a `doi` field is present, and a hover tooltip shows
  the destination — link previews shouldn't require a click. External
  badges (Official Link, Full Text, BibTeX) open in a new tab; internal
  site navigation does not.
- **Full Text (PDF)** (amber) — a file exists at `papers/pdfs/<slug>.pdf`.
  Named for what it is (a self-hosted copy of the paper) rather than
  "Preprint," since these aren't necessarily pre-review drafts.
- **No Public Link Yet** (gray) — neither of the above. Deliberately
  neutral wording — it doesn't promise a link is coming.
- **BibTeX** (neutral) — always shown. Clicking copies the entry straight
  to the clipboard (`copyBibtex()`, prevents the default navigation);
  the badge still has a real `href` to `bibtex/<slug>.bib` so
  middle-click/"open in new tab"/"save link as" still gets the raw file.
  Hovering previews the actual BibTeX text via `data-tooltip`.

These three are deliberately different colors so a visitor can tell at a
glance whether they're about to land on the publisher's page or a
self-hosted file — do not merge them into one generic "link" style. A paper
can show **both** Official Link and Full Text (PDF) at once (many official
links are paywalled) — see `docs/CONTENT_GUIDE.md`.

## Home page: identity tag + timeline

- `identity_tag` in `papers.json` is a single terse sentence rendered right
  under the name in the hero (`.identity-tag`, accent-colored) — e.g.
  "Aerospace GNC Researcher → AI & Software Engineer."
  This is a one-second summary, distinct from `tagline` (a slightly longer,
  muted-color line) and `bio` (the full paragraph). Keep it short; if it
  needs a comma-separated list of clauses, it's become a tagline instead.
- The Home page's Timeline section (`render_timeline()` in `generate.py`)
  merges `experience` and `education` into one reverse-chronological list
  instead of two separate blocks — this was a deliberate choice (see
  `docs/LINK_RESEARCH.md`'s companion research on notable personal
  homepages) to narrate a single continuous arc rather than silo "career"
  from "school." Sort order comes from `_timeline_sort_key()`, which reads
  the last 4-digit year in each entry's `period` string ("Present" sorts as
  newest). If you add a new timeline-eligible section (e.g. a future role
  change), give it a `period` string in the same format
  (`"Mon YYYY – Mon YYYY"` or `"Mon YYYY – Present"`) so the sort keeps
  working without changes to the parser.

## Publications page: category vs. theme grouping

The Publications page has a client-side toggle (`view-toggle`,
`setPubView()`) between two precomputed groupings of the same 43 papers:

- **By Category** — bibliographic type (`CATEGORY_ORDER` in `generate.py`:
  international/domestic journal, international/domestic conference,
  thesis). This is the standard, expected grouping for an academic reader.
- **By Research Theme** — `THEME_ORDER` in `generate.py`, a hand-assigned
  `theme` field per paper reflecting actual research sub-areas
  (Morphing-Wing Aircraft Control; Autonomous Carrier Landing & Guidance;
  Target Tracking & Sensing; Path Planning for Search & Rescue; UAV
  Pitch-Hold Control for Mine Detection; Satellite & Lunar Orbiter GNC).
  The tracking/planning/pitch-hold split used to be one combined theme —
  broken apart because the pitch-hold/mine-detection papers are really
  UAV control work wearing a sensing-mission label, and lumping them in
  with the actual tracking/path-planning papers obscured that.

**Deliberately not split by "aerospace vs. semiconductor AI"**: every one
of the 43 publications is aerospace/GNC research from the PhD era — the
current semiconductor-AI day job has no publications to group, so forcing
that split would misrepresent the actual data. If that changes (e.g. a
future patent or paper from the industry role), add a new theme rather than
bending an aerospace paper into an unrelated bucket.

When adding a new paper, set its `theme` to the closest existing value in
`THEME_ORDER`, or add a new theme (and add it to `THEME_ORDER`) if it
genuinely doesn't fit any existing one.

## Frequent Collaborators (CV page)

`render_collaborators_section()` in `generate.py` computes co-authorship
counts directly from `papers.json`'s `papers` array (not a hand-maintained
list) — it will automatically recompute if papers are added/removed. Only
`papers.json`'s `collaborator_affiliations` dict (name → affiliation
string) is hand-maintained, and only for names that actually appear in the
list; an unlisted co-author still shows up with just their paper count, no
affiliation line. The `min_count`/`top_n` thresholds
(`render_collaborators_section(min_count=4, top_n=10)`) control who
qualifies as "frequent" — raise `min_count` if the list gets too long as
more papers are added.

## BibTeX generation (`to_bibtex`, `render_bibtex`, `parse_venue`)

- `parse_venue()` pulls `Vol.`/`No.`/`pp. X-Y` (or a bare trailing article
  number, MDPI-style) out of the free-text `venue` string into proper
  `volume`/`number`/`pages` BibTeX fields, instead of leaving them folded
  into the `journal`/`booktitle` field as one blob. If a future paper's
  venue string uses a format these regexes don't catch, the raw venue
  falls back into the journal/booktitle field unsplit — not wrong, just
  less structured.
- **Citation keys must be unique across `bibtex/all.bib`, not just within
  each per-paper `.bib` file.** `render_bibtex()` computes all 43 keys
  together first and appends `a`/`b`/`c`... to any repeat of the same
  `AuthorYear` base (e.g. three 2018 papers with a first-author surname
  "Lee" become `Lee2018`, `Lee2018a`, `Lee2018b`) — do not revert to calling
  `bibtex_key()` independently per file, that's what caused the original
  collision bug.
- A first-author name that isn't Latin script (e.g. a Korean-only author
  list) strips down to nothing alphabetic under `bibtex_key()`'s
  non-alphanumeric filter — it falls back to the paper's `slug` for the key
  in that case, so it doesn't collapse to a bare, collision-prone year like
  `{2024}`.

## Head metadata (favicon, OG/Twitter, JSON-LD)

`render_common_head()` in `generate.py` is called once per page and emits:
canonical link, `favicon.svg` link, `theme-color` (light/dark via media
query), Open Graph tags, and Twitter Card tags — all derived from that
page's own title/description/URL, not hardcoded per page. `favicon.svg`
(repo root, static file, not generated) uses `prefers-color-scheme` inside
its own `<style>` block since a standalone favicon can't read this site's
CSS custom properties.

`render_person_jsonld()` runs on the homepage only, emitting a
`schema.org` `Person` + `ProfilePage` graph. The `sameAs` array (Scholar/
ORCID/ResearchGate/LinkedIn/GitHub) is the highest-value field — it's what
lets Google disambiguate this identity, which matters more than usual for
a common-format Korean name spanning two unrelated fields (aerospace vs.
industrial AI). `affiliation` is split on `" — "` into `worksFor`
(Organization) and `jobTitle` — don't feed the combined string into
`jobTitle` directly, that was a bug caught and fixed once already.
