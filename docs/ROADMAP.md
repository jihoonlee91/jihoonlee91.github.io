# Roadmap / Ideas Not Yet Done

Things worth doing next, roughly grouped. None of these are committed to —
this is a parking lot so ideas don't get lost between sessions, not a
promise. Cross off / delete an item once it's actually done rather than
leaving it stale here. See `CLAUDE.md`'s "Who this site is for" section
before adding anything — check a new idea serves recruiters and
collaborators too, not just an academic-reader lens.

## Needs real content from the site owner (don't fabricate)

- **"Open to" / availability line** — recruiters and potential
  collaborators both benefit from a one-line signal of what the owner is
  open to right now (e.g. consulting, collaboration, not job-hunting,
  open to X). Don't guess this — it changes over time and is the owner's
  call, not an inference from the CV.
- **Side projects section** — explicitly wanted (see conversation history)
  but nothing exists yet. Don't create a placeholder/empty section; add it
  only once there's an actual project (title, description, stack, link).
- **Remaining 8 publications with no link** — mostly 2015–2018 domestic
  conference papers DBpia/RISS/FDCL couldn't confirm. Either find them via
  another `/check-links` round, or the owner uploads preprint PDFs directly
  to `papers/pdfs/`.
- **Patents** — if any exist from the Samsung role, run them through
  `docs/CONTENT_POLICY.md`'s checklist before adding anything.
- **Talks/presentations** — conference talks, the 2016 Grand Prize
  presentation, internal tech talks (non-confidential), etc.
- **Now/Currently blurb** — a short "what I'm focused on right now" line,
  refreshed periodically so the site doesn't look frozen at PhD graduation.
  Considered but not built — needs the owner to actually say what's current.

## Technical/SEO gaps (no new content needed, just implementation)

- **No favicon** — every page currently has none; add one (simple
  monogram or a small logo) via `<link rel="icon">` in each page's `<head>`.
- **No Open Graph / Twitter Card meta tags** — sharing a link to this site
  in Slack/Twitter/LinkedIn currently renders with no preview image/
  description. Add `og:title`, `og:description`, `og:image` (profile
  photo), `og:url`, and `twitter:card` to every page's `<head>`.
- **No structured data (JSON-LD)** — a `schema.org/Person` block on the
  homepage (name, affiliation, sameAs: [scholar/orcid/linkedin/github
  URLs]) and `schema.org/ScholarlyArticle` on each paper page would help
  Google understand the site beyond plain HTML and could improve how it
  shows up in search results / Google Scholar's own crawling.
- **No print stylesheet for `cv.html`** — a `@media print` block hiding the
  nav/footer and tightening spacing would let a visitor "print to PDF" a
  clean CV directly from the browser, without needing a separately
  maintained CV PDF.
- **Custom domain** — currently `jihoonlee91.github.io`; if the owner ever
  buys a personal domain, `docs/DESIGN.md`/`README.md` would need a CNAME
  file and a DNS note (see the earlier conversation about this trade-off —
  the repo would need to change if a root-domain-per-repo name change is
  desired instead).
- **Korean-language toggle** — the site is English-only by design (see
  `CLAUDE.md`), but if Korean-speaking recruiters/visitors become a bigger
  audience, a `/ko/` mirror or a language switcher could be considered
  later. Not planned now — would roughly double the maintenance surface.

## Content/structure ideas considered but intentionally not done (yet)

- **Notes/writing section** — Chris Olah-style low-pressure short posts.
  Requires the owner to actually write something; don't scaffold an empty
  "Notes" nav item ahead of having a first post, it'll just look unfinished.
- **Word cloud for keywords** — explicitly discussed and rejected in favor
  of the current horizontal bar chart (word clouds don't allow precise
  comparison — see `docs/DESIGN.md` / the dataviz skill). A treemap was
  offered as a more legitimate alternative if the bar chart ever feels
  insufficient.

## Already done (for reference — don't re-suggest these)

Identity tag, unified timeline, category/theme toggle on Publications,
Frequent Collaborators, dark/light theme, 1600px layout, icon+text social
badges, BibTeX volume/number/pages + cross-file key dedup, Tech Stack chips
on Home, "Currently" role pill. See git log / other docs for detail.
