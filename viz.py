"""Static SVG chart generation for the Publications page.

Two charts, both built as plain inline SVG (no JS charting lib) so they stay
crawlable and theme-reactive via CSS custom properties:
  - Publications per year, stacked by category (magnitude + identity)
  - Top research keywords by frequency (magnitude, single hue)

Categorical palette (5 slots) and single sequential hue were validated with
the dataviz skill's validate_palette.js against this site's own dark
(#0d1117) and light (#ffffff) surfaces before use — see docs/DESIGN.md.
"""
import html
import re
from collections import Counter

CATEGORY_ORDER = ["int-journal", "domestic-journal", "int-conference", "domestic-conference", "thesis"]
CATEGORY_SHORT = {
    "int-journal": "Int'l Journal",
    "domestic-journal": "Domestic Journal",
    "int-conference": "Int'l Conference",
    "domestic-conference": "Domestic Conference",
    "thesis": "Ph.D. Dissertation",
}
# slot -> CSS var name, defined once in style.css for both themes
SLOT_VARS = ["--series-1", "--series-2", "--series-3", "--series-4", "--series-5"]

STOPWORDS = {
    "a", "an", "the", "of", "for", "and", "using", "based", "in", "on", "to", "with", "by", "from",
    "system", "systems", "study", "analysis", "development", "design", "via", "towards", "toward",
    "approach", "technique", "method", "methods", "model", "modeling", "scheme", "evaluation",
    "verification", "during", "under", "its", "into", "is", "as", "at", "part", "primary", "conceptual",
}


def esc(s):
    return html.escape(s or "", quote=True)


def _rounded_top_rect(x, y, w, h, r):
    r = min(r, w / 2, h)
    return (
        f'M{x},{y + h} '
        f'L{x},{y + r} '
        f'Q{x},{y} {x + r},{y} '
        f'L{x + w - r},{y} '
        f'Q{x + w},{y} {x + w},{y + r} '
        f'L{x + w},{y + h} Z'
    )


def year_category_chart(papers):
    by_year = {}
    for p in papers:
        y = p.get("year")
        if not y:
            continue
        by_year.setdefault(y, Counter())[p["category"]] += 1

    if not by_year:
        return ""

    years = list(range(min(by_year), max(by_year) + 1))
    max_total = max(sum(by_year.get(y, Counter()).values()) for y in years) or 1

    width, height = 980, 340
    margin = {"top": 30, "right": 20, "bottom": 40, "left": 36}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    baseline = margin["top"] + plot_h

    n = len(years)
    slot_w = plot_w / n
    bar_w = slot_w * 0.6
    gap_px = 2
    scale = plot_h / max_total

    bars_svg = []
    gridlines = []
    # gridlines at 0, 25%, 50%, 75%, 100% of max_total
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        gy = baseline - plot_h * frac
        gridlines.append(f'<line x1="{margin["left"]}" y1="{gy:.1f}" x2="{width - margin["right"]}" y2="{gy:.1f}" class="viz-grid"/>')

    for i, year in enumerate(years):
        counts = by_year.get(year, Counter())
        x = margin["left"] + i * slot_w + (slot_w - bar_w) / 2
        cumulative = 0
        total = sum(counts.values())
        nonzero_cats = [c for c in CATEGORY_ORDER if counts.get(c, 0) > 0]
        for j, cat in enumerate(CATEGORY_ORDER):
            count = counts.get(cat, 0)
            if count == 0:
                continue
            seg_h = count * scale
            y = baseline - cumulative - seg_h
            is_top = cat == nonzero_cats[-1]
            slot_idx = CATEGORY_ORDER.index(cat)
            fill = f"var({SLOT_VARS[slot_idx]})"
            title = f"{CATEGORY_SHORT[cat]}, {year}: {count}"
            if is_top and seg_h > 4:
                path = _rounded_top_rect(x, y, bar_w, seg_h, 4)
                bars_svg.append(f'<path d="{path}" fill="{fill}"><title>{esc(title)}</title></path>')
            else:
                bars_svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(seg_h, 0):.1f}" fill="{fill}"><title>{esc(title)}</title></rect>')
            cumulative += seg_h + gap_px
        if total:
            bars_svg.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{baseline - cumulative - 6:.1f}" '
                f'class="viz-value-label" text-anchor="middle">{total}</text>'
            )
        bars_svg.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{baseline + 20}" class="viz-axis-label" text-anchor="middle">{year}</text>'
        )

    legend_items = []
    for i, cat in enumerate(CATEGORY_ORDER):
        legend_items.append(
            f'<span class="viz-legend-item"><span class="viz-swatch" style="background:var({SLOT_VARS[i]})"></span>{esc(CATEGORY_SHORT[cat])}</span>'
        )

    table_rows = []
    for year in years:
        counts = by_year.get(year, Counter())
        cells = "".join(f"<td>{counts.get(c, 0)}</td>" for c in CATEGORY_ORDER)
        table_rows.append(f"<tr><th>{year}</th>{cells}</tr>")
    table_header = "".join(f"<th>{esc(CATEGORY_SHORT[c])}</th>" for c in CATEGORY_ORDER)

    return f'''<div class="viz-block">
      <h3>Publications by Year</h3>
      <svg viewBox="0 0 {width} {height}" class="viz-svg" role="img" aria-label="Stacked bar chart of publications per year by category">
        {"".join(gridlines)}
        {"".join(bars_svg)}
      </svg>
      <div class="viz-legend">{"".join(legend_items)}</div>
      <details class="viz-table-toggle">
        <summary>Table view</summary>
        <table class="viz-table">
          <thead><tr><th>Year</th>{table_header}</tr></thead>
          <tbody>{"".join(table_rows)}</tbody>
        </table>
      </details>
    </div>'''


def citation_year_chart(citation_stats):
    by_year = citation_stats.get("citations_by_year") or {}
    if not by_year:
        return ""

    years = sorted(int(y) for y in by_year)
    counts = {y: by_year[str(y)] for y in years}
    max_count = max(counts.values()) or 1

    width, height = 980, 340
    margin = {"top": 30, "right": 20, "bottom": 40, "left": 36}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    baseline = margin["top"] + plot_h

    n = len(years)
    slot_w = plot_w / n
    bar_w = slot_w * 0.6
    scale = plot_h / max_count

    bars_svg = []
    gridlines = []
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        gy = baseline - plot_h * frac
        gridlines.append(f'<line x1="{margin["left"]}" y1="{gy:.1f}" x2="{width - margin["right"]}" y2="{gy:.1f}" class="viz-grid"/>')

    for i, year in enumerate(years):
        count = counts[year]
        x = margin["left"] + i * slot_w + (slot_w - bar_w) / 2
        bar_h = count * scale
        y = baseline - bar_h
        title = f"{year}: {count} citations"
        if bar_h > 4:
            path = _rounded_top_rect(x, y, bar_w, bar_h, 4)
            bars_svg.append(f'<path d="{path}" fill="var(--series-1)"><title>{esc(title)}</title></path>')
        else:
            bars_svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(bar_h, 0):.1f}" fill="var(--series-1)"><title>{esc(title)}</title></rect>')
        bars_svg.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 6:.1f}" class="viz-value-label" text-anchor="middle">{count}</text>'
        )
        bars_svg.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{baseline + 20}" class="viz-axis-label" text-anchor="middle">{year}</text>'
        )

    table_rows = "".join(f"<tr><th>{year}</th><td>{counts[year]}</td></tr>" for year in years)

    return f'''<div class="viz-block">
      <h3>Citations by Year</h3>
      <svg viewBox="0 0 {width} {height}" class="viz-svg" role="img" aria-label="Bar chart of citations received per year, per Google Scholar">
        {"".join(gridlines)}
        {"".join(bars_svg)}
      </svg>
      <details class="viz-table-toggle">
        <summary>Table view</summary>
        <table class="viz-table">
          <thead><tr><th>Year</th><th>Citations</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </details>
    </div>'''


def keyword_chart(papers, top_n=25):
    counter = Counter()
    for p in papers:
        text = p.get("title_en") or p["title"]
        for word in re.findall(r"[A-Za-z][A-Za-z\-]+", text):
            w = word.lower().strip("-")
            if len(w) > 2 and w not in STOPWORDS:
                counter[w] += 1

    top = counter.most_common(top_n)
    if not top:
        return ""

    max_count = top[0][1]
    min_count = top[-1][1]
    span = max_count - min_count or 1
    min_font, max_font = 13, 38

    def font_size(count):
        t = ((count - min_count) / span) ** 0.5
        return min_font + t * (max_font - min_font)

    width = 980
    max_row_width = width - 40
    row_gap = 14

    rows, row = [], []
    row_width = 0
    for word, count in top:
        fs = font_size(count)
        w = len(word) * fs * 0.58 + 20
        if row and row_width + w > max_row_width:
            rows.append(row)
            row, row_width = [], 0
        row.append((word, count, fs, w))
        row_width += w
    if row:
        rows.append(row)

    elements = []
    y = 12
    for row in rows:
        row_width = sum(w for _, _, _, w in row)
        row_height = max(fs for _, _, fs, _ in row)
        x = (width - row_width) / 2
        baseline = y + row_height
        for word, count, fs, w in row:
            weight = 700 if fs > (min_font + max_font) / 2 else 500
            opacity = 0.55 + 0.45 * ((fs - min_font) / (max_font - min_font) if max_font > min_font else 1)
            elements.append(
                f'<text x="{x + w / 2:.1f}" y="{baseline:.1f}" text-anchor="middle" '
                f'font-size="{fs:.1f}" font-weight="{weight}" fill="var(--series-1)" '
                f'opacity="{opacity:.2f}">{esc(word)}<title>{esc(word)}: {count}</title></text>'
            )
            x += w
        y = baseline + row_gap
    height = y + 8

    table_rows = "".join(f"<tr><th>{esc(word)}</th><td>{count}</td></tr>" for word, count in top)

    return f'''<div class="viz-block">
      <h3>Top Research Keywords</h3>
      <svg viewBox="0 0 {width} {height:.0f}" class="viz-svg" role="img" aria-label="Word cloud of the most frequent keywords across publication titles, sized by frequency">
        {"".join(elements)}
      </svg>
      <details class="viz-table-toggle">
        <summary>Table view</summary>
        <table class="viz-table">
          <thead><tr><th>Keyword</th><th>Occurrences</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </details>
    </div>'''
