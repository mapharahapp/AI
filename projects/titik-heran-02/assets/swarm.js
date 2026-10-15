// swarm.js — the drawn layer of Titik Heran #2: moth swarms, wind, map pins, map camera and map labels.
// Everything here is a PURE FUNCTION OF COMPOSITION TIME: drawAll(t) clears and redraws from the tables that
// build.mjs writes into window.SWP (seeded at build time — no Math.random, no clocks, no state between frames),
// so any frame renders identically whether the renderer seeks forwards, backwards or straight to it.
// It is driven twice, on purpose: by a proxy tween's onUpdate on the main timeline, and by the runtime's
// "hf-seek" event. Both call drawAll with the same t; drawing twice is harmless.
(function () {
  const P = window.SWP, W = P.W, H = P.H;
  const cv = document.getElementById("swarm"), g = cv.getContext("2d");
  const MAP = document.getElementById("map"), MAPZ = document.getElementById("mapz");
  const PINS = P.pins.map((id) => document.getElementById(id));
  const GMASK = document.getElementById("g-mask"), GLINE = document.getElementById("g-line"), GHEAD = document.getElementById("g-head");
  const TAU = Math.PI * 2;
  const md = (a, n) => ((a % n) + n) % n;
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const sstep = (v) => { v = clamp(v, 0, 1); return v * v * (3 - 2 * v); };
  const EASE = {};
  const ease = (name) => EASE[name] || (EASE[name] = window.gsap.parseEase(name));

  // moth, top view, head up (-y); unit = half the wingspan. Wings are one path, mirrored, scaled in x to flap.
  const BODY = new Path2D("M0 -0.52 C0.08 -0.52 0.1 -0.36 0.09 -0.18 C0.11 0.12 0.08 0.44 0 0.6 C-0.08 0.44 -0.11 0.12 -0.09 -0.18 C-0.1 -0.36 -0.08 -0.52 0 -0.52Z");
  const WING = new Path2D("M0.07 -0.26 C0.3 -0.46 0.78 -0.42 1 -0.22 C0.94 -0.02 0.74 0.12 0.46 0.16 L0.08 0.06Z M0.08 0 C0.36 0.06 0.62 0.2 0.56 0.42 C0.5 0.58 0.26 0.62 0.12 0.44 C0.08 0.3 0.07 0.16 0.08 0Z");
  const ANT = new Path2D("M0.03 -0.5 Q0.12 -0.78 0.32 -0.9 M-0.03 -0.5 Q-0.12 -0.78 -0.32 -0.9");
  // Soft (out-of-focus) moths come from sprites blurred ONCE, on small canvases: a canvas `filter: blur()` per
  // draw call costs seconds per frame in the software rasterizer the renderer runs (measured: 22 s/frame).
  const NF = 8, SR = 64, SPR = {};
  function drawShape(c2, flap, fill, r) {
    c2.fillStyle = fill;
    c2.save(); c2.scale(flap, 1); c2.fill(WING); c2.scale(-1, 1); c2.fill(WING); c2.restore();
    c2.fill(BODY);
    if (r > 5) { c2.lineWidth = 0.05; c2.strokeStyle = fill; c2.stroke(ANT); }
  }
  function sprite(fill, lvl, fi) {
    const key = fill + "|" + lvl;
    if (!SPR[key]) {
      SPR[key] = [];
      for (let i = 0; i < NF; i++) {
        const pad = 10 + lvl * 9, size = 2 * (SR + pad), oc = document.createElement("canvas");
        oc.width = oc.height = size;
        const c2 = oc.getContext("2d");
        c2.filter = `blur(${lvl * 3}px)`;
        c2.translate(size / 2, size / 2); c2.scale(SR, SR);
        drawShape(c2, 0.16 + (0.84 * i) / (NF - 1), fill, SR);
        SPR[key].push(oc);
      }
    }
    return SPR[key][fi];
  }
  function moth(x, y, ang, size, flap, fill, alpha, blur) {
    if (alpha <= 0.01 || size <= 0.3 || x < -200 || x > W + 200 || y < -200 || y > H + 200) return;
    g.save();
    g.globalAlpha = Math.min(1, alpha);
    g.translate(x, y); g.rotate(ang);
    if (blur > 0.4) {
      // blur is in screen px at this size; pick the sprite whose relative softness is closest
      const lvl = blur / size * SR > 4.5 ? 2 : 1, spr = sprite(fill, lvl, Math.round(((flap - 0.16) / 0.84) * (NF - 1)));
      const k = size / SR; g.scale(k, k); g.drawImage(spr, -spr.width / 2, -spr.height / 2);
    } else {
      g.scale(size, size);
      drawShape(g, flap, fill, size);
    }
    g.restore();
  }
  const flapAt = (m, s) => 0.16 + 0.84 * Math.abs(Math.cos(TAU * m.fq * s + m.ph));
  const heading = (dx, dy) => Math.atan2(dy, dx) + Math.PI / 2;

  // ---------------------------------------------------------------- map camera (analytic, so pins + moths agree)
  function cam(t) {
    const K = P.cam;
    if (t < K[0].t0) return K[0].a;
    let seg = K[0];
    for (const k of K) if (k.t0 <= t) seg = k;
    if (t >= seg.t1) return seg.b;
    const e = ease(seg.ease)((t - seg.t0) / (seg.t1 - seg.t0));
    return { s: seg.a.s + (seg.b.s - seg.a.s) * e, x: seg.a.x + (seg.b.x - seg.a.x) * e, y: seg.a.y + (seg.b.y - seg.a.y) * e };
  }
  const toScreen = (C, mx, my) => [mx * C.s + C.x, my * C.s + C.y];
  const mapAlpha = () => +window.gsap.getProperty(MAP, "opacity") || 0;
  const R = P.route;   // quadratic bezier in map space: o -> q -> a
  const bez = (u) => { const v = 1 - u; return [v * v * R.o[0] + 2 * v * u * R.q[0] + u * u * R.a[0], v * v * R.o[1] + 2 * v * u * R.q[1] + u * u * R.a[1]]; };
  const bezT = (u) => [2 * (1 - u) * (R.q[0] - R.o[0]) + 2 * u * (R.a[0] - R.q[0]), 2 * (1 - u) * (R.q[1] - R.o[1]) + 2 * u * (R.a[1] - R.q[1])];

  // ---------------------------------------------------------------- scene modes
  const DRAW = {
    // a lit swarm drifting over a night city; positions wrap horizontally so density never thins (and s may be < 0)
    city(s, S, A) {
      // a dense swirl in front of the floodlit sails, then the drifting swarm over the whole sky
      for (const m of P.cityOrb) {
        const pos = (q) => {
          const th = m.w * q + m.p, rr = m.r + m.j * Math.sin(m.jw * q + m.p);
          const ox = rr * Math.cos(th), oy = rr * m.e * Math.sin(th), c = Math.cos(m.tilt), sn = Math.sin(m.tilt);
          return [S.oc[0] + ox * c - oy * sn, S.oc[1] + ox * sn + oy * c];
        };
        const [x, y] = pos(s), [x2, y2] = pos(s + 0.02);
        moth(x, y, heading(x2 - x, y2 - y), m.size, flapAt(m, s), S.fill, A * m.al, 0);
      }
      for (const m of P.city) {
        const pos = (q) => [md(m.x0 + m.vx * q + m.ax * Math.sin(m.wx * q + m.px) + 160, W + 320) - 160, m.y0 + m.vy * q + m.ay * Math.sin(m.wy * q + m.py)];
        const [x, y] = pos(s), [x2, y2] = pos(s + 0.02), [gx, gy] = pos(s - 0.04);
        let dx = x2 - x; if (Math.abs(dx) > 400) dx = m.vx;
        const ang = heading(dx, y2 - y), fl = flapAt(m, s);
        if (Math.abs(gx - x) < 300) moth(gx, gy, ang, m.size, fl, m.f || S.fill, A * m.al * 0.26, m.blur);
        moth(x, y, ang, m.size, fl, m.f || S.fill, A * m.al, m.blur);
      }
    },
    // stars in the black around a studio shot; they flare on the word "bintang"
    twinkle(s, S, A, t) {
      const f = t < S.flare ? 0 : clamp((t - S.flare) / 0.14, 0, 1) * Math.exp(-(t - S.flare) / 0.7);
      for (const st of P.stars) {
        const a = A * clamp(st.a * (0.62 + 0.38 * Math.sin(st.w * s + st.p)) * (1 + 1.5 * f), 0, 1);
        if (a < 0.02) continue;
        g.globalAlpha = a * 0.28; g.fillStyle = "#cfe0ff";
        g.beginPath(); g.arc(st.x, st.y, st.r * (3 + 2.5 * f), 0, TAU); g.fill();
        g.globalAlpha = a; g.fillStyle = "#ffffff";
        g.beginPath(); g.arc(st.x, st.y, st.r * (1 + 0.5 * f), 0, TAU); g.fill();
      }
      g.globalAlpha = 1;
    },
    // map: a stream of moths leaves the breeding plains along the route and settles at the mountains
    route(s, S, A, t) {
      const C = cam(t), a = A * mapAlpha(); if (a < 0.01) return;
      const sz = S.size * Math.sqrt(C.s);
      for (const m of P.routeM) {
        const u = clamp((s - m.d) / S.T, 0, 1); if (u <= 0) continue;
        const [bx, by] = bez(u), [tx, ty] = bezT(u), n = Math.hypot(tx, ty) || 1;
        const arr = sstep((s - m.d - S.T) / 0.5);                  // 0 while flying, 1 once settled
        const off = m.j * Math.sin(m.w * s + m.p) * (1 - arr);
        const mx = bx - (ty / n) * off + arr * m.cr * Math.cos(m.cw * s + m.p), my = by + (tx / n) * off + arr * m.cr * Math.sin(m.cw * s + m.p);
        const [x, y] = toScreen(C, mx, my);
        const ang = arr < 1 ? heading(tx, ty) + 0.35 * Math.sin(m.w * 1.7 * s) : m.cw * s + m.p + Math.PI;
        moth(x, y, ang, sz * m.k, flapAt(m, s), S.fill, a * m.al, 0);
      }
    },
    // map: the stream again, then wind pushes every moth east to the coast round Sydney
    wind(s, S, A, t) {
      const C = cam(t), a = A * mapAlpha(); if (a < 0.01) return;
      const we = clamp((t - S.w0) / 0.3, 0, 1) * clamp((S.w1 - t) / 0.3, 0, 1);
      if (we > 0) {
        g.save(); g.lineCap = "round";
        for (const k of P.streaks) {
          // head runs right and down (a north-west wind); the tail fades out behind it
          const x = md(k.x0 + k.v * s, W + 700) - 350, y = k.y0 + x * S.slope;
          const x0 = x - k.len, y0 = y - k.len * S.slope;
          const gr = g.createLinearGradient(x0, y0, x, y);
          gr.addColorStop(0, "rgba(220,235,255,0)"); gr.addColorStop(1, `rgba(220,235,255,${(k.al * we * a).toFixed(3)})`);
          g.strokeStyle = gr; g.lineWidth = k.wd;
          g.beginPath(); g.moveTo(x0, y0); g.lineTo(x, y); g.stroke();
        }
        g.restore();
      }
      const push = sstep((t - S.p0) / (S.p1 - S.p0));
      const sz = S.size * Math.sqrt(C.s);
      const sFreeze = Math.min(s, S.p0 - S.t0 + (S.s0 || 0));   // stop advancing along the route once the wind takes them
      for (const m of P.windM) {
        const u = md(sFreeze / S.T + m.o, 1);
        const [bx, by] = bez(u), [tx, ty] = bezT(u);
        const fx = m.tx + m.r * Math.cos(m.w * s + m.p), fy = m.ty + m.r * 0.7 * Math.sin(m.w * 1.3 * s + m.p);
        const e = clamp(push * m.lag, 0, 1) ** 1.2;
        const mx = bx + (fx - bx) * e, my = by + (fy - by) * e;
        const [x, y] = toScreen(C, mx, my);
        const ang = e > 0.02 && e < 0.98 ? heading(fx - bx, fy - by) : e >= 0.98 ? m.w * s + m.p + Math.PI / 2 : heading(tx, ty);
        const al = a * m.al * Math.max(Math.sin(Math.PI * u), Math.min(1, push * 2));
        moth(x, y, ang + 0.3 * Math.sin(m.w * 2 * s), sz * m.k, flapAt(m, s), S.fill, al, 0);
      }
    },
    // moths circling a city light, lit by it
    orbit(s, S, A) {
      g.save(); g.globalCompositeOperation = "lighter"; g.globalAlpha = A;
      const gr = g.createRadialGradient(S.cx, S.cy, 0, S.cx, S.cy, S.glow);
      gr.addColorStop(0, "rgba(255,226,170,0.42)"); gr.addColorStop(0.35, "rgba(255,210,150,0.14)"); gr.addColorStop(1, "rgba(255,210,150,0)");
      g.fillStyle = gr; g.fillRect(S.cx - S.glow, S.cy - S.glow, 2 * S.glow, 2 * S.glow); g.restore();
      for (const m of P.orbit) {
        const pos = (q) => {
          const th = m.w * q + m.p, rr = m.r + m.j * Math.sin(m.jw * q + m.p);
          const ox = rr * Math.cos(th), oy = rr * m.e * Math.sin(th), c = Math.cos(m.tilt), sn = Math.sin(m.tilt);
          return [S.cx + ox * c - oy * sn, S.cy + ox * sn + oy * c, Math.sin(th)];
        };
        const [x, y, dz] = pos(s), [x2, y2] = pos(s + 0.02);
        const near = 1 + 0.28 * dz * m.depth, lit = clamp(1.25 - Math.hypot(x - S.cx, y - S.cy) / (S.glow * 1.4), 0.35, 1);
        moth(x, y, heading(x2 - x, y2 - y), m.size * near, flapAt(m, s), S.fill, A * m.al * lit, m.blur);
      }
    },
    // dark silhouettes climbing into the Milky Way, shrinking with distance
    ascend(s, S, A) {
      const span = H + 300;
      for (const m of P.ascend) {
        const pos = (q) => [m.x0 + m.vx * q + m.ax * Math.sin(m.wx * q + m.px), H + 150 - md(m.y0 + m.vy * q, span)];
        const [x, y] = pos(s), [x2, y2] = pos(s + 0.02);
        if (y2 > y + 50) continue;   // the wrap frame
        const persp = 0.3 + 0.7 * clamp(y / H, 0, 1);
        moth(x, y, heading(x2 - x, y2 - y), m.size * persp, flapAt(m, s), S.fill, A * m.al * (0.45 + 0.55 * persp), 0);
      }
    },
    // a few moths flying past the camera into the dark of the cave
    cave(s, S, A) {
      for (const m of P.cave) {
        const p = md((s - m.tau) / m.D, 1), k = 1 / (1 + 5 * p);
        const fade = clamp(p / 0.08, 0, 1) * clamp((1 - p) / 0.3, 0, 1);
        const x = S.vx + m.sx * k, y = S.vy + m.sy * k;
        moth(x, y, heading(-m.sx, -m.sy), m.size * k, flapAt(m, s), S.fill, A * m.al * fade, m.blur * k);
      }
    },
    // map, close on Sydney: moths arrive from inland and crowd the dot
    converge(s, S, A, t) {
      const C = cam(t), a = A * mapAlpha(); if (a < 0.01) return;
      const [cx, cy] = toScreen(C, S.syd[0], S.syd[1]);
      for (const m of P.conv) {
        const p = clamp((t - (S.go + m.del)) / m.D, 0, 1); if (p <= 0) continue;
        const e = 1 - Math.pow(1 - p, 2.4);
        const th = m.th + m.spin * e + (p >= 1 ? m.w * (t - (S.go + m.del + m.D)) : 0);
        const r = m.d * (1 - e) + m.re * e;
        const pos = (th2, r2) => [cx + r2 * Math.cos(th2), cy + r2 * Math.sin(th2) * 0.8];
        const [x, y] = pos(th, r), [x2, y2] = pos(th + m.spin * 0.01 + (p >= 1 ? m.w * 0.02 : 0), r - (p < 1 ? (m.d - m.re) * 0.02 : 0));
        moth(x, y, heading(x2 - x, y2 - y), m.size, flapAt(m, s), S.fill, a * m.al, 0);
      }
    },
    // map labels at a fixed screen size, following the camera
    labels(s, S, A, t) {
      const C = cam(t), a = A * mapAlpha(); if (a < 0.01) return;
      g.save(); g.font = "800 30px Inter, sans-serif"; g.textBaseline = "middle"; g.letterSpacing = "3px"; g.lineJoin = "round";
      for (const L of P.labels) {
        if (t < L.t0 || t > L.t1) continue;
        const la = a * clamp((t - L.t0) / 0.25, 0, 1) * clamp((L.t1 - t) / 0.2, 0, 1); if (la < 0.01) continue;
        const [x, y] = toScreen(C, L.m[0], L.m[1]);
        g.globalAlpha = la; g.textAlign = L.al;
        g.lineWidth = 7; g.strokeStyle = "rgba(3,5,8,0.8)"; g.strokeText(L.txt, x + L.d[0], y + L.d[1]);
        g.fillStyle = L.c; g.fillText(L.txt, x + L.d[0], y + L.d[1]);
      }
      g.restore();
    },
  };

  function drawAll(t) {
    t = Math.max(0, +t || 0);
    // the map camera and its pins (constant screen size)
    const C = cam(t);
    MAPZ.style.transform = `translate(${C.x.toFixed(2)}px, ${C.y.toFixed(2)}px) scale(${C.s.toFixed(4)})`;
    for (const el of PINS) if (el) el.setAttribute("transform", `scale(${(1 / C.s).toFixed(4)})`);
    // the graph's line head follows its reveal (one source: the GR proxy the timeline tweens)
    if (GMASK && GLINE) {
      const len = Math.max(0, Math.min(P.graph.L, window.GR.len));
      GMASK.setAttribute("stroke-dashoffset", (P.graph.L - len).toFixed(1));
      const pt = GLINE.getPointAtLength(len);
      GHEAD.setAttribute("transform", `translate(${pt.x.toFixed(1)} ${pt.y.toFixed(1)})`);
    }
    g.clearRect(0, 0, W, H);
    for (const S of P.scenes) {
      if (t < S.t0 || t > S.t1) continue;
      let A = 1;
      if (S.fi) A *= clamp((t - S.t0) / S.fi, 0, 1);
      if (S.fo) A *= clamp((S.t1 - t) / S.fo, 0, 1);
      if (A <= 0) continue;
      DRAW[S.m](t - S.t0 + (S.s0 || 0), S, A, t);
    }
  }
  window.drawAll = drawAll;
  window.addEventListener("hf-seek", (e) => { try { drawAll(e.detail.time); } catch (err) { console.error(err); } });
})();
