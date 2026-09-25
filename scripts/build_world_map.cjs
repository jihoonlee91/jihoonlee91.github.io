// One-off generator for assets/life/world-map.json (the Life page travel map).
// Not part of the site build: generate.py only reads the JSON output, so the
// site still builds with Python alone. Re-run only to change the projection
// or map resolution:
//
//   npm i world-atlas@2 topojson-client@3 d3-geo@3 i18n-iso-countries@7
//   node scripts/build_world_map.cjs
//
// Source: Natural Earth 1:110m admin-0 boundaries (public domain) via the
// world-atlas package. Countries are keyed by ISO 3166-1 alpha-2 code.
const fs = require('fs');
const path = require('path');
const { feature } = require('topojson-client');
const { geoNaturalEarth1, geoPath } = require('d3-geo');
const iso = require('i18n-iso-countries');

const topo = require('world-atlas/countries-110m.json');
const world = feature(topo, topo.objects.countries);
// Drop Antarctica: it takes a fifth of the height and is never a destination here.
world.features = world.features.filter((f) => f.properties.name !== 'Antarctica');

const width = 960;
const height = 470;
const projection = geoNaturalEarth1().fitSize([width, height], world);
const pathGen = geoPath(projection).digits(1);

// `c` (projected centroid) and `a` (projected area) let the page add a dot
// marker for visited countries too small to see at this scale (e.g. Cyprus).
const countries = world.features.map((f) => ({
  code: iso.numericToAlpha2(f.id) || null,
  name: f.properties.name,
  d: pathGen(f),
  c: pathGen.centroid(f).map((v) => Math.round(v * 10) / 10),
  a: Math.round(pathGen.area(f)),
}));

const out = path.join(__dirname, '..', 'assets', 'life', 'world-map.json');
fs.writeFileSync(out, JSON.stringify({ viewBox: `0 0 ${width} ${height}`, countries }));
console.log(`wrote ${out}: ${countries.length} countries, ${fs.statSync(out).size} bytes`);
