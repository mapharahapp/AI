// make_map.mjs — the "Titik Heran" map plate: North Atlantic, Ireland + USA as their own paths,
// projected once at build time so the composition only carries static SVG paths.
//   node tools/make_map.mjs .   ->  assets/map/atlantic.json  { w, h, land, ireland, usa, grat, pts }
// Data: world-atlas 2.0.2 (Natural Earth 1:50m, public domain) via topojson-client + d3-geo.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { feature } from "topojson-client";
import { geoMercator, geoPath, geoGraticule10 } from "d3-geo";

const proj = process.argv[2] || ".";
const require = createRequire(import.meta.url);
const t50 = require("world-atlas/countries-50m.json"), t110 = require("world-atlas/countries-110m.json");
const c50 = feature(t50, t50.objects.countries).features, c110 = feature(t110, t110.objects.countries).features;

const W = 1080, H = 1920;
// Frame the North Atlantic by LONGITUDE: the US east coast (-84) to the left edge, Europe's edge (+4) to the
// right, centred on lat 46, so the two dots the story needs are ~650 px apart across a 1080 frame.
const projection = geoMercator().center([-40, 46]).scale(1).translate([W / 2, 900]);
const [x0] = projection([-84, 46]), [x1] = projection([4, 46]);
projection.scale(1000 / (x1 - x0)).clipExtent([[-60, -60], [W + 60, H + 60]]);
const p = geoPath(projection).digits(1);

const IRL = "372", USA = "840", GBR = "826";
// 1:50m where the camera zooms in (Ireland, Britain), 1:110m everywhere else — keeps the page light.
const fine = new Set([IRL, GBR]);
const visible = [...c110.filter((f) => !fine.has(f.id) && f.id !== USA), ...c50.filter((f) => f.id === GBR)];
const countries = c50;
const out = {
  w: W, h: H,
  land: p({ type: "FeatureCollection", features: visible }),
  ireland: p(countries.find((f) => f.id === IRL)),
  usa: p(c110.find((f) => f.id === USA)),
  grat: p(geoGraticule10()),
  pts: {
    ireland: projection([-8.0, 53.35]).map((v) => +v.toFixed(1)),   // island centroid, not a town
    america: projection([-74.0, 40.7]).map((v) => +v.toFixed(1)),   // US east coast, unlabelled city
  },
};
fs.writeFileSync(path.join(proj, "assets/map/atlantic.json"), JSON.stringify(out));
console.log("map", Object.fromEntries(Object.entries(out).map(([k, v]) => [k, typeof v === "string" ? v.length + " chars" : v])));
