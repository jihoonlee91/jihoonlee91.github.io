"""Generate the full static site (Home / Publications / CV / Wiki / Life /
paper pages / BibTeX) from papers.json and wiki.json.

Run `python generate.py` after editing papers.json (e.g. adding an
official_link/doi, or dropping a PDF into papers/pdfs/) to rebuild the site.
A GitHub Actions workflow (.github/workflows/build.yml) runs this
automatically on every push to main.
"""
import hashlib
import html
import json
import os
import re
from collections import Counter
from urllib.parse import quote_plus, urlparse

import viz

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "style.css"), "rb") as f:
    # Normalize Git's platform-dependent line endings so local Windows
    # previews and the Linux Pages runner produce the same cache key.
    css_bytes = f.read().replace(b"\r\n", b"\n")
    STYLE_VERSION = hashlib.sha256(css_bytes).hexdigest()[:12]

with open(os.path.join(ROOT, "papers.json"), encoding="utf-8") as f:
    DATA = json.load(f)

with open(os.path.join(ROOT, "wiki.json"), encoding="utf-8") as f:
    WIKI_DATA = json.load(f)

NON_FINAL_SOURCE_HOSTS = {
    "doi.org",
    "dx.doi.org",
    "fdcl.snu.ac.kr",
    "riss.kr",
    "riss.or.kr",
    "linkinghub.elsevier.com",
    "semanticscholar.org",
    "researchgate.net",
    "scholar.google.com",
}

for paper in DATA["papers"]:
    source_host = urlparse(paper.get("official_link") or "").netloc.lower().removeprefix("www.")
    if source_host in NON_FINAL_SOURCE_HOSTS:
        raise ValueError(
            f'{paper["slug"]}: official_link must be the final publisher or full-text URL, not {source_host}'
        )

SITE_URL = "https://{}.github.io".format(
    DATA["github_url"].rstrip("/").rsplit("/", 1)[-1]
)

CATEGORY_LABELS = {
    "int-journal": "International Journal Articles",
    "domestic-journal": "Domestic Journal Articles",
    "int-conference": "International Conference Papers",
    "domestic-conference": "Domestic Conference Papers",
    "thesis": "Ph.D. Dissertation",
}
CATEGORY_ORDER = ["int-journal", "domestic-journal", "int-conference", "domestic-conference", "thesis"]

# These are intentionally curated rather than extracted from CV prose.  The
# chart combines durable professional focus areas with the publication corpus,
# without promoting incidental resume words such as job titles or workflow
# descriptions.  Scores set visual emphasis; paper-title/abstract frequencies
# are added separately in viz.keyword_chart().
CURATED_RESEARCH_FOCUS = [
    ("Semiconductor AI", 138),
    ("Machine Learning", 124),
    ("Engineering Software", 116),
    ("Aerospace GNC", 112),
    ("UAV Guidance & Control", 108),
    ("Morphing Aircraft", 104),
    ("Optimization", 96),
    ("Industrial AI", 84),
    ("Autonomous Systems", 78),
]

# Citation counts are a point-in-time snapshot rather than live data.  Prefer
# the date stored with that snapshot; the fallback keeps older data files
# renderable until they acquire the field.
CITATION_STATS_UPDATED = (DATA.get("citation_stats") or {}).get("updated") or "Jul 2026"

THEME_INIT_SCRIPT = """<script>
(function () {
  var saved = localStorage.getItem('theme');
  document.documentElement.setAttribute('data-theme', saved === 'dark' ? 'dark' : 'light');
})();
</script>"""

THEME_TOGGLE_SCRIPT = """<script>
function toggleTheme() {
  var html = document.documentElement;
  var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

function copyBibtex(el, ev) {
  var text = el.getAttribute('data-tooltip');
  if (navigator.clipboard && text) {
    navigator.clipboard.writeText(text);
    var orig = el.textContent;
    el.textContent = 'Copied!';
    setTimeout(function () { el.textContent = orig; }, 1200);
  }
  ev.preventDefault();
  return false;
}
</script>"""


def esc(s):
    return html.escape(s or "", quote=True)


def paper_display_titles(paper):
    """Return the English-first display title and an optional Korean subtitle.

    Legacy Korean records keep their source-language title in ``title`` and
    their English translation in ``title_en``. English records use ``title``;
    ``title_ko`` supplies a Korean subtitle when one is available (notably for
    the dissertation).
    """
    primary = paper.get("title_en") or paper["title"]
    secondary = paper.get("title_ko") or (paper["title"] if paper.get("title_en") else "")
    return primary, secondary if secondary != primary else ""


def render_common_head(page_path, title, description, base=""):
    """Favicon, theme-color, canonical, and Open Graph/Twitter Card tags —
    shared across every page so link previews (Slack/LinkedIn/Twitter) and
    search engines get consistent metadata. See docs/ROADMAP.md."""
    url = f"{SITE_URL}/{page_path}"
    # Landscape OG/Twitter card (1200x630) — a properly-sized link-preview
    # image, distinct from the portrait profile photo used elsewhere on the
    # site. See docs/ROADMAP.md.
    card_url = f"{SITE_URL}/assets/og-card.png"
    tags = [
        f'<link rel="canonical" href="{esc(url)}">',
        f'<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">',
        '<meta name="theme-color" content="#0d1117" media="(prefers-color-scheme: dark)">',
        '<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">',
        '<meta property="og:type" content="profile">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{esc(url)}">',
        f'<meta property="og:image" content="{esc(card_url)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
        f'<meta name="twitter:image" content="{esc(card_url)}">',
    ]
    return "\n".join(tags)


def render_person_jsonld():
    """schema.org Person + ProfilePage graph for the homepage only — sameAs
    links are what let Google disambiguate this identity across Scholar/
    ORCID/LinkedIn/GitHub, especially for a common-format Korean name
    spanning two unrelated fields. See docs/ROADMAP.md."""
    same_as = [DATA[k] for k in ("scholar_url", "orcid_url", "researchgate_url", "linkedin_url", "github_url") if DATA.get(k)]
    affiliation = DATA.get("affiliation", "")
    org_name, _, job_title = affiliation.partition(" — ")
    person = {
        "@type": "Person",
        "@id": f"{SITE_URL}/#person",
        "name": DATA["name"],
        "url": f"{SITE_URL}/",
        "sameAs": same_as,
    }
    if job_title:
        person["jobTitle"] = job_title
        if org_name:
            person["worksFor"] = {"@type": "Organization", "name": org_name}
    elif affiliation:
        person["jobTitle"] = affiliation
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            person,
            {
                "@type": "ProfilePage",
                "@id": f"{SITE_URL}/#profilepage",
                "url": f"{SITE_URL}/",
                "mainEntity": {"@id": f"{SITE_URL}/#person"},
            },
        ],
    }
    if DATA.get("photo"):
        graph["@graph"][0]["image"] = f"{SITE_URL}/{DATA['photo']}"
    return f'<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>'


def has_local_pdf(paper):
    return os.path.isfile(os.path.join(ROOT, paper["pdf"]))


def bibtex_key(paper):
    first_author = paper["authors"].split(",")[0].strip().split(" ")[-1]
    year = paper["year"] or "nd"
    key = re.sub(r"[^A-Za-z0-9]", "", f"{first_author}{year}")
    # a Korean (or otherwise non-Latin) author name strips down to nothing
    # but digits — fall back to the slug so the key stays unique and
    # actually identifies the paper rather than just its year
    if not key or not re.search(r"[A-Za-z]", key):
        return re.sub(r"[^A-Za-z0-9]", "", paper["slug"])
    return key


def parse_venue(venue):
    """Split a free-text venue string into (clean_name, volume, number, pages).

    Venue strings look like "IEEE Access, Vol. 11, pp. 40930-40943" or
    "Sensors, Vol. 23, No. 6, 3075" — pull out the structured bibliographic
    fields BibTeX/reference managers expect instead of leaving them folded
    into one free-text journal/booktitle field.
    """
    volume = number = pages = None
    remainder = venue

    m = re.search(r"\bVol\.?\s*(\d+)", remainder, re.IGNORECASE)
    if m:
        volume = m.group(1)
        remainder = remainder[:m.start()] + remainder[m.end():]

    m = re.search(r"\bNo\.?\s*(\d+)", remainder, re.IGNORECASE)
    if m:
        number = m.group(1)
        remainder = remainder[:m.start()] + remainder[m.end():]

    m = re.search(r"\bpp\.?\s*([\d]+-[\d]+)", remainder, re.IGNORECASE)
    if m:
        pages = m.group(1)
        remainder = remainder[:m.start()] + remainder[m.end():]

    # rebuild from non-empty comma-separated pieces, dropping anything the
    # removals above left blank
    pieces = [piece.strip() for piece in remainder.split(",")]
    pieces = [piece for piece in pieces if piece]

    # a lone trailing number (no "pp." prefix) is an MDPI-style article
    # number, e.g. "Sensors, Vol. 23, No. 6, 3075" -> pages = 3075
    if pieces and not pages and re.fullmatch(r"\d+", pieces[-1]):
        pages = pieces.pop()

    clean = ", ".join(pieces)
    return clean, volume, number, pages


def to_bibtex(paper, key):
    is_article = paper["category"] in ("int-journal", "domestic-journal")
    entry_type = "mastersthesis" if paper["category"] == "thesis" else ("article" if is_article else "inproceedings")
    primary_title, secondary_title = paper_display_titles(paper)
    lines = [f"@{entry_type}{{{key},"]
    lines.append(f'  title     = {{{primary_title}}},')
    lines.append(f'  author    = {{{paper["authors"].replace(", ", " and ")}}},')
    if paper.get("year"):
        lines.append(f'  year      = {{{paper["year"]}}},')
    if paper.get("venue"):
        clean_venue, volume, number, pages = parse_venue(paper["venue"])
        field = "journal" if is_article else ("school" if entry_type == "mastersthesis" else "booktitle")
        lines.append(f'  {field:<9} = {{{clean_venue}}},')
        if volume:
            lines.append(f'  volume    = {{{volume}}},')
        if number:
            lines.append(f'  number    = {{{number}}},')
        if pages:
            lines.append(f'  pages     = {{{pages}}},')
    if paper.get("doi"):
        lines.append(f'  doi       = {{{paper["doi"]}}},')
    if secondary_title:
        lines.append(f'  note      = {{Original Korean title: {secondary_title}}},')
    lines.append("}")
    return "\n".join(lines)


SOCIAL_LINKS = [
    ("scholar_url", "Google Scholar", "scholar"),
    ("orcid_url", "ORCID", "orcid"),
    ("researchgate_url", "ResearchGate", "rg"),
    ("linkedin_url", "LinkedIn", "linkedin"),
    ("github_url", "GitHub", "github"),
]

LIFE_SOCIAL_LINKS = [
    ("instagram_url", "Instagram", "instagram"),
    ("facebook_url", "Facebook", "facebook"),
]

# Simplified monochrome brand marks (currentColor-filled, so they follow the
# badge's own text color per theme) rather than a generic circle+initials —
# kept minimal/geometric per-glyph instead of importing an icon font.
_SOCIAL_ICON_PATHS = {
    "scholar": '<path d="M12 2 1 8l11 6 9-4.91V17h2V8L12 2zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>',
    "orcid": '<circle cx="12" cy="12" r="11" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="7.8" cy="7.6" r="1.15"/><rect x="6.9" y="10.2" width="1.8" height="7.4"/><path d="M10.4 10.2h3.6c3 0 4.6 1.7 4.6 3.7s-1.6 3.7-4.6 3.7h-3.6v-7.4zm1.8 1.6v4.2h1.7c2 0 2.9-1 2.9-2.1s-.9-2.1-2.9-2.1h-1.7z"/>',
    "rg": '<rect x="2" y="2" width="20" height="20" rx="4" fill="none" stroke="currentColor" stroke-width="1.6"/><text x="12" y="16" text-anchor="middle" font-size="9" font-weight="700" fill="currentColor">RG</text>',
    "linkedin": '<path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45z"/>',
    "github": '<path d="M12 .3a12 12 0 0 0-3.8 23.39c.6.11.82-.26.82-.58l-.01-2.04c-3.34.73-4.04-1.61-4.04-1.61-.55-1.38-1.33-1.75-1.33-1.75-1.09-.74.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.49 1 .11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3-.54-1.52.11-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.29-1.23 3.29-1.23.65 1.66.24 2.88.12 3.18.77.84 1.23 1.91 1.23 3.22 0 4.61-2.8 5.63-5.48 5.92.43.37.81 1.1.81 2.22l-.01 3.29c0 .32.21.7.82.58A12 12 0 0 0 12 .3z"/>',
    "instagram": '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="4.3" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="17.4" cy="6.6" r="1.15"/>',
    "facebook": '<path d="M14.1 21v-8h2.68l.4-3.11h-3.08V7.9c0-.9.25-1.51 1.54-1.51h1.64V3.61A22 22 0 0 0 14.85 3.5c-2.36 0-3.97 1.44-3.97 4.08v2.31H8.2V13h2.68v8h3.22z"/>',
    "cv": '<rect x="3" y="2" width="18" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M7 7h10M7 11h10M7 15h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
}


def _icon_badge(css_class):
    inner = _SOCIAL_ICON_PATHS.get(css_class, "")
    return f'<svg class="social-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">{inner}</svg>'


def render_social_links(extra_class="", links_config=None, include_cv=True):
    links = []
    for key, label, css_class in links_config or SOCIAL_LINKS:
        if DATA.get(key):
            links.append(
                f'<a class="social-btn {css_class}" href="{esc(DATA[key])}" target="_blank" rel="noopener">'
                f'{_icon_badge(css_class)}<span>{label}</span></a>'
            )
    if include_cv and DATA.get("cv_url"):
        links.append(f'<a class="social-btn cv" href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">{_icon_badge("cv")}<span>CV (PDF)</span></a>')
    return f'<nav class="social-links {extra_class}">{"".join(links)}</nav>'


def render_nav(active, base=""):
    items = [("index.html", "Home"), ("publications.html", "Publications"), ("cv.html", "CV")]
    if WIKI_DATA.get("notes"):
        items.append(("wiki.html", "Wiki"))
    items.append(("life.html", "Life"))
    links = "".join(
        f'<a href="{base}{href}" class="{"active" if name == active else ""}">{name}</a>'
        for href, name in items
    )
    return (
        f'<nav class="site-nav"><div class="nav-inner">'
        f'<a class="brand" href="{base}index.html">{esc(DATA["name"])}</a>'
        f'<div class="nav-links">{links}</div>'
        f'<button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme" title="Toggle light/dark theme">&#9788;</button>'
        f'</div></nav>'
    )


def render_profile_header():
    photo_html = ""
    if DATA.get("photo") and os.path.isfile(os.path.join(ROOT, DATA["photo"])):
        photo_html = f'<img class="profile-photo" src="{esc(DATA["photo"])}" alt="{esc(DATA["name"])}">'

    interests_html = ""
    if DATA.get("interests"):
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in DATA["interests"])
        interests_html = f'<p class="interests">{tags}</p>'

    contact_parts = []
    if DATA.get("location"):
        maps_url = f"https://www.google.com/maps/search/?api=1&query={DATA['location'].replace(' ', '+')}"
        contact_parts.append(f'<a href="{esc(maps_url)}" target="_blank" rel="noopener">&#128205; {esc(DATA["location"])}</a>')
    if DATA.get("email"):
        contact_parts.append(f'<a href="mailto:{esc(DATA["email"])}">&#9993; {esc(DATA["email"])}</a>')
    contact_html = f'<p class="contact">{" &middot; ".join(contact_parts)}</p>' if contact_parts else ""

    bio_html = f'<p class="bio">{esc(DATA["bio"])}</p>' if DATA.get("bio") else ""
    identity_tag_html = f'<p class="identity-tag">{esc(DATA["identity_tag"])}</p>' if DATA.get("identity_tag") else ""

    return f'''<section class="hero">
    {photo_html}
    <div class="hero-text">
      <h1>{esc(DATA['name'])}{' <span class="name-ko">(' + esc(DATA['name_ko']) + ')</span>' if DATA.get('name_ko') else ''}</h1>
      {identity_tag_html}
      {contact_html}
      {bio_html}
      {interests_html}
      {render_social_links()}
    </div>
  </section>'''


def _timeline_sort_key(period):
    if "Present" in period:
        return 9999
    years = re.findall(r"\d{4}", period)
    return int(years[-1]) if years else 0


def _combined_period(items):
    """Return the earliest start and latest end across grouped entries."""
    periods = [item.get("period", "") for item in items]

    def start_year(period):
        years = re.findall(r"\d{4}", period)
        return int(years[0]) if years else 9999

    def end_year(period):
        if "Present" in period:
            return 9999
        years = re.findall(r"\d{4}", period)
        return int(years[-1]) if years else 0

    start_period = min(periods, key=start_year)
    end_period = max(periods, key=end_year)
    start = re.split(r"\s+[–—]\s+", start_period, maxsplit=1)[0]
    end = re.split(r"\s+[–—]\s+", end_period, maxsplit=1)[-1]
    return f"{start} – {end}"


def render_side_projects():
    """Live, non-work software projects — evidence of current hands-on
    engineering for the recruiter audience (see CLAUDE.md), distinct from
    the CV page's funded research 'projects'. Reuses the compact paper-list
    styles so it needs no new CSS."""
    items = DATA.get("side_projects") or []
    if not items:
        return ""
    rows = []
    for sp in items:
        links = [f'<a href="{esc(sp["url"])}" target="_blank" rel="noopener">{esc(sp["name"])}</a>']
        sub_bits = [esc(sp.get("description", ""))]
        meta = " · ".join(esc(b) for b in (sp.get("stack"), sp.get("period")) if b)
        repo = sp.get("repo")
        repo_link = f' · <a href="{esc(repo)}" target="_blank" rel="noopener">GitHub</a>' if repo else ""
        rows.append(f'''      <li class="paper-compact">
        {links[0]}
        <span class="paper-sub">{sub_bits[0]}</span>
        <span class="paper-sub">{meta}{repo_link}</span>
      </li>''')
    return f'''<section>
      <h2>Side Projects</h2>
      <ul class="paper-list compact">
{chr(10).join(rows)}
      </ul>
    </section>'''


def render_section_nav(items, extra_class=""):
    links = "".join(f'<a href="#{esc(anchor)}">{esc(label)}</a>' for label, anchor in items)
    grid_class = " section-nav-grid" if len(items) > 6 else ""
    extra = f" {extra_class.strip()}" if extra_class.strip() else ""
    return f'<nav class="section-nav{grid_class}{extra}" aria-label="On this page">{links}</nav>'


def render_timeline():
    entries = []
    work_groups = _group_consecutive_by_parent(DATA.get("experience", []), "organization")
    for g in work_groups:
        if len(g["items"]) == 1:
            sub, e = g["items"][0]
            org = f'{sub}, {g["parent"]}' if sub else g["parent"]
            entries.append({
                "period": e["period"],
                "title": org,
                "detail": e["position"].split(" — ")[0] if " — " in e["position"] else e["position"],
                "focus": e.get("focus"),
                "url": e.get("url"),
                "kind": "work",
            })
        else:
            combined_period = _combined_period([e for _, e in g["items"]])
            positions = list(dict.fromkeys(e["position"] for _, e in g["items"]))
            subitems = [
                {
                    "period": e["period"],
                    "title": sub or g["parent"],
                    "detail": e["position"],
                }
                for sub, e in g["items"]
            ]
            entries.append({
                "period": combined_period,
                "title": g["parent"],
                "detail": positions[0] if len(positions) == 1 else f'{len(g["items"])} internal roles',
                "focus": next((e.get("focus") for _, e in g["items"] if e.get("focus")), None),
                "url": None,
                "kind": "work",
                "subitems": subitems,
            })
    edu_groups = _group_consecutive_by_parent(DATA.get("education", []), "school", split_char="\x00")
    for g in edu_groups:
        if len(g["items"]) == 1:
            _, e = g["items"][0]
            entries.append({
                "period": e["period"],
                "title": g["parent"],
                "detail": e["degree"].split(" — ")[0],
                "focus": e.get("focus"),
                "url": e.get("url"),
                "kind": "education",
            })
        else:
            combined_period = _combined_period([e for _, e in g["items"]])
            subitems = [
                {
                    "period": e["period"],
                    "title": e["degree"].split(" — ")[0],
                    "detail": e["degree"].split(" — ", 1)[1] if " — " in e["degree"] else "",
                }
                for _, e in g["items"]
            ]
            entries.append({
                "period": combined_period,
                "title": g["parent"],
                "detail": f'{len(g["items"])} degrees',
                "focus": next((e.get("focus") for _, e in g["items"] if e.get("focus")), None),
                "url": None,
                "kind": "education",
                "subitems": subitems,
            })
    # A grad-school stint (PhD research) and its lab affiliation (work
    # experience) can share the exact same period and university — that's
    # one life event, not two, so merge them into a single timeline entry
    # rather than showing two overlapping dots for the same years.
    by_period = {}
    for e in entries:
        by_period.setdefault(e["period"], []).append(e)
    merged_entries = []
    skip_ids = set()
    for period, group in by_period.items():
        work = next((e for e in group if e["kind"] == "work" and "Seoul National University" in e["title"] and not e.get("subitems")), None)
        edu = next((e for e in group if e["kind"] == "education" and e["title"] == "Seoul National University" and not e.get("subitems")), None)
        if work and edu:
            advisor_match = re.search(r"Advisor: ([^,)]+)", next(iter(DATA["education"]), {}).get("degree", ""))
            for ed in DATA["education"]:
                if ed["school"] == "Seoul National University" and ed["period"] == period:
                    advisor_match = re.search(r"Advisor: ([^,)]+)", ed["degree"])
                    break
            advisor = f" — Advisor: {advisor_match.group(1)}" if advisor_match else ""
            lab_name = work["title"].split(", ", 1)[0]
            merged_entries.append({
                "period": period,
                "title": edu["title"],
                "detail": f'{edu["detail"]} · {lab_name}{advisor}',
                "focus": edu.get("focus") or work.get("focus"),
                "url": work.get("url") or edu.get("url"),
                "kind": "education",
            })
            skip_ids.add(id(work))
            skip_ids.add(id(edu))
    entries = [e for e in entries if id(e) not in skip_ids] + merged_entries
    entries.sort(key=lambda e: _timeline_sort_key(e["period"]), reverse=True)

    if not entries:
        return ""

    rows = []
    for e in entries:
        title = f'<a href="{esc(e["url"])}" target="_blank" rel="noopener">{esc(e["title"])}</a>' if e.get("url") else esc(e["title"])
        focus_html = f'<div class="timeline-focus"><span>Focus</span>{esc(e["focus"])}</div>' if e.get("focus") else ""
        subitems_html = ""
        if e.get("subitems"):
            sub_rows = "".join(f'''        <li class="timeline-subitem">
          <span class="timeline-subitem-period">{esc(s['period'])}</span>
          <span class="timeline-subitem-title">{esc(s['title'])}</span>
          <span class="timeline-subitem-detail">{esc(s['detail'])}</span>
        </li>''' for s in e["subitems"])
            subitems_html = f'<ul class="timeline-subitems">{sub_rows}</ul>'
        rows.append(f'''      <li class="timeline-item timeline-{e['kind']}">
        <div class="timeline-period">{esc(e['period'])}</div>
        <div class="timeline-body">
          <div class="timeline-title">{title}</div>
          <div class="timeline-detail">{esc(e['detail'])}</div>
          {focus_html}
          {subitems_html}
        </div>
      </li>''')

    return f'''<section id="timeline">
      <h2>Timeline</h2>
      <ul class="timeline">
{chr(10).join(rows)}
      </ul>
    </section>'''


def render_index():
    top_papers = sorted(DATA["papers"], key=lambda p: -(p["citations"] or 0))[:5]
    rows = []
    for p in top_papers:
        year = p["year"] if p.get("year") else "n.d."
        primary_title, secondary_title = paper_display_titles(p)
        secondary_html = f'<span class="paper-title-secondary" lang="ko">{esc(secondary_title)}</span>' if secondary_title else ""
        rows.append(f'''      <li class="paper-compact">
        <a href="papers/{esc(p['slug'])}.html">{esc(primary_title)}</a>
        {secondary_html}
        <span class="paper-sub">{esc(p['venue'])}, {year} &middot; {p['citations']} citations</span>
      </li>''')

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>{esc(DATA['name'])}{' (' + esc(DATA['name_ko']) + ')' if DATA.get('name_ko') else ''}</title>
<meta name="description" content="{esc(DATA['name'])} - {esc(DATA.get('tagline', ''))}">
{render_common_head('index.html', DATA['name'], DATA.get('tagline', ''))}
{render_person_jsonld()}
<link rel="stylesheet" href="style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Home")}
  <main class="container">
    {render_profile_header()}

    <div class="home-grid">
      <div class="home-panel">
        {render_timeline()}
      </div>
      <div class="home-panel">
        {render_side_projects()}
        <section id="highlights">
          <div class="section-head">
            <h2>Highlighted Publications</h2>
            <a class="see-all" href="publications.html">View all {len(DATA['papers'])} publications &rarr;</a>
          </div>
          <ul class="paper-list compact">
{chr(10).join(rows)}
          </ul>
        </section>
      </div>
    </div>
  </main>
  <footer class="site-footer">
    <p>&copy; {esc(DATA['name'])}. Built with a <a href="{esc(DATA['github_url'])}/{esc(DATA['github_url'].rstrip('/').rsplit('/', 1)[-1])}.github.io" target="_blank" rel="noopener">static site generator</a>. Full BibTeX: <a href="bibtex/all.bib" target="_blank" rel="noopener">bibtex/all.bib</a></p>
  </footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def publication_source_label(url):
    """Name the actual publication source instead of calling every index an official link."""
    host = urlparse(url).netloc.lower().removeprefix("www.")
    source_labels = {
        "dbpia.co.kr": "DBpia",
        "dcollection.snu.ac.kr": "SNU Repository",
        "icas.org": "ICAS Archive",
        "ipnt.or.kr": "IPNT Proceedings",
        "ieeexplore.ieee.org": "IEEE Xplore",
        "arc.aiaa.org": "AIAA ARC",
        "journals.sagepub.com": "SAGE Journals",
        "sciencedirect.com": "ScienceDirect",
        "mdpi.com": "MDPI",
        "link.springer.com": "SpringerLink",
        "eucass.eu": "EUCASS",
        "sase.or.kr": "SASE Proceedings",
        "search.informit.org": "Informit",
    }
    return source_labels.get(host, host or "Publisher Page")


def link_badges(p, base="papers/pdfs/", paper_page=False):
    """Render publication-source, self-hosted PDF, and BibTeX badges."""
    official = p.get("official_link")
    local_pdf = has_local_pdf(p)
    badges = []
    if official:
        label = publication_source_label(official)
        tooltip_target = official
        badges.append(
            f'<a class="badge badge-official" href="{esc(official)}" target="_blank" rel="noopener" '
            f'data-tooltip="{esc(tooltip_target)}">{label}</a>'
        )
    if local_pdf:
        pdf_path = ("../" if paper_page else "") + p["pdf"]
        badges.append(
            f'<a class="badge badge-preprint" href="{esc(pdf_path)}" target="_blank" rel="noopener" '
            f'data-tooltip="{esc(pdf_path)}">Author PDF</a>'
        )
    if not official and not local_pdf:
        badges.append('<span class="badge badge-pending">No Public Link Yet</span>')
    bib_path = ("../" if paper_page else "") + f'bibtex/{p["slug"]}.bib'
    bib_preview = to_bibtex(p, bibtex_key(p))
    badges.append(
        f'<a class="badge badge-bibtex" href="{esc(bib_path)}" target="_blank" rel="noopener" data-tooltip="{esc(bib_preview)}" '
        f'onclick="return copyBibtex(this, event)">BibTeX</a>'
    )
    return "".join(badges)


def _abstract_paragraphs(text):
    """Render blank-line-separated source paragraphs."""
    return "".join(f"<p>{esc(para.strip())}</p>" for para in text.split("\n\n") if para.strip())


def _render_abstract_body(p):
    """Render English as the primary abstract and Korean as supporting text."""
    primary = _abstract_paragraphs(p.get("abstract", ""))
    secondary = p.get("abstract_ko", "")
    if not secondary:
        return primary
    return (
        f'{primary}<div class="abstract-secondary" lang="ko">'
        '<div class="abstract-language-label">Korean abstract</div>'
        f'{_abstract_paragraphs(secondary)}</div>'
    )


def _render_secondary_metadata(p):
    rows = []
    if p.get("authors_ko"):
        rows.append(f'<span>{esc(p["authors_ko"])}</span>')
    if p.get("venue_ko"):
        rows.append(f'<span>{esc(p["venue_ko"])}</span>')
    return f'<div class="paper-meta-secondary" lang="ko">{" · ".join(rows)}</div>' if rows else ""


def _render_paper_item(p, i):
    year = p["year"] if p.get("year") else "n.d."
    primary_title, secondary_title = paper_display_titles(p)
    secondary_html = f'<div class="paper-title-secondary" lang="ko">{esc(secondary_title)}</div>' if secondary_title else ""
    secondary_meta_html = _render_secondary_metadata(p)
    abstract_html = (
        f'<details class="paper-abstract-toggle"><summary>Abstract</summary>{_render_abstract_body(p)}</details>'
        if p.get("abstract") else ""
    )
    return f'''        <li class="paper">
          <div class="paper-title"><span class="paper-index">{i}.</span> <a href="papers/{esc(p['slug'])}.html">{esc(primary_title)}</a></div>
          {secondary_html}
          <div class="paper-meta">{esc(p['authors'])}</div>
          <div class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" &middot; {p['citations']} citations" if p['citations'] else ""}</div>
          {secondary_meta_html}
          {abstract_html}
          <div class="paper-badges">{link_badges(p)}</div>
        </li>'''


def _render_grouped_sections(groups, order, css_class="pub-category"):
    sections = []
    for key in order:
        papers = groups.get(key) or []
        if not papers:
            continue
        papers = sorted(papers, key=lambda p: -(p["year"] or 0))
        items = [_render_paper_item(p, i) for i, p in enumerate(papers, 1)]
        sections.append(f'''    <section class="{css_class}">
      <h2>{esc(key)} <span class="count">({len(papers)})</span></h2>
      <ul class="paper-list">
{chr(10).join(items)}
      </ul>
    </section>''')
    return "\n".join(sections)


THEME_ORDER = [
    "Morphing-Wing Aircraft Control",
    "Dynamic Soaring & Learning-Based Control",
    "Autonomous Carrier Landing & Guidance",
    "Target Tracking & Sensing",
    "Path Planning for Search & Rescue",
    "UAV Pitch-Hold Control for Mine Detection",
    "Satellite & Lunar Orbiter GNC",
]

VIEW_TOGGLE_SCRIPT = """<script>
function setPubView(view) {
  document.getElementById('view-category').style.display = view === 'category' ? '' : 'none';
  document.getElementById('view-theme').style.display = view === 'theme' ? '' : 'none';
  document.querySelectorAll('.view-toggle-btn').forEach(function (b) {
    var isActive = b.dataset.view === view;
    b.classList.toggle('active', isActive);
    b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
  });
}
</script>"""


PUBLICATION_UX_SCRIPT = """<script>
(function () {
  var insights = document.getElementById('insights');
  var compactLayout = window.matchMedia('(max-width: 900px)');

  function syncInsights(e) {
    if (insights) insights.open = !e.matches;
  }

  syncInsights(compactLayout);
  if (compactLayout.addEventListener) {
    compactLayout.addEventListener('change', syncInsights);
  } else if (compactLayout.addListener) {
    compactLayout.addListener(syncInsights);
  }

  var browse = document.getElementById('browse');
  if (!browse) return;

  function alignBrowse(focus, behavior) {
    browse.scrollIntoView({block: 'start', behavior: behavior || 'auto'});
    if (focus) browse.focus({preventScroll: true});
  }

  function settleBrowse(focus, smooth) {
    var behavior = smooth && !window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'smooth'
      : 'auto';
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        alignBrowse(false, behavior);
      });
    });
    window.setTimeout(function () { alignBrowse(focus, 'auto'); }, 360);
  }

  document.querySelectorAll('a[href="#browse"]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      if (window.location.hash !== '#browse') {
        window.history.pushState(null, '', '#browse');
      }
      settleBrowse(true, true);
    });
  });

  window.addEventListener('hashchange', function () {
    if (window.location.hash === '#browse') settleBrowse(true, false);
  });
  window.addEventListener('load', function () {
    if (window.location.hash === '#browse') settleBrowse(false, false);
  });
  if (window.location.hash === '#browse') settleBrowse(false, false);
})();
</script>"""


def render_publications():
    by_category = {c: [] for c in CATEGORY_ORDER}
    by_theme = {t: [] for t in THEME_ORDER}
    for p in DATA["papers"]:
        by_category.setdefault(p["category"], []).append(p)
        by_theme.setdefault(p.get("theme") or "Other", []).append(p)

    category_labels_map = {c: CATEGORY_LABELS[c] for c in CATEGORY_ORDER}
    category_sections = _render_grouped_sections(
        {category_labels_map[c]: papers for c, papers in by_category.items()},
        [category_labels_map[c] for c in CATEGORY_ORDER],
    )
    theme_sections = _render_grouped_sections(by_theme, THEME_ORDER + ["Other"], css_class="pub-category pub-theme")
    pending_legend = (
        '<span class="badge badge-pending">No Public Link Yet</span> not available'
        if any(not p.get("official_link") and not has_local_pdf(p) for p in DATA["papers"])
        else ""
    )

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>Publications - {esc(DATA['name'])}</title>
<meta name="description" content="Full publication list of {esc(DATA['name'])} (Journal / International Conference / Domestic Conference / Ph.D. Dissertation)">
{render_common_head('publications.html', f"Publications - {DATA['name']}", f"{len(DATA['papers'])} publications by {DATA['name']} — journal articles, conference papers, and PhD dissertation.")}
<link rel="stylesheet" href="style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Publications")}
  <main class="container">
    <header class="page-header">
      <h1>Publications</h1>
      <p class="page-intro">{len(DATA['papers'])} publications total &middot; a unified list combining Google Scholar records with additional entries. Also available on my <a href="{esc(DATA['scholar_url'])}" target="_blank" rel="noopener">Google Scholar profile</a>.</p>
    </header>
    {render_section_nav([("Insights", "insights"), ("Browse publications", "browse")], "publication-section-nav")}
    <div class="publication-quick-actions">
      <a class="browse-publications-cta" href="#browse">
        <span>Browse publications</span>
        <span>{len(DATA['papers'])} papers &darr;</span>
      </a>
    </div>
    <details class="publication-insights" id="insights" open>
      <summary class="insights-summary">
        <span>Publication insights</span>
        <small>Year, venues, citations, and research focus</small>
      </summary>
      <div class="viz-dashboard">
        {viz.year_category_chart(DATA['papers'])}
        {viz.venue_statistics(DATA['papers'])}
        {viz.citation_year_chart(DATA.get('citation_stats') or {}, updated_label=CITATION_STATS_UPDATED)}
        {viz.keyword_chart(DATA['papers'], curated_terms=CURATED_RESEARCH_FOCUS)}
      </div>
    </details>
    <div class="publication-toolbar" id="browse" tabindex="-1">
      <div class="legend">
        <span class="badge badge-official">Publication Source</span> DOI, publisher, repository, or scholarly database
        <span class="badge badge-preprint">Author PDF</span> self-hosted author copy
        {pending_legend}
      </div>
      <div class="view-control">
        <span class="view-toggle-label">View publications by</span>
        <div class="view-toggle" role="group" aria-label="Group publications by">
          <button type="button" class="view-toggle-btn active" data-view="category" aria-pressed="true" onclick="setPubView('category')">Category</button>
          <button type="button" class="view-toggle-btn" data-view="theme" aria-pressed="false" onclick="setPubView('theme')">Research Theme</button>
        </div>
      </div>
    </div>
    <div id="view-category">
{category_sections}
    </div>
    <div id="view-theme" style="display:none">
{theme_sections}
    </div>
  </main>
  <footer class="site-footer">
    <p>Full BibTeX: <a href="bibtex/all.bib" target="_blank" rel="noopener">bibtex/all.bib</a></p>
  </footer>
  {THEME_TOGGLE_SCRIPT}
  {VIEW_TOGGLE_SCRIPT}
  {PUBLICATION_UX_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "publications.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_list_section(title, items, fields):
    if not items:
        return f'<section><h2>{title}</h2><p class="pending">Nothing added yet.</p></section>'
    rows = []
    for item in items:
        parts = [esc(item.get(f, "")) for f in fields]
        if item.get("url") and parts:
            parts[0] = f'<a href="{esc(item["url"])}" target="_blank" rel="noopener">{parts[0]}</a>'
        rows.append(f'<li>{" &mdash; ".join(p for p in parts if p)}</li>')
    return f'''<section>
    <h2>{title}</h2>
    <ul class="plain-list">
      {"".join(rows)}
    </ul>
  </section>'''


def render_projects_section(projects):
    """Like render_list_section but each project can also point at the
    publications it produced by slug (related_papers) or by research theme
    (related_themes), connecting each funded project to its research record."""
    if not projects:
        return '<section><h2>Projects</h2><p class="pending">Nothing added yet.</p></section>'
    papers_by_slug = {p["slug"]: p for p in DATA.get("papers", [])}
    rows = []
    for proj in projects:
        title = esc(proj.get("title", ""))
        if proj.get("url"):
            title = f'<a href="{esc(proj["url"])}" target="_blank" rel="noopener">{title}</a>'
        title_ko = f'<div class="project-title-ko" lang="ko">{esc(proj["title_ko"])}</div>' if proj.get("title_ko") else ""
        sponsor = f'<div class="project-sponsor">{esc(proj["sponsor"])}</div>' if proj.get("sponsor") else ""
        line = (
            '<li class="project-entry">'
            f'<div class="project-heading"><div class="project-title-en" lang="en">{title}</div>'
            f'{title_ko}{sponsor}'
            f'<span class="project-period">{esc(proj.get("period", ""))}</span></div>'
        )
        collaborators = proj.get("collaborators") or []
        if collaborators:
            names = ", ".join(esc(name) for name in collaborators)
            line += f'<div class="project-collaborators"><strong>Primary collaborators:</strong> {names}</div>'
        slugs = list(proj.get("related_papers") or [])
        themes = set(proj.get("related_themes") or [])
        if themes:
            themed_papers = sorted(
                (p for p in DATA.get("papers", []) if p.get("theme") in themes),
                key=lambda p: (-(p.get("year") or 0), (p.get("title_en") or p["title"]).lower()),
            )
            slugs.extend(p["slug"] for p in themed_papers if p["slug"] not in slugs)
        links = []
        for slug in slugs:
            p = papers_by_slug.get(slug)
            if not p:
                continue
            primary_title, _ = paper_display_titles(p)
            links.append(f'<a href="papers/{esc(slug)}.html">{esc(primary_title)} ({p["year"]})</a>')
        if links:
            label = "Selected related publications" if proj.get("related_note") else "Related publications"
            note = f' <em>({esc(proj["related_note"])})</em>' if proj.get("related_note") else ""
            related_items = "".join(f'<li>{link}</li>' for link in links)
            line += f'<div class="related-label">{label}{note}</div><ol class="related-publications">{related_items}</ol>'
        line += "</li>"
        rows.append(line)
    return f'''<section>
    <h2>Projects</h2>
    <ul class="plain-list">
      {"".join(rows)}
    </ul>
  </section>'''


def _group_consecutive_by_parent(items, name_field, split_char=", "):
    """Group consecutive items whose name_field shares a common trailing
    ", Parent" segment (e.g. "Research Group, Parent Organization"),
    so multiple roles/degrees at the same org render under one header
    instead of repeating the parent name on every row."""
    groups = []
    for item in items:
        name = item.get(name_field, "")
        if split_char in name:
            sub, parent = name.rsplit(split_char, 1)
        else:
            sub, parent = None, name
        if groups and groups[-1]["parent"] == parent:
            groups[-1]["items"].append((sub, item))
        else:
            groups.append({"parent": parent, "items": [(sub, item)]})
    return groups


def render_experience_section(items):
    if not items:
        return '<section><h2>Experience</h2><p class="pending">Nothing added yet.</p></section>'

    def render_focus(item):
        return f'<div class="experience-focus"><span>Focus</span>{esc(item["focus"])}</div>' if item.get("focus") else ""

    def render_role(sub, item, show_focus=True):
        role_title = esc(sub or item.get("position", ""))
        position = esc(item.get("position", "")) if sub else ""
        header = f'<div class="experience-role-head"><strong>{role_title}</strong><span>{esc(item.get("period", ""))}</span></div>'
        position_html = f'<div class="experience-position">{position}</div>' if position else ""
        focus_html = render_focus(item) if show_focus else ""
        highlights = item.get("highlights")
        if highlights:
            bullets = "".join(f"<li>{esc(h)}</li>" for h in highlights)
            return f'<li class="experience-role">{header}{position_html}{focus_html}<ul class="experience-highlights">{bullets}</ul></li>'
        return f'<li class="experience-role">{header}{position_html}{focus_html}</li>'

    groups = _group_consecutive_by_parent(items, "organization")
    rows = []
    for g in groups:
        if len(g["items"]) == 1:
            sub, item = g["items"][0]
            org = f'{sub}, {g["parent"]}' if sub else g["parent"]
            org_html = f'<a href="{esc(item["url"])}" target="_blank" rel="noopener">{esc(org)}</a>' if item.get("url") else esc(org)
            highlights = "".join(f"<li>{esc(h)}</li>" for h in item.get("highlights") or [])
            highlights_html = f'<ul class="experience-highlights">{highlights}</ul>' if highlights else ""
            rows.append(f'''<li class="experience-entry">
              <div class="experience-role-head"><strong>{org_html}</strong><span>{esc(item.get("period", ""))}</span></div>
              <div class="experience-position">{esc(item.get("position", ""))}</div>
              {render_focus(item)}
              {highlights_html}
            </li>''')
        else:
            focuses = list(dict.fromkeys(item.get("focus") for _, item in g["items"] if item.get("focus")))
            group_focus = f'<div class="experience-focus"><span>Focus</span>{esc(focuses[0])}</div>' if len(focuses) == 1 else ""
            sub_rows = "".join(render_role(sub, item, show_focus=len(focuses) != 1) for sub, item in g["items"])
            rows.append(f'<li class="experience-group"><div class="experience-company">{esc(g["parent"])}</div>{group_focus}<ul class="experience-roles">{sub_rows}</ul></li>')

    return f'''<section>
    <h2>Experience</h2>
    <ul class="plain-list">
      {"".join(rows)}
    </ul>
  </section>'''


def render_awards_section():
    awards = DATA.get("awards") or []
    if not awards:
        return ""
    items = "".join(f'<li><strong>{esc(a["title"])}</strong><br>{esc(a.get("detail", ""))}</li>' for a in awards)
    return f'<section><h2>Awards</h2><ul class="plain-list">{items}</ul></section>'


def render_skills_section():
    skills = DATA.get("skills") or {}
    if not skills:
        return ""
    rows = "".join(
        f'<div class="skill-row"><span class="skill-cat">{esc(cat)}</span><span class="skill-items">{esc(", ".join(items))}</span></div>'
        for cat, items in skills.items()
    )
    return f'<section><h2>Skills</h2><div class="skill-table">{rows}</div></section>'


OWN_NAME_VARIANTS = {"jihoon lee", "j lee", "이지훈", "jihoon", "jh lee"}


def render_collaborators_section(min_count=4, top_n=10):
    counter = Counter()
    for p in DATA["papers"]:
        for a in p["authors"].split(","):
            name = a.strip()
            if name and name.lower() not in OWN_NAME_VARIANTS:
                counter[name] += 1

    affiliations = DATA.get("collaborator_affiliations", {})
    frequent = [(name, count) for name, count in counter.most_common() if count >= min_count][:top_n]
    if not frequent:
        return ""

    rows = []
    for name, count in frequent:
        affil = affiliations.get(name, "")
        detail = f"{esc(affil)} &middot; {count} co-authored papers" if affil else f"{count} co-authored papers"
        rows.append(f'<li><strong>{esc(name)}</strong><br>{detail}</li>')

    return f'''<section>
    <h2>Frequent Collaborators</h2>
    <p class="page-intro">Co-authors on {min_count}+ publications together, out of {sum(1 for _ in DATA["papers"])} total.</p>
    <ul class="plain-list">{"".join(rows)}</ul>
  </section>'''


def render_education_section(items):
    if not items:
        return '<section><h2>Education</h2><p class="pending">Nothing added yet.</p></section>'

    groups = _group_consecutive_by_parent(items, "school", split_char="\x00")  # school has no built-in "Sub, Parent" split

    def _split_degree(item):
        """Split off the (department/lab/advisor/thesis) tail from the short
        degree title, so a long single-line entry doesn't turn into a
        wall-of-text link — the tail renders as a separate muted line."""
        primary, _, detail = item.get("degree", "").partition(" — ")
        primary_html = esc(primary)
        if item.get("url"):
            primary_html = f'<a href="{esc(item["url"])}" target="_blank" rel="noopener">{primary_html}</a>'
        detail_html = f'<span class="paper-sub">{esc(detail)}</span>' if detail else ""
        return primary_html, detail_html

    rows = []
    for g in groups:
        if len(g["items"]) == 1:
            _, item = g["items"][0]
            primary_html, detail_html = _split_degree(item)
            rows.append(
                f'<li><strong>{esc(g["parent"])}</strong> &mdash; {primary_html} '
                f'&mdash; {esc(item.get("period", ""))}{detail_html}</li>'
            )
        else:
            sub_rows = []
            for _, item in g["items"]:
                primary_html, detail_html = _split_degree(item)
                sub_rows.append(f'<li>{primary_html} &mdash; {esc(item.get("period", ""))}{detail_html}</li>')
            rows.append(
                f'<li class="experience-group"><div class="experience-company">{esc(g["parent"])}</div>'
                f'<ul class="experience-roles">{"".join(sub_rows)}</ul></li>'
            )
    return f'''<section>
    <h2>Education</h2>
    <ul class="plain-list">
      {"".join(rows)}
    </ul>
  </section>'''


def render_cv():
    education_html = render_education_section(DATA.get("education", []))
    experience_html = render_experience_section(DATA.get("experience", []))
    projects_html = render_projects_section(DATA.get("projects", []))
    awards_html = render_awards_section()
    skills_html = render_skills_section()
    collaborators_html = render_collaborators_section()

    cv_download = ""
    if DATA.get("cv_url"):
        cv_download = f'<p><a class="badge badge-official" href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">Download CV (PDF)</a></p>'

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>CV - {esc(DATA['name'])}</title>
<meta name="description" content="CV of {esc(DATA['name'])} — education, experience, awards, and skills.">
{render_common_head('cv.html', f"CV - {DATA['name']}", f"Education, experience, awards, and skills — {DATA['name']}.")}
<link rel="stylesheet" href="style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("CV")}
  <main class="container">
    <header class="page-header">
      <h1>CV</h1>
      {cv_download}
    </header>
    {render_section_nav([("Experience", "experience"), ("Education", "education"), ("Awards", "awards"), ("Skills", "skills"), ("Projects", "projects"), ("Collaborators", "collaborators")])}
    <div class="cv-grid">
      <div class="cv-panel cv-span" id="experience">{experience_html}</div>
      <div class="cv-panel" id="education">{education_html}</div>
      <div class="cv-panel" id="awards">{awards_html}</div>
      <div class="cv-panel cv-span" id="skills">{skills_html}</div>
      <div class="cv-panel" id="projects">{projects_html}</div>
      <div class="cv-panel" id="collaborators">{collaborators_html}</div>
    </div>
  </main>
  <footer class="site-footer"></footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "cv.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


LIFE_SECTION_EMOJI = {
    "Cycling": "🚴",
    "Triathlon": "🏅",
    "Swimming": "🏊",
    "Running": "🏃",
    "Rowing": "🚣",
    "Hiking": "🥾",
    "Travel": "✈️",
    "Photography": "📷",
}


def _render_race_table(races):
    if not races:
        return ""
    rows = []
    for r in races:
        rows.append(
            "<tr>"
            f"<td>{esc(r.get('name', ''))}</td>"
            f"<td>{esc(r.get('date', ''))}</td>"
            f"<td>{esc(r.get('location', ''))}</td>"
            f"<td>{esc(r.get('swim', ''))}</td>"
            f"<td>{esc(r.get('bike', ''))}</td>"
            f"<td>{esc(r.get('run', ''))}</td>"
            f"<td>{esc(r.get('total', ''))}</td>"
            f"<td>{esc(r.get('rank', ''))}</td>"
            f"<td>{esc(r.get('category', ''))}</td>"
            "</tr>"
        )
    return f'''<details class="viz-table-toggle">
        <summary>Race results ({len(races)})</summary>
        <table class="viz-table">
          <thead><tr><th>Race</th><th>Date</th><th>Location</th><th>Swim</th><th>Bike</th><th>Run</th><th>Total</th><th>Rank</th><th>Category</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </details>'''


def _render_records_table(records, label="Records"):
    if not records:
        return ""
    rows = "".join(
        f"<tr><td>{esc(r.get('name', ''))}</td><td>{esc(r.get('detail', ''))}</td><td>{esc(r.get('date', ''))}</td></tr>"
        for r in records
    )
    return f'''<details class="viz-table-toggle">
        <summary>{esc(label)} ({len(records)})</summary>
        <table class="viz-table">
          <thead><tr><th>Event</th><th>Result</th><th>Date</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </details>'''


def render_life():
    life = DATA.get("life") or {}
    intro_html = f'<p class="page-intro">{esc(life["intro"])}</p>' if life.get("intro") else ""
    life_socials = render_social_links(
        extra_class="life-social-links",
        links_config=LIFE_SOCIAL_LINKS,
        include_cv=False,
    )

    sections_html = []
    for section in life.get("sections", []):
        content = section.get("content")
        body = f'<p>{esc(content)}</p>' if content else '<p class="pending">Coming soon.</p>'
        club_html = ""
        if section.get("club_url"):
            club_html = f'<p><a href="{esc(section["club_url"])}" target="_blank" rel="noopener">{esc(section.get("club_label") or "Club page")} &rarr;</a></p>'
        photos = section.get("photos") or []
        gallery = ""
        if photos:
            thumbs = ""
            for photo in photos:
                if isinstance(photo, dict):
                    src = photo.get("src", "")
                    alt = photo.get("alt") or f'{section["title"]} photo'
                    featured = photo.get("featured", False)
                else:
                    src = photo
                    alt = f'{section["title"]} photo'
                    featured = False
                link_class = "life-photo-link life-photo-link-featured" if featured else "life-photo-link"
                thumbs += f'<a class="{link_class}" href="{esc(src)}" target="_blank" rel="noopener"><img class="life-photo" src="{esc(src)}" alt="{esc(alt)}" loading="lazy"></a>'
            gallery = f'<div class="life-gallery">{thumbs}</div>'
        races_html = ""
        records_html = ""
        emoji = LIFE_SECTION_EMOJI.get(section["title"], "")
        heading = f'{emoji} {esc(section["title"])}'.strip()
        width_class = ""
        section_id = "life-" + re.sub(r"[^a-z0-9]+", "-", section["title"].lower()).strip("-")
        sections_html.append(f'<section class="life-section{width_class}" id="{section_id}"><h2>{heading}</h2>{body}{club_html}{gallery}{races_html}{records_html}</section>')
    if not sections_html:
        sections_html.append('<p class="pending">Nothing added yet.</p>')

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>Life - {esc(DATA['name'])}</title>
<meta name="description" content="Outside research and engineering — {esc(DATA['name'])}'s life outside of work.">
{render_common_head('life.html', f"Life - {DATA['name']}", f"Outside research and engineering — {DATA['name']}'s life outside of work.")}
<link rel="stylesheet" href="style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Life")}
  <main class="container">
    <header class="page-header">
      <h1>Life</h1>
      {intro_html}
    </header>
    <div class="life-grid">{"".join(sections_html)}</div>
    <section class="life-section life-social-section">
      <h2>Social</h2>
      {life_socials}
    </section>
  </main>
  <footer class="site-footer"></footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "life.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def _wiki_tags(tags):
    return "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags or [])


def render_wiki_index():
    notes = sorted(WIKI_DATA.get("notes", []), key=lambda note: note.get("updated", note.get("published", "")), reverse=True)
    cards = []
    for note in notes:
        cards.append(f'''<article class="wiki-card">
          <p class="wiki-meta">Updated {esc(note.get("updated") or note.get("published", ""))}</p>
          <h2><a href="wiki/{esc(note['slug'])}.html">{esc(note['title'])}</a></h2>
          <p>{esc(note.get('summary', ''))}</p>
          <div class="wiki-tags">{_wiki_tags(note.get('tags'))}</div>
        </article>''')
    body = "".join(cards) if cards else '<p class="pending">No notes published yet.</p>'
    description = "Public notes on engineering, research, and career development."
    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>Wiki - {esc(DATA['name'])}</title>
<meta name="description" content="{esc(description)}">
{render_common_head('wiki.html', f"Wiki - {DATA['name']}", description)}
<link rel="stylesheet" href="style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Wiki")}
  <main class="container">
    <header class="page-header">
      <h1>Wiki</h1>
      <p class="page-intro">Working notes on engineering, research, and career development. These pages share public frameworks and sources, not confidential work or personal records.</p>
    </header>
    <div class="wiki-grid" id="notes">{body}</div>
  </main>
  <footer class="site-footer"></footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "wiki.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_wiki_page(note):
    sections = []
    for section in note.get("sections", []):
        paragraphs = "".join(f'<p>{esc(p)}</p>' for p in section.get("paragraphs", []))
        bullets = section.get("bullets") or []
        bullet_html = "" if not bullets else f'<ul>{"".join(f"<li>{esc(item)}</li>" for item in bullets)}</ul>'
        sections.append(f'<section class="wiki-section"><h2>{esc(section["heading"])}</h2>{paragraphs}{bullet_html}</section>')

    sources = note.get("sources") or []
    source_html = ""
    if sources:
        source_items = "".join(
            f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener">{esc(source["label"])}</a>'
            f'{f" — {esc(source.get("description"))}" if source.get("description") else ""}</li>'
            for source in sources
        )
        source_html = f'<section class="wiki-section"><h2>Public sources</h2><ul>{source_items}</ul></section>'

    description = note.get("summary", "")
    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>{esc(note['title'])} - {esc(DATA['name'])}</title>
<meta name="description" content="{esc(description)}">
{render_common_head(f"wiki/{note['slug']}.html", f"{note['title']} - {DATA['name']}", description, base="../")}
<link rel="stylesheet" href="../style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Wiki", base="../")}
  <main class="container wiki-article">
    <p><a href="../wiki.html">&larr; Back to Wiki</a></p>
    <header class="wiki-header">
      <p class="wiki-meta">Published {esc(note.get('published', ''))} &middot; Updated {esc(note.get('updated', note.get('published', '')))}</p>
      <h1>{esc(note['title'])}</h1>
      <p class="page-intro">{esc(description)}</p>
      <div class="wiki-tags">{_wiki_tags(note.get('tags'))}</div>
    </header>
    <aside class="wiki-notice">{esc(note.get('notice', ''))}</aside>
    {"".join(sections)}
    {source_html}
  </main>
  <footer class="site-footer"></footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "wiki", f"{note['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_paper_page(p):
    primary_title, secondary_title = paper_display_titles(p)
    # English is the primary language across visible UI, citation metadata,
    # and exports. The source-language Korean title remains supporting data.
    meta_tags = [f'<meta name="citation_title" content="{esc(primary_title)}">']
    for author in [a.strip() for a in p["authors"].split(",")]:
        meta_tags.append(f'<meta name="citation_author" content="{esc(author)}">')
    if p.get("year"):
        meta_tags.append(f'<meta name="citation_publication_date" content="{p["year"]}">')
    if p.get("venue"):
        meta_tags.append(f'<meta name="citation_journal_title" content="{esc(p["venue"])}">')
    if p.get("doi"):
        meta_tags.append(f'<meta name="citation_doi" content="{esc(p["doi"])}">')
    if has_local_pdf(p):
        pdf_url = f"{SITE_URL}/{p['pdf']}"
        meta_tags.append(f'<meta name="citation_pdf_url" content="{esc(pdf_url)}">')

    secondary_html = f'<p class="paper-title-secondary" lang="ko">{esc(secondary_title)}</p>' if secondary_title else ""
    secondary_meta_html = _render_secondary_metadata(p)
    abstract_html = f'<div class="abstract">{_render_abstract_body(p)}</div>' if p.get("abstract") else ""
    year = p["year"] if p.get("year") else "n.d."
    scholar_search = f"https://scholar.google.com/scholar?q={quote_plus(primary_title)}"
    meta_description = f"{p['authors']} — {p['venue']}{', ' + str(year) if p.get('year') else ''}. By {DATA['name']}."

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>{esc(primary_title)}</title>
<meta name="description" content="{esc(meta_description)}">
{render_common_head(f"papers/{p['slug']}.html", primary_title, meta_description, base="../")}
{chr(10).join(meta_tags)}
<link rel="stylesheet" href="../style.css?v={STYLE_VERSION}">
</head>
<body>
  {render_nav("Publications", base="../")}
  <main class="container">
    <p><a href="../publications.html">&larr; Back to Publications</a></p>
    <h1>{esc(primary_title)}</h1>
    {secondary_html}
    <p class="paper-meta">{esc(p['authors'])}</p>
    <p class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" &middot; {p['citations']} citations" if p['citations'] else ""}</p>
    {secondary_meta_html}
    {abstract_html}
    <div class="paper-badges large">{link_badges(p, paper_page=True)}</div>
    <p class="scholar-search"><a href="{esc(scholar_search)}" target="_blank" rel="noopener">Search on Google Scholar &rarr;</a></p>
  </main>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "papers", f"{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_bibtex():
    os.makedirs(os.path.join(ROOT, "bibtex"), exist_ok=True)

    # de-duplicate keys across the WHOLE collection (not just per-file) —
    # bibtex/all.bib concatenates every entry into one file, so two papers
    # sharing a base key like "Lee2018" would silently collide there even
    # though their individual bibtex/<slug>.bib files look fine on their own
    seen = Counter()
    keys = {}
    for p in DATA["papers"]:
        base = bibtex_key(p)
        seen[base] += 1
        keys[p["slug"]] = base if seen[base] == 1 else f"{base}{chr(ord('a') + seen[base] - 2)}"

    all_entries = []
    for p in DATA["papers"]:
        entry = to_bibtex(p, keys[p["slug"]])
        all_entries.append(entry)
        with open(os.path.join(ROOT, "bibtex", f"{p['slug']}.bib"), "w", encoding="utf-8") as f:
            f.write(entry + "\n")
    with open(os.path.join(ROOT, "bibtex", "all.bib"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_entries) + "\n")


def render_sitemap():
    urls = [f"{SITE_URL}/index.html", f"{SITE_URL}/publications.html", f"{SITE_URL}/cv.html", f"{SITE_URL}/life.html"]
    if WIKI_DATA.get("notes"):
        urls.append(f"{SITE_URL}/wiki.html")
    for note in WIKI_DATA.get("notes", []):
        urls.append(f"{SITE_URL}/wiki/{note['slug']}.html")
    for p in DATA["papers"]:
        urls.append(f"{SITE_URL}/papers/{p['slug']}.html")
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
'''
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def render_robots():
    txt = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "papers"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "papers", "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "wiki"), exist_ok=True)
    render_index()
    render_publications()
    render_cv()
    if WIKI_DATA.get("notes"):
        render_wiki_index()
    for note in WIKI_DATA.get("notes", []):
        render_wiki_page(note)
    render_life()
    for paper in DATA["papers"]:
        render_paper_page(paper)
    render_bibtex()
    render_sitemap()
    render_robots()
    missing_pdf = [p["slug"] for p in DATA["papers"] if not p.get("official_link") and not has_local_pdf(p)]
    print(f"Site generated: {len(DATA['papers'])} papers.")
    if missing_pdf:
        print(f"\n{len(missing_pdf)} papers still have no official link / PDF:")
        for slug in missing_pdf:
            print(f"  - papers/pdfs/{slug}.pdf")
