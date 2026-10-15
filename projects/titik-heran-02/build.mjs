// build.mjs — Titik Heran #2, "ngengat bogong". The generator is the source of truth; index.html is its output.
//
//   node build.mjs .            final build — refuses to run while any b-roll slot has no Pixabay clip
//   DRAFT=1 node build.mjs .    preview build — empty slots render as labelled placeholders
//
// PLAN -> cue table (chained to voice-over WORDS) -> shots + beats -> one HTML page with a paused GSAP timeline.
// No timing below is a stopwatch number: every cue is "the next occurrence of this word after the previous cue",
// resolved against assets/vo/audio_meta.json (ElevenLabs "Akram", single take, pauses capped).
// The drawn layer (moth swarms, wind, map camera + pins + labels) lives in assets/swarm.js and is a pure function of
// time fed by the seeded tables this file writes into window.SWP.
import fs from "node:fs";
import path from "node:path";

// ---------------------------------------------------------------- PLAN -------------------------------
// Naskah & storyboard: "Titik Heran: Naskah & Storyboard Video #2". `from`/`to` are WORDS in the narration.
export const PLAN = [
  { beat: "1 hook",     from: "start",      to: "Padahal",    hero: "footage:sydney",   frame: "absent", zones: "night harbour + drawn swarm / type 250-520 / subs 1230" },
  { beat: "1b hook",    from: "Padahal",    to: "Namanya",    hero: "footage:mothFace", frame: "absent", zones: "moth on black + stars / type 250-700 / subs 1230" },
  { beat: "2 latar",    from: "Namanya",    to: "gua",        hero: "map:australia",    frame: "absent", zones: "map full / type 250-560 / subs 1230" },
  { beat: "3 latar",    from: "gua",        to: "Masalahnya", hero: "footage:sky",      frame: "absent", zones: "cave, then Milky Way + star-moth / type 250-580 / subs 1230" },
  { beat: "4 masalah",  from: "Masalahnya", to: "Tapi",       hero: "footage:city",     frame: "absent", zones: "map + wind, city lights, window / type 250-400 / subs 1230" },
  { beat: "5 resolusi", from: "Tapi",       to: "Kirim",      hero: "graph:population", frame: "absent", zones: "graph, screen, bulb, Milky Way / type 250-480 / subs 1230" },
  { beat: "6 cta",      from: "Kirim",      to: "end",        hero: "map:sydney",       frame: "absent", zones: "map close on Sydney / type 240-560 / subs 1230" },
];

// Pixabay b-roll slots. `need` is what the frame must show; `q` the Pixabay searches that source it.
export const SLOTS = {
  sydney:   { need: "Sydney Opera House at night, dark sky above", q: ["sydney opera house night"] },
  mothFace: { need: "a brown moth, close, on black", q: ["moth", "bogong moth"] },
  cave:     { need: "dark rock cave or crevice", q: ["cave"] },
  sky:      { need: "Milky Way, vertical", q: ["milky way"] },
  city:     { need: "Sydney skyline lights at night", q: ["sydney night"] },
  window:   { need: "a moth on a house window", q: ["moths window"] },
  screen:   { need: "a moth on a window fly screen", q: ["moths window"] },
  bulb:     { need: "a light bulb switching off", q: ["light switch", "light bulb"] },
  stars:    { need: "Milky Way over mountains", q: ["milky way mountains"] },
};

const proj = process.argv[2] || ".";
const DRAFT = process.env.DRAFT === "1" || process.argv.includes("--draft");
const read = (p) => JSON.parse(fs.readFileSync(path.join(proj, p), "utf8"));
const VO = read("assets/vo/audio_meta.json").scenes[0];
const MAP = read("assets/map/australia.json");
const FOOT = fs.existsSync(path.join(proj, "assets/footage/manifest.json")) ? read("assets/footage/manifest.json") : {};

const missing = Object.keys(SLOTS).filter((s) => !FOOT[s]);
if (missing.length && !DRAFT) throw new Error(`no Pixabay clip yet for: ${missing.join(", ")} — source them (assets/footage/manifest.json) or build with DRAFT=1`);

const W = 1080, H = 1920;
const BG = "#050608", INK = "#F7F2E8", MUTED = "#B9B2A6", ACCENT = "#FF9A1F", RED = "#FF2D2D";
const fx = (n) => +(+n).toFixed(3);
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
const VO_START = 0.35;                       // a beat of air before the first word

/** TA = Time After. The next occurrence of `word` AFTER `after`. Chain these; never count occurrences. */
function TA(word, after) {
  for (const w of VO.words) {
    const t = fx(VO_START + w.start);
    if (t > after + 0.01 && norm(w.text).startsWith(norm(word))) return t;
  }
  throw new Error(`cue "${word}" after ${after}s not found — the script changed; re-cue this beat`);
}

// ---------------------------------------------------------------- cue table (chained) -----------------
const c = {};
c.jutaan = TA("Jutaan", -1);
c.menyerbu = TA("menyerbu", c.jutaan);
c.sydney1 = TA("Sydney", c.menyerbu);
c.padahal = TA("Padahal", c.sydney1);
c.mereka1 = TA("mereka", c.padahal);
c.bisa1 = TA("bisa", c.mereka1);
c.bintang1 = TA("bintang", c.bisa1);
c.namanya = TA("Namanya", c.bintang1);
c.ngengat2 = TA("ngengat", c.namanya);
c.bogong = TA("bogong", c.ngengat2);
c.tiap = TA("Tiap", c.bogong);
c.terbang = TA("terbang", c.tiap);
c.sampai = TA("sampai", c.terbang);
c.seribu = TA("1.000", c.sampai);
c.km = TA("km", c.seribu);
c.gua = TA("gua", c.km);
c.dipandu = TA("dipandu", c.gua);
c.bintang2 = TA("bintang", c.dipandu);
c.bima = TA("Bima", c.bintang2);
c.masalah = TA("Masalahnya", c.bima);
c.angin = TA("angin", c.masalah);
c.pesisir = TA("pesisir", c.angin);
c.dan2 = TA("dan", c.pesisir);
c.lampu1 = TA("lampu", c.dan2);
c.akhirnya = TA("Akhirnya", c.lampu1);
c.nyasar = TA("nyasar", c.akhirnya);
c.tapi = TA("Tapi", c.nyasar);
c.kabar = TA("kabar", c.tapi);
c.ngengat3 = TA("Ngengat", c.kabar);
c.nyaris = TA("nyaris", c.ngengat3);
c.habis = TA("habis", c.nyaris);
c.sedang2 = TA("sedang", c.habis);
c.pulih = TA("pulih", c.sedang2);
c.jadi = TA("Jadi", c.pulih);
c.jangan = TA("jangan", c.jadi);
c.matikan = TA("Matikan", c.jangan);
c.lampu2 = TA("lampu", c.matikan);
c.biar = TA("biar", c.lampu2);
c.membaca2 = TA("membaca", c.biar);
c.kirim = TA("Kirim", c.membaca2);
c.sydney2 = TA("Sydney", c.kirim);
c.sebelum = TA("sebelum", c.sydney2);
const VO_END = fx(VO_START + VO.duration);
c.endcut = fx(Math.min(VO_END, VO_START + VO.words.at(-1).end) + 0.06);   // hard cut back to the opening frame
const END_HOLD = 1.0;
const TOTAL = fx(c.endcut + END_HOLD);
if (TOTAL > 179) throw new Error(`total ${TOTAL}s exceeds the 2:59 ceiling — see hyperframe-pro-voice`);

const tl = [], body = [];
const X = 0.42;                              // exits start this long before the next cue

// ---------------------------------------------------------------- motion helpers ----------------------
const enter = (sel, at, { d = 0.32, y = 30 } = {}) =>
  tl.push(`tl.fromTo("${sel}",{autoAlpha:0,y:${y}},{autoAlpha:1,y:0,duration:${d},ease:"power3.out"},${fx(at)});`);
const slam = (sel, at, { d = 0.28, from = 1.35 } = {}) =>
  tl.push(`tl.fromTo("${sel}",{autoAlpha:0,scale:${from}},{autoAlpha:1,scale:1,duration:${d},ease:"power4.out"},${fx(at)});`);
const exit = (sel, at, { d = 0.22, y = -24 } = {}) => {
  tl.push(`tl.to("${sel}",{autoAlpha:0,y:${y},duration:${d},ease:"power2.in"},${fx(at)});`);
  tl.push(`tl.set("${sel}",{autoAlpha:0},${fx(at + d)});`);   // hard kill: survives non-linear seeking
};
// a ring that pings out from a dot. set-then-to: a fromTo would paint its FROM state on every earlier frame
const ping = (sel, at, to = 3.2) => {
  tl.push(`tl.set("${sel}",{scale:0.4,autoAlpha:0.9},${fx(at)});`);
  tl.push(`tl.to("${sel}",{scale:${to},autoAlpha:0,duration:0.7,ease:"power2.out"},${fx(at + 0.01)});`);
};
const pop = (sel, at, { d = 0.3, from = 0.4 } = {}) =>
  tl.push(`tl.fromTo("${sel}",{autoAlpha:0,scale:${from}},{autoAlpha:1,scale:1,duration:${d},ease:"back.out(2.6)"},${fx(at)});`);
const cut = (sel, at) => tl.push(`tl.set("${sel}",{autoAlpha:0},${fx(at)});`);
const show = (sel, at) => tl.push(`tl.set("${sel}",{autoAlpha:1},${fx(at)});`);
const fadeIn = (sel, at, d = 0.3, first = false) =>
  tl.push(`tl.fromTo("${sel}",{autoAlpha:0},{autoAlpha:1,duration:${d},ease:"power2.out"${first ? "" : ",immediateRender:false"}},${fx(at)});`);
const fadeOut = (sel, at, d = 0.3) => {
  tl.push(`tl.to("${sel}",{autoAlpha:0,duration:${d},ease:"power2.in"},${fx(at)});`);
  tl.push(`tl.set("${sel}",{autoAlpha:0},${fx(at + d + 0.02)});`);
};

// ---------------------------------------------------------------- shots (footage) ---------------------
// One <video class="clip footage"> per window. data-start/data-duration own its visibility (never GSAP it);
// the Ken Burns and grade tweens live on the wrapper .shot around it.
let nShot = 0;
function shot(slot, from, to, { at = null, kb = [1.0, 1.08], dx = 0, dy = 0, grade = "", z = 1, origin = "50% 45%", hold = false } = {}) {
  const id = `sh${++nShot}`, dur = fx(to - from), f = FOOT[slot];
  const mediaStart = fx(at ?? (f?.at ?? 0));
  const inner = f
    ? `<video id="v${nShot}" class="clip footage" muted playsinline preload="auto" src="${f.file}" data-start="${fx(from)}" data-duration="${dur}" data-media-start="${mediaStart}"></video>`
    : `<div id="v${nShot}" class="ph footage"><b>B-ROLL PIXABAY</b><span>${esc(slot)} — ${esc(SLOTS[slot].need)}</span></div>`;
  if (f && f.dur && mediaStart + dur > f.dur + 0.01) throw new Error(`${slot}: trim ${mediaStart}+${dur}s runs past the clip (${f.dur}s) — the plate would go black mid-beat`);
  body.push(`<div id="${id}" class="shot ${grade}" style="z-index:${z};transform-origin:${origin}">${inner}</div>`);
  if (!f) { show(`#v${nShot}`, from); cut(`#v${nShot}`, to); }          // placeholders are plain divs: GSAP owns them
  if (!hold) tl.push(`tl.fromTo("#${id}",{scale:${kb[0]},x:0,y:${dy}},{scale:${kb[1]},x:${dx},y:${dy},duration:${dur},ease:"none"},${fx(from)});`);
  return id;
}

// ---------------------------------------------------------------- seeded tables for swarm.js -----------
let seed = 0x6d2b79f5;
const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => +(a + (b - a) * rnd()).toFixed(3);
const sgn = () => (rnd() < 0.5 ? -1 : 1);
const flap = () => ({ fq: R(5, 8.5), ph: R(0, 6.283) });
const SWP = { W, H, scenes: [], pins: ["m-oK", "m-aK", "m-sK"] };

// the hook swarm: far specks, mid moths, and a few big blurred fly-bys close to the lens (backlit, dark)
SWP.city = [];
for (let i = 0; i < 110; i++) SWP.city.push({ x0: R(-160, W + 160), y0: R(100, 1120), vx: R(25, 80), vy: R(-6, 8), ax: R(6, 22), wx: R(1.8, 4.5), px: R(0, 6.283), ay: R(6, 24), wy: R(2, 5), py: R(0, 6.283), size: R(4.5, 8), al: R(0.6, 0.9), blur: 0, ...flap() });
for (let i = 0; i < 46; i++) SWP.city.push({ x0: R(-160, W + 160), y0: R(60, 1500), vx: R(60, 160), vy: R(-14, 16), ax: R(15, 45), wx: R(1.5, 4), px: R(0, 6.283), ay: R(15, 45), wy: R(1.5, 4.5), py: R(0, 6.283), size: R(10, 18), al: R(0.85, 1), blur: 0.4, ...flap() });
for (let i = 0; i < 7; i++) SWP.city.push({ x0: R(-160, W + 160), y0: R(-40, 1960), vx: R(280, 520), vy: R(-80, 80), ax: R(20, 60), wx: R(1, 2.5), px: R(0, 6.283), ay: R(30, 90), wy: R(1, 2.5), py: R(0, 6.283), size: R(40, 80), al: R(0.6, 0.85), blur: R(1.5, 3.5), f: "#3a2d20", fq: R(4, 6), ph: R(0, 6.283) });
SWP.cityOrb = [];
for (let i = 0; i < 80; i++) SWP.cityOrb.push({ r: fx(40 + 300 * rnd() ** 1.3), e: R(0.3, 0.6), tilt: R(-0.35, 0.25), w: R(1.6, 4.2) * sgn(), p: R(0, 6.283), j: R(5, 30), jw: R(2, 6), size: R(4, 9.5), al: R(0.65, 1), ...flap() });
// stars round the studio moth (the plate is black above y 450 and below y 1350)
SWP.stars = [];
for (let i = 0; i < 120; i++) { const top = i < 56; SWP.stars.push({ x: R(20, W - 20), y: top ? R(100, 445) : R(1365, 1900), r: R(1, 3), a: R(0.45, 1), w: R(1.5, 5), p: R(0, 6.283) }); }
// the route, in map space: inland NSW -> Snowy Mountains, bowed slightly west
const [ox, oy] = MAP.pts.origin, [ax, ay] = MAP.pts.alps, [sx, sy] = MAP.pts.sydney;
{
  const mx = (ox + ax) / 2, my = (oy + ay) / 2, dxr = ax - ox, dyr = ay - oy, n = Math.hypot(dxr, dyr);
  SWP.route = { o: [ox, oy], q: [fx(mx - (dyr / n) * 22), fx(my + (dxr / n) * 22)], a: [ax, ay] };
}
const RQ = SWP.route.q;
SWP.routeM = [];
for (let i = 0; i < 24; i++) SWP.routeM.push({ d: R(i * 0.056, i * 0.056 + 0.03), j: R(3, 9), w: R(3, 7), p: R(0, 6.283), k: R(0.75, 1.25), al: R(0.75, 1), cr: R(1.5, 6), cw: R(1.5, 3) * sgn(), ...flap() });
// the wind act: a stream on the route, then everyone ends up on the coast round Sydney
const [cnx, cny] = MAP.pts.coastN, [csx, csy] = MAP.pts.coastS;
SWP.windM = [];
for (let i = 0; i < 34; i++) {
  const toSyd = rnd() < 0.4, u = rnd();
  const tx = toSyd ? sx + R(-5, 5) : cnx + (csx - cnx) * u - R(1, 7), ty = toSyd ? sy + R(-5, 5) : cny + (csy - cny) * u + R(-3, 3);
  SWP.windM.push({ o: R(0, 1), tx: fx(tx), ty: fx(ty), r: R(2, 6), w: R(2, 5), p: R(0, 6.283), k: R(0.75, 1.2), al: R(0.75, 1), lag: R(1.0, 1.6), ...flap() });
}
SWP.streaks = [];
for (let i = 0; i < 26; i++) SWP.streaks.push({ x0: R(0, W + 700), y0: R(150, 1350), v: R(1100, 1800), len: R(140, 320), wd: R(2, 4), al: R(0.25, 0.5) });
// city lights: moths circling a light, a few big ones swinging close to the lens
SWP.orbit = [];
for (let i = 0; i < 40; i++) SWP.orbit.push({ r: fx(30 + 250 * rnd() ** 1.5), e: R(0.35, 0.85), tilt: R(-0.6, 0.6), w: R(1.8, 4.5) * sgn(), p: R(0, 6.283), j: R(5, 25), jw: R(2, 6), size: R(5, 13), depth: R(0.5, 1), al: R(0.7, 1), blur: 0, ...flap() });
for (let i = 0; i < 4; i++) SWP.orbit.push({ r: R(200, 380), e: R(0.4, 0.7), tilt: R(-0.5, 0.5), w: R(1.2, 2.2) * sgn(), p: R(0, 6.283), j: R(10, 30), jw: R(1, 3), size: R(26, 44), depth: 1, al: 0.7, blur: R(2, 4), ...flap() });
// lights out: silhouettes climbing into the Milky Way
SWP.ascend = [];
for (let i = 0; i < 34; i++) SWP.ascend.push({ x0: R(40, 1040), y0: R(0, H + 300), vy: R(110, 240), vx: R(-40, 5), ax: R(8, 30), wx: R(2, 5), px: R(0, 6.283), size: R(15, 36), al: R(0.75, 0.95), ...flap() });
// the cave: a few moths flying past the camera into the dark
SWP.cave = [];
for (let i = 0; i < 16; i++) { const th = R(0, 6.283), rr = R(520, 900); SWP.cave.push({ tau: R(0, 2), D: R(1.1, 1.7), sx: fx(rr * Math.cos(th)), sy: fx(rr * Math.sin(th)), size: R(30, 60), blur: R(1, 4), al: R(0.6, 0.85), ...flap() }); }
// CTA: moths arriving on Sydney from inland (the west)
SWP.conv = [];
for (let i = 0; i < 34; i++) SWP.conv.push({ th: R(2.3, 4.2), d: R(680, 1000), del: R(-1.4, 2.6), D: R(1.3, 2.2), re: R(16, 80), spin: R(-0.6, 0.6), w: R(1.5, 3.5) * sgn(), size: R(8, 14), al: R(0.75, 1), ...flap() });

// ---------------------------------------------------------------- map camera (evaluated by swarm.js) ----
// transform-origin 0 0: a camera is {s, x, y} with screen = map * s + (x, y). cam() puts map point (mx,my) at (px,py).
const cam = (s, mx, my, px, py) => ({ s, x: fx(px - mx * s), y: fx(py - my * s) });
const V0 = cam(1.0, 540, 960, 540, 1010), V0b = cam(1.1, 540, 960, 540, 1010);
const V1 = cam(2.6, 880, 1120, 540, 930), V1z = cam(2.72, 880, 1120, 540, 930);
const V2 = cam(2.5, 900, 1120, 540, 930), V2z = cam(2.74, 900, 1120, 540, 930);
const V3 = cam(5.0, sx, sy, 540, 960), V3z = cam(5.75, sx, sy, 540, 960);
SWP.cam = [
  { t0: fx(c.namanya - 0.2), t1: fx(c.tiap - 0.1), a: V0, b: V0b, ease: "none" },
  { t0: fx(c.tiap - 0.1), t1: fx(c.terbang - 0.05), a: V0b, b: V1, ease: "power2.inOut" },
  { t0: fx(c.terbang - 0.05), t1: fx(c.gua + 0.2), a: V1, b: V1z, ease: "none" },
  { t0: fx(c.masalah - 0.25), t1: fx(c.dan2 + 0.1), a: V2, b: V2z, ease: "none" },
  { t0: fx(c.kirim - 0.25), t1: fx(c.sydney2 + 0.3), a: V2, b: V3, ease: "power2.inOut" },
  { t0: fx(c.sydney2 + 0.3), t1: c.endcut, a: V3, b: V3z, ease: "none" },
];
SWP.labels = [
  { txt: "PEDALAMAN NSW", m: [ox, oy], d: [-34, 0], al: "right", c: INK, t0: fx(c.bogong + 0.25), t1: fx(c.gua + 0.3) },
  { txt: "SNOWY MOUNTAINS", m: [ax, ay], d: [34, 0], al: "left", c: INK, t0: fx(c.km + 0.3), t1: fx(c.gua + 0.3) },
  { txt: "PEDALAMAN NSW", m: [ox, oy], d: [-34, 0], al: "right", c: INK, t0: fx(c.masalah - 0.25), t1: fx(c.dan2 + 0.2) },
  { txt: "SNOWY MOUNTAINS", m: [ax, ay], d: [34, 0], al: "left", c: INK, t0: fx(c.masalah - 0.25), t1: fx(c.dan2 + 0.2) },
  { txt: "SYDNEY", m: [sx, sy], d: [34, 0], al: "left", c: INK, t0: fx(c.pesisir + 0.1), t1: fx(c.dan2 + 0.2) },
  { txt: "SYDNEY", m: [sx, sy], d: [40, 0], al: "left", c: INK, t0: fx(c.sydney2 + 0.05), t1: TOTAL },
];

// ---------------------------------------------------------------- B1 hook -----------------------------
// Frame 0 is Sydney at night, already moving (push-in), the swarm already flying.
const HOOK_AT = FOOT.sydney?.at ?? 1.2;      // media time of the opening frame; the end card returns to it
const LOOP_SCALE = 1.08, HOOK_SCALE = 1.2, HOOK_DY = -90;
const hook = shot("sydney", 0, c.padahal, { at: HOOK_AT, z: 2, hold: true, origin: "42% 56%" });
tl.push(`tl.fromTo("#${hook}",{scale:${LOOP_SCALE},y:${HOOK_DY}},{scale:${HOOK_SCALE},y:${HOOK_DY},duration:${c.padahal},ease:"none"},0);`);
SWP.scenes.push({ m: "city", t0: 0, t1: c.padahal, s0: 0, fill: "#ecd5a8", oc: [330, 905] });
slam("#t1", 0.1);
slam("#t1b", fx(c.menyerbu - 0.04), { from: 1.5, d: 0.24 });
cut("#t1, #t1b", c.padahal);

// ---------------------------------------------------------------- B1b: "Padahal... bisa baca bintang" ---
shot("mothFace", c.padahal, fx(c.namanya + 0.2), { kb: [1.0, 1.12], z: 3, origin: "50% 41%" });
SWP.scenes.push({ m: "twinkle", t0: c.padahal, t1: fx(c.namanya + 0.15), fo: 0.35, flare: c.bintang1 });
slam("#t2", c.padahal, { from: 1.25 });
enter("#t2b", fx(c.bisa1 - 0.04), { y: 22 });
slam("#t2c", fx(c.bintang1 - 0.04), { from: 1.6, d: 0.26 });
exit("#t2, #t2b, #t2c", fx(c.namanya - 0.3));

// ---------------------------------------------------------------- B2 latar: the map -------------------
// Dark Australia; the red dot drops on inland NSW ON "bogong"; the camera dives; the route runs to the mountains.
fadeIn("#map", fx(c.namanya - 0.2), 0.35, true);
tl.push(`tl.fromTo("#m-odot",{y:-700,autoAlpha:0},{y:0,autoAlpha:1,duration:0.42,ease:"power3.in"},${fx(c.bogong - 0.42)});`);
ping("#m-oring", fx(c.bogong + 0.02));
ping("#m-oring2", fx(c.terbang - 0.05), 2.6);
slam("#t3", c.ngengat2);
exit("#t3", fx(c.tiap - 0.3));
// the route: dashed line revealed by a mask, from the dot to the mountains
const RL = (() => { let L = 0, [px, py] = [ox, oy]; for (let i = 1; i <= 200; i++) { const u = i / 200, v = 1 - u; const x = v * v * ox + 2 * v * u * RQ[0] + u * u * ax, y = v * v * oy + 2 * v * u * RQ[1] + u * u * ay; L += Math.hypot(x - px, y - py); px = x; py = y; } return Math.ceil(L); })();
const routeT0 = c.terbang, routeT1 = fx(c.km + 0.35);
SWP.scenes.push({ m: "route", t0: fx(routeT0 - 0.05), t1: fx(c.gua + 0.2), s0: -0.05, size: 7, T: fx(routeT1 - routeT0), fill: "#f2dfb8" });
tl.push(`tl.fromTo("#m-route",{autoAlpha:0},{autoAlpha:1,duration:0.2,ease:"none"},${fx(routeT0)});`);
tl.push(`tl.fromTo("#m-routeMask",{strokeDashoffset:${RL}},{strokeDashoffset:0,duration:${fx(routeT1 - routeT0)},ease:"none"},${fx(routeT0)});`);
pop("#m-adot", fx(routeT1 - 0.05));
ping("#m-aring", fx(routeT1 - 0.04));
enter("#t4", c.sampai, { y: 20 });
slam("#t4b", fx(c.seribu - 0.04), { from: 1.6, d: 0.26 });
exit("#t4, #t4b", fx(c.gua - 0.3));
fadeOut("#map", fx(c.gua - 0.2), 0.3);

// ---------------------------------------------------------------- B3 latar: cave, then the sky ---------
shot("cave", fx(c.gua - 0.2), c.dipandu, { kb: [1.05, 1.18], z: 5, origin: "62% 48%" });
SWP.scenes.push({ m: "cave", t0: fx(c.gua - 0.15), t1: c.dipandu, fi: 0.3, vx: 700, vy: 860, fill: "#cdb48c" });
const sky = shot("sky", c.dipandu, fx(c.masalah + 0.15), { kb: [1.22, 1.3], z: 6, origin: "50% 18%" });
tl.push(`tl.fromTo("#${sky}",{filter:"brightness(1) saturate(1)"},{filter:"brightness(1.32) saturate(1.15)",duration:0.7,ease:"power2.out"},${fx(c.bima)});`);
// a moth drawn in stars: the stars pop on "dipandu ... bintang", the lines join them on "bintang ... Bima Sakti"
const CST = [[540, 760], [540, 830], [540, 1090], [615, 820], [800, 780], [772, 945], [640, 965], [702, 1090], [592, 1120],
  [465, 820], [280, 780], [308, 945], [440, 965], [378, 1090], [488, 1120], [612, 690], [468, 690]];
const CLN = [[15, 0], [0, 16], [0, 1], [1, 2], [1, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 2], [1, 9], [9, 10], [10, 11], [11, 12], [12, 13], [13, 14], [14, 2]];
const cPath = CLN.map(([a, b]) => `M${CST[a][0]} ${CST[a][1]} L${CST[b][0]} ${CST[b][1]}`).join(" ");
const CL = Math.ceil(CLN.reduce((s, [a, b]) => s + Math.hypot(CST[b][0] - CST[a][0], CST[b][1] - CST[a][1]), 0));
fadeIn("#cons", fx(c.dipandu), 0.2, true);
CST.forEach((_, i) => pop(`#c-s${i}`, fx(c.dipandu + 0.05 + i * ((c.bintang2 + 0.35 - c.dipandu) / CST.length)), { d: 0.25, from: 0 }));
tl.push(`tl.fromTo("#c-mask",{strokeDashoffset:${CL}},{strokeDashoffset:0,duration:${fx(c.bima + 0.3 - c.bintang2)},ease:"power1.inOut"},${fx(c.bintang2)});`);
tl.push(`tl.fromTo("#c-glow",{opacity:0.25},{opacity:0.85,duration:0.6,ease:"power2.out"},${fx(c.bima)});`);
fadeOut("#cons", fx(c.masalah - 0.25), 0.3);
slam("#t5", c.dipandu, { from: 1.3 });
enter("#t5b", fx(c.bima - 0.04), { y: 20 });
enter("#t5n", fx(c.bima + 0.3), { y: 12 });
exit("#t5, #t5b, #t5n", fx(c.masalah - 0.3));

// ---------------------------------------------------------------- B4 masalah ---------------------------
// The map again: the stream on its route, then a north-west wind shoves it east to the coast; Sydney pings.
fadeIn("#map", fx(c.masalah - 0.2), 0.3);
SWP.scenes.push({ m: "wind", t0: fx(c.masalah - 0.25), t1: fx(c.dan2 + 0.15), s0: 3, size: 6.6, T: 2.2, fill: "#f2dfb8",
  w0: fx(c.angin - 0.25), w1: fx(c.dan2 + 0.1), p0: fx(c.angin + 0.1), p1: fx(c.pesisir + 0.25), slope: 0.3 });
pop("#m-sw", fx(c.pesisir - 0.05), { from: 0 });
ping("#m-sring", fx(c.pesisir));
slam("#t6a", c.masalah, { from: 1.25 });
cut("#t6a", fx(c.angin - 0.02));
slam("#t6", fx(c.angin - 0.02));
exit("#t6", fx(c.dan2 - 0.3));
fadeOut("#map", fx(c.dan2 - 0.25), 0.3);
// city lights: moths circling a tower's glow
shot("city", fx(c.dan2 - 0.25), c.akhirnya, { kb: [1.0, 1.1], z: 7, origin: "52% 30%" });
SWP.scenes.push({ m: "orbit", t0: fx(c.dan2 - 0.2), t1: c.akhirnya, fi: 0.3, cx: 560, cy: 600, glow: 280, fill: "#ffe3b4" });
slam("#t7", c.lampu1);
exit("#t7", fx(c.akhirnya - 0.25));
// lost: a moth on somebody's window
shot("window", c.akhirnya, fx(c.tapi + 0.25), { kb: [1.0, 1.14], z: 8, origin: "50% 46%" });
slam("#t8", c.nyasar);
exit("#t8", fx(c.tapi - 0.25));

// ---------------------------------------------------------------- B5 resolusi --------------------------
// The population line: a plateau, the 2017 crash, the recovery to this year's best in almost a decade.
const GSEG = [[110, 720], [190, 712, 250, 722, 300, 752], [345, 780, 352, 1095, 395, 1100], [450, 1106, 540, 1098, 610, 1088], [720, 1072, 800, 960, 860, 860], [900, 800, 935, 778, 970, 770]];
const gPath = `M${GSEG[0][0]} ${GSEG[0][1]} ` + GSEG.slice(1).map((s) => `C${s[0]} ${s[1]} ${s[2]} ${s[3]} ${s[4]} ${s[5]}`).join(" ");
const gLens = []; {
  let [px, py] = GSEG[0];
  for (const s of GSEG.slice(1)) {
    let L = 0, [qx, qy] = [px, py];
    for (let i = 1; i <= 100; i++) { const u = i / 100, v = 1 - u; const x = v ** 3 * px + 3 * v * v * u * s[0] + 3 * v * u * u * s[2] + u ** 3 * s[4], y = v ** 3 * py + 3 * v * v * u * s[1] + 3 * v * u * u * s[3] + u ** 3 * s[5]; L += Math.hypot(x - qx, y - qy); qx = x; qy = y; }
    gLens.push(L); [px, py] = [s[4], s[5]];
  }
}
const cum = (n) => fx(gLens.slice(0, n).reduce((a, b) => a + b, 0));
const GL = Math.ceil(cum(gLens.length));
SWP.graph = { L: GL };
fadeIn("#graph", fx(c.tapi - 0.1), 0.3, true);
tl.push(`tl.fromTo("#graph",{scale:1},{scale:1.06,duration:${fx(c.jangan + 0.1 - (c.tapi - 0.1))},ease:"none"},${fx(c.tapi - 0.1)});`);
tl.push(`tl.to(GR,{len:${cum(1)},duration:${fx(c.nyaris - c.tapi - 0.3)},ease:"none"},${fx(c.tapi + 0.3)});`);
tl.push(`tl.to(GR,{len:${cum(2)},duration:${fx(c.habis + 0.25 - c.nyaris)},ease:"power2.in"},${fx(c.nyaris)});`);
tl.push(`tl.to(GR,{len:${cum(3)},duration:${fx(c.sedang2 - 0.2 - (c.habis + 0.25))},ease:"none"},${fx(c.habis + 0.25)});`);
tl.push(`tl.to(GR,{len:${GL},duration:${fx(c.pulih + 0.45 - (c.sedang2 - 0.2))},ease:"power2.out"},${fx(c.sedang2 - 0.2)});`);
pop("#g-low", fx(c.habis + 0.1), { from: 0.5 });
pop("#g-y17", fx(c.habis + 0.2), { from: 0.6 });
ping("#g-lring", fx(c.habis + 0.25), 2.8);
pop("#g-y26", fx(c.pulih + 0.3), { from: 0.6 });
ping("#g-ering", fx(c.pulih + 0.45), 2.8);
slam("#t9a", c.tapi, { from: 1.25 });
cut("#t9a", fx(c.kabar - 0.02));
slam("#t9", fx(c.kabar - 0.02));
cut("#t9", fx(c.sedang2 - 0.06));
slam("#t9b", fx(c.sedang2 - 0.06), { from: 1.25 });
exit("#t9b", fx(c.jangan - 0.32));
fadeOut("#graph", fx(c.jangan - 0.2), 0.3);
// don't spray; switch the light off; the stars come back
shot("screen", fx(c.jangan - 0.2), c.matikan, { kb: [1.05, 1.16], z: 9, origin: "50% 44%" });
slam("#t10", fx(c.jangan - 0.04));
cut("#t10", fx(c.matikan - 0.02));
const OFF_T = fx(c.lampu2 + 0.16);           // the bulb clip switches off at clip time 1.23: land it just after "lampu"
const BULB_OFF = 1.23;
shot("bulb", c.matikan, fx(c.biar + 0.1), { at: fx(BULB_OFF - (OFF_T - c.matikan)), kb: [1.0, 1.06], z: 10, origin: "50% 38%" });
tl.push(`tl.fromTo("#dark",{autoAlpha:0},{autoAlpha:0.88,duration:0.3,ease:"power2.out"},${fx(OFF_T + 0.04)});`);
cut("#dark", fx(c.biar + 0.6));
slam("#t11", fx(c.matikan - 0.02));
exit("#t11", fx(c.biar + 0.35));
const stars = shot("stars", fx(c.biar - 0.12), fx(c.kirim + 0.15), { kb: [1.0, 1.1], z: 12, origin: "40% 40%" });
tl.push(`tl.fromTo("#${stars}",{filter:"brightness(0)"},{filter:"brightness(1)",duration:0.8,ease:"power1.out"},${fx(c.biar - 0.12)});`);
SWP.scenes.push({ m: "ascend", t0: fx(c.biar - 0.1), t1: fx(c.kirim + 0.1), fi: 0.6, fo: 0.3, fill: "#05070a" });
enter("#t12", fx(c.membaca2 - 0.04), { y: 22 });
exit("#t12", fx(c.kirim - 0.3));

// ---------------------------------------------------------------- B6 CTA + loop ------------------------
cut("#m-odot, #m-adot, #m-route, #m-sw", fx(c.kirim - 0.3));
fadeIn("#map", fx(c.kirim - 0.25), 0.3);
SWP.scenes.push({ m: "converge", t0: fx(c.kirim - 0.25), t1: c.endcut, go: c.kirim, syd: [sx, sy], fill: "#f2dfb8" });
tl.push(`tl.fromTo("#m-sdot",{y:-700,autoAlpha:0},{y:0,autoAlpha:1,duration:0.42,ease:"power3.in"},${fx(c.sydney2 - 0.42)});`);
ping("#m-sring2", fx(c.sydney2 + 0.02));
enter("#t13", c.kirim, { y: 26 });
enter("#t13b", fx(c.kirim + 0.45), { y: 14 });
cut("#t13, #t13b, #map", c.endcut);
// end card: the opening frame again (same clip, same scale, same swarm time) so the LAST frame meets the FIRST
const endCard = shot("sydney", c.endcut, TOTAL, { at: fx(HOOK_AT - END_HOLD), z: 30, hold: true, origin: "42% 56%" });
const rate = (HOOK_SCALE - LOOP_SCALE) / c.padahal;
tl.push(`tl.fromTo("#${endCard}",{scale:${fx(LOOP_SCALE - rate * END_HOLD)},y:${HOOK_DY}},{scale:${LOOP_SCALE},y:${HOOK_DY},duration:${END_HOLD},ease:"none"},${c.endcut});`);
SWP.scenes.push({ m: "city", t0: c.endcut, t1: fx(TOTAL + 0.05), s0: fx(c.endcut - TOTAL), fill: "#ecd5a8", oc: [330, 905] });
SWP.scenes.push({ m: "labels", t0: 0, t1: TOTAL });

// ---------------------------------------------------------------- captions ---------------------------
// The whole VO, 2-4 words a chunk, bold; "bintang" and "1.000 km" in the accent colour.
// Chunks are cut per clause (at , . ... ?) by a small DP: never one word alone (a one-word clause joins its
// neighbour), never ending on a word that needs the next one, and preferring chunks that fit on one line.
const caps = [];
{
  const NOBREAK = new Set(["yang", "ke", "di", "dengan", "sampai", "dan", "lalu", "untuk", "jadi", "ini", "tak", "jauh", "sudah", "biar", "bisa", "tiap", "sebelum", "pernah", "sedang"]);
  const bare = (w) => w.text.toLowerCase().replace(/[^a-z0-9]/g, "");
  const len = (ws) => ws.reduce((a, w) => a + w.text.length, 0) + ws.length - 1;
  let clauses = []; let cur = [];
  for (const w of VO.words) { cur.push(w); if (/[.,?!…]$|\.\.\.$/.test(w.text)) { clauses.push(cur); cur = []; } }
  if (cur.length) clauses.push(cur);
  for (let i = 0; i < clauses.length; i++) {
    if (clauses[i].length !== 1) continue;
    if (clauses[i + 1] && clauses[i + 1].length <= 3) { clauses[i + 1] = clauses[i].concat(clauses[i + 1]); clauses[i] = null; }
    else if (clauses[i - 1] && clauses[i - 1].length <= 3) { clauses[i - 1] = clauses[i - 1].concat(clauses[i]); clauses[i] = null; }
  }
  clauses = clauses.filter(Boolean);
  // one line holds ~22 characters at 66 px; two lines (<= 34) are fine, three never
  // word pairs that read as one thing: a chunk boundary between them costs more than a clumsy chunk
  const NOSPLIT = new Set(["lampu kota", "bima sakti", "1000 km", "musim semi", "nyaris habis", "ngengat bogong", "belum pernah", "salah arah"]);
  const cost = (ws, next) => (ws.length === 1 ? 40 : 0) + (len(ws) > 22 ? 6 : 0) + (len(ws) > 34 ? 40 : 0)
    + (NOBREAK.has(bare(ws.at(-1))) && !/[.,?!…]$/.test(ws.at(-1).text) ? 18 : 0)
    + (next && NOSPLIT.has(`${bare(ws.at(-1))} ${bare(next)}`) ? 25 : 0) + 7;
  const chunks = [];
  for (const cl of clauses) {
    const n = cl.length, best = Array(n + 1).fill(Infinity), prev = Array(n + 1).fill(0); best[0] = 0;
    for (let j = 1; j <= n; j++) for (let k = Math.max(0, j - 4); k < j; k++) {
      const v = best[k] + cost(cl.slice(k, j), cl[j]); if (v < best[j]) { best[j] = v; prev[j] = k; }
    }
    const cuts = []; for (let j = n; j > 0; j = prev[j]) cuts.unshift([prev[j], j]);
    for (const [a, b] of cuts) chunks.push(cl.slice(a, b));
  }
  const hot = (t) => /^(bintang|1\.000|km)/i.test(t);
  // the aligner runs LATE after a pause, never early: snap each chunk start back to the voice's rise out of
  // silence within 0.3 s before the aligned start (a caption must never trail its word)
  const wav = fs.readFileSync(path.join(proj, "assets/vo", VO.wav));
  const dataAt = wav.indexOf("data") + 8, nS = (wav.length - dataAt) >> 1, sr = wav.readUInt32LE(24), hop = Math.round(sr / 100);
  const rms = []; let peak = 0;
  for (let i = 0; i + hop <= nS; i += hop) { let a = 0; for (let k = 0; k < hop; k++) { const v = wav.readInt16LE(dataAt + 2 * (i + k)); a += v * v; } const r = Math.sqrt(a / hop); rms.push(r); if (r > peak) peak = r; }
  const onset = (t) => {
    const thr = peak * 0.03, f0 = Math.max(1, Math.round((t - 0.3) * 100)), f1 = Math.min(rms.length - 1, Math.round((t + 0.02) * 100));
    let best = null;
    for (let f = f0; f <= f1; f++) if (rms[f - 1] < thr && rms[f] >= thr && (best === null || Math.abs(f / 100 - t) < Math.abs(best - t))) best = f / 100;
    return best ?? t;
  };
  const startOf = (ch) => onset(ch[0].start);
  chunks.forEach((ch, i) => {
    const st = fx(VO_START + startOf(ch) - 0.05), nx = chunks[i + 1];
    const en = fx(nx ? VO_START + startOf(nx) - 0.05 : Math.min(c.endcut, VO_START + ch.at(-1).end + 0.25));
    const html = ch.map((w) => { const t = esc(w.text.replace(/\.\.\.$/, "…")); return hot(w.text) ? `<em>${t}</em>` : t; }).join(" ");
    caps.push(`<div class="cap clip" id="cap-${i}" data-start="${st}" data-duration="${fx(en - st)}">${html}</div>`);
    tl.push(`tl.fromTo("#cap-${i}",{y:14,scale:0.96,opacity:0},{y:0,scale:1,opacity:1,duration:0.14,ease:"power2.out"},${st});`);
  });
  fs.writeFileSync(path.join(proj, "captions.txt"), chunks.map((ch) => ch.map((w) => w.text).join(" ")).join("\n") + "\n");
}

// ---------------------------------------------------------------- SVG layers --------------------------
const pin = (id, x, y, inner) => `<g transform="translate(${x} ${y})"><g id="${id}">${inner}</g></g>`;
const mapSvg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <defs>
    <filter id="f-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
    <mask id="mk-route" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">
      <path id="m-routeMask" d="M${ox} ${oy} Q${RQ[0]} ${RQ[1]} ${ax} ${ay}" fill="none" stroke="#fff" stroke-width="10" stroke-dasharray="${RL}" stroke-dashoffset="${RL}"/>
    </mask>
  </defs>
  <path d="${MAP.grat}" fill="none" stroke="#162030" stroke-width="0.8"/>
  <path d="${MAP.land}" fill="#141b26" stroke="#243145" stroke-width="0.6"/>
  <path id="m-aus" d="${MAP.aus}" fill="#1f2a3b" stroke="#3a4b66" stroke-width="0.8"/>
  <g id="m-route" mask="url(#mk-route)"><path d="M${ox} ${oy} Q${RQ[0]} ${RQ[1]} ${ax} ${ay}" fill="none" stroke="${INK}" stroke-width="2" stroke-dasharray="5 4.5" stroke-linecap="round" opacity="0.85"/></g>
  ${pin("m-aK", ax, ay, `<circle id="m-aring" r="16" fill="none" stroke="${INK}" stroke-width="3"/><g id="m-adot"><circle r="18" fill="${INK}" filter="url(#f-glow)" opacity="0.6"/><circle r="10" fill="${INK}"/></g>`)}
  ${pin("m-sK", sx, sy, `<circle id="m-sring" r="16" fill="none" stroke="${INK}" stroke-width="3"/><circle id="m-sring2" r="22" fill="none" stroke="${RED}" stroke-width="4"/><g id="m-sw"><circle r="10" fill="${INK}"/></g><g id="m-sdot"><circle r="26" fill="${RED}" filter="url(#f-glow)" opacity="0.85"/><circle r="15" fill="${RED}"/></g>`)}
  ${pin("m-oK", ox, oy, `<circle id="m-oring" r="22" fill="none" stroke="${RED}" stroke-width="4"/><circle id="m-oring2" r="22" fill="none" stroke="${RED}" stroke-width="3"/><g id="m-odot"><circle r="24" fill="${RED}" filter="url(#f-glow)" opacity="0.85"/><circle r="14" fill="${RED}"/></g>`)}
</svg>`;

const consSvg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="f-cglow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>
    <mask id="mk-c" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><path id="c-mask" d="${cPath}" fill="none" stroke="#fff" stroke-width="16" stroke-linecap="round" stroke-dasharray="${CL}" stroke-dashoffset="${CL}"/></mask>
  </defs>
  <g mask="url(#mk-c)">
    <path id="c-glow" d="${cPath}" fill="none" stroke="#a9d8ff" stroke-width="9" filter="url(#f-cglow)" opacity="0.25"/>
    <path d="${cPath}" fill="none" stroke="#eef7ff" stroke-width="2.6" stroke-linecap="round" opacity="0.92"/>
  </g>
  ${CST.map(([x, y], i) => `<g transform="translate(${x} ${y})"><g id="c-s${i}" class="cstar"><circle r="${i < 3 ? 9 : 7}" fill="#cfe9ff" opacity="0.35"/><circle r="${i < 3 ? 4.5 : 3.6}" fill="#ffffff"/></g></g>`).join("\n  ")}
</svg>`;

const graphSvg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="g-bg" cx="50%" cy="48%" r="70%"><stop offset="0" stop-color="#0f1622"/><stop offset="1" stop-color="#040507"/></radialGradient>
    <linearGradient id="g-fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${INK}" stop-opacity="0.9"/><stop offset="0.3" stop-color="${RED}"/><stop offset="0.55" stop-color="${RED}"/><stop offset="1" stop-color="${ACCENT}"/></linearGradient>
    <mask id="mk-g" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><path id="g-mask" d="${gPath}" fill="none" stroke="#fff" stroke-width="30" stroke-dasharray="${GL}" stroke-dashoffset="${GL}"/></mask>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#g-bg)"/>
  <g stroke="#1b2533" stroke-width="2">${[720, 845, 970].map((y) => `<line x1="110" y1="${y}" x2="970" y2="${y}"/>`).join("")}</g>
  <line x1="110" y1="1120" x2="970" y2="1120" stroke="#3b4759" stroke-width="3"/>
  <line x1="395" y1="1100" x2="395" y2="1120" stroke="${RED}" stroke-width="3" opacity="0.6"/>
  <path id="g-line" d="${gPath}" fill="none" stroke="url(#g-fade)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" mask="url(#mk-g)"/>
  <g transform="translate(395 1100)"><circle id="g-lring" r="18" fill="none" stroke="${RED}" stroke-width="4"/></g>
  <g transform="translate(970 770)"><circle id="g-ering" r="18" fill="none" stroke="${ACCENT}" stroke-width="4"/></g>
  <g id="g-head" transform="translate(110 720)"><circle r="26" fill="${INK}" opacity="0.2"/><circle r="12" fill="${INK}"/></g>
  <text id="g-low" x="412" y="996" fill="${RED}" style="font:400 104px Anton,Impact,sans-serif">−99,5%</text>
  <text id="g-y17" x="395" y="1172" fill="${INK}" text-anchor="middle" style="font:800 40px Inter,sans-serif">2017</text>
  <text id="g-y26" x="970" y="1172" fill="${ACCENT}" text-anchor="end" style="font:800 40px Inter,sans-serif">2026</text>
  <text x="970" y="682" fill="${MUTED}" text-anchor="end" opacity="0.7" style="font:600 26px Inter,sans-serif">ilustrasi tren · populasi ngengat bogong</text>
</svg>`;

// ---------------------------------------------------------------- HTML -------------------------------
const draftBadge = DRAFT ? `<div id="draft">DRAFT · b-roll Pixabay belum tersedia</div>` : "";
const page = `<!doctype html>
<html lang="id"><head><meta charset="UTF-8" /><meta name="viewport" content="width=${W}, height=${H}" />
<script src="assets/vendor/gsap.min.js"></script>
<style>
@font-face{font-family:"Anton";src:url(assets/fonts/anton-latin-400-normal.woff2) format("woff2");font-weight:400}
@font-face{font-family:"Inter";src:url(assets/fonts/inter-latin-600-normal.woff2) format("woff2");font-weight:600}
@font-face{font-family:"Inter";src:url(assets/fonts/inter-latin-800-normal.woff2) format("woff2");font-weight:800}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:${BG}}
body{font-family:Inter,system-ui,sans-serif;color:${INK};-webkit-font-smoothing:antialiased}
#root{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:${BG}}
.shot{position:absolute;inset:0}
.shot video,.shot .ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ph{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;text-align:center;padding:0 120px;
  background:repeating-linear-gradient(135deg,#14181f 0 38px,#0e1116 38px 76px);opacity:0;visibility:hidden}
.ph b{font:400 64px/1 Anton,sans-serif;letter-spacing:0.02em;color:${ACCENT}}
.ph span{font:600 40px/1.25 Inter,sans-serif;color:${MUTED}}
#map{position:absolute;inset:0;z-index:20;opacity:0;visibility:hidden;overflow:hidden;
  background:radial-gradient(ellipse at 62% 42%,#0d1522 0,#05070b 78%)}
#mapz{position:absolute;left:0;top:0;width:${W}px;height:${H}px;transform-origin:0 0}
#m-oring,#m-oring2,#m-aring,#m-sring,#m-sring2,#m-adot,#m-sw,#m-sdot,#m-odot{transform-box:fill-box;transform-origin:50% 50%}
#m-oring,#m-oring2,#m-aring,#m-sring,#m-sring2,#m-adot,#m-sw,#m-sdot,#m-odot,#m-route{opacity:0}
#cons{position:absolute;inset:0;z-index:23;pointer-events:none}
.cstar{transform-box:fill-box;transform-origin:50% 50%;opacity:0}
#graph{position:absolute;inset:0;z-index:22;transform-origin:50% 50%}
#g-low,#g-y17,#g-y26,#g-lring,#g-ering{transform-box:fill-box;transform-origin:50% 50%;opacity:0}
#dark{position:absolute;inset:0;z-index:11;background:#000;opacity:0;visibility:hidden}
#swarm{position:absolute;left:0;top:0;width:${W}px;height:${H}px;z-index:31;pointer-events:none}
#vig{position:absolute;inset:0;z-index:32;pointer-events:none;
  background:radial-gradient(ellipse at 50% 46%,rgba(0,0,0,0) 52%,rgba(0,0,0,0.55) 100%),
  linear-gradient(180deg,rgba(0,0,0,0.6) 0,rgba(0,0,0,0) 700px),linear-gradient(0deg,rgba(0,0,0,0.6) 0,rgba(0,0,0,0) 820px)}
.ct{position:absolute;opacity:0;visibility:hidden;z-index:40;will-change:transform}
#map.ct{z-index:20} #graph.ct{z-index:22} #cons.ct{z-index:23}
.ttl{left:64px;right:150px;text-align:center;font:400 128px/0.98 Anton,Impact,sans-serif;letter-spacing:0.01em;text-transform:uppercase;
  text-shadow:0 6px 30px rgba(0,0,0,0.75),0 2px 4px rgba(0,0,0,0.9)}
.ttl em,.kick em{font-style:normal;color:${ACCENT}}
.kick{left:64px;right:150px;text-align:center;font:600 46px/1.2 Inter,sans-serif;color:${INK};text-shadow:0 2px 14px rgba(0,0,0,0.9)}
.note{left:90px;right:170px;text-align:center;font:600 34px/1.3 Inter,sans-serif;color:${INK};text-shadow:0 2px 12px rgba(0,0,0,0.95)}
#t1{top:250px;font-size:124px} #t1b{top:380px;font-size:150px}
#t2{top:250px;font-size:112px;color:${INK}} #t2b{top:380px;font-size:112px} #t2c{top:505px;font-size:176px;color:${ACCENT}}
#t3{top:260px;font-size:124px}
#t4{top:250px;font-size:92px} #t4b{top:350px;font-size:176px;color:${ACCENT}}
#t5{top:250px;font-size:112px} #t5b{top:372px;font-size:112px} #t5n{top:510px}
#t6a{top:260px;font-size:120px} #t6{top:260px} #t7{top:260px} #t8{top:260px;font-size:116px}
#t9a{top:260px;font-size:140px} #t9{top:260px;font-size:140px} #t9b{top:250px;font-size:96px}
#t10{top:260px;font-size:112px} #t11{top:260px} #t12{top:260px;font-size:112px}
#t13{top:240px;font-size:108px} #t13b{top:500px;font:800 40px/1.2 Inter,sans-serif;color:${INK};letter-spacing:0.02em}
.cap{position:absolute;left:70px;right:150px;top:1230px;text-align:center;z-index:45;opacity:0;
  font:800 66px/1.12 Inter,sans-serif;color:#fff;letter-spacing:-0.01em;
  -webkit-text-stroke:2px rgba(0,0,0,0.85);paint-order:stroke fill;text-shadow:0 4px 18px rgba(0,0,0,0.85)}
.cap em{font-style:normal;color:${ACCENT}}
#draft{position:absolute;left:0;right:0;top:40px;z-index:60;text-align:center;font:800 30px/1 Inter,sans-serif;color:#fff;opacity:0.7;letter-spacing:0.06em}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="${W}" data-height="${H}">
  ${body.join("\n  ")}
  <div id="dark"></div>
  <div id="map" class="ct"><div id="mapz" data-layout-allow-overflow>${mapSvg}</div></div>
  <div id="graph" class="ct" data-layout-allow-occlusion>${graphSvg}</div>
  <div id="cons" class="ct">${consSvg}</div>
  <canvas id="swarm" width="${W}" height="${H}" data-layout-allow-overflow></canvas>
  <div id="vig"></div>
  <div id="t1" class="ttl ct">Jutaan ngengat</div>
  <div id="t1b" class="ttl ct">serbu <em>Sydney</em></div>
  <div id="t2" class="ttl ct">Padahal…</div>
  <div id="t2b" class="ttl ct">bisa baca</div>
  <div id="t2c" class="ttl ct">bintang</div>
  <div id="t3" class="ttl ct">Ngengat <em>bogong</em></div>
  <div id="t4" class="ttl ct">sampai</div>
  <div id="t4b" class="ttl ct">1.000 km</div>
  <div id="t5" class="ttl ct">Dipandu <em>bintang</em></div>
  <div id="t5b" class="ttl ct">&amp; Bima Sakti</div>
  <div id="t5n" class="note ct">Dibuktikan di jurnal <i>Nature</i>, 2025</div>
  <div id="t6a" class="ttl ct">Masalahnya…</div>
  <div id="t6" class="ttl ct">Angin <em>kencang</em></div>
  <div id="t7" class="ttl ct">Lampu <em>kota</em></div>
  <div id="t8" class="ttl ct">Nyasar ke <em>rumah</em></div>
  <div id="t9a" class="ttl ct">Tapi…</div>
  <div id="t9" class="ttl ct">Kabar <em>baik</em></div>
  <div id="t9b" class="ttl ct">Terbaik dalam<br><em>hampir 10 tahun</em></div>
  <div id="t10" class="ttl ct">Jangan <em>disemprot</em></div>
  <div id="t11" class="ttl ct">Matikan <em>lampu</em></div>
  <div id="t12" class="ttl ct">Baca <em>bintang</em> lagi</div>
  <div id="t13" class="ttl ct">Kirim ke temanmu<br>di <em>Sydney</em></div>
  <div id="t13b" class="kick ct">@titikheran · Fakta 30 Detik</div>
  ${caps.join("\n  ")}
  ${draftBadge}
  <audio id="vo" src="assets/vo/${VO.wav}" data-start="${VO_START}" data-duration="${fx(VO.duration)}" data-volume="1"></audio>
</div>
<script>window.GR = { len: 0 }; window.SWP = ${JSON.stringify(SWP)};</script>
<script src="assets/swarm.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  gsap.set(".ct",{autoAlpha:0});
  const GR = window.GR, CLK = { t: 0 };
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
  ${tl.reduce((rows, x, i) => (i % 3 ? (rows[rows.length - 1] += " " + x) : rows.push(x), rows), []).join("\n  ")}
  // the drawn layer follows the playhead: a full-length proxy tween drives it (seek-safe, a pure function of t)
  tl.fromTo(CLK,{t:0},{t:${TOTAL},duration:${TOTAL},ease:"none",onUpdate:()=>drawAll(CLK.t)},0);
  drawAll(0);
  window.__timelines["main"] = tl;
</script>
</body></html>
`;
fs.writeFileSync(path.join(proj, "index.html"), page);
fs.writeFileSync(path.join(proj, "cues.json"), JSON.stringify({ VO_START, TOTAL, OFF_T, ...c }, null, 1));
console.log(`wrote index.html  total=${TOTAL}s  tweens=${tl.length}  captions=${caps.length}  shots=${nShot}  routeL=${RL}  graphL=${GL}${DRAFT ? `  DRAFT (empty slots: ${missing.length})` : ""}`);
