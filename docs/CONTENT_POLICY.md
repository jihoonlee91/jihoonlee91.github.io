# Content Policy — Confidentiality Check Before Publishing

**Repository and site status (2026-07-16): public.** Source files,
documentation, commit history, and the generated GitHub Pages site can all be
read, indexed, cached, or copied by third parties. A detail is public even when
it exists only in `papers.json` or `docs/` and is not rendered on the website.
Treat every push to `main` as an immediate publication event.

## Rule

Before adding or editing employer-related content in `experience`, `projects`,
`bio`, `skills`, documentation, assets, or any new section, review it sentence
by sentence against this policy. Public portfolio text should describe the
professional domain and contribution at a high level; it must not explain the
employer's non-public data, process, workflow, validation, or decision logic.

### Never include

- Process recipe parameters, defect/yield figures, specification values,
  tolerance bands, or other non-public performance metrics.
- Internal tool, model, pipeline, system, project, or product codenames.
- Customer names, unreleased products, process nodes, roadmaps, or schedules.
- Screenshots, diagrams, code, prompts, or prose detailed enough to reconstruct
  a proprietary system, model, process, or operating procedure.
- Anything marked confidential or historically treated as confidential in
  internal documents, repositories, meetings, or messages.
- Non-public dataset names, field names, feature names, data-source lists, or
  **taxonomies of data categories**, unless the employer has already published
  that exact classification.
- Non-public **workflow or pipeline stages**, including any ordered description
  of internal data handling, validation, hand-off, or decision-support work.
- Validation criteria, decision rules, acceptance gates, operational pain
  points, or descriptions of how engineering work is performed internally.
- Exact counts of internal requests, sources, systems, people, experiments, or
  similar operational scope. A rounded `N+` figure may be used only when the
  owner has explicitly reviewed that individual statement and it does not
  reveal confidential scale or activity.

## Owner-approved organization-name exception

The owner has explicitly chosen to publish the Samsung Electronics
sub-organization names **Digital Twin Center**, **Mechatronics Research**, and
**Memory Manufacturing Technology Center** in the Experience timeline. This is
a narrow display choice, not evidence of employer approval and not a general
exception to this policy.

In particular, publishing an organization name does **not** authorize any
dataset taxonomy, workflow sequence, validation method, decision rule,
architecture detail, operational issue, internal metric, or unpublished
project description associated with that organization. Those details remain
prohibited even when the organization itself is named.

## Suitable public content

- Public academic work, including papers, proceedings records, and the
  dissertation; follow the provenance rules in [`DATA_SOURCES.md`](DATA_SOURCES.md).
- Independent open-source projects and personal research that do not use or
  derive from employer information, resources, code, data, or work product.
- Employer, approved organization name, public job title, and dates.
- High-level role summaries such as developing AI and software for complex
  semiconductor engineering applications, provided they do not expose the
  restricted details above.
- Broad, transferable capabilities already evident from public work, such as
  machine learning, optimization, software engineering, and cross-functional
  collaboration.

## Publishing checklist

1. Review the complete diff, including JSON, documentation, images, and files
   that are not rendered on the website.
2. Remove or generalize non-public names, categories, workflow steps, methods,
   metrics, problems, and outcomes.
3. Verify every factual claim that relies on a public source and retain the
   final source-of-record URL where appropriate.
4. Run `python generate.py` and inspect the generated pages.
5. Commit and push only after the public-site and public-repository views both
   pass this review.

When the boundary is unclear, omit the detail until the owner can confirm that
the employer has already made it public. This policy also applies to future AI
assistant sessions; see [`CLAUDE.md`](../CLAUDE.md).
