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
import math
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
    "proposed", "propose", "proposes", "presented", "present", "shown", "shows", "show", "considering",
    "considered", "demonstrate", "demonstrated", "demonstrates", "effectiveness", "numerical", "results",
    "result", "performed", "perform", "obtained", "used", "use", "studies", "investigated", "investigate",
    "designed", "verify", "verified", "compared", "comparison", "such", "that", "this", "these", "those",
    "can", "which", "also", "due", "each", "when", "while", "where", "than", "then", "however", "therefore",
    "case", "cases", "order", "various", "different", "several", "new", "novel", "well", "one", "two",
    "three", "first", "second", "final", "finally", "paper", "author", "authors", "work", "problem",
    "problems", "process", "processes", "given", "provide", "provides", "provided", "make", "makes",
    "made", "not", "only", "both", "were", "was", "are", "been", "has", "have", "had", "will", "may",
    "including", "across", "within", "involving", "spanning", "own",
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


def _count_words(text, counter, weight):
    for word in re.findall(r"[A-Za-z][A-Za-z\-]+", text or ""):
        w = word.lower().strip("-")
        if len(w) > 2 and w not in STOPWORDS:
            counter[w] += weight


def _boxes_overlap(a, b, pad=3):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + pad < bx0 or bx1 + pad < ax0 or ay1 + pad < by0 or by1 + pad < ay0)


def keyword_chart(papers, extra_texts=None, top_n=32):
    """Spiral-packed word cloud (Wordle-style): largest word centered, each
    subsequent word walks an outward spiral until it finds a free spot,
    checked against every word already placed. Draws from paper titles
    (weighted highest), abstracts, and optional extra text (CV bio/
    experience copy) so the cloud reflects the whole site, not just
    publication metadata."""
    counter = Counter()
    for p in papers:
        _count_words(p.get("title_en") or p["title"], counter, weight=3)
        _count_words(p.get("abstract"), counter, weight=1)
    for text in (extra_texts or []):
        _count_words(text, counter, weight=5)

    top = counter.most_common(top_n)
    if not top:
        return ""

    max_count = top[0][1]
    min_count = top[-1][1]
    span = max_count - min_count or 1
    min_font, max_font = 12, 68

    def font_size(count):
        t = ((count - min_count) / span) ** 0.55
        return min_font + t * (max_font - min_font)

    # Deterministic (not random, so regenerating the site doesn't churn the
    # SVG on every run) but varied tilt sequence, cycled by index — reads as
    # organically scattered rather than a mechanical alternation.
    tilt_sequence = [0, -13, 10, -19, 15, -7, 6, -16, 12, 0, -10, 17, -5, 8, -14, 3]

    search_radius_cap = 2600
    placed_boxes = []
    elements = []
    # Cycle through the site's full categorical palette (not just one hue)
    # and vary tilt per word (see tilt_sequence), so the cloud reads as an
    # actual varied word-cloud rather than a size-sorted list in one color.
    for idx, (word, count) in enumerate(top):
        fs = font_size(count)
        w = len(word) * fs * 0.62
        h = fs * 1.15
        tilt = tilt_sequence[idx % len(tilt_sequence)]
        if tilt:
            # Conservative axis-aligned box for a rotated label, so the
            # collision check doesn't let a tilted word overlap its
            # upright neighbors.
            rad = math.radians(abs(tilt))
            w, h = (
                abs(w * math.cos(rad)) + abs(h * math.sin(rad)),
                abs(w * math.sin(rad)) + abs(h * math.cos(rad)),
            )
        angle = idx * 0.6  # stagger each word's spiral start so same-size
        radius = 0.0        # words don't all fan out along the same ray
        spot = None
        while radius < search_radius_cap:
            cx = radius * math.cos(angle)
            cy = radius * math.sin(angle) * 0.7  # flatten to a wide oval, more "cloud"-shaped
            box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if not any(_boxes_overlap(box, b) for b in placed_boxes):
                spot = (cx, cy)
                placed_boxes.append(box)
                break
            angle += 0.24
            radius += 1.5
        if spot is None:
            continue
        tx, ty = spot
        weight_css = 700 if fs > (min_font + max_font) / 2 else 500
        opacity = 0.7 + 0.3 * ((fs - min_font) / (max_font - min_font) if max_font > min_font else 1)
        color = f"var({SLOT_VARS[idx % len(SLOT_VARS)]})"
        transform = f' transform="rotate({tilt} {tx:.1f} {ty:.1f})"' if tilt else ""
        elements.append(
            f'<text x="{tx:.1f}" y="{ty + fs * 0.34:.1f}" text-anchor="middle"{transform} '
            f'font-size="{fs:.1f}" font-weight="{weight_css}" fill="{color}" '
            f'opacity="{opacity:.2f}">{esc(word)}<title>{esc(word)}: {count}</title></text>'
        )

    margin = 16
    min_x = min(b[0] for b in placed_boxes) - margin
    min_y = min(b[1] for b in placed_boxes) - margin
    max_x = max(b[2] for b in placed_boxes) + margin
    max_y = max(b[3] for b in placed_boxes) + margin
    vb_w = max_x - min_x
    vb_h = max_y - min_y

    table_rows = "".join(f"<tr><th>{esc(word)}</th><td>{count}</td></tr>" for word, count in top)

    return f'''<div class="viz-block">
      <h3>Top Research Keywords</h3>
      <svg viewBox="{min_x:.1f} {min_y:.1f} {vb_w:.1f} {vb_h:.1f}" class="viz-svg" role="img" aria-label="Word cloud of the most frequent keywords across publications and professional background, sized by frequency">
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
