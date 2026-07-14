# Content Policy — Confidentiality Check Before Publishing

This site is public and indexed by search engines. The site owner is a Staff
Engineer at Samsung Electronics working on AI systems for semiconductor
manufacturing (V-NAND, DRAM, HARC etch process AI). **Any content added to
this repo about that work must be screened for confidential/trade-secret
material before it is committed or pushed**, because a `git push` here is a
public disclosure with no way to fully retract it (search engines and forks
cache it).

## Rule

Before adding or editing any text that touches current employer work
(`experience`, `projects`, `bio`, `skills`, or any new section) in
`papers.json`, check every new sentence against this list. If unsure, leave
it out or generalize it — do not guess.

**Never include:**

- Specific process recipe parameters, defect/yield numbers, or specification
  values (e.g. exact etch rates, target percentages, tolerance bands).
- Internal tool, model, pipeline, or system codenames that aren't already
  public.
- Customer names, internal project codenames, or unreleased product/node
  names (e.g. an unannounced process node).
- Screenshots, diagrams, or descriptions detailed enough to reconstruct a
  proprietary process or system architecture.
- Anything marked or historically treated as confidential in internal
  documents, even if it seems minor.

**Generally safe (already reflected in this site as of 2026-07):**

- High-level domain area: "V-NAND / DRAM-related processes, HARC etch
  applications" — a category label, not a specific recipe.
- Role/scope description in generic engineering-management language ("owns
  dataset construction, predictive modeling... leads ML development within a
  cross-functional project involving 20+ engineers").
- Public academic work (papers, dissertation) — normal academic disclosure
  rules apply instead, see [`DATA_SOURCES.md`](DATA_SOURCES.md).

## Process for new content

1. Draft the new `papers.json` text.
2. Re-read it sentence by sentence against the "never include" list above.
3. If any sentence names a specific number, tool, customer, or unreleased
   product — cut it or ask the site owner to confirm it's already public
   before committing.
4. Only then run `python generate.py`, commit, and push.

This applies to future Claude Code sessions working on this repo as much as
to the human owner — see the reminder in [`CLAUDE.md`](../CLAUDE.md).
