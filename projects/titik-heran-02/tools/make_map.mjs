// make_map.mjs — the "Titik Heran" map plate for #2: Australia, projected once at build time so the composition
// only carries static SVG paths.
//   node tools/make_map.mjs .   ->  assets/map/australia.json  { w, h, land, aus, grat, pts, pxPerDeg }
// Data: world-atlas 2.0.2 (Natural Earth 1:50m, public domain) via topojson-client + d3-geo.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { feature } from "topojson-client";
import { geoMercator, geoPath, geoGraticule } from "d3-geo";

const proj = process.argv[2] || ".";
const require = createRequire(import.meta.url);
const t50 = require("world-atlas/countries-50m.json");
const c50 = feature(t50, t50.objects.countries).features;

const W = 1080, H = 1920;
// Frame Australia by LONGITUDE: 110E to the left edge, 157E to the right, centred on lat -27 at y 960 — the whole
// continent reads in the wide shot, and the build zooms into the south-east (route, wind, Sydney) from there.
const projection = geoMercator().center([133.5, -27]).scale(1).translate([W / 2, 960]);
const [x0] = projection([110, -27]), [x1] = projection([157, -27]);
projection.scale(W / (x1 - x0)).clipExtent([[-80, -80], [W + 80, H + 80]]);
const p = geoPath(projection).digits(1);

const AUS = "036";
const aus = c50.find((f) => f.id === AUS);
const others = c50.filter((f) => f.id !== AUS);
const at = (lon, lat) => projection([lon, lat]).map((v) => +v.toFixed(1));
const out = {
  w: W, h: H,
  land: p({ type: "FeatureCollection", features: others }),
  aus: p(aus),
  grat: p(geoGraticule().step([5, 5])()),
  pxPerDeg: +(W / 47).toFixed(3),
  pts: {
    origin: at(147.2, -29.4),     // inland NSW, the breeding plains (a region, not a town)
    alps: at(148.26, -36.46),     // Snowy Mountains — Mt Kosciuszko
    sydney: at(151.21, -33.87),
    coastN: at(152.5, -31.0),     // coast north of Sydney: where the wind drops them
    coastS: at(150.2, -35.6),     // coast south of Sydney
  },
};
fs.mkdirSync(path.join(proj, "assets/map"), { recursive: true });
fs.writeFileSync(path.join(proj, "assets/map/australia.json"), JSON.stringify(out));
const bb = p.bounds(aus).map((q) => q.map((v) => Math.round(v)));
console.log("map", Object.fromEntries(Object.entries(out).map(([k, v]) => [k, typeof v === "string" ? v.length + " chars" : v])), "aus bounds", bb);
