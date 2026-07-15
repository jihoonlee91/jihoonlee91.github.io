# Content Policy — Confidentiality Check Before Publishing

This site and its Git history are public and may be indexed or copied. **Do
not publish substantive descriptions of current or former employer work.** A
`git push` is a public disclosure that cannot be assumed retractable because
search engines, caches, and forks may retain it.

## Rule

Before adding or editing any text that touches employer work
(`experience`, `projects`, `bio`, `skills`, or any new section) in
`papers.json`, apply this policy. If unsure, leave it out; generalization is
not sufficient when the underlying fact is not cleared for publication.

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
- Employer organization names below the public company level, team scope,
  staffing, timelines, responsibilities, project outcomes, and business
  impact unless the employer has independently made the exact fact public.
- Non-public datasets, data sources, workflows, validation practices,
  operational problems, or descriptions of how work is performed.

**Allowed public content:**

- Public academic work (papers, dissertation) — normal academic disclosure
  rules apply instead, see [`DATA_SOURCES.md`](DATA_SOURCES.md).
- Independent open-source projects and personal research that do not use or
  derive from employer information, resources, code, data, or work product.
- A minimal generic role label only when the owner has explicitly chosen to
  publish it. Do not infer responsibilities from that label.

## Process for new content

1. Draft the new `papers.json` text.
2. Re-read it sentence by sentence against the "never include" list above.
3. Remove employer names, sub-organizations, products, project descriptions,
   numbers, tools, data, outcomes, and non-public responsibilities.
4. Only then run `python generate.py`, commit, and push.

This applies to future Claude Code sessions working on this repo as much as
to the human owner — see the reminder in [`CLAUDE.md`](../CLAUDE.md).
