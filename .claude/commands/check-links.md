Report the current state of official links / preprint PDFs across all
publications in `papers.json`.

1. Run `python generate.py` and read its "still have no official link / PDF"
   output.
2. For each paper still missing a link, show: slug, title, category, year.
3. Read `docs/LINK_RESEARCH.md` for the reliability-ranked source list and
   the reusable agent prompt template.
4. If the user wants another research round, offer to fan out parallel
   Agent calls (3-4 papers per agent) following that runbook — but do not
   spawn agents unless the user confirms, since each round costs real time/
   tokens for often-diminishing returns (most easy hits have already been
   found; remaining ones are the hardest cases).
5. Never fabricate a URL. Any link an agent reports must have been actually
   fetched and verified (title + authors + year match) before it goes into
   `papers.json` — see `docs/CONTENT_GUIDE.md` and `docs/LINK_RESEARCH.md`
   for the exact rule.
