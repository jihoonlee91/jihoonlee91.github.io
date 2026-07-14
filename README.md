<div align="center">

# Jihoon Lee

**Aerospace GNC · UAV Control · Semiconductor / Industrial AI**

[![Live Site](https://img.shields.io/badge/live%20site-jihoonlee91.github.io-1d4ed8?style=flat-square)](https://jihoonlee91.github.io)
[![Build and deploy](https://img.shields.io/github/actions/workflow/status/jihoonlee91/jihoonlee91.github.io/build.yml?branch=main&label=build%20%26%20deploy&style=flat-square)](https://github.com/jihoonlee91/jihoonlee91.github.io/actions/workflows/build.yml)
[![Publications](https://img.shields.io/badge/publications-43-15803d?style=flat-square)](https://jihoonlee91.github.io/publications.html)
[![Google Scholar](https://img.shields.io/badge/Google%20Scholar-profile-4285F4?style=flat-square&logo=googlescholar&logoColor=white)](https://scholar.google.co.kr/citations?user=vNY8rPEAAAAJ)

</div>

---

Personal homepage — publications, CV, and contact info. This repo
**is** a static site generator, not a hand-built site: `papers.json` is the
only source of truth committed to git. `generate.py` + `viz.py` build
`index.html`, `publications.html`, `cv.html`, per-paper pages, BibTeX,
sitemap, and robots.txt from it — **those generated files are build output,
not source, and are gitignored** (see `.gitignore`). GitHub Actions builds
them fresh on every deploy; running `generate.py` locally is just for
previewing in a browser before you push.

```
papers.json  →  generate.py + viz.py  →  index.html / publications.html / cv.html   (gitignored)
                                          papers/<slug>.html   (Google Scholar meta tags, gitignored)
                                          bibtex/<slug>.bib    (gitignored)
                                          sitemap.xml, robots.txt (gitignored)
```

Only `papers.json`, `papers/pdfs/*.pdf` (self-hosted preprints), `assets/`,
and the Python/CSS source are committed.

## Quick start

```bash
# after editing papers.json
python generate.py   # optional — just to preview locally, e.g. open index.html
git add -A && git commit -m "..." && git push
```

Pushing to `main` triggers `.github/workflows/build.yml`, which runs
`generate.py` on GitHub's runner and deploys the result to GitHub Pages — you
never need to commit generated HTML/BibTeX yourself.

## Documentation

| Doc | Covers |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Start here if you're an AI assistant working on this repo |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Design tokens, dark/light theme system, chart color palette |
| [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md) | How to add/edit a publication, upload a preprint PDF, edit CV content |
| [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) | Where every field came from (Scholar, ORCID, weebly, DBpia) and what's still unverified |
| [`docs/CONTENT_POLICY.md`](docs/CONTENT_POLICY.md) | **Confidentiality checklist — read before adding anything about current employer work** |
| [`docs/LINK_RESEARCH.md`](docs/LINK_RESEARCH.md) | Runbook for using research agents to find official links for the remaining papers |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Ideas not yet done — check here before proposing something that might already be planned |

## Status

- ~24 domestic conference papers (mostly 2015–2018) have no verified public
  link yet — see `docs/DATA_SOURCES.md` for what's been tried and why DBpia
  lookups mostly failed (JS-rendered listings).
