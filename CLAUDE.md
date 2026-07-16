# CLAUDE.md

Guidance for Claude Code sessions working in this repo.

## Hard rule: no job-search / immigration content, ever, in this repo

**Never add anything to this repo — file content, commit message, or
docs/*.md note — that relates to a job application, an employer the owner
is applying to or interviewing with, or an immigration/visa process.**
This includes material sourced from personal career-document folders, such as
application-specific resumes, portal files, or private legal documents. If a
file path or pasted content appears to come from one of those sources, do not
copy it into this repository; ask the owner to provide only the specific public
fact needed. Source files, documentation, and old commits can remain
discoverable even when a detail is not rendered on the site.

## Repo visibility

This repo and its GitHub Pages site are **public**. Treat every source file,
documentation edit, commit message, and push as a publication event; content
does not become private merely because the generator does not render it.
Changing repository visibility is the owner's decision alone.

## Who this site is for

Not a single-audience academic CV page. Three audiences need to be served
at once, and any new section/content decision should check it doesn't
serve one at the expense of the others:

- **General information sharing** — anyone who just wants to know who this
  person is, professionally.
- **Recruiters / hiring managers** — need current role, skills, experience,
  and contact info fast. This is why the "Currently" role pill, Tech Stack
  chips, and CV page exist and are kept prominent, not buried under the
  43-paper publication list.
- **Research collaborators / academic peers** — need the publication
  record, research themes, Scholar/ORCID links. This is most of the
  content by volume, but shouldn't crowd out the other two audiences —
  see the earlier decision to stop calling this an "academic homepage" and
  the benchmarking-driven additions (identity tag, timeline, Tech Stack) in
  git history for how this tension has been handled so far.

## What this is

Jihoon Lee's personal homepage, served at
**https://jihoonlee91.github.io** via GitHub Pages from this repo
(`jihoonlee91/jihoonlee91.github.io`). The repo name must stay exactly
`<username>.github.io` — that's a GitHub Pages requirement for a root-domain
user site, not a naming choice to "fix".

It is a **static site generator**, not a hand-edited site:

- `papers.json` — the single source of truth (profile, CV, all 43
  publications).
- `wiki.json` — optional public wiki-note metadata and structured note content;
  it is currently empty, so no Wiki tab or page is published.
- `generate.py` — reads `papers.json`, writes `index.html`,
  `publications.html`, `cv.html`, `life.html`, `papers/<slug>.html` per paper,
  `bibtex/*.bib`, `sitemap.xml`, and `robots.txt`; it also writes `wiki.html`
  and `wiki/<slug>.html` when `wiki.json` has notes.
- `viz.py` — generates four Publications insight blocks: publications per
  year, venue statistics, citations per year, and the research-focus word
  cloud. Three use inline SVG; venue statistics use semantic HTML.
- `style.css` — one stylesheet, light-default theme with a dark toggle (see
  `docs/DESIGN.md`).

**Never hand-edit `index.html`, `publications.html`, `cv.html`, `wiki.html`, `life.html`,
or any `wiki/*.html` or `papers/*.html` file directly** — they're regenerated from `papers.json` and `wiki.json` by
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
(audit publication source/PDF coverage, per `docs/LINK_RESEARCH.md`),
and `/add-paper` (add a new publication entry with the right schema).
`.claude/settings.json` allowlists a handful of read-only commands used
constantly in this repo (git status/log/diff, gh run/repo view,
`python generate.py`) — it deliberately does **not** allowlist
`git commit`/`git push`/`git add`, since auto-approving those would widen
standing permissions beyond what was explicitly asked for.

## Read before touching content

- **`docs/CONTENT_POLICY.md` — read this first if you're adding or editing
  anything about the site owner's current or former employment.** This is a
  public site and repository. Do not publish substantive employer-work
  descriptions. This is a hard gate, not a style preference.
- `docs/DESIGN.md` — design tokens, theme system, chart palette, why the
  three link badges are different colors. Follow it rather than
  reinventing a convention.
- `docs/DATA_SOURCES.md` — verified publication provenance, final-link rules,
  and current 43/43 source/Author-PDF coverage.
- `docs/CONTENT_GUIDE.md` — the mechanics of adding a paper, an Author PDF,
  or CV content.

## Working conventions established in this repo

- **Never fabricate a URL.** Every `official_link` in `papers.json` must be
  the final publisher, proceedings, scholarly-database, or full-text
  repository destination and must match title+authors+year. DOI resolvers,
  RISS hand-off pages, lab pages, Scholar, and ResearchGate are discovery
  sources, not final links. If no final destination can be verified, leave the
  field `null` and use an exact Author PDF when self-hosting is permitted — a
  wrong link is worse than a missing one.
- Widths: content container is `1200px` max, reduced from `1600px` after a
  wide-desktop review to improve line length and information density.
- Site language is English throughout the UI (nav, badges, section
  headers) — the CV/papers are in English and the audience is
  international academic readers via Google Scholar. Korean paper titles
  stay in Korean (with an English `title_en` translation shown beneath) since
  that's how they were actually published, but everything else on the page
  (labels, buttons, intro copy) is English. This repo's own maintenance
  docs (this file, `README.md`, `docs/*.md`) are written in Korean/English
  as fits the human maintainer — that's a separate decision from the
  site's own UI language.
- Theme: light is the default; dark is available through the toggle.
- When adding a new publication category or badge type, update
  `CATEGORY_LABELS`/`CATEGORY_ORDER` in `generate.py` and the legend in
  `render_publications()` together — don't let them drift out of sync.
