Add a new publication to `papers.json`.

Ask the user (if not already given) for: title, authors (full names,
comma-separated), venue, year, category
(`int-journal`/`domestic-journal`/`int-conference`/`domestic-conference`/
`thesis`), and — if the title is in Korean — an English translation for
`title_en`.

Steps:
1. Generate a `slug`: lowercase, hyphenated, starting with the year if
   known (e.g. `2026-example-paper-title`). Must be unique against existing
   slugs in `papers.json`.
2. Add the entry to the `papers` array with `citations: 0`, `doi: null`,
   `abstract: ""`, `official_link: null`, and
   `pdf: "papers/pdfs/<slug>.pdf"` — matching the schema of existing
   entries (see `docs/CONTENT_GUIDE.md` for the full field reference).
3. Try to find a real official link via the ORCID API first
   (`https://pub.orcid.org/v3.0/0000-0001-5327-824X/works`) before asking
   the user or spawning a research agent — see `docs/LINK_RESEARCH.md`.
4. Run `python generate.py` to confirm it builds without errors and shows
   up in the right category section.
5. Remind the user this repo doesn't commit generated output (see
   `.gitignore`) — only `papers.json` (and a PDF under `papers/pdfs/` if
   they have one) needs to be committed and pushed.
