# Content Policy — Confidentiality Check Before Publishing

**Repo status (2026-07-16): private.** The owner set this repo private
deliberately, to work on content without every draft being an instant public
disclosure, and intends to review everything before flipping it back to
public. While private, drafting is not itself a publication event — but
still write as if it could go public at any moment, since the point of the
review pass is catching mistakes, not relying on privacy as the actual
safety net. Treat `git push` to a private repo as reversible-with-review, not
as consequence-free.

**Do not publish substantive descriptions of current or former employer
work** once the repo is public again. Before that point, a `git push` here
stays within GitHub's private-repo boundary (only the owner and anyone they
explicitly grant access to can see it) — it is not the same event as a push
to a public repo, which search engines, caches, and forks can retain
permanently.

## Rule

Before adding or editing any text that touches employer work
(`experience`, `projects`, `bio`, `skills`, or any new section) in
`papers.json`, apply this policy. The owner has said not to over-apply this
by default — they're reviewing everything before it goes public again, so
don't strip detail preemptively out of caution alone. The "never include"
list below is the actual hard line (real trade secrets, unreleased product
info, customer names); everything else is a normal editorial judgment call,
not a compliance gate.

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
- Non-public datasets, data sources, workflows, validation practices,
  operational problems, or descriptions of how work is performed.
- Exact/precise counts (e.g. "37 requests", "14 data sources") — round
  figures like "20+", "30+" are the owner's explicitly authorized ceiling
  (see the exception below); anything more precise than that is still off
  limits.

**Exception, set explicitly by the site owner (2026-07-15):** internal
sub-organization names at Samsung Electronics (e.g. "Digital Twin Center",
"Mechatronics Research", "Memory Manufacturing Technology Center") and
rounded, non-precise scope figures (team size, request counts, data-source
counts, expressed as "N+") **may** appear in `experience` entries — the
owner reviewed this specific content and asked for it to stay, overriding
the general "below public company level" rule above for this one section.
This does not extend to anything else on the "never include" list
(recipe/process parameters, unreleased product names, customer names,
proprietary architecture detail) — those remain hard-blocked regardless of
who asks, since they're the employer's information, not the owner's alone
to disclose.

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
