"""Static visualization generation for the Publications and Life pages.

Charts use plain inline SVG (no JS charting library), while venue statistics
use semantic HTML. Everything stays crawlable and theme-reactive:
  - Publications per year, stacked by category (magnitude + identity)
  - Publication venues, grouped by journal/conference series
  - Citations received per year
  - Top research keywords by frequency (magnitude, single hue)
  - Life: training hours per year by discipline, and the last 52 weeks

Categorical palette (5 slots) and single sequential hue were validated with
the dataviz skill's validate_palette.js against this site's own dark
(#0d1117) and light (#ffffff) surfaces before use — see docs/DESIGN.md.
"""
import datetime as dt
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
    "add", "staff", "engineer", "develop", "developed", "developing", "through", "workflow",
    "workflows", "research",
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


def citation_year_chart(citation_stats, updated_label=None):
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

    updated_html = f" &middot; updated {esc(updated_label)}" if updated_label else ""

    return f'''<div class="viz-block">
      <h3>Citations by Year</h3>
      <p class="viz-note viz-source">Source: Google Scholar &middot; {years[0]}&ndash;{years[-1]}{updated_html}</p>
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


# ---- Life page: training charts from assets/life/training.json ----
# Same validated 5-slot palette; the sixth bucket ("Other") is a neutral gray,
# so color is never the only cue (legend, value labels, table view as above).
TRAINING_ORDER = ["swim", "bike", "run", "row", "hike", "other"]
TRAINING_LABELS = {"swim": "Swim", "bike": "Bike", "run": "Run", "row": "Row", "hike": "Hike", "other": "Other"}
TRAINING_FILLS = {"swim": "var(--series-1)", "bike": "var(--series-2)", "run": "var(--series-3)",
                  "row": "var(--series-5)", "hike": "var(--series-4)", "other": "var(--series-other)"}
TRAINING_OTHER_NOTE = "strength, climbing, multisport races, paddling, walking"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Small viewBox so the 13px labels stay readable when the chart shrinks to a phone column.
_TW, _TH = 480, 260


def _nice_step(max_value, ticks=4):
    raw = max_value / ticks
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500):
        if step >= raw:
            return step
    return 1000


def _y_axis(max_value, margin, plot_h, baseline, unit=""):
    step = _nice_step(max_value)
    top = step * math.ceil(max_value / step) or step
    out = []
    v = 0
    while v <= top + 1e-9:
        gy = baseline - plot_h * v / top
        out.append(f'<line x1="{margin["left"]}" y1="{gy:.1f}" x2="{_TW - margin["right"]}" y2="{gy:.1f}" class="viz-grid"/>')
        out.append(f'<text x="{margin["left"] - 6}" y="{gy + 4:.1f}" class="viz-axis-label" text-anchor="end">{v:g}{unit}</text>')
        v += step
    return top, out


def training_year_chart(training, current_year=None):
    years = training.get("years") or []
    if not years:
        return ""
    totals = [sum(y["hours"].values()) for y in years]
    margin = {"top": 26, "right": 8, "bottom": 34, "left": 40}
    plot_w = _TW - margin["left"] - margin["right"]
    plot_h = _TH - margin["top"] - margin["bottom"]
    baseline = margin["top"] + plot_h
    top, svg = _y_axis(max(totals), margin, plot_h, baseline)
    slot_w = plot_w / len(years)
    bar_w = slot_w * 0.62
    scale = plot_h / top
    for i, row in enumerate(years):
        year, hours = row["year"], row["hours"]
        x = margin["left"] + i * slot_w + (slot_w - bar_w) / 2
        ytd = " (year to date)" if year == current_year else ""
        cumulative = 0.0
        shown = [d for d in TRAINING_ORDER if hours.get(d, 0) * scale >= 0.5]
        for d in shown:
            seg_h = hours[d] * scale
            y = baseline - cumulative - seg_h
            title = esc(f"{TRAINING_LABELS[d]}, {year}{ytd}: {hours[d]:.0f} h")
            if d == shown[-1] and seg_h > 4:
                svg.append(f'<path d="{_rounded_top_rect(x, y, bar_w, seg_h, 3)}" fill="{TRAINING_FILLS[d]}"><title>{title}</title></path>')
            else:
                svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{seg_h:.1f}" fill="{TRAINING_FILLS[d]}"><title>{title}</title></rect>')
            cumulative += seg_h
        svg.append(f'<text x="{x + bar_w / 2:.1f}" y="{baseline - cumulative - 6:.1f}" class="viz-value-label" text-anchor="middle">{totals[i]:.0f}</text>')
        label = f"&#8217;{str(year)[2:]}" + ("*" if ytd else "")
        svg.append(f'<text x="{x + bar_w / 2:.1f}" y="{baseline + 20}" class="viz-axis-label" text-anchor="middle">{label}</text>')
    other_title = f' title="{esc(TRAINING_OTHER_NOTE)}"'
    legend = "".join(
        f'<span class="viz-legend-item"{other_title if d == "other" else ""}>'
        f'<span class="viz-swatch" style="background:{TRAINING_FILLS[d]}"></span>{TRAINING_LABELS[d]}</span>'
        for d in TRAINING_ORDER
    )
    head = "".join(f"<th>{TRAINING_LABELS[d]}</th>" for d in TRAINING_ORDER)
    rows = "".join(
        f"<tr><th>{r['year']}{'*' if r['year'] == current_year else ''}</th>"
        + "".join(f"<td>{r['hours'].get(d, 0):.0f}</td>" for d in TRAINING_ORDER)
        + f"<td>{t:.0f}</td></tr>"
        for r, t in zip(years, totals)
    )
    ytd_note = f" &middot; *{current_year} so far" if current_year and years[-1]["year"] == current_year else ""
    return f'''<div class="viz-block">
        <h3>Hours per year</h3>
        <p class="viz-note">Stacked by discipline{ytd_note}</p>
        <svg viewBox="0 0 {_TW} {_TH}" class="viz-svg" role="img" aria-label="Stacked bar chart of training hours per year by discipline, {years[0]['year']} to {years[-1]['year']}">{"".join(svg)}</svg>
        <div class="viz-legend">{legend}</div>
        <details class="viz-table-toggle">
          <summary>Table view</summary>
          <table class="viz-table">
            <thead><tr><th>Year</th>{head}<th>Total</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
          <p class="viz-note training-other-note">Other: {esc(TRAINING_OTHER_NOTE)}.</p>
        </details>
      </div>'''


def training_week_chart(training):
    weeks = training.get("weeks") or []
    if not weeks:
        return ""
    hours = [w["hours"] for w in weeks]
    avg = sum(hours) / len(hours)
    margin = {"top": 26, "right": 8, "bottom": 34, "left": 40}
    plot_w = _TW - margin["left"] - margin["right"]
    plot_h = _TH - margin["top"] - margin["bottom"]
    baseline = margin["top"] + plot_h
    top, svg = _y_axis(max(hours), margin, plot_h, baseline, unit=" h")
    slot_w = plot_w / len(weeks)
    bar_w = max(slot_w - 2, 1)
    scale = plot_h / top
    last_label_i = -99
    for i, w in enumerate(weeks):
        start = dt.date.fromisoformat(w["start"])
        x = margin["left"] + i * slot_w + (slot_w - bar_w) / 2
        bar_h = w["hours"] * scale
        title = esc(f"Week of {MONTHS[start.month - 1]} {start.day}, {start.year}: {w['hours']:.1f} h")
        # A transparent full-height hit area keeps the hover tooltip usable on near-empty weeks.
        svg.append(f'<rect x="{margin["left"] + i * slot_w:.1f}" y="{margin["top"]}" width="{slot_w:.1f}" height="{plot_h}" fill="transparent"><title>{title}</title></rect>')
        if bar_h > 0:
            svg.append(f'<rect x="{x:.1f}" y="{baseline - bar_h:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="1.5" fill="var(--series-1)" pointer-events="none"/>')
        # Month tick where a month starts inside this week; skip ticks that would collide.
        end = start + dt.timedelta(days=6)
        if (start.day == 1 or end.month != start.month) and i - last_label_i >= 4:
            month = end.month if end.month != start.month else start.month
            svg.append(f'<text x="{x + bar_w / 2:.1f}" y="{baseline + 20}" class="viz-axis-label" text-anchor="middle">{MONTHS[month - 1]}</text>')
            last_label_i = i
    ay = baseline - avg * scale
    svg.append(f'<line x1="{margin["left"]}" y1="{ay:.1f}" x2="{_TW - margin["right"]}" y2="{ay:.1f}" class="training-avg-line"/>')
    svg.append(f'<text x="{_TW - margin["right"]}" y="{ay - 6:.1f}" class="viz-value-label training-avg-label" text-anchor="end">avg {avg:.1f} h</text>')
    first = dt.date.fromisoformat(weeks[0]["start"])
    last = dt.date.fromisoformat(weeks[-1]["start"])
    rows = "".join(f"<tr><th>{w['start']}</th><td>{w['hours']:.1f}</td></tr>" for w in weeks)
    return f'''<div class="viz-block">
        <h3>Last 52 weeks</h3>
        <p class="viz-note">Hours per week &middot; {MONTHS[first.month - 1]} {first.year} &ndash; {MONTHS[last.month - 1]} {last.year}</p>
        <svg viewBox="0 0 {_TW} {_TH}" class="viz-svg" role="img" aria-label="Bar chart of training hours per week over the last 52 weeks, averaging {avg:.1f} hours">{"".join(svg)}</svg>
        <details class="viz-table-toggle">
          <summary>Table view</summary>
          <table class="viz-table">
            <thead><tr><th>Week starting</th><th>Hours</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </details>
      </div>'''


VENUE_PATTERNS = (
    (r"AIAA SciTech \d{4} Forum", "AIAA SciTech Forum"),
    (r"IFAC Symposium on Automatic Control in Aerospace", "IFAC Symposium on Automatic Control in Aerospace (ACA)"),
    (r"European Control Conference \(ECC\)", "European Control Conference (ECC)"),
    (r"International Conference on Control, Automation and Systems \(ICCAS\)", "ICCAS"),
    (r"European Conference for Aeronautics and Space Sciences \(EUCASS\)", "EUCASS"),
    (r"Congress of the International Council of the Aeronautical Sciences \(ICAS\)", "ICAS Congress"),
    (r"Asia-Pacific International Symposium on Aerospace Technology \(APISAT\)", "APISAT"),
    (r"IPNT Conference", "IPNT Conference"),
    (r"KSAS (?:Spring|Fall) Conference", "KSAS Conference"),
    (r"SASE (?:Spring|Fall) Conference", "SASE Conference"),
    (r"Aviation-Specialized University Conference", "Aviation-Specialized University Conference"),
)


def _canonical_venue(paper):
    venue = paper.get("venue") or "Unspecified venue"
    category = paper.get("category")
    if category in ("int-journal", "domestic-journal"):
        return re.split(r",\s+Vol\.", venue, maxsplit=1)[0]
    if category == "thesis":
        return "Seoul National University"
    for pattern, label in VENUE_PATTERNS:
        if re.search(pattern, venue, flags=re.IGNORECASE):
            return label
    return venue.split(",", 1)[0]


def scholar_index_table(citation_stats, updated_label=None):
    """All-time vs. since-2021 citation/h-index/i10-index breakdown, as
    shown on the owner's Google Scholar profile — a compact complement to
    the citations-by-year bar chart, which only shows the yearly count."""
    rows = [
        ("Citations", citation_stats.get("citations_all"), citation_stats.get("citations_since_2021")),
        ("h-index", citation_stats.get("h_index_all"), citation_stats.get("h_index_since_2021")),
        ("i10-index", citation_stats.get("i10_index_all"), citation_stats.get("i10_index_since_2021")),
    ]
    if not any(all_val is not None for _, all_val, _ in rows):
        return ""

    table_rows = "".join(
        f"<tr><th>{esc(label)}</th><td>{all_val if all_val is not None else '—'}</td>"
        f"<td>{since_val if since_val is not None else '—'}</td></tr>"
        for label, all_val, since_val in rows
    )
    updated_html = f" &middot; updated {esc(updated_label)}" if updated_label else ""

    return f'''<div class="viz-block">
      <h3>Google Scholar Index</h3>
      <p class="viz-note viz-source">Source: Google Scholar{updated_html}</p>
      <table class="viz-table scholar-index-table">
        <thead><tr><th></th><th>All</th><th>Since 2021</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>'''


def venue_statistics(papers):
    """Summarize publication destinations by venue series, not event year."""
    grouped = {category: Counter() for category in CATEGORY_ORDER}
    for paper in papers:
        category = paper.get("category")
        if category in grouped:
            grouped[category][_canonical_venue(paper)] += 1

    max_count = max((count for venues in grouped.values() for count in venues.values()), default=1)
    sections = []
    for category in CATEGORY_ORDER:
        venues = grouped[category]
        if not venues:
            continue
        paper_count = sum(venues.values())
        venue_count = len(venues)
        rows = []
        for name, count in sorted(venues.items(), key=lambda item: (-item[1], item[0].lower())):
            width = max(4, count / max_count * 100)
            rows.append(f'''<li class="venue-row">
              <span class="venue-name">{esc(name)}</span>
              <span class="venue-bar-track" aria-hidden="true"><span class="venue-bar" style="width:{width:.1f}%"></span></span>
              <strong class="venue-count">{count}</strong>
            </li>''')
        paper_word = "publication" if paper_count == 1 else "publications"
        venue_word = "venue" if venue_count == 1 else "venues"
        sections.append(f'''<section class="venue-group">
          <div class="venue-group-head">
            <h4>{esc(CATEGORY_SHORT[category])}</h4>
            <span>{paper_count} {paper_word} · {venue_count} {venue_word}</span>
          </div>
          <ul class="venue-list">{"".join(rows)}</ul>
        </section>''')

    return f'''<div class="viz-block venue-stats">
      <h3>Publication Venues</h3>
      <p class="viz-note">Journal titles and recurring conference series are grouped across years.</p>
      <div class="venue-groups">{"".join(sections)}</div>
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


def keyword_chart(papers, curated_terms=None, top_n=64):
    """Spiral-packed word cloud (Wordle-style): largest word centered, each
    subsequent word walks an outward spiral until it finds a free spot,
    checked against every word already placed. Draws from paper titles,
    abstracts, and a small explicit set of durable professional focus terms.
    It deliberately does not ingest raw CV prose, which would over-promote
    incidental job-title and workflow vocabulary."""
    counter = Counter()
    for p in papers:
        _count_words(p.get("title_en") or p["title"], counter, weight=3)
        _count_words(p.get("abstract"), counter, weight=1)
    for term, score in (curated_terms or []):
        label = (term or "").strip()
        if label and score > 0:
            # Merge an exact corpus token into its curated, presentation-case
            # label (for example optimization -> Optimization) instead of
            # rendering two visually duplicated entries.
            corpus_score = counter.pop(label.lower(), 0)
            counter[label] += score + corpus_score

    top = counter.most_common(top_n)
    if not top:
        return ""

    max_count = top[0][1]
    min_count = top[-1][1]
    span = max_count - min_count or 1
    min_font, max_font = 10, 62

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
      <h3>Research &amp; Engineering Focus</h3>
      <p class="viz-note">Publication language with curated professional focus areas; size shows weighted prominence.</p>
      <svg viewBox="{min_x:.1f} {min_y:.1f} {vb_w:.1f} {vb_h:.1f}" class="viz-svg" role="img" aria-label="Word cloud combining publication keywords with curated research and engineering focus areas, sized by weighted prominence">
        {"".join(elements)}
      </svg>
      <details class="viz-table-toggle">
        <summary>Table view</summary>
        <table class="viz-table">
          <thead><tr><th>Keyword</th><th>Weighted score</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </details>
    </div>'''
