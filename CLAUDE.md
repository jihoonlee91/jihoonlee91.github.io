# CLAUDE.md

Guidance for Claude Code sessions working in this repo.

## Hard rule: no job-search / immigration content, ever, in this repo

**Never add anything to this repo — file content, commit message, or
docs/*.md note — that relates to a job application, an employer the owner
is applying to or interviewing with, or an immigration/visa process.**
This includes material sourced from the owner's personal career-document
folders (resumes prepared for a specific application, application-portal
files, petition drafts). If a file path or pasted content looks like it's
from one of those folders, don't pull content from it into this repo —
ask the owner to paste just the specific fact needed instead. This is a
standing rule regardless of whether the repo is currently public or
private (see below) — a private repo can flip back to public, and old
commits are easy to miss when that happens. Violating this once already
required a force-push history rewrite; don't create a second one.

## Repo visibility

This repo is **currently private** (owner's call, so drafts don't become
instant public disclosures — see `docs/CONTENT_POLICY.md`). Don't assume
it's public, and don't assume it'll stay private either — always write
content as if it could go public at any time. Making it public again is
the owner's decision alone; don't suggest or attempt it.

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
- `wiki.json` — public wiki-note metadata and structured note content.
- `generate.py` — reads `papers.json`, writes `index.html`,
  `publications.html`, `cv.html`, `wiki.html`, `wiki/<slug>.html`, `life.html`, `papers/<slug>.html` per
  paper, `bibtex/*.bib`, `sitemap.xml`, `robots.txt`.
- `viz.py` — generates the three static SVG charts embedded in
  `publications.html` (publications-per-year, citations-per-year, keyword
  word cloud).
- `style.css` — one stylesheet, dark-default theme with a light toggle (see
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
(report which papers still lack a verified link, per `docs/LINK_RESEARCH.md`),
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
