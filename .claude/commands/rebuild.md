Regenerate the static site from `papers.json` and report what changed.

1. Run `python generate.py` and show its output verbatim (it prints the
   total paper count and lists any papers still missing an official link
   or preprint PDF).
2. Run `git status --short` to show what changed (remember: generated HTML/
   BibTeX/sitemap are gitignored — see `.gitignore` — so they won't show up
   here; only `papers.json`, source files, or files under `papers/pdfs/`
   should appear).
3. Do NOT commit or push automatically — just report status and wait for
   the user to confirm before committing.
