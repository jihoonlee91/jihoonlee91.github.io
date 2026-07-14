# Design System

Static site, no build tooling beyond Python + plain CSS. Everything below is
implemented in `style.css` (tokens, layout, components) and `viz.py` (chart
SVG generation).

## Theme: dark default, light opt-in

- `:root` in `style.css` defines the **dark** palette (this is the default —
  no `data-theme` attribute needed).
- `:root[data-theme="light"]` overrides every token for light mode.
- `generate.py`'s `THEME_INIT_SCRIPT` runs in `<head>` on every page, before
  paint, reading `localStorage.theme` and setting `data-theme` on `<html>` —
  this avoids a flash of the wrong theme.
- `THEME_TOGGLE_SCRIPT` (loaded once near `</body>`) defines
  `window.toggleTheme()`, wired to the nav bar's toggle button
  (`render_nav()` in `generate.py`), which flips `data-theme` and persists it
  to `localStorage`.
- **When adding new UI, always use CSS custom properties** (`var(--fg)`,
  `var(--accent)`, etc.) — never a hardcoded hex — so it reacts to both
  themes automatically.

## Layout

- Content width: `max-width: 1180px` on `.container`, `.nav-inner`, and
  `footer.site-footer` — sized for a normal laptop/monitor viewport, not a
  narrow text column. Do not shrink this back down; an earlier 860px version
  was reported as too narrow.
- Single mobile breakpoint at `640px` — nav/hero/stats stack and center.
- Sticky top nav (`.site-nav`) with `Home / Publications / CV` links plus the
  theme toggle button.

## Typography

One font stack everywhere — `-apple-system, "Segoe UI", "Malgun Gothic",
Arial, sans-serif` — declared once on `body` and inherited by every element.
Do not introduce a second `font-family` declaration anywhere in the CSS; if a
new component seems to need a different typeface, that's a sign to reuse an
existing text class instead (`.paper-meta`, `.paper-venue`, `.tagline`, etc.
already cover the type scale in use: sizes range 0.8rem–2.1rem, weights
400/600/700 only).

## Color roles (non-chart)

| Token | Role |
|---|---|
| `--fg` / `--muted` | primary / secondary text |
| `--accent` | links, active nav, hover states |
| `--border` | hairline dividers |
| `--bg` / `--bg-soft` | page background / card-like surfaces |
| `--official` / `--official-bg` | "Official Link" badge (green) |
| `--preprint` / `--preprint-bg` | "Preprint PDF" badge (amber) |
| `--pending` | "Coming Soon" badge (gray) |
| `--tag-bg` | interest chips |

## Chart color palette (viz.py)

The Publications page renders two static SVG charts (publications-by-year
stacked bar, keyword-frequency bar) via `viz.py`, following the dataviz
skill's procedure: pick the form → assign color by job → **validate the
palette with the skill's script** → apply mark specs → provide a legend/table
fallback.

The 5-slot categorical palette (one slot per publication category) and the
single sequential blue hue are the skill's documented reference palette
(`references/palette.md`), re-validated against this site's own surfaces
(not the skill's defaults) before use:

```
node scripts/validate_palette.js "#2a78d6,#1baf7a,#eda100,#008300,#4a3aa7" --mode light --surface "#ffffff"
node scripts/validate_palette.js "#3987e5,#199e70,#c98500,#008300,#9085e9" --mode dark  --surface "#0d1117"
```

Both passed all four checks (lightness band, chroma floor, CVD separation,
contrast), with the contrast/CVD results at the floor band — which is why
every chart also ships a legend, direct value labels on segments/bars, and a
`<details>` table-view fallback rather than relying on color alone.

**If you ever change `--bg` (the dark surface) or the light surface, re-run
the validator against the new surface before reusing this palette** — the
contrast checks are surface-relative.

## Badges (Official Link / Preprint PDF / Coming Soon)

Every publication, on both the Publications list and its own paper page,
shows a small badge row from `link_badges()` in `generate.py`:

- **Official Link** (green) — `official_link` is set (a DOI or publisher/
  DBpia/library URL). Label appends "(DOI)" when a `doi` field is present.
- **Preprint PDF** (amber) — a file exists at `papers/pdfs/<slug>.pdf`.
- **Coming Soon** (gray) — neither of the above.
- **BibTeX** (neutral) — always shown, links to `bibtex/<slug>.bib`.

These three are deliberately different colors so a visitor can tell at a
glance whether they're about to land on the publisher's page or a
self-hosted file — do not merge them into one generic "link" style.
