# Data Sources & Verification Status

This document records publication provenance and the current verification
baseline. It distinguishes a discovery source from the final page or file that
the public site links to.

## Publication list

- **Base list:** the owner's Google Scholar profile
  (`https://scholar.google.co.kr/citations?user=vNY8rPEAAAAJ`), 43 entries in
  total. Scholar is useful for discovery and citation counts, but scraped
  Korean titles may be garbled and are not accepted without another source.
- **Titles, authors, venues, and categories:** cross-checked against the
  owner's former publication page, publisher/proceedings metadata, DBpia,
  Crossref where available, and the owner's corrections. The current list has
  43 records.
- **Dissertation:** the owner's CV confirms the degree as Ph.D.; the public
  full-text record is the SNU dCollection repository page.

## What counts as a publication-source link

`papers.json` retains the field name `official_link` for compatibility. The
public interface instead labels the link by its actual destination, such as
`IEEE Xplore`, `AIAA ARC`, `DBpia`, or `EUCASS`.

The stored URL must be the final useful destination:

1. final publisher article page;
2. final proceedings paper or archive PDF;
3. final scholarly-database article page, such as DBpia or Informit; or
4. full-text institutional repository page for a thesis.

DOI resolvers, RISS hand-off pages, laboratory index pages, Google Scholar,
ResearchGate, Semantic Scholar, and search-result pages may be used to discover
a record, but are not stored when a deeper final destination exists.
`generate.py` rejects known intermediate/discovery hosts in `official_link`.

Before accepting a link, verify the title, authors, venue, and year against the
target record. A plausible URL or search snippet alone is insufficient.

## Current source coverage (verified 2026-07-16)

| Final destination | Papers |
|---|---:|
| DBpia | 18 |
| IEEE Xplore | 6 |
| AIAA ARC | 2 |
| EUCASS | 2 |
| ICAS Archive | 2 |
| SAGE Journals | 1 |
| ScienceDirect | 1 |
| MDPI | 1 |
| SpringerLink | 1 |
| SNU dCollection | 1 |
| IPNT Proceedings | 1 |
| SASE Proceedings | 1 |
| Informit | 1 |
| **Publication-source links** | **38** |

The remaining five publications have exact, verified local Author PDFs:

- `2021-optimal-policy-pitch-hold-milp-conf`
- `2018-frequency-apportioned-control-allocation`
- `2016-nn-carrier-landing-risk-assessment-ko`
- `2015-stochastic-risk-wave-off-decision`
- `2015-autonomous-uav-takeoff-landing-carrier`

One additional paper, `2021-target-tracking-laser-rangefinder`, has both an
IEEE Xplore source link and a local Author PDF. Therefore:

- 38 papers have a publication-source link;
- 6 local Author PDF files exist, including 1 that supplements a source link;
- 5 papers rely on an Author PDF as their only public copy; and
- all 43 papers have at least one public access path (**43/43 coverage**).

There are currently no unresolved link-only records and no active need to use
the `No Public Link Yet` state.

## Abstracts

- **18 of 43** records currently contain a verified abstract.
- **25 of 43** intentionally have a blank abstract.
- Abstract text was accepted only from a source record tied to the exact paper
  or from the paper itself. Korean and English abstracts are preserved
  separately when both were published.
- A blank abstract is a valid checked state. Never fabricate an abstract,
  translate one without marking that work, or paraphrase an abstract from the
  title simply to increase coverage.

## Discovery sources used during the audit

- ORCID public API, Crossref, and exact-title Semantic Scholar records for DOI,
  bibliographic metadata, or abstract discovery.
- Publisher sites and IEEE/AIAA/SAGE/ScienceDirect/MDPI/Springer records.
- ICAS, EUCASS, IPNT, and SASE proceedings archives.
- DBpia article pages for Korean journal and conference records.
- RISS, the former FDCL laboratory site, Scholar, and general web search for
  discovery only; the site follows through to the deeper destination.
- The owner's local paper archive for the five records that lack a public
  individual proceedings page.

Some publisher sites apply browser or bot checks. In those cases, metadata was
cross-checked through the publisher's visible record, Crossref/ORCID, and the
paper itself rather than treating an automated HTTP status as proof that a link
was invalid.

## arXiv and code repositories

All 43 titles were checked against arXiv, Semantic Scholar external IDs, and
paper-title GitHub searches. No paper-specific arXiv record or explicitly
cited code repository was confirmed. Several of the owner's repositories are
topically related to morphing-aircraft control, but they are not attached to an
individual paper unless the owner confirms that relationship; see
[`ACTION_ITEMS.md`](ACTION_ITEMS.md).

## Profile and CV data

- Name, affiliation, bio, experience, education, awards, skills, email,
  location, and Life text were provided or corrected directly by the owner.
- The profile photo originated from the owner's former site.
- Scholar, ORCID, ResearchGate, LinkedIn, GitHub, Instagram, and Facebook URLs
  were supplied by the owner.
- Employer-related content must also pass
  [`CONTENT_POLICY.md`](CONTENT_POLICY.md), regardless of who supplied it.
