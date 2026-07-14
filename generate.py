"""Generate the full static site (Home / Publications / CV / paper pages / BibTeX)
from papers.json.

Run `python generate.py` after editing papers.json (e.g. adding an
official_link/doi, or dropping a PDF into papers/pdfs/) to rebuild the site.
A GitHub Actions workflow (.github/workflows/build.yml) runs this
automatically on every push to main.
"""
import html
import json
import os
import re
from collections import Counter

import viz

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "papers.json"), encoding="utf-8") as f:
    DATA = json.load(f)

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

THEME_INIT_SCRIPT = """<script>
(function () {
  var saved = localStorage.getItem('theme');
  document.documentElement.setAttribute('data-theme', saved === 'light' ? 'light' : 'dark');
})();
</script>"""

THEME_TOGGLE_SCRIPT = """<script>
function toggleTheme() {
  var html = document.documentElement;
  var next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
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


def render_common_head(page_path, title, description, base=""):
    """Favicon, theme-color, canonical, and Open Graph/Twitter Card tags —
    shared across every page so link previews (Slack/LinkedIn/Twitter) and
    search engines get consistent metadata. See docs/ROADMAP.md."""
    url = f"{SITE_URL}/{page_path}"
    photo_url = f"{SITE_URL}/{DATA['photo']}" if DATA.get("photo") else ""
    tags = [
        f'<link rel="canonical" href="{esc(url)}">',
        f'<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">',
        '<meta name="theme-color" content="#0d1117" media="(prefers-color-scheme: dark)">',
        '<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">',
        '<meta property="og:type" content="profile">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{esc(url)}">',
    ]
    if photo_url:
        tags.append(f'<meta property="og:image" content="{esc(photo_url)}">')
    tags += [
        '<meta name="twitter:card" content="summary">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
    ]
    if photo_url:
        tags.append(f'<meta name="twitter:image" content="{esc(photo_url)}">')
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
    lines = [f"@{entry_type}{{{key},"]
    lines.append(f'  title     = {{{paper["title"]}}},')
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
    lines.append("}")
    return "\n".join(lines)


SOCIAL_LINKS = [
    ("scholar_url", "Google Scholar", "scholar", "S"),
    ("orcid_url", "ORCID", "orcid", "iD"),
    ("researchgate_url", "ResearchGate", "rg", "RG"),
    ("linkedin_url", "LinkedIn", "linkedin", "in"),
    ("github_url", "GitHub", "github", "GH"),
    ("instagram_url", "Instagram", "instagram", "IG"),
    ("facebook_url", "Facebook", "facebook", "f"),
]


def _icon_badge(initial):
    return (
        f'<svg class="social-icon" viewBox="0 0 20 20" width="16" height="16" aria-hidden="true">'
        f'<circle cx="10" cy="10" r="9.25" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        f'<text x="10" y="13.5" text-anchor="middle" font-size="{9 if len(initial) > 1 else 11}" '
        f'font-weight="700" fill="currentColor">{esc(initial)}</text>'
        f'</svg>'
    )


def render_social_links(extra_class=""):
    links = []
    for key, label, css_class, initial in SOCIAL_LINKS:
        if DATA.get(key):
            links.append(
                f'<a class="social-btn {css_class}" href="{esc(DATA[key])}" target="_blank" rel="noopener">'
                f'{_icon_badge(initial)}<span>{label}</span></a>'
            )
    if DATA.get("cv_url"):
        links.append(f'<a class="social-btn cv" href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">{_icon_badge("CV")}<span>CV (PDF)</span></a>')
    return f'<nav class="social-links {extra_class}">{"".join(links)}</nav>'


def render_nav(active, base=""):
    items = [("index.html", "Home"), ("publications.html", "Publications"), ("cv.html", "CV"), ("life.html", "Life")]
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

    stats = DATA.get("citation_stats") or {}
    stats_html = ""
    if stats:
        stats_html = f'''<div class="stats-row">
      <div class="stat"><span class="stat-num">{stats.get('citations_all', '-')}</span><span class="stat-label">Citations</span></div>
      <div class="stat"><span class="stat-num">{stats.get('h_index_all', '-')}</span><span class="stat-label">h-index</span></div>
      <div class="stat"><span class="stat-num">{stats.get('i10_index_all', '-')}</span><span class="stat-label">i10-index</span></div>
      <div class="stat"><span class="stat-num">{len(DATA['papers'])}</span><span class="stat-label">Publications</span></div>
    </div>'''

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
      <p class="current-role">&#128295; Currently: {esc(DATA.get('affiliation', ''))}</p>
      {contact_html}
      {bio_html}
      {interests_html}
      {render_social_links()}
    </div>
  </section>
  {stats_html}'''


def _timeline_sort_key(period):
    if "Present" in period:
        return 9999
    years = re.findall(r"\d{4}", period)
    return int(years[-1]) if years else 0


def render_timeline():
    entries = []
    for e in DATA.get("experience", []):
        entries.append({
            "period": e["period"],
            "title": e["organization"],
            "detail": e["position"].split(" — ")[0] if " — " in e["position"] else e["position"],
            "url": e.get("url"),
            "kind": "work",
        })
    for e in DATA.get("education", []):
        degree_short = e["degree"].split(" — ")[0]
        entries.append({
            "period": e["period"],
            "title": e["school"],
            "detail": degree_short,
            "url": e.get("url"),
            "kind": "education",
        })
    entries.sort(key=lambda e: _timeline_sort_key(e["period"]), reverse=True)

    if not entries:
        return ""

    rows = []
    for e in entries:
        title = f'<a href="{esc(e["url"])}" target="_blank" rel="noopener">{esc(e["title"])}</a>' if e.get("url") else esc(e["title"])
        rows.append(f'''      <li class="timeline-item timeline-{e['kind']}">
        <div class="timeline-period">{esc(e['period'])}</div>
        <div class="timeline-body">
          <div class="timeline-title">{title}</div>
          <div class="timeline-detail">{esc(e['detail'])}</div>
        </div>
      </li>''')

    return f'''<section>
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
        rows.append(f'''      <li class="paper-compact">
        <a href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a>
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
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("Home")}
  <main class="container">
    {render_profile_header()}

    {render_timeline()}

    <section>
      <div class="section-head">
        <h2>Highlighted Publications</h2>
        <a class="see-all" href="publications.html">View all {len(DATA['papers'])} publications &rarr;</a>
      </div>
      <ul class="paper-list compact">
{chr(10).join(rows)}
      </ul>
    </section>
  </main>
  <footer class="site-footer">
    <p>&copy; {esc(DATA['name'])}. Built with a <a href="{esc(DATA['github_url'])}/{esc(DATA['github_url'].rstrip('/').rsplit('/', 1)[-1])}.github.io">static site generator</a>. Full BibTeX: <a href="bibtex/all.bib">bibtex/all.bib</a></p>
  </footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def link_badges(p, base="papers/pdfs/", paper_page=False):
    """Render clearly distinguished official-link vs preprint/PDF vs BibTeX badges."""
    official = p.get("official_link")
    doi = p.get("doi")
    local_pdf = has_local_pdf(p)
    badges = []
    if official:
        label = f"Official Link &middot; DOI: {esc(doi)}" if doi else "Official Link"
        tooltip_target = f"doi.org/{doi}" if doi else official
        badges.append(
            f'<a class="badge badge-official" href="{esc(official)}" target="_blank" rel="noopener" '
            f'data-tooltip="{esc(tooltip_target)}">{label}</a>'
        )
    if local_pdf:
        pdf_path = ("../" if paper_page else "") + p["pdf"]
        badges.append(f'<a class="badge badge-preprint" href="{esc(pdf_path)}" data-tooltip="{esc(pdf_path)}">Preprint PDF</a>')
    if not official and not local_pdf:
        badges.append('<span class="badge badge-pending">PDF Coming Soon</span>')
    bib_path = ("../" if paper_page else "") + f'bibtex/{p["slug"]}.bib'
    bib_preview = to_bibtex(p, bibtex_key(p))
    badges.append(
        f'<a class="badge badge-bibtex" href="{esc(bib_path)}" data-tooltip="{esc(bib_preview)}" '
        f'onclick="return copyBibtex(this, event)">BibTeX</a>'
    )
    return "".join(badges)


def _render_paper_item(p, i):
    year = p["year"] if p.get("year") else "n.d."
    title_en = f'<div class="paper-title-en">{esc(p["title_en"])}</div>' if p.get("title_en") else ""
    abstract_html = (
        f'<details class="paper-abstract-toggle"><summary>Abstract</summary><p>{esc(p["abstract"])}</p></details>'
        if p.get("abstract") else ""
    )
    return f'''        <li class="paper">
          <div class="paper-title"><span class="paper-index">{i}.</span> <a href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a></div>
          {title_en}
          <div class="paper-meta">{esc(p['authors'])}</div>
          <div class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" &middot; {p['citations']} citations" if p['citations'] else ""}</div>
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
    "Autonomous Carrier Landing & Guidance",
    "Target Tracking, Sensing & Path Planning",
    "Satellite & Lunar Orbiter GNC",
]

VIEW_TOGGLE_SCRIPT = """<script>
function setPubView(view) {
  document.getElementById('view-category').style.display = view === 'category' ? '' : 'none';
  document.getElementById('view-theme').style.display = view === 'theme' ? '' : 'none';
  document.querySelectorAll('.view-toggle-btn').forEach(function (b) {
    b.classList.toggle('active', b.dataset.view === view);
  });
}
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

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>Publications - {esc(DATA['name'])}</title>
<meta name="description" content="Full publication list of {esc(DATA['name'])} (Journal / International Conference / Domestic Conference / Ph.D. Dissertation)">
{render_common_head('publications.html', f"Publications - {DATA['name']}", f"{len(DATA['papers'])} publications by {DATA['name']} — journal articles, conference papers, and PhD dissertation.")}
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("Publications")}
  <main class="container">
    <h1>Publications</h1>
    <p class="page-intro">{len(DATA['papers'])} publications total &middot; a unified list combining Google Scholar records with additional entries. Also available on my <a href="{esc(DATA['scholar_url'])}" target="_blank" rel="noopener">Google Scholar profile</a>.</p>
    {viz.year_category_chart(DATA['papers'])}
    {viz.citation_year_chart(DATA.get('citation_stats') or {})}
    {viz.keyword_chart(DATA['papers'])}
    <div class="legend">
      <span class="badge badge-official">Official Link</span> publisher / DOI source
      <span class="badge badge-preprint">Preprint PDF</span> self-hosted file
      <span class="badge badge-pending">PDF Coming Soon</span> not available yet
    </div>
    <div class="view-toggle">
      <button class="view-toggle-btn active" data-view="category" onclick="setPubView('category')">By Category</button>
      <button class="view-toggle-btn" data-view="theme" onclick="setPubView('theme')">By Research Theme</button>
    </div>
    <div id="view-category">
{category_sections}
    </div>
    <div id="view-theme" style="display:none">
{theme_sections}
    </div>
  </main>
  <footer class="site-footer">
    <p>Full BibTeX: <a href="bibtex/all.bib">bibtex/all.bib</a></p>
  </footer>
  {THEME_TOGGLE_SCRIPT}
  {VIEW_TOGGLE_SCRIPT}
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


def _group_consecutive_by_parent(items, name_field, split_char=", "):
    """Group consecutive items whose name_field shares a common trailing
    ", Parent" segment (e.g. "Digital Twin Center, Samsung Electronics"),
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

    def render_role(sub, item):
        label_parts = [p for p in (sub, item.get("position", "")) if p]
        header = f'{esc(" &mdash; ".join(label_parts))} &mdash; {esc(item.get("period", ""))}'
        highlights = item.get("highlights")
        if highlights:
            bullets = "".join(f"<li>{esc(h)}</li>" for h in highlights)
            return f'<li>{header}<ul class="experience-highlights">{bullets}</ul></li>'
        return f'<li>{header}</li>'

    groups = _group_consecutive_by_parent(items, "organization")
    rows = []
    for g in groups:
        if len(g["items"]) == 1:
            sub, item = g["items"][0]
            org = f'{sub}, {g["parent"]}' if sub else g["parent"]
            header = f'{esc(org)} &mdash; {esc(item.get("position", ""))} &mdash; {esc(item.get("period", ""))}'
            highlights = item.get("highlights")
            bullets = f'<ul class="experience-highlights">{"".join(f"<li>{esc(h)}</li>" for h in highlights)}</ul>' if highlights else ""
            rows.append(f'<li>{header}{bullets}</li>')
        else:
            sub_rows = "".join(render_role(sub, item) for sub, item in g["items"])
            rows.append(f'<li class="experience-group"><div class="experience-company">{esc(g["parent"])}</div><ul class="experience-roles">{sub_rows}</ul></li>')

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
    rows = []
    for g in groups:
        if len(g["items"]) == 1:
            _, item = g["items"][0]
            degree = esc(item.get("degree", ""))
            if item.get("url"):
                degree = f'<a href="{esc(item["url"])}" target="_blank" rel="noopener">{degree}</a>'
            rows.append(f'<li>{esc(g["parent"])} &mdash; {degree} &mdash; {esc(item.get("period", ""))}</li>')
        else:
            sub_rows = []
            for _, item in g["items"]:
                degree = esc(item.get("degree", ""))
                if item.get("url"):
                    degree = f'<a href="{esc(item["url"])}" target="_blank" rel="noopener">{degree}</a>'
                sub_rows.append(f'<li>{degree} &mdash; {esc(item.get("period", ""))}</li>')
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
    projects_html = render_list_section("Projects", DATA.get("projects", []), ["title", "description", "period"])
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
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("CV")}
  <main class="container">
    <h1>CV</h1>
    {cv_download}
    {experience_html}
    {education_html}
    {awards_html}
    {skills_html}
    {projects_html}
    {collaborators_html}
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
}


def render_life():
    life = DATA.get("life") or {}
    intro_html = f'<p class="page-intro">{esc(life["intro"])}</p>' if life.get("intro") else ""

    sections_html = []
    for section in life.get("sections", []):
        content = section.get("content")
        body = f'<p>{esc(content)}</p>' if content else '<p class="pending">Coming soon.</p>'
        photos = section.get("photos") or []
        gallery = ""
        if photos:
            thumbs = "".join(
                f'<a href="{esc(photo)}" target="_blank" rel="noopener"><img class="life-photo" src="{esc(photo)}" alt="{esc(section["title"])} photo" loading="lazy"></a>'
                for photo in photos
            )
            gallery = f'<div class="life-gallery">{thumbs}</div>'
        emoji = LIFE_SECTION_EMOJI.get(section["title"], "")
        heading = f'{emoji} {esc(section["title"])}'.strip()
        sections_html.append(f'<section><h2>{heading}</h2>{body}{gallery}</section>')
    if not sections_html:
        sections_html.append('<p class="pending">Nothing added yet.</p>')

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>Life - {esc(DATA['name'])}</title>
<meta name="description" content="Outside the lab and the fab — {esc(DATA['name'])}'s life outside of work.">
{render_common_head('life.html', f"Life - {DATA['name']}", f"Outside the lab and the fab — {DATA['name']}'s life outside of work.")}
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("Life")}
  <main class="container">
    <h1>Life</h1>
    {intro_html}
    {"".join(sections_html)}
  </main>
  <footer class="site-footer"></footer>
  {THEME_TOGGLE_SCRIPT}
</body>
</html>
'''
    with open(os.path.join(ROOT, "life.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_paper_page(p):
    meta_tags = [f'<meta name="citation_title" content="{esc(p["title"])}">']
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

    title_en_html = f'<p class="paper-title-en">{esc(p["title_en"])}</p>' if p.get("title_en") else ""
    abstract_html = f'<p class="abstract">{esc(p["abstract"])}</p>' if p.get("abstract") else ""
    year = p["year"] if p.get("year") else "n.d."
    scholar_search = f"https://scholar.google.com/scholar?q={p['title'].replace(' ', '+')}"
    meta_description = f"{p['authors']} — {p['venue']}{', ' + str(year) if p.get('year') else ''}. By {DATA['name']}."

    html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{THEME_INIT_SCRIPT}
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(meta_description)}">
{render_common_head(f"papers/{p['slug']}.html", p['title'], meta_description, base="../")}
{chr(10).join(meta_tags)}
<link rel="stylesheet" href="../style.css">
</head>
<body>
  {render_nav("Publications", base="../")}
  <main class="container">
    <p><a href="../publications.html">&larr; Back to Publications</a></p>
    <h1>{esc(p['title'])}</h1>
    {title_en_html}
    <p class="paper-meta">{esc(p['authors'])}</p>
    <p class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" &middot; {p['citations']} citations" if p['citations'] else ""}</p>
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
    urls = [f"{SITE_URL}/index.html", f"{SITE_URL}/publications.html", f"{SITE_URL}/cv.html"]
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
    render_index()
    render_publications()
    render_cv()
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
