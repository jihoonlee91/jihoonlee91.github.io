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
  call, not an inference from the CV. **Explicitly not inferred from the
  owner's private career documents**. Those describe intent in a different,
  non-public context; publishing anything derived from them without explicit
  permission could have professional consequences. Wait for the owner to state
  this directly.
- **Side projects section** — explicitly wanted (see conversation history)
  but nothing exists yet. Don't create a placeholder/empty section; add it
  only once there's an actual project (title, description, stack, link).
- **Abstracts still missing for 25/43 papers** — same two research passes
  filled in 18/43 with verified text. The other 25 remain intentionally blank;
  a blank abstract is preferable to a title-derived paraphrase. Add one only
  when exact text is available from the paper or a record tied to that paper.
- **Patents** — add only independently public records after applying
  `docs/CONTENT_POLICY.md`; do not add non-public employer context.
- **Talks/presentations** — conference talks, the 2016 Grand Prize
  presentation, internal tech talks (non-confidential), etc.
- **Now/Currently blurb** — a short "what I'm focused on right now" line,
  refreshed periodically so the site doesn't look frozen at PhD graduation.
  Considered but not built — needs the owner to actually say what's current.

## Technical/SEO gaps (no new content needed, just implementation)

- **Custom domain** — currently `jihoonlee91.github.io`; if the owner ever
  buys a personal domain, `docs/DESIGN.md`/`README.md` would need a CNAME
  file and a DNS note (see the earlier conversation about this trade-off —
  the repo would need to change if a root-domain-per-repo name change is
  desired instead).
- **Korean-language toggle** — the site is English-only by design (see
  `CLAUDE.md`), but if Korean-speaking recruiters/visitors become a bigger
  audience, a `/ko/` mirror or a language switcher could be considered
  later. Not planned now — would roughly double the maintenance surface.
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

- ~~Explicit "why GNC/UAV control transfers to industrial AI" sentence~~ —
  done (see `papers.json` `bio`), sourced from the owner's own resume
  materials but rewritten generic — no employer name, team, or numbers
  carried over per `docs/CONTENT_POLICY.md`.
- **Explicit collaboration call-to-action** — e.g. "Open to collaborating
  on X, Y, Z — reach out at [email]" rather than expecting a visitor to
  infer openness from a CV. Doubles as the "Open to" line already listed
  above.
- **Quantified outcomes where independently publishable** — use only metrics
  already public or explicitly cleared for external disclosure. Never infer,
  estimate, or expose internal performance, workload, or scope figures; see
  `docs/CONTENT_POLICY.md`.
- **A "selected work" or case-study section distinct from Publications** —
  2-4 short write-ups (problem → approach → outcome) would show
  production/deployment thinking that a pure publication list can't. Gated
  by `docs/CONTENT_POLICY.md` for anything connected to employer work.
- **Backlinks from owned profiles** — the owner should set the "homepage"
  field on the Google Scholar profile, ResearchGate, and any lab page they
  can edit to point back to this site. This can't be done from this repo;
  it's an action item for the owner on those platforms.

## Content/structure ideas considered but intentionally not done (yet)

- **Wiki/notes section** — generator support is implemented but `wiki.json` is
  currently empty, so no Wiki tab or page is published. Add a future note only
  when there is substantive public content; keep employer-confidential and
  personal evidence outside the public repository.

## Already done (for reference — don't re-suggest these)

Identity tag, unified timeline (now grouped by org/school so a multi-year
stint at one place shows as one branch, not N repeated dots — includes a
special-cased merge of the PhD-education entry with its lab-experience
entry when they share the exact same period), category/theme toggle on
Publications (theme list later split from 4 to 6 — see `docs/DESIGN.md`),
Frequent Collaborators, dark/light theme, responsive 1200px layout, icon+text social
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
Publications / CV / **Life**) with per-hobby sections, and publication-source/
BibTeX/Author-PDF hover previews so a visitor can see where a link goes before
clicking.
The "Tech Stack" chip row that used to sit on Home was removed — it
duplicated the Skills section on the CV page and visually collided with
the interests tags right above it. See git log / other docs for detail.

A `cv.html` print stylesheet
(`@media print` in `style.css`), and a proper landscape OG/Twitter card
(`assets/og-card.png`, 1200×630, generated via a headless-browser screenshot
of a themed HTML card rather than hand-drawn — see git log). The arXiv/code
research pass for all 43 papers came back negative for every paper (see
`docs/DATA_SOURCES.md`) — don't re-run without new information.

Publication access coverage is also complete: 38 papers have a verified final
publication-source link and the other 5 have a verified Author PDF (43/43).
