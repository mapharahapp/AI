// build.mjs — Titik Heran #1, "lentera lobak". The generator is the source of truth; index.html is its output.
//
//   node build.mjs .            final build — refuses to run while any b-roll slot has no Pixabay clip
//   DRAFT=1 node build.mjs .    preview build — empty slots render as labelled placeholders
//
// PLAN (what each beat does) -> cue table (chained to voice-over WORDS) -> shots + beats -> one HTML page with
// a paused GSAP timeline. No timing below is a stopwatch number: every cue is "the next occurrence of this word
// after the previous cue", resolved against assets/vo/audio_meta.json (ElevenLabs "Akram", take 3, pauses capped).
import fs from "node:fs";
import path from "node:path";

// ---------------------------------------------------------------- PLAN -------------------------------
// Naskah & storyboard: "Titik Heran: Naskah & Storyboard Video #1". `from`/`to` are WORDS in the narration.
export const PLAN = [
  { beat: "1 hook",      from: "start",      to: "Irlandia",   hero: "footage:turnip",  frame: "absent", zones: "media full / type 250-640 / subs 1230" },
  { beat: "2 latar",     from: "Irlandia",   to: "orang",      hero: "map:ireland",     frame: "absent", zones: "map full / type 250-560 / subs 1230" },
  { beat: "3 latar",     from: "orang",      to: "Masalahnya", hero: "footage:carve",   frame: "absent", zones: "media full / type 250-560 / subs 1230" },
  { beat: "4 masalah",   from: "Masalahnya", to: "Tapi",       hero: "footage:museum",  frame: "absent", zones: "media full sepia / type 250-640 / subs 1230" },
  { beat: "5 resolusi",  from: "Tapi",       to: "Kirim",      hero: "map:route",       frame: "absent", zones: "map, then media, then split / type 250-560 / subs 1230" },
  { beat: "6 cta",       from: "Kirim",      to: "end",        hero: "footage:pumpkin", frame: "absent", zones: "split L|R / type 250-680 / subs 1230" },
];

// Pixabay b-roll slots. `need` is what the frame must show; `q` the Pixabay searches that source it.
// The sourcing step writes assets/footage/manifest.json: { <slot>: { file, w, h, dur, at, pixabay: {...} } }.
export const SLOTS = {
  turnip:       { need: "close-up carved turnip lantern face, candle glowing inside, dark", q: ["turnip lantern", "carved turnip", "turnip halloween", "rübengeist"] },
  night:        { need: "misty countryside / full moon at night, eerie", q: ["foggy night moon", "misty field night", "full moon clouds night"] },
  carve:        { need: "hands hollowing a root vegetable with a small knife, close", q: ["carving vegetable knife", "hollowing out vegetable", "knife carving hands"] },
  carveFace:    { need: "knife cutting eyes/mouth into a lantern face, close", q: ["carving pumpkin face", "pumpkin carving close up"] },
  candleLight:  { need: "match lighting a candle in the dark", q: ["lighting candle match", "match candle dark"] },
  window:       { need: "candle or lantern glowing on an old window / stone sill, night, mist", q: ["candle window night", "lantern window night", "candle old window"] },
  handover:     { need: "hands placing or handing over an old wooden box", q: ["old wooden box hands", "vintage box hands", "antique box"] },
  museum:       { need: "old museum gallery / display cases", q: ["museum interior", "museum hall", "museum display"] },
  candleOut:    { need: "a candle being blown out, smoke rising", q: ["candle blow out", "candle extinguish smoke", "blowing out candle"] },
  pumpkin:      { need: "glowing carved jack-o'-lantern face, close, dark", q: ["jack o lantern", "halloween pumpkin glowing", "pumpkin face night"] },
  pumpkinCarve: { need: "hands carving a pumpkin easily", q: ["pumpkin carving", "carving pumpkin hands"] },
};

const proj = process.argv[2] || ".";
const DRAFT = process.env.DRAFT === "1" || process.argv.includes("--draft");
const read = (p) => JSON.parse(fs.readFileSync(path.join(proj, p), "utf8"));
const VO = read("assets/vo/audio_meta.json").scenes[0];
const MAP = read("assets/map/atlantic.json");
const FOOT = fs.existsSync(path.join(proj, "assets/footage/manifest.json")) ? read("assets/footage/manifest.json") : {};
const SFX = fs.existsSync(path.join(proj, "assets/audio/sfx.json")) ? read("assets/audio/sfx.json") : {};

const missing = Object.keys(SLOTS).filter((s) => !FOOT[s]);
if (missing.length && !DRAFT) throw new Error(`no Pixabay clip yet for: ${missing.join(", ")} — source them (assets/footage/manifest.json) or build with DRAFT=1`);

const W = 1080, H = 1920;
const BG = "#050608", INK = "#F7F2E8", MUTED = "#B9B2A6", ACCENT = "#FF9A1F", RED = "#FF2D2D";
const fx = (n) => +(+n).toFixed(3);
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
const VO_START = 0.35;                       // a beat of air: the match strike lands before the first word

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
c.bukan = TA("BUKAN", -1);
c.mumi = TA("mumi", c.bukan);
c.ini2 = TA("Ini", c.mumi);
c.lobak = TA("lobak", c.ini2);
c.nenek = TA("nenek", c.lobak);
c.irl = TA("Irlandia", c.nenek);
c.sekitar = TA("sekitar", c.irl);
c.y1900 = TA("1900", c.sekitar);
c.tiap = TA("Tiap", c.y1900);
c.orang = TA("orang", c.tiap);
c.mengukir = TA("mengukir", c.orang);
c.wajah = TA("wajah", c.mengukir);
c.menyalakan = TA("menyalakan", c.wajah);
c.lilin = TA("lilin", c.menyalakan);
c.untuk = TA("untuk", c.lilin);
c.mengusir = TA("mengusir", c.untuk);
c.masalah = TA("Masalahnya", c.mengusir);
c.memudar = TA("memudar", c.masalah);
c.seorang = TA("Seorang", c.memudar);
c.museum = TA("museum", c.seorang);
c.karena = TA("karena", c.museum);
c.tak = TA("tak", c.karena);
c.membuat = TA("membuatnya", c.tak);
c.tapi = TA("Tapi", c.membuat);
c.mati = TA("mati", c.tapi);
c.imigran = TA("Imigran", c.mati);
c.membawa = TA("membawanya", c.imigran);
c.amerika = TA("Amerika", c.membawa);
c.mengganti = TA("mengganti", c.amerika);
c.lobak2 = TA("lobak", c.mengganti);
c.labu2 = TA("labu", c.lobak2);
c.jauh = TA("jauh", c.labu2);
c.cuma = TA("Cuma", c.jauh);
c.benua = TA("benua", c.cuma);
c.ganti = TA("ganti", c.benua);
c.kirim = TA("Kirim", c.ganti);
c.reaksi = TA("reaksinya", c.kirim);
const VO_END = fx(VO_START + VO.duration);
c.endcut = fx(Math.min(VO_END, VO_START + VO.words.at(-1).end) + 0.06);   // hard cut back to the opening frame
const END_HOLD = 1.0;
const TOTAL = fx(c.endcut + END_HOLD);
if (TOTAL > 179) throw new Error(`total ${TOTAL}s exceeds the 2:59 ceiling — see hyperframe-pro-voice`);

const tl = [], body = [], audio = [];
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
const cut = (sel, at) => tl.push(`tl.set("${sel}",{autoAlpha:0},${fx(at)});`);
const show = (sel, at) => tl.push(`tl.set("${sel}",{autoAlpha:1},${fx(at)});`);
const sfx = (name, at, vol = 0.8) => {
  const f = SFX[name];
  if (!f) { if (!DRAFT) throw new Error(`sfx "${name}" missing from assets/audio/sfx.json`); return; }
  const d = fx(Math.min(f.dur, TOTAL - at)), fade = d < f.dur ? ` data-fade-out="0.35"` : "";
  audio.push(`<audio id="sfx-${name}-${audio.length}" src="${f.file}" data-start="${fx(at)}" data-duration="${d}" data-volume="${vol}"${fade}></audio>`);
};

// ---------------------------------------------------------------- shots (footage) ---------------------
// One <video class="clip footage"> per window. data-start/data-duration own its visibility (never GSAP it);
// the Ken Burns and grade tweens live on the wrapper .shot around it.
let nShot = 0;
function shot(slot, from, to, { at = null, kb = [1.0, 1.08], dx = 0, dy = 0, grade = "", z = 1, pos = "50% 50%", hold = false } = {}) {
  const id = `sh${++nShot}`, dur = fx(to - from), f = FOOT[slot];
  const mediaStart = fx(at ?? (f?.at ?? 0));
  const style = `object-position:${pos}`;
  const inner = f
    ? `<video id="v${nShot}" class="clip footage" muted playsinline preload="auto" src="${f.file}" data-start="${fx(from)}" data-duration="${dur}" data-media-start="${mediaStart}" style="${style}"></video>`
    : `<div id="v${nShot}" class="ph footage"><b>B-ROLL PIXABAY</b><span>${esc(slot)} — ${esc(SLOTS[slot].need)}</span></div>`;
  if (f && f.dur && mediaStart + dur > f.dur + 0.01) throw new Error(`${slot}: trim ${mediaStart}+${dur}s runs past the clip (${f.dur}s) — the plate would go black mid-beat`);
  body.push(`<div id="${id}" class="shot ${grade}" style="z-index:${z}">${inner}</div>`);
  if (!f) { show(`#v${nShot}`, from); cut(`#v${nShot}`, to); }          // placeholders are plain divs: GSAP owns them
  if (!hold) tl.push(`tl.fromTo("#${id}",{scale:${kb[0]},x:0,y:${dy}},{scale:${kb[1]},x:${dx},y:${dy},duration:${dur},ease:"none"},${fx(from)});`);
  else tl.push(`tl.set("#${id}",{scale:${kb[0]},x:0,y:${dy}},${fx(from)});`);
  return id;
}

// ---------------------------------------------------------------- B1 hook -----------------------------
// Frame 0 is the turnip face, already moving (push-in); a zoom jolt lands ON "lobak".
const HOOK_AT = FOOT.turnip?.at ?? 1.2;      // media time of the opening frame; the end card returns to it
const hook = shot("turnip", 0, c.irl, { at: HOOK_AT, kb: [1.03, 1.03], z: 2, hold: true });
const LOOP_SCALE = 1.03;                     // first frame == last frame: the end card pushes in to exactly this
tl.push(`tl.fromTo("#${hook}",{scale:${LOOP_SCALE}},{scale:1.07,duration:${fx(c.lobak - 0.04)},ease:"none"},0);`);
tl.push(`tl.to("#${hook}",{scale:1.2,duration:0.16,ease:"power4.out"},${fx(c.lobak - 0.04)});`);
tl.push(`tl.to("#${hook}",{scale:1.25,duration:${fx(c.irl - c.lobak - 0.13)},ease:"none"},${fx(c.lobak + 0.13)});`);
slam("#t1", 0.1);
cut("#t1", fx(c.lobak - 0.04));               // same position, so a hard swap — never a soft overlap
slam("#t2", fx(c.lobak - 0.04), { from: 1.5, d: 0.22 });
enter("#t2k", c.nenek, { y: 18 });
exit("#t2, #t2k", fx(c.irl - X + 0.1));
sfx("match", 0.0, 0.9);
sfx("hum", 0.0, 0.12);

// ---------------------------------------------------------------- B2 latar: the map -------------------
// Dark map, the Titik Heran red dot drops onto Ireland ON "Irlandia", then the camera dives to the island.
const [ix, iy] = MAP.pts.ireland, [ax, ay] = MAP.pts.america;
const ZOOM = 3.4, ZX = fx(540 - ix), ZY = fx(860 - iy);
tl.push(`tl.set("#mapz",{transformOrigin:"${ix}px ${iy}px",scale:1.12,x:0,y:0},0);`);
tl.push(`tl.fromTo("#map",{autoAlpha:0},{autoAlpha:1,duration:0.3,ease:"power2.out"},${fx(c.irl - 0.28)});`);
tl.push(`tl.to("#mapz",{scale:1,duration:0.6,ease:"power3.out"},${fx(c.irl - 0.28)});`);
tl.push(`tl.fromTo("#m-dot",{y:-760,autoAlpha:0},{y:0,autoAlpha:1,duration:0.42,ease:"power3.in"},${fx(c.irl - 0.3)});`);
ping("#m-ring", fx(c.irl + 0.12));
tl.push(`tl.fromTo("#m-irl",{fill:"#1d2636"},{fill:"#5a3412",duration:0.5,ease:"power2.out"},${fx(c.irl + 0.12)});`);
tl.push(`tl.to("#mapz",{scale:${ZOOM},x:${ZX},y:${ZY},duration:${fx(c.y1900 - c.sekitar + 0.5)},ease:"power2.inOut"},${fx(c.sekitar - 0.1)});`);
ping("#m-ring2", fx(c.y1900 + 0.2), 2.6);
const diveEnd = fx(c.sekitar - 0.1 + c.y1900 - c.sekitar + 0.5);
tl.push(`tl.to("#mapz",{scale:${fx(ZOOM * 1.08)},duration:${fx(c.tiap + 0.15 - diveEnd)},ease:"none"},${diveEnd});`);
sfx("whoosh", fx(c.irl - 0.32), 0.5);
sfx("ting", fx(c.irl + 0.1), 0.7);
sfx("wind", fx(c.irl - 0.2), 0.25);
slam("#t3", c.irl);
enter("#t3y", c.sekitar, { y: 22 });
tl.push(`tl.to(YR,{v:1900,duration:${fx(c.y1900 - c.sekitar - 0.05)},ease:"power2.out",snap:{v:1},onUpdate:()=>{document.getElementById("yr").textContent=Math.round(YR.v);}},${fx(c.sekitar + 0.05)});`);
exit("#t3, #t3y", fx(c.tiap - 0.3));
tl.push(`tl.to("#map",{autoAlpha:0,duration:0.35,ease:"power2.in"},${fx(c.tiap - 0.2)});`);
tl.push(`tl.set("#map",{autoAlpha:0},${fx(c.tiap + 0.15)});`);
shot("night", fx(c.tiap - 0.2), c.orang, { kb: [1.12, 1.02], z: 3 });

// ---------------------------------------------------------------- B3 latar: the making -----------------
shot("carveFace", c.orang, c.wajah, { kb: [1.02, 1.1], dx: -18, z: 4 });
shot("carve", c.wajah, c.menyalakan, { kb: [1.12, 1.04], z: 5 });
c.di = TA("di", c.lilin);
shot("candleLight", c.menyalakan, c.di, { kb: [1.0, 1.06], z: 6 });
shot("turnip", c.di, c.untuk, { at: HOOK_AT + 0.5, kb: [1.16, 1.06], z: 6 });
sfx("flame", fx(c.menyalakan + 0.05), 0.4);
shot("window", c.untuk, c.masalah, { kb: [1.1, 1.0], z: 7 });
sfx("carve", fx(c.mengukir - 0.1), 0.3);
slam("#t4", c.lilin);
cut("#t4", fx(c.untuk - 0.02));
slam("#t5", fx(c.untuk - 0.02));
exit("#t5", fx(c.masalah - X));

// ---------------------------------------------------------------- B4 masalah: it fades -----------------
// The hook's own face, draining to sepia ON "memudar"; then archive-toned museum shots; the candle goes out.
const fade = shot("turnip", c.masalah, c.seorang, { at: HOOK_AT + 1.0, kb: [1.08, 1.0], z: 8 });
tl.push(`tl.fromTo("#${fade}",{filter:"sepia(0) saturate(1) brightness(1)"},{filter:"sepia(0.9) saturate(0.35) brightness(0.6)",duration:${fx(c.seorang - c.memudar)},ease:"power1.inOut"},${fx(c.memudar - 0.2)});`);
shot("handover", c.seorang, c.museum, { kb: [1.0, 1.07], grade: "g-sepia", z: 9 });
shot("museum", c.museum, c.tak, { kb: [1.1, 1.02], dx: -20, grade: "g-sepia", z: 10 });
shot("candleOut", c.tak, c.tapi, { kb: [1.0, 1.05], grade: "g-sepia", z: 11 });
show("#archive", c.masalah);
tl.push(`tl.fromTo("#archive",{opacity:0},{opacity:1,duration:0.6,ease:"none"},${fx(c.memudar - 0.2)});`);
cut("#archive", c.tapi);
enter("#t6", c.memudar, { y: 0 });
tl.push(`tl.to("#t6",{opacity:0,filter:"blur(14px)",duration:${fx(c.seorang - c.memudar - 0.5)},ease:"power1.in"},${fx(c.memudar + 0.45)});`);
cut("#t6", fx(c.seorang - 0.02));
slam("#t7", c.seorang);
enter("#t7n", fx(c.seorang + 0.35), { y: 16 });
exit("#t7", fx(c.tak - 0.25));
exit("#t7n", fx(c.tapi - 0.3));
slam("#t8", fx(c.tak - 0.02));
exit("#t8", fx(c.tapi - 0.3));
sfx("blow", fx(c.membuat - 0.03), 0.5);

// ---------------------------------------------------------------- B5 resolusi -----------------------------
// Colour comes back on "Tapi"; the dot crosses the Atlantic; the turnip match-cuts to a pumpkin ON "labu".
const relight = shot("candleLight", c.tapi, fx(c.imigran + 0.2), { at: (FOOT.candleLight?.at ?? 0) + 0.4, kb: [1.08, 1.0], z: 12 });
tl.push(`tl.fromTo("#${relight}",{filter:"sepia(0.9) saturate(0.35) brightness(0.6)"},{filter:"sepia(0) saturate(1.1) brightness(1)",duration:0.9,ease:"power2.out"},${fx(c.tapi)});`);
slam("#t9", fx(c.tapi + 0.05));
sfx("flame", fx(c.tapi + 0.05), 0.4);
exit("#t9", fx(c.imigran - 0.3));

// map, second visit: wide, the dot sails Ireland -> America along a dashed arc
const qx = fx((ix + ax) / 2), qy = fx(Math.min(iy, ay) - 300);
const bez = (t) => [(1 - t) ** 2 * ix + 2 * (1 - t) * t * qx + t * t * ax, (1 - t) ** 2 * iy + 2 * (1 - t) * t * qy + t * t * ay];
let L = 0; { let [px, py] = bez(0); for (let i = 1; i <= 200; i++) { const [x2, y2] = bez(i / 200); L += Math.hypot(x2 - px, y2 - py); px = x2; py = y2; } }
L = Math.ceil(L);
const sail0 = fx(c.imigran + 0.35), sail1 = fx(c.amerika + 0.3);
tl.push(`tl.set("#mapz",{scale:1,x:0,y:0},${fx(c.imigran - 0.5)});`);
tl.push(`tl.set("#m-irl",{fill:"#5a3412"},${fx(c.imigran - 0.5)});`);
tl.push(`tl.fromTo("#map",{autoAlpha:0},{autoAlpha:1,duration:0.3,ease:"power2.out",immediateRender:false},${fx(c.imigran - 0.2)});`);
tl.push(`tl.to("#mapz",{scale:1.05,duration:${fx(c.mengganti - c.imigran + 0.2)},ease:"none"},${fx(c.imigran - 0.2)});`);
tl.push(`tl.fromTo("#m-route",{autoAlpha:0},{autoAlpha:1,duration:0.2,ease:"none"},${sail0});`);
tl.push(`tl.fromTo("#m-routeMask",{strokeDashoffset:${L}},{strokeDashoffset:0,duration:${fx(sail1 - sail0)},ease:"power1.inOut"},${sail0});`);
tl.push(`tl.fromTo("#m-ship",{autoAlpha:0},{autoAlpha:1,duration:0.2,ease:"none"},${sail0});`);
tl.push(`tl.to(SAIL,{t:1,duration:${fx(sail1 - sail0)},ease:"power1.inOut",onUpdate:()=>{const t=SAIL.t,u=1-t;` +
  `const x=u*u*${ix}+2*u*t*${qx}+t*t*${ax},y=u*u*${iy}+2*u*t*${qy}+t*t*${ay};` +
  `const dx=2*u*(${qx}-${ix})+2*t*(${ax}-${qx}),dy=2*u*(${qy}-${iy})+2*t*(${ay}-${qy});` +
  `document.getElementById("m-shipT").setAttribute("transform","translate("+x.toFixed(1)+","+y.toFixed(1)+")");` +
  `document.getElementById("m-ship").setAttribute("transform","scale("+(dx<0?1:-1)+",1)");}},${sail0});`);
tl.push(`tl.fromTo("#m-adot",{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.3,ease:"back.out(3)"},${sail1});`);
ping("#m-aring", sail1);
tl.push(`tl.fromTo("#m-usa",{fill:"#1d2636"},{fill:"#5a3412",duration:0.5,ease:"power2.out"},${sail1});`);
sfx("whoosh", fx(sail0 - 0.05), 0.25);
sfx("ting", fx(sail1), 0.6);
slam("#t10", c.imigran);
enter("#t10b", c.amerika, { y: 20 });
exit("#t10, #t10b", fx(c.mengganti - X + 0.1));
tl.push(`tl.to("#map",{autoAlpha:0,duration:0.3,ease:"power2.in"},${fx(c.mengganti - 0.32)});`);
tl.push(`tl.set("#map",{autoAlpha:0},${fx(c.mengganti)});`);

// the swap: turnip, then the SAME framing as a pumpkin, cut ON "labu" behind a flash
shot("turnip", fx(c.mengganti - 0.3), c.labu2, { at: HOOK_AT + 2.0, kb: [1.0, 1.08], z: 13 });
shot("pumpkin", c.labu2, fx(c.jauh + 0.4), { kb: [1.08, 1.12], dy: 140, z: 14 });
shot("pumpkinCarve", fx(c.jauh + 0.4), fx(c.cuma - 0.05), { kb: [1.0, 1.08], grade: "g-night", z: 15 });
tl.push(`tl.set("#flash",{autoAlpha:0.3},${fx(c.labu2)});`);
tl.push(`tl.to("#flash",{autoAlpha:0,duration:0.32,ease:"power2.out"},${fx(c.labu2 + 0.01)});`);
sfx("pop", fx(c.labu2 - 0.03), 0.8);
slam("#t11", c.lobak2);
enter("#t11b", c.labu2, { y: 20 });
exit("#t11, #t11b", fx(c.cuma - X));

// split screen: turnip | pumpkin, both staring out; the line lands as one sentence
tl.push(`tl.fromTo("#splitL",{autoAlpha:0,x:-120},{autoAlpha:1,x:0,duration:0.35,ease:"power3.out"},${fx(c.cuma - 0.1)});`);
tl.push(`tl.fromTo("#splitR",{autoAlpha:0,x:120},{autoAlpha:1,x:0,duration:0.35,ease:"power3.out"},${fx(c.cuma - 0.1)});`);
tl.push(`tl.fromTo("#splitBar",{scaleY:0},{scaleY:1,duration:0.4,ease:"power3.out"},${fx(c.cuma + 0.1)});`);
enter("#chipL", fx(c.cuma + 0.2), { y: 12 });
enter("#chipR", fx(c.cuma + 0.3), { y: 12 });
sfx("whoosh", fx(c.cuma - 0.39), 0.3);
slam("#t12", c.cuma);
slam("#t12b", fx(c.ganti - 0.05), { from: 1.5 });
exit("#t12, #t12b", fx(c.kirim - 0.3));

// ---------------------------------------------------------------- B6 CTA + loop ------------------------
enter("#t13", c.kirim, { y: 26 });
enter("#t13b", fx(c.kirim + 0.45), { y: 14 });
cut("#t13, #t13b, #chipL, #chipR, #splitL, #splitR", c.endcut);
// end card: the opening frame again (same clip, same scale), arriving so the LAST frame is the FIRST frame
shot("turnip", c.endcut, TOTAL, { at: fx(HOOK_AT - END_HOLD), kb: [1.0, LOOP_SCALE], z: 30 });
sfx("sting", fx(c.endcut - 0.02), 0.75);

// ---------------------------------------------------------------- candle flicker on a still lantern -----
if (FOOT.turnip?.still) {
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const REST = 0.34;
  const flicker = (from, to) => {
    tl.push(`tl.set("#flick",{opacity:${REST}},${fx(from)});`);
    for (let t = from + 0.05; ;) {
      const d = 0.06 + rnd() * 0.1, o = 0.16 + rnd() * 0.36;
      if (t + d > to - 0.13) break;
      tl.push(`tl.to("#flick",{opacity:${o.toFixed(2)},duration:${fx(d)},ease:"sine.inOut"},${fx(t)});`);
      t = fx(t + d + 0.005);
    }
    tl.push(`tl.to("#flick",{opacity:${REST},duration:0.1,ease:"sine.inOut"},${fx(to - 0.12)});`);
    tl.push(`tl.set("#flick",{opacity:0},${fx(to)});`);
  };
  flicker(0, c.irl);
  flicker(c.masalah, c.seorang);
  flicker(fx(c.mengganti - 0.3), c.labu2);
  flicker(c.di, c.untuk);
  flicker(c.endcut, TOTAL);                 // ends at REST on the last frame, the level frame 0 starts at
}

// ---------------------------------------------------------------- split panels (videos inside) --------
function panel(slot, from, to, at) {
  const f = FOOT[slot], dur = fx(to - from);
  if (!f) return `<div class="ph footage" style="position:absolute;inset:0;opacity:1;visibility:visible"><b>B-ROLL PIXABAY</b><span>${esc(slot)}</span></div>`;
  return `<div id="pz-${slot}" class="pz"><video id="p-${slot}" class="clip footage" muted playsinline preload="auto" src="${f.file}" data-start="${fx(from)}" data-duration="${dur}" data-media-start="${fx(at)}"></video></div>`;
}
const splitFrom = fx(c.cuma - 0.1);
const splitL = panel("turnip", splitFrom, c.endcut, HOOK_AT + 3.0);
const splitR = panel("pumpkin", splitFrom, c.endcut, (FOOT.pumpkin?.at ?? 0) + 1.0);
// measured glow boxes (1080 frame): turnip x 374-732 (centre 553), pumpkin x 342-716 (centre 529) — both fit the
// 540-px panel at scale >= 1, so never scale below 1 (that shows the clip's edges); just centre each face
if (FOOT.turnip) tl.push(`tl.fromTo("#pz-turnip",{scale:1.0,x:-13},{scale:1.06,x:-13,duration:${fx(c.endcut - splitFrom)},ease:"none"},${splitFrom});`);
if (FOOT.pumpkin) tl.push(`tl.fromTo("#pz-pumpkin",{scale:1.05,x:11},{scale:1.0,x:11,duration:${fx(c.endcut - splitFrom)},ease:"none"},${splitFrom});`);

// ---------------------------------------------------------------- captions ---------------------------
// The whole VO, 2-4 words a chunk, bold; "lobak", "1900" and "labu" in the accent colour.
// Chunks are cut per clause (at , . ... ?) by a small DP: never one word alone (a one-word clause joins its
// neighbour), never ending on a word that needs the next one, and preferring chunks that fit on one line.
const caps = [];
{
  const NOBREAK = new Set(["yang", "ke", "di", "dengan", "satu", "sampai", "dan", "lalu", "untuk", "jadi", "ini", "tak"]);
  const bare = (w) => w.text.toLowerCase().replace(/[^a-z0-9]/g, "");
  const len = (ws) => ws.reduce((a, w) => a + w.text.length, 0) + ws.length - 1;
  // clauses, then glue one-word clauses onto a neighbour (forward first) when the result stays <= 4 words
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
  const cost = (ws) => (ws.length === 1 ? 40 : 0) + (len(ws) > 22 ? 6 : 0) + (len(ws) > 34 ? 40 : 0)
    + (NOBREAK.has(bare(ws.at(-1))) && !/[.,?!…]$/.test(ws.at(-1).text) ? 18 : 0) + 7;
  const chunks = [];
  for (const cl of clauses) {
    const n = cl.length, best = Array(n + 1).fill(Infinity), prev = Array(n + 1).fill(0); best[0] = 0;
    for (let j = 1; j <= n; j++) for (let k = Math.max(0, j - 4); k < j; k++) {
      const v = best[k] + cost(cl.slice(k, j)); if (v < best[j]) { best[j] = v; prev[j] = k; }
    }
    const cuts = []; for (let j = n; j > 0; j = prev[j]) cuts.unshift([prev[j], j]);
    for (const [a, b] of cuts) chunks.push(cl.slice(a, b));
  }
  const hot = (t) => /^(lobak|labu|1900)/i.test(t);
  chunks.forEach((ch, i) => {
    const st = fx(VO_START + ch[0].start - 0.05), nx = chunks[i + 1];
    const en = fx(nx ? VO_START + nx[0].start - 0.05 : Math.min(c.endcut, VO_START + ch.at(-1).end + 0.25));
    const html = ch.map((w) => { const t = esc(w.text.replace(/\.\.\.$/, "…")); return hot(w.text) ? `<em>${t}</em>` : t; }).join(" ");
    caps.push(`<div class="cap clip" id="cap-${i}" data-start="${st}" data-duration="${fx(en - st)}">${html}</div>`);
    tl.push(`tl.fromTo("#cap-${i}",{y:14,scale:0.96,opacity:0},{y:0,scale:1,opacity:1,duration:0.14,ease:"power2.out"},${st});`);
  });
  fs.writeFileSync(path.join(proj, "captions.txt"), chunks.map((ch) => ch.map((w) => w.text).join(" ")).join("\n") + "\n");
}

// ---------------------------------------------------------------- map SVG ----------------------------
const ship = `<path d="M-26 6 L26 6 L18 18 L-18 18 Z" fill="${INK}"/><path d="M-2 4 L-2 -34 L-22 2 Z" fill="${INK}" opacity="0.9"/><path d="M2 4 L2 -30 L20 2 Z" fill="${INK}" opacity="0.75"/>`;
const mapSvg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="g-ocean" cx="60%" cy="42%" r="75%"><stop offset="0" stop-color="#0d1420"/><stop offset="1" stop-color="#030406"/></radialGradient>
    <filter id="f-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
    <mask id="mk-route" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}">
      <path id="m-routeMask" d="M${ix} ${iy} Q${qx} ${qy} ${ax} ${ay}" fill="none" stroke="#fff" stroke-width="16" stroke-dasharray="${L}" stroke-dashoffset="${L}"/>
    </mask>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#g-ocean)"/>
  <path d="${MAP.grat}" fill="none" stroke="#18212f" stroke-width="1"/>
  <path d="${MAP.land}" fill="#1d2636" stroke="#2d3a50" stroke-width="1"/>
  <path id="m-usa" d="${MAP.usa}" fill="#1d2636" stroke="#2d3a50" stroke-width="1"/>
  <path id="m-irl" d="${MAP.ireland}" fill="#1d2636" stroke="#c96d1c" stroke-width="1.2"/>
  <g id="m-route" mask="url(#mk-route)"><path d="M${ix} ${iy} Q${qx} ${qy} ${ax} ${ay}" fill="none" stroke="${INK}" stroke-width="5" stroke-dasharray="14 12" stroke-linecap="round" opacity="0.9"/></g>
  <g transform="translate(${ax} ${ay})"><circle id="m-aring" r="22" fill="none" stroke="${RED}" stroke-width="4"/><g id="m-adot"><circle r="22" fill="${RED}" filter="url(#f-glow)" opacity="0.8"/><circle r="13" fill="${RED}"/></g></g>
  <g id="m-shipT" transform="translate(${ix} ${iy})"><g id="m-ship">${ship}</g></g>
  <g transform="translate(${ix} ${iy})"><circle id="m-ring" r="22" fill="none" stroke="${RED}" stroke-width="4"/><circle id="m-ring2" r="22" fill="none" stroke="${RED}" stroke-width="3"/><g id="m-dot"><circle r="24" fill="${RED}" filter="url(#f-glow)" opacity="0.85"/><circle r="14" fill="${RED}"/></g></g>
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
.shot{position:absolute;inset:0;transform-origin:50% 45%}
.shot video,.shot .ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.g-night video{filter:brightness(0.5) saturate(0.9) contrast(1.1)}
.g-dim video{filter:sepia(0.6) saturate(0.55) brightness(0.58) contrast(1.15)}
.g-sepia video,.g-sepia .ph{filter:sepia(0.85) saturate(0.45) contrast(1.08) brightness(0.72)}
.ph{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;text-align:center;padding:0 120px;
  background:repeating-linear-gradient(135deg,#14181f 0 38px,#0e1116 38px 76px);opacity:0;visibility:hidden}
.ph b{font:400 64px/1 Anton,sans-serif;letter-spacing:0.02em;color:${ACCENT}}
.ph span{font:600 40px/1.25 Inter,sans-serif;color:${MUTED}}
#map{position:absolute;inset:0;z-index:20;opacity:0;visibility:hidden}
#mapz{position:absolute;inset:0}
#m-ring,#m-ring2,#m-aring,#m-adot,#m-dot,#m-ship{transform-box:fill-box;transform-origin:50% 50%}
#m-ring,#m-aring,#m-ring2,#m-adot,#m-route,#m-ship{opacity:0}
#split{position:absolute;inset:0;z-index:25;pointer-events:none}
#splitL,#splitR{position:absolute;top:0;bottom:0;width:540px;overflow:hidden;opacity:0;visibility:hidden}
#splitL{left:0} #splitR{right:0}
#splitL video,#splitR video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.pz{position:absolute;inset:0;transform-origin:50% 48%}
#splitBar{position:absolute;left:536px;top:0;width:8px;height:${H}px;background:${ACCENT};transform-origin:50% 50%;z-index:41}
.chip{position:absolute;top:1400px;padding:10px 22px;border-radius:999px;background:rgba(5,6,8,0.72);font:800 40px/1 Inter,sans-serif;letter-spacing:0.04em}
#chipL{left:40px;color:${INK}} #chipR{left:580px;color:${ACCENT}}
#archive{position:absolute;inset:0;z-index:21;pointer-events:none;opacity:0;
  background:radial-gradient(ellipse at 50% 45%,rgba(60,38,10,0) 40%,rgba(30,18,4,0.55) 100%),repeating-linear-gradient(90deg,rgba(255,240,200,0.035) 0 2px,transparent 2px 160px)}
#flash{position:absolute;inset:0;z-index:28;background:#fff6e6;opacity:0;visibility:hidden}
#flick{position:absolute;inset:0;z-index:31;pointer-events:none;mix-blend-mode:screen;opacity:0;
  background:radial-gradient(circle at 50% ${FOOT.turnip?.glowY ?? 52}%,rgba(255,150,40,0.6) 0,rgba(255,110,25,0.2) 26%,rgba(0,0,0,0) 58%)}
#vig{position:absolute;inset:0;z-index:32;pointer-events:none;
  background:radial-gradient(ellipse at 50% 46%,rgba(0,0,0,0) 52%,rgba(0,0,0,0.6) 100%),
  linear-gradient(180deg,rgba(0,0,0,0.62) 0,rgba(0,0,0,0) 720px),linear-gradient(0deg,rgba(0,0,0,0.6) 0,rgba(0,0,0,0) 860px)}
.ct{position:absolute;opacity:0;visibility:hidden;z-index:40;will-change:transform}
.ttl{left:64px;right:150px;text-align:center;font:400 128px/0.98 Anton,Impact,sans-serif;letter-spacing:0.01em;text-transform:uppercase;
  text-shadow:0 6px 30px rgba(0,0,0,0.75),0 2px 4px rgba(0,0,0,0.9)}
.ttl em,.kick em{font-style:normal;color:${ACCENT}}
.kick{left:64px;right:150px;text-align:center;font:600 46px/1.2 Inter,sans-serif;color:${INK};text-shadow:0 2px 14px rgba(0,0,0,0.9)}
.note{left:90px;right:170px;text-align:center;font:600 34px/1.3 Inter,sans-serif;color:${MUTED};text-shadow:0 2px 12px rgba(0,0,0,0.95)}
#t1{top:270px} #t2{top:300px;font-size:168px} #t2k{top:500px}
#t3{top:270px} #t3y{top:420px;font-size:96px;color:${INK}} #t3y span{color:${ACCENT}}
#t4{top:300px} #t5{top:270px}
#t6{top:340px;font-size:150px;color:#e9dcc2} #t7{top:280px;color:#f1e3c4} #t7n{top:600px;left:110px;right:190px;padding:14px 22px;border-radius:16px;background:rgba(5,6,8,0.66);color:${INK};font-size:38px}
#t7n span{white-space:nowrap}
.arw{position:relative;display:inline-block}
.arw svg{position:absolute;right:100%;margin-right:22px;top:50%;height:0.46em;width:auto;transform:translateY(-50%)} #t8{top:270px;color:#f1e3c4}
#t9{top:270px} #t10{top:270px} #t10b{top:410px;font-size:110px;color:${ACCENT}}
#t11{top:280px} #t11b{top:420px;font-size:150px;color:${ACCENT}}
#t12{top:250px;font-size:100px;white-space:nowrap} #t12b{top:370px;font-size:126px;color:${ACCENT};white-space:nowrap}
#t13{top:250px;font-size:116px} #t13b{top:520px;font:800 40px/1.2 Inter,sans-serif;color:${INK};letter-spacing:0.02em}
.cap{position:absolute;left:70px;right:150px;top:1230px;text-align:center;z-index:45;opacity:0;
  font:800 66px/1.12 Inter,sans-serif;color:#fff;letter-spacing:-0.01em;
  -webkit-text-stroke:2px rgba(0,0,0,0.85);paint-order:stroke fill;text-shadow:0 4px 18px rgba(0,0,0,0.85)}
.cap em{font-style:normal;color:${ACCENT}}
#draft{position:absolute;left:0;right:0;top:40px;z-index:60;text-align:center;font:800 30px/1 Inter,sans-serif;color:#fff;opacity:0.7;letter-spacing:0.06em}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="${W}" data-height="${H}">
  ${body.join("\n  ")}
  <div id="archive"></div>
  <div id="map" class="ct"><div id="mapz">${mapSvg}</div></div>
  <div id="split"><div id="splitL" class="ct">${splitL}</div><div id="splitR" class="ct">${splitR}</div><div id="splitBar"></div></div>
  <div id="chipL" class="chip ct">LOBAK</div><div id="chipR" class="chip ct">LABU</div>
  <div id="flash"></div>
  <div id="flick"></div>
  <div id="vig"></div>
  <div id="t1" class="ttl ct">Ini bukan<br>kepala mumi</div>
  <div id="t2" class="ttl ct">Ini <em>lobak</em></div>
  <div id="t2k" class="kick ct">nenek moyang labu Halloween</div>
  <div id="t3" class="ttl ct">Irlandia</div>
  <div id="t3y" class="ttl ct">sekitar <span id="yr">1890</span></div>
  <div id="t4" class="ttl ct">Lilin<br>di dalam</div>
  <div id="t5" class="ttl ct">Untuk mengusir<br><em>arwah</em></div>
  <div id="t6" class="ttl ct">memudar</div>
  <div id="t7" class="ttl ct">1943, Donegal</div>
  <div id="t7n" class="note ct">Cetakan gips lentera itu kini dipajang di <span>National Museum of Ireland</span></div>
  <div id="t8" class="ttl ct">Tak ada lagi<br>yang membuat</div>
  <div id="t9" class="ttl ct">Tapi<br><em>nggak mati</em></div>
  <div id="t10" class="ttl ct">Irlandia</div>
  <div id="t10b" class="ttl ct"><span class="arw"><svg viewBox="0 0 120 70"><path d="M0 24H74V0L120 35L74 70V46H0Z" fill="currentColor"/></svg>Amerika</span></div>
  <div id="t11" class="ttl ct">Lobak</div>
  <div id="t11b" class="ttl ct"><span class="arw"><svg viewBox="0 0 120 70"><path d="M0 24H74V0L120 35L74 70V46H0Z" fill="currentColor"/></svg>Labu</span></div>
  <div id="t12" class="ttl ct">Cuma pindah benua</div>
  <div id="t12b" class="ttl ct">&amp; ganti sayur</div>
  <div id="t13" class="ttl ct">Kirim ke teman<br><em>paling penakut</em></div>
  <div id="t13b" class="kick ct">@titikheran · Fakta 30 Detik</div>
  ${caps.join("\n  ")}
  ${draftBadge}
  <audio id="vo" src="assets/vo/${VO.wav}" data-start="${VO_START}" data-duration="${fx(VO.duration)}" data-volume="1"></audio>
  <audio id="music" src="assets/audio/music.m4a" data-start="0" data-duration="${TOTAL}" data-volume="0.26" data-fade-out="0.6"></audio>
  ${audio.join("\n  ")}
</div>
<script>
  window.__timelines = window.__timelines || {};
  gsap.set(".ct",{autoAlpha:0});
  gsap.set("#splitBar",{scaleY:0});
  const YR = { v: 1890 }, SAIL = { t: 0 };
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
  ${tl.join("\n  ")}
  window.__timelines["main"] = tl;
</script>
</body></html>
`;
fs.writeFileSync(path.join(proj, "index.html"), page);
fs.writeFileSync(path.join(proj, "cues.json"), JSON.stringify({ VO_START, TOTAL, ...c }, null, 1));
console.log(`wrote index.html  total=${TOTAL}s  tweens=${tl.length}  captions=${caps.length}  shots=${nShot}  sfx=${audio.length}${DRAFT ? `  DRAFT (empty slots: ${missing.length})` : ""}`);
