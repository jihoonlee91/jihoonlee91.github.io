<div align="center">

# Jihoon Lee

**Aerospace GNC · UAV Control · Semiconductor / Industrial AI**

[![Live Site](https://img.shields.io/badge/live%20site-jihoonlee91.github.io-1d4ed8?style=flat-square)](https://jihoonlee91.github.io)
[![Build and deploy](https://img.shields.io/github/actions/workflow/status/jihoonlee91/jihoonlee91.github.io/build.yml?branch=main&label=build%20%26%20deploy&style=flat-square)](https://github.com/jihoonlee91/jihoonlee91.github.io/actions/workflows/build.yml)
[![Publications](https://img.shields.io/badge/publications-43-15803d?style=flat-square)](https://jihoonlee91.github.io/publications.html)
[![Google Scholar](https://img.shields.io/badge/Google%20Scholar-profile-4285F4?style=flat-square&logo=googlescholar&logoColor=white)](https://scholar.google.co.kr/citations?user=vNY8rPEAAAAJ)

</div>

---

Personal professional homepage and portfolio. The public site currently has
four primary sections: **Home**, **Publications**, **CV**, and **Life**.

This repository contains a small static-site generator rather than hand-edited
HTML. `papers.json` is the primary content source; `generate.py` and `viz.py`
build the site pages, per-paper pages, BibTeX files, sitemap, and robots.txt.
`wiki.json` is retained for optional future notes, but it is currently empty, so
no Wiki tab or Wiki page is published. Generated files are build output,
not source, and are gitignored (see `.gitignore`). GitHub Actions rebuilds them
for every deployment; running `generate.py` locally is only for previewing.

```
papers.json  ──────────┐
                         ├─→  generate.py + viz.py  ─→  index.html / publications.html / cv.html / life.html
wiki.json (optional) ──┘                                 papers/<slug>.html
                                                      bibtex/<slug>.bib + bibtex/all.bib
                                                      sitemap.xml + robots.txt
```

The maintained sources include `papers.json`, the optional `wiki.json`,
`papers/pdfs/*.pdf` (self-hosted author copies), `assets/`, documentation, and
the Python/CSS source. Generated HTML and BibTeX output are not committed.

## Quick start

```bash
# after editing papers.json
python generate.py       # optional local preview
git status --short       # review every public-repository change
git add papers.json      # add only the source files intentionally changed
git commit -m "..." && git push
```

Pushing to `main` triggers `.github/workflows/build.yml`, which runs
`generate.py` on GitHub's runner and deploys the result to GitHub Pages — you
never need to commit generated HTML/BibTeX yourself.

## Documentation

| Doc | Covers |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Start here if you're an AI assistant working on this repo |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Design tokens, dark/light theme system, chart color palette |
| [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md) | How to add/edit a publication, upload an Author PDF, and edit CV content |
| [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) | Publication provenance, source-link verification rules, and current coverage |
| [`docs/CONTENT_POLICY.md`](docs/CONTENT_POLICY.md) | **Confidentiality policy — read before adding anything about employment** |
| [`docs/LINK_RESEARCH.md`](docs/LINK_RESEARCH.md) | Historical runbook used to research publication source links |
| [`docs/SPORTS_RECORDS.md`](docs/SPORTS_RECORDS.md) | Competition and activity archive kept out of the public Life-page content |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Ideas not yet done — check here before proposing something that might already be planned |

## Status

- **43 publications total.**
- **38** have a verified final publication-source link (publisher,
  proceedings archive, scholarly database, or institutional repository).
- The other **5** have a verified self-hosted **Author PDF**; current public
  access coverage is therefore **43/43**.
- Six local Author PDF files exist in total: one supplements a paper that also
  has a publication-source link, while five provide the only public copy.
- `wiki.json` currently contains no notes, so the public navigation is
  **Home / Publications / CV / Life**.
