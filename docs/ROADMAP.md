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
  conference papers DBpia/RISS/FDCL couldn't confirm. Two separate research
  passes (see git log) both came back empty for these specific 8 — DBpia/
  RISS genuinely have no page for them, not just a fetch/JS-rendering
  issue. Unlikely to be findable by another automated pass; needs the
  owner to upload a preprint PDF directly to `papers/pdfs/` if they still
  have a copy, or confirm there's truly nothing public to link.
- **Abstracts still missing for 25/43 papers** — same two research passes
  filled in 18/43 with verified text (CrossRef, Semantic Scholar, DOAJ,
  RISS, publisher pages); the other 25 are confirmed genuinely unavailable
  (DBpia/RISS pages with no abstract on file, AIAA ARC's bot-challenge
  page, or papers with no `official_link` at all) — not just "couldn't
  fetch." Same owner-upload path as above is the only way forward for most
  of these.
- **Patents** — if any exist from the Samsung role, run them through
  `docs/CONTENT_POLICY.md`'s checklist before adding anything.
- **Talks/presentations** — conference talks, the 2016 Grand Prize
  presentation, internal tech talks (non-confidential), etc.
- **Now/Currently blurb** — a short "what I'm focused on right now" line,
  refreshed periodically so the site doesn't look frozen at PhD graduation.
  Considered but not built — needs the owner to actually say what's current.

## Technical/SEO gaps (no new content needed, just implementation)

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
- **Non-square profile photo used as OG/Twitter image** — `assets/profile.jpg`
  is 142×189 (portrait), not the recommended ~1200×630 landscape OG card.
  Works fine as-is but a proper landscape "og-card.png" (name + tagline
  over a clean background) would look better in link previews. Needs image
  editing not available in this environment — flagging for the owner or a
  future session with image tooling.
- **`apple-touch-icon`** — not added (needs a proper square PNG; the
  profile photo isn't square and `favicon.svg` alone covers modern
  browsers/bookmarks fine per current research, see git history for the
  research findings this is based on).

## Recruiter- and collaborator-facing content gaps (research-backed, need owner input)

Three rounds of research (recruiter-scanning behavior, academic-collaborator
discovery, and general personal-site benchmarking — see git log around
"multiple research rounds" commits for full findings) converged on the same
few gaps. None of these can be fabricated — they need the owner's actual
input:

- **Explicit "why GNC/UAV control transfers to industrial AI" sentence.**
  Recruiters unfamiliar with control theory won't infer the connection
  themselves — the bio should say it outright, not imply it. Currently
  hinted at but not spelled out as its own callout.
- **Explicit collaboration call-to-action** — e.g. "Open to collaborating
  on X, Y, Z — reach out at [email]" rather than expecting a visitor to
  infer openness from a CV. Doubles as the "Open to" line already listed
  above.
- **Quantified outcomes wherever possible** — recruiters and collaborators
  both respond more to "reduced X by Y%" than a bare list of
  responsibilities. Needs real numbers from the owner; do not estimate or
  round from vague statements.
- **A "selected work" or case-study section distinct from Publications** —
  2-4 short write-ups (problem → approach → outcome) would show
  production/deployment thinking that a pure publication list can't. Gated
  by `docs/CONTENT_POLICY.md` for anything about the Samsung role.
- **Per-paper code/data links or arXiv/green-OA mirrors**, where they
  actually exist — cited as the single most concrete signal a paper is
  reusable, and would independently improve citation counts for older
  aerospace-venue papers. Needs a research pass to check which of the 43
  papers actually have a public code repo or preprint mirror — don't
  assume none exist without checking.
- **Backlinks from owned profiles** — the owner should set the "homepage"
  field on the Google Scholar profile, ResearchGate, and any lab page they
  can edit to point back to this site. This can't be done from this repo;
  it's an action item for the owner on those platforms.

## Content/structure ideas considered but intentionally not done (yet)

- **Notes/writing section** — Chris Olah-style low-pressure short posts.
  Requires the owner to actually write something; don't scaffold an empty
  "Notes" nav item ahead of having a first post, it'll just look unfinished.

## Already done (for reference — don't re-suggest these)

Identity tag, unified timeline (now grouped by org/school so a multi-year
stint at one place shows as one branch, not N repeated dots — includes a
special-cased merge of the PhD-education entry with its lab-experience
entry when they share the exact same period), category/theme toggle on
Publications (theme list later split from 4 to 6 — see `docs/DESIGN.md`),
Frequent Collaborators, dark/light theme, 1600px layout, icon+text social
badges with real per-platform brand marks and colors (replaced the earlier
initials-in-a-circle placeholder), BibTeX volume/number/pages + cross-file
key dedup, BibTeX click-to-copy with a hover preview of the entry text,
"Currently" role pill, favicon, Open Graph/Twitter Card tags, schema.org
Person+ProfilePage JSON-LD with sameAs links, canonical tags, citations-
by-year chart, keyword word cloud (word clouds were earlier rejected here
in favor of a bar chart on precision-of-comparison grounds — the owner
explicitly asked for the word cloud anyway in a later session; the bar
chart's imprecision concern was judged an acceptable trade-off once
title+abstract text gave it more words to draw from), a Life page (Home /
Publications / CV / **Life**) with per-hobby sections, and DOI/BibTeX/PDF
link hover previews so a visitor can see where a link goes before clicking.
The "Tech Stack" chip row that used to sit on Home was removed — it
duplicated the Skills section on the CV page and visually collided with
the interests tags right above it. See git log / other docs for detail.
