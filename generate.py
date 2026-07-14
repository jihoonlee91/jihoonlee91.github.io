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

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "papers.json"), encoding="utf-8") as f:
    DATA = json.load(f)

SITE_URL = "https://{}.github.io".format(
    DATA["github_url"].rstrip("/").rsplit("/", 1)[-1]
)

CATEGORY_LABELS = {
    "journal": "Journal Articles",
    "int-conference": "International Conference Papers",
    "domestic-conference": "Domestic Conference Papers",
    "thesis": "Ph.D. Dissertation",
}
CATEGORY_ORDER = ["journal", "int-conference", "domestic-conference", "thesis"]


def esc(s):
    return html.escape(s or "", quote=True)


def has_local_pdf(paper):
    return os.path.isfile(os.path.join(ROOT, paper["pdf"]))


def bibtex_key(paper):
    first_author = paper["authors"].split(",")[0].strip().split(" ")[-1]
    year = paper["year"] or "nd"
    return re.sub(r"[^A-Za-z0-9]", "", f"{first_author}{year}") or paper["slug"]


def to_bibtex(paper):
    is_article = paper["category"] == "journal"
    entry_type = "mastersthesis" if paper["category"] == "thesis" else ("article" if is_article else "inproceedings")
    key = bibtex_key(paper)
    lines = [f"@{entry_type}{{{key},"]
    lines.append(f'  title     = {{{paper["title"]}}},')
    lines.append(f'  author    = {{{paper["authors"].replace(", ", " and ")}}},')
    if paper.get("year"):
        lines.append(f'  year      = {{{paper["year"]}}},')
    if paper.get("venue"):
        field = "journal" if is_article else ("school" if entry_type == "mastersthesis" else "booktitle")
        lines.append(f'  {field:<9} = {{{paper["venue"]}}},')
    if paper.get("doi"):
        lines.append(f'  doi       = {{{paper["doi"]}}},')
    lines.append("}")
    return "\n".join(lines)


SOCIAL_LINKS = [
    ("scholar_url", "Google Scholar", "scholar"),
    ("orcid_url", "ORCID", "orcid"),
    ("researchgate_url", "ResearchGate", "rg"),
    ("linkedin_url", "LinkedIn", "linkedin"),
    ("github_url", "GitHub", "github"),
]


def render_social_links(extra_class=""):
    links = []
    for key, label, css_class in SOCIAL_LINKS:
        if DATA.get(key):
            links.append(f'<a class="social-btn {css_class}" href="{esc(DATA[key])}" target="_blank" rel="noopener">{label}</a>')
    if DATA.get("cv_url"):
        links.append(f'<a class="social-btn cv" href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">CV (PDF)</a>')
    return f'<nav class="social-links {extra_class}">{"".join(links)}</nav>'


def render_nav(active, base=""):
    items = [("index.html", "Home"), ("publications.html", "Publications"), ("cv.html", "CV")]
    links = "".join(
        f'<a href="{base}{href}" class="{"active" if name == active else ""}">{name}</a>'
        for href, name in items
    )
    return f'<nav class="site-nav"><div class="nav-inner"><a class="brand" href="{base}index.html">{esc(DATA["name"])}</a><div class="nav-links">{links}</div></div></nav>'


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
        contact_parts.append(f'<span>📍 {esc(DATA["location"])}</span>')
    if DATA.get("email"):
        contact_parts.append(f'<a href="mailto:{esc(DATA["email"])}">✉ {esc(DATA["email"])}</a>')
    contact_html = f'<p class="contact">{" · ".join(contact_parts)}</p>' if contact_parts else ""

    bio_html = f'<p class="bio">{esc(DATA["bio"])}</p>' if DATA.get("bio") else ""

    return f'''<section class="hero">
    {photo_html}
    <div class="hero-text">
      <h1>{esc(DATA['name'])}{' <span class="name-ko">(' + esc(DATA['name_ko']) + ')</span>' if DATA.get('name_ko') else ''}</h1>
      <p class="tagline">{esc(DATA.get('tagline', ''))}</p>
      <p class="affiliation">{esc(DATA.get('affiliation', ''))}</p>
      {contact_html}
      {bio_html}
      {interests_html}
      {render_social_links()}
    </div>
  </section>
  {stats_html}'''


def render_index():
    top_papers = sorted(DATA["papers"], key=lambda p: -(p["citations"] or 0))[:5]
    rows = []
    for p in top_papers:
        year = p["year"] if p.get("year") else "n.d."
        rows.append(f'''      <li class="paper-compact">
        <a href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a>
        <span class="paper-sub">{esc(p['venue'])}, {year} · 인용 {p['citations']}회</span>
      </li>''')

    html_out = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(DATA['name'])}{' (' + esc(DATA['name_ko']) + ')' if DATA.get('name_ko') else ''}</title>
<meta name="description" content="{esc(DATA['name'])} - {esc(DATA.get('tagline', ''))}">
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("Home")}
  <main class="container">
    {render_profile_header()}

    <section>
      <div class="section-head">
        <h2>Highlighted Publications</h2>
        <a class="see-all" href="publications.html">전체 {len(DATA['papers'])}편 보기 &rarr;</a>
      </div>
      <ul class="paper-list compact">
{chr(10).join(rows)}
      </ul>
    </section>
  </main>
  <footer class="site-footer">
    <p>&copy; {esc(DATA['name'])}. Built with a <a href="https://github.com/{esc(DATA['github_url'].rstrip('/').rsplit('/', 1)[-1])}/{esc(DATA['github_url'].rstrip('/').rsplit('/', 1)[-1])}.github.io">static site generator</a>. Full BibTeX: <a href="bibtex/all.bib">bibtex/all.bib</a></p>
  </footer>
</body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def link_badges(p, base="papers/pdfs/", paper_page=False):
    """Render clearly distinguished official-link vs preprint/PDF vs BibTeX badges."""
    official = p.get("official_link")
    local_pdf = has_local_pdf(p)
    badges = []
    if official:
        badges.append(f'<a class="badge badge-official" href="{esc(official)}" target="_blank" rel="noopener">공식 링크{" (DOI)" if p.get("doi") else ""}</a>')
    if local_pdf:
        pdf_path = ("../" if paper_page else "") + p["pdf"]
        badges.append(f'<a class="badge badge-preprint" href="{esc(pdf_path)}">Preprint PDF</a>')
    if not official and not local_pdf:
        badges.append('<span class="badge badge-pending">PDF 준비 중</span>')
    bib_path = ("../" if paper_page else "") + f'bibtex/{p["slug"]}.bib'
    badges.append(f'<a class="badge badge-bibtex" href="{esc(bib_path)}">BibTeX</a>')
    return "".join(badges)


def render_publications():
    by_category = {c: [] for c in CATEGORY_ORDER}
    for p in DATA["papers"]:
        by_category.setdefault(p["category"], []).append(p)

    sections = []
    for cat in CATEGORY_ORDER:
        papers = by_category.get(cat) or []
        if not papers:
            continue
        papers = sorted(papers, key=lambda p: -(p["year"] or 0))
        items = []
        for i, p in enumerate(papers, 1):
            year = p["year"] if p.get("year") else "n.d."
            title_en = f'<div class="paper-title-en">{esc(p["title_en"])}</div>' if p.get("title_en") else ""
            items.append(f'''        <li class="paper">
          <div class="paper-title"><span class="paper-index">{i}.</span> <a href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a></div>
          {title_en}
          <div class="paper-meta">{esc(p['authors'])}</div>
          <div class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" · 인용 {p['citations']}회" if p['citations'] else ""}</div>
          <div class="paper-badges">{link_badges(p)}</div>
        </li>''')
        sections.append(f'''    <section class="pub-category">
      <h2>{CATEGORY_LABELS[cat]} <span class="count">({len(papers)})</span></h2>
      <ul class="paper-list">
{chr(10).join(items)}
      </ul>
    </section>''')

    html_out = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Publications - {esc(DATA['name'])}</title>
<meta name="description" content="{esc(DATA['name'])}의 전체 논문 목록 (저널/국제학회/국내학회/학위논문)">
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_nav("Publications")}
  <main class="container">
    <h1>Publications</h1>
    <p class="page-intro">총 {len(DATA['papers'])}편 · Google Scholar와 개인 정리 목록을 통합한 전체 목록입니다. <a href="{esc(DATA['scholar_url'])}" target="_blank" rel="noopener">Google Scholar 프로필</a>에서도 확인할 수 있습니다.</p>
    <div class="legend">
      <span class="badge badge-official">공식 링크</span> 출판사/DOI 원문
      <span class="badge badge-preprint">Preprint PDF</span> 직접 업로드한 파일
      <span class="badge badge-pending">PDF 준비 중</span> 아직 링크 없음
    </div>
{chr(10).join(sections)}
  </main>
  <footer class="site-footer">
    <p>Full BibTeX: <a href="bibtex/all.bib">bibtex/all.bib</a></p>
  </footer>
</body>
</html>
'''
    with open(os.path.join(ROOT, "publications.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_list_section(title, items, fields):
    if not items:
        return f'<section><h2>{title}</h2><p class="pending">아직 등록된 내용이 없습니다.</p></section>'
    rows = []
    for item in items:
        parts = [esc(item.get(f, "")) for f in fields]
        rows.append(f'<li>{" — ".join(p for p in parts if p)}</li>')
    return f'''<section>
    <h2>{title}</h2>
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


def render_cv():
    education_html = render_list_section("Education", DATA.get("education", []), ["school", "degree", "period"])
    experience_html = render_list_section("Experience", DATA.get("experience", []), ["organization", "position", "period"])
    projects_html = render_list_section("Projects", DATA.get("projects", []), ["title", "description", "period"])
    awards_html = render_awards_section()
    skills_html = render_skills_section()

    cv_download = ""
    if DATA.get("cv_url"):
        cv_download = f'<p><a class="badge badge-official" href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">CV 다운로드 (PDF)</a></p>'

    html_out = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CV - {esc(DATA['name'])}</title>
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
  </main>
  <footer class="site-footer"></footer>
</body>
</html>
'''
    with open(os.path.join(ROOT, "cv.html"), "w", encoding="utf-8") as f:
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
        meta_tags.append(f'<meta name="citation_pdf_url" content="{SITE_URL}/{p['pdf']}">')

    title_en_html = f'<p class="paper-title-en">{esc(p["title_en"])}</p>' if p.get("title_en") else ""
    abstract_html = f'<p class="abstract">{esc(p["abstract"])}</p>' if p.get("abstract") else ""
    year = p["year"] if p.get("year") else "n.d."
    scholar_search = f"https://scholar.google.com/scholar?q={p['title'].replace(' ', '+')}"

    html_out = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(p['title'])}</title>
{chr(10).join(meta_tags)}
<link rel="stylesheet" href="../style.css">
</head>
<body>
  {render_nav("Publications", base="../")}
  <main class="container">
    <p><a href="../publications.html">&larr; 전체 목록으로</a></p>
    <h1>{esc(p['title'])}</h1>
    {title_en_html}
    <p class="paper-meta">{esc(p['authors'])}</p>
    <p class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}{f" · 인용 {p['citations']}회" if p['citations'] else ""}</p>
    {abstract_html}
    <div class="paper-badges large">{link_badges(p, paper_page=True)}</div>
    <p class="scholar-search"><a href="{esc(scholar_search)}" target="_blank" rel="noopener">Google Scholar에서 검색 &rarr;</a></p>
  </main>
</body>
</html>
'''
    with open(os.path.join(ROOT, "papers", f"{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_bibtex():
    os.makedirs(os.path.join(ROOT, "bibtex"), exist_ok=True)
    all_entries = []
    for p in DATA["papers"]:
        entry = to_bibtex(p)
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
    for paper in DATA["papers"]:
        render_paper_page(paper)
    render_bibtex()
    render_sitemap()
    render_robots()
    missing_pdf = [p["slug"] for p in DATA["papers"] if not p.get("official_link") and not has_local_pdf(p)]
    print(f"Site generated: {len(DATA['papers'])} papers.")
    if missing_pdf:
        print(f"\n공식 링크/PDF가 모두 없는 논문 {len(missing_pdf)}편:")
        for slug in missing_pdf:
            print(f"  - papers/pdfs/{slug}.pdf")
