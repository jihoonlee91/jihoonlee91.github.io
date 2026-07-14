# CLAUDE.md

Guidance for Claude Code sessions working in this repo.

## What this is

Jihoon Lee's personal homepage, served at
**https://jihoonlee91.github.io** via GitHub Pages from this repo
(`jihoonlee91/jihoonlee91.github.io`). The repo name must stay exactly
`<username>.github.io` — that's a GitHub Pages requirement for a root-domain
user site, not a naming choice to "fix".

It is a **static site generator**, not a hand-edited site:

- `papers.json` — the single source of truth (profile, CV, all 43
  publications).
- `generate.py` — reads `papers.json`, writes `index.html`,
  `publications.html`, `cv.html`, `papers/<slug>.html` per paper,
  `bibtex/*.bib`, `sitemap.xml`, `robots.txt`.
- `viz.py` — generates the two static SVG charts embedded in
  `publications.html` (publications-per-year, keyword frequency).
- `style.css` — one stylesheet, dark-default theme with a light toggle (see
  `docs/DESIGN.md`).

**Never hand-edit `index.html`, `publications.html`, `cv.html`, or any
`papers/*.html` file directly** — they're regenerated from `papers.json` by
`generate.py` and any manual edit will be silently overwritten on the next
run. These generated files (plus `bibtex/*.bib`, `sitemap.xml`,
`robots.txt`) are **gitignored** — GitHub Actions builds them fresh on every
push to `main` and deploys straight from the runner's filesystem, so they
are never committed to this repo. Edit `papers.json` and/or
`generate.py`/`viz.py`/`style.css`, then run:

```bash
python generate.py   # local preview only — not required before pushing
```

## Project slash commands

`.claude/commands/` has three commands scoped to this repo:
`/rebuild` (regenerate + report status without committing), `/check-links`
(report which papers still lack a verified link, per `docs/LINK_RESEARCH.md`),
and `/add-paper` (add a new publication entry with the right schema).
`.claude/settings.json` allowlists a handful of read-only commands used
constantly in this repo (git status/log/diff, gh run/repo view,
`python generate.py`) — it deliberately does **not** allowlist
`git commit`/`git push`/`git add`, since auto-approving those would widen
standing permissions beyond what was explicitly asked for.

## Read before touching content

- **`docs/CONTENT_POLICY.md` — read this first if you're adding or editing
  anything about the site owner's current job.** The owner works on AI for
  semiconductor manufacturing at Samsung Electronics; this is a public site.
  Screen every new sentence in `experience`/`projects`/`bio` against that
  doc's checklist before committing. This is a hard gate, not a style
  preference.
- `docs/DESIGN.md` — design tokens, theme system, chart palette, why the
  three link badges are different colors. Follow it rather than
  reinventing a convention.
- `docs/DATA_SOURCES.md` — what's verified vs. still-missing in the
  publication data, and which lookup sources are reliable (ORCID API: yes;
  DBpia: mostly no, JS-rendered; ResearchGate: blocked/403).
- `docs/CONTENT_GUIDE.md` — the mechanics of adding a paper, a preprint PDF,
  or CV content.

## Working conventions established in this repo

- **Never fabricate a URL.** Every `official_link` in `papers.json` was
  added only after actually fetching the page and confirming
  title+authors+year match. If you can't verify a link, leave the field
  `null` — a wrong link is worse than a missing one, especially for a
  public academic identity site.
- Widths: content container is `1600px` max (widened twice from an initial
  `860px`, then `1180px`, both reported as too narrow for laptop/desktop
  screens) — don't shrink it back down.
- Site language is English throughout the UI (nav, badges, section
  headers) — the CV/papers are in English and the audience is
  international academic readers via Google Scholar. Korean paper titles
  stay in Korean (with an English `title_en` translation shown beneath) since
  that's how they were actually published, but everything else on the page
  (labels, buttons, intro copy) is English. This repo's own maintenance
  docs (this file, `README.md`, `docs/*.md`) are written in Korean/English
  as fits the human maintainer — that's a separate decision from the
  site's own UI language.
- Theme: dark is the default, light is a toggle (not the other way around).
- When adding a new publication category or badge type, update
  `CATEGORY_LABELS`/`CATEGORY_ORDER` in `generate.py` and the legend in
  `render_publications()` together — don't let them drift out of sync.
