"""Generate index.html, per-paper landing pages, and BibTeX from papers.json.

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


def esc(s):
    return html.escape(s or "", quote=True)


def paper_href(paper):
    if paper.get("official_link"):
        return paper["official_link"]
    return paper["pdf"]


def has_local_pdf(paper):
    return os.path.isfile(os.path.join(ROOT, paper["pdf"]))


def bibtex_key(paper):
    first_author = paper["authors"].split(",")[0].strip().split(" ")[-1]
    year = paper["year"] or "n_d_"
    return re.sub(r"[^A-Za-z0-9]", "", f"{first_author}{year}") or paper["slug"]


def to_bibtex(paper):
    entry_type = "article" if "Journal" in paper["venue"] or "Transactions" in paper["venue"] or "Access" in paper["venue"] or "Sensors" in paper["venue"] else "inproceedings"
    key = bibtex_key(paper)
    lines = [f"@{entry_type}{{{key},"]
    lines.append(f'  title     = {{{paper["title"]}}},')
    lines.append(f'  author    = {{{paper["authors"].replace(", ", " and ")}}},')
    if paper.get("year"):
        lines.append(f'  year      = {{{paper["year"]}}},')
    if paper.get("venue"):
        field = "journal" if entry_type == "article" else "booktitle"
        lines.append(f'  {field:<9} = {{{paper["venue"]}}},')
    if paper.get("doi"):
        lines.append(f'  doi       = {{{paper["doi"]}}},')
    lines.append("}")
    return "\n".join(lines)


def render_profile_header(base=""):
    links = []
    for key, label in [
        ("scholar_url", "Google Scholar"),
        ("github_url", "GitHub"),
        ("linkedin_url", "LinkedIn"),
        ("orcid_url", "ORCID"),
        ("researchgate_url", "ResearchGate"),
    ]:
        if DATA.get(key):
            links.append(f'<a href="{esc(DATA[key])}" target="_blank" rel="noopener">{label}</a>')
    if DATA.get("cv_url"):
        links.append(f'<a href="{esc(DATA["cv_url"])}" target="_blank" rel="noopener">CV</a>')

    photo_html = ""
    if DATA.get("photo") and os.path.isfile(os.path.join(ROOT, DATA["photo"])):
        photo_html = f'<img class="profile-photo" src="{base}{esc(DATA["photo"])}" alt="{esc(DATA["name"])}">'

    stats = DATA.get("citation_stats") or {}
    stats_html = ""
    if stats:
        stats_html = f'''<p class="stats">
      인용 {stats.get('citations_all', '-')}회 (2021년 이후 {stats.get('citations_since_2021', '-')}회) ·
      h-index {stats.get('h_index_all', '-')} · i10-index {stats.get('i10_index_all', '-')}
    </p>'''

    interests_html = ""
    if DATA.get("interests"):
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in DATA["interests"])
        interests_html = f'<p class="interests">{tags}</p>'

    contact_html = ""
    if DATA.get("email"):
        contact_html = f'<p class="contact"><a href="mailto:{esc(DATA["email"])}">{esc(DATA["email"])}</a></p>'

    return f'''<header class="profile">
    {photo_html}
    <div class="profile-text">
      <h1>{esc(DATA['name'])}{' (' + esc(DATA['name_ko']) + ')' if DATA.get('name_ko') else ''}</h1>
      <p class="tagline">{esc(DATA.get('tagline', ''))}</p>
      <p class="affiliation">{esc(DATA.get('affiliation', ''))}</p>
      {contact_html}
      {interests_html}
      {stats_html}
      <nav class="social-links">
        {" · ".join(links)}
      </nav>
    </div>
  </header>'''


def render_list_section(title, items, fields):
    if not items:
        return ""
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


def render_index():
    rows = []
    for p in DATA["papers"]:
        available = bool(p.get("official_link")) or has_local_pdf(p)
        badge = "" if available else ' <span class="pending">(PDF 준비 중)</span>'
        year = p["year"] if p.get("year") else "n.d."
        rows.append(f'''      <li class="paper">
        <div class="paper-title">
          <a href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a>{badge}
        </div>
        <div class="paper-meta">{esc(p['authors'])}</div>
        <div class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year}
          <span class="citations">· 인용 {p['citations']}회</span>
        </div>
      </li>''')

    education_html = render_list_section("Education", DATA.get("education", []), ["school", "degree", "period"])
    experience_html = render_list_section("Experience", DATA.get("experience", []), ["organization", "position", "period"])
    projects_html = render_list_section("Projects", DATA.get("projects", []), ["title", "description", "period"])

    html_out = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(DATA['name'])} - Publications</title>
<meta name="description" content="{esc(DATA['name'])}의 논문 목록과 원문 링크">
<link rel="stylesheet" href="style.css">
</head>
<body>
  {render_profile_header()}

  <main>
    {education_html}
    {experience_html}
    {projects_html}

    <section>
      <h2>Publications ({len(DATA['papers'])})</h2>
      <ul class="paper-list">
{chr(10).join(rows)}
      </ul>
    </section>
  </main>

  <footer>
    <p>Last generated from <code>papers.json</code>. Full BibTeX: <a href="bibtex/all.bib">bibtex/all.bib</a></p>
  </footer>
</body>
</html>
'''
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def render_paper_page(p):
    pdf_available = has_local_pdf(p)
    official = p.get("official_link")

    meta_tags = [f'<meta name="citation_title" content="{esc(p["title"])}">']
    for author in [a.strip() for a in p["authors"].split(",")]:
        meta_tags.append(f'<meta name="citation_author" content="{esc(author)}">')
    if p.get("year"):
        meta_tags.append(f'<meta name="citation_publication_date" content="{p["year"]}">')
    if p.get("venue"):
        meta_tags.append(f'<meta name="citation_journal_title" content="{esc(p["venue"])}">')
    if p.get("doi"):
        meta_tags.append(f'<meta name="citation_doi" content="{esc(p["doi"])}">')
    if pdf_available:
        pdf_url = f"{SITE_URL}/{p['pdf']}"
        meta_tags.append(f'<meta name="citation_pdf_url" content="{esc(pdf_url)}">')

    action_html = []
    if official:
        action_html.append(f'<a class="btn" href="{esc(official)}" target="_blank" rel="noopener">원문 보기 (공식 링크)</a>')
    if pdf_available:
        action_html.append(f'<a class="btn" href="../{esc(p["pdf"])}">PDF 다운로드</a>')
    action_html.append(f'<a class="btn" href="../bibtex/{esc(p["slug"])}.bib">BibTeX</a>')
    if not official and not pdf_available:
        action_html.append('<p class="pending">원문/PDF 준비 중입니다.</p>')

    abstract_html = f'<p class="abstract">{esc(p["abstract"])}</p>' if p.get("abstract") else ""
    year = p["year"] if p.get("year") else "n.d."

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
  <header>
    <p><a href="../index.html">&larr; 목록으로</a></p>
  </header>
  <main>
    <h1>{esc(p['title'])}</h1>
    <p class="paper-meta">{esc(p['authors'])}</p>
    <p class="paper-venue">{esc(p['venue'])}{', ' if p['venue'] else ''}{year} · 인용 {p['citations']}회</p>
    {abstract_html}
    <div class="actions">
      {chr(10).join(action_html)}
    </div>
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
    urls = [f"{SITE_URL}/index.html"]
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
    for paper in DATA["papers"]:
        render_paper_page(paper)
    render_bibtex()
    render_sitemap()
    render_robots()
    missing_pdf = [p["slug"] for p in DATA["papers"] if not p.get("official_link") and not has_local_pdf(p)]
    print(f"Site generated: {len(DATA['papers'])} papers.")
    if missing_pdf:
        print(f"\nPDF/원문 링크가 없는 논문 {len(missing_pdf)}편 (papers/pdfs/ 에 파일을 넣거나 papers.json의 official_link를 채워주세요):")
        for slug in missing_pdf:
            print(f"  - papers/pdfs/{slug}.pdf")
