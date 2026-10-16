// Render carousel perkenalan @titikheran: 1080x1350 PNG per slide.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2];
const TOTAL = 7;

const css = `
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1350px; }
body {
  font-family: 'Inter Display', 'Inter', 'Noto Color Emoji', sans-serif;
  background: #0E1726; color: #F4F1E8; overflow:hidden; position:relative;
}
.bg-dots { position:absolute; inset:0;
  background-image: radial-gradient(rgba(255,200,61,0.10) 2.5px, transparent 2.5px);
  background-size: 54px 54px; }
.glow { position:absolute; width:900px; height:900px; border-radius:50%;
  background: radial-gradient(circle, rgba(255,200,61,0.22), transparent 65%); }
.wrap { position:absolute; inset:0; padding:96px 92px; display:flex; flex-direction:column; }
.top { display:flex; justify-content:space-between; align-items:center; font-size:30px; font-weight:600; letter-spacing:0.5px; }
.brand { display:flex; align-items:center; gap:14px; }
.dot { width:22px; height:22px; border-radius:50%; background:#FFC83D; box-shadow:0 0 24px rgba(255,200,61,.7); }
.page { color: rgba(244,241,232,.55); font-weight:500; }
.kicker { display:inline-block; font-size:30px; font-weight:700; letter-spacing:3px; text-transform:uppercase;
  color:#0E1726; background:#FFC83D; padding:10px 22px; border-radius:10px; align-self:flex-start; }
h1 { font-weight:900; line-height:1.02; letter-spacing:-2px; }
h2 { font-weight:800; line-height:1.08; letter-spacing:-1.5px; font-size:84px; }
p { font-size:44px; line-height:1.38; font-weight:400; color:rgba(244,241,232,.88); }
.y { color:#FFC83D; }
.bottom { margin-top:auto; display:flex; justify-content:space-between; align-items:center; font-size:28px; color:rgba(244,241,232,.6); font-weight:500; }
.swipe { display:flex; align-items:center; gap:12px; color:#FFC83D; font-weight:700; }
.card { background: rgba(255,255,255,0.06); border:1.5px solid rgba(255,255,255,0.12); border-radius:28px; padding:34px 38px; }
.card .tag { font-size:24px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#FFC83D; margin-bottom:10px; }
.card .t { font-size:40px; font-weight:800; line-height:1.15; letter-spacing:-0.5px; }
.card .d { font-size:30px; line-height:1.35; color:rgba(244,241,232,.75); margin-top:10px; }
.big-num { font-size:220px; font-weight:900; line-height:.9; letter-spacing:-8px; color:#FFC83D; }
`;

const top = (n) => `<div class="top"><div class="brand"><div class="dot"></div>@titikheran</div><div class="page">${n}/${TOTAL}</div></div>`;
const bottom = (left, swipe = true) => `<div class="bottom"><div>${left}</div>${swipe ? '<div class="swipe">Geser <span style="font-size:36px">&rarr;</span></div>' : ''}</div>`;

const slides = [
// 1. Cover
`<div class="bg-dots"></div><div class="glow" style="right:-300px;top:-250px"></div>
<div class="wrap">${top(1)}
  <div style="margin-top:150px">
    <div class="kicker">Halo, kenalan dulu</div>
    <h1 style="font-size:150px;margin-top:44px">Titik<br>Heran<span class="y">.</span></h1>
    <p style="font-size:50px;margin-top:44px;font-weight:600;color:#F4F1E8;max-width:860px">Tempatnya fakta yang bikin kamu bilang <span class="y">&ldquo;Hah, serius?&rdquo;</span></p>
  </div>
  ${bottom('Fakta unik dunia &amp; Indonesia')}
</div>`,

// 2. Siapa kami
`<div class="bg-dots"></div><div class="glow" style="left:-450px;bottom:-400px"></div>
<div class="wrap">${top(2)}
  <div style="margin:auto 0;padding-bottom:40px">
    <div class="kicker">Siapa kami</div>
    <h2 style="margin-top:40px">Kenapa namanya <span class="y">Titik Heran</span>?</h2>
    <p style="margin-top:44px">Karena setiap fakta punya satu titik: detik ketika kamu berhenti scroll, mengernyitkan dahi, lalu berpikir, <b style="color:#F4F1E8">&ldquo;kok bisa?&rdquo;</b></p>
    <p style="margin-top:34px">Di sini kami mengumpulkan titik-titik itu. Pengetahuan umum yang jarang orang tahu, dirangkum jadi video <b class="y">30 detik</b>.</p>
  </div>
  ${bottom('Satu fakta, satu titik heran')}
</div>`,

// 3. Misi
`<div class="bg-dots"></div><div class="glow" style="right:-400px;bottom:-350px"></div>
<div class="wrap">${top(3)}
  <div style="margin:auto 0;padding-bottom:40px">
    <div class="kicker">Misi kami</div>
    <h2 style="margin-top:40px">Bikin rasa penasaran jadi <span class="y">kebiasaan</span>.</h2>
    <p style="margin-top:44px">Belajar tidak harus berat. Cukup 30 detik untuk tahu sesuatu yang baru tentang alam, sejarah, sains, dan manusia.</p>
    <p style="margin-top:34px">Kami ingin kamu menutup aplikasi dengan satu cerita baru yang seru untuk diceritakan ke teman.</p>
  </div>
  ${bottom('Singkat. Seru. Bikin mikir.')}
</div>`,

// 4. Ide 1: selang-seling
`<div class="bg-dots"></div><div class="glow" style="left:-350px;top:-350px"></div>
<div class="wrap">${top(4)}
  <div style="margin-top:80px">
    <div class="kicker">Ide #1</div>
    <h2 style="margin-top:36px">Keliling dunia, lalu <span class="y">pulang ke Indonesia</span>.</h2>
    <p style="margin-top:30px;font-size:36px">Fakta kami selang-seling: satu dari luar negeri, satu dari Nusantara.</p>
    <div style="display:flex;flex-direction:column;gap:24px;margin-top:44px">
      <div class="card"><div class="tag">🌍 Luar negeri</div><div class="t">Hiu Greenland diperkirakan bisa hidup sekitar 400 tahun</div><div class="d">Umurnya dihitung lewat lensa mata.</div></div>
      <div class="card"><div class="tag">🇮🇩 Indonesia</div><div class="t">Limpa Suku Bajau sekitar 50% lebih besar</div><div class="d">Terkait gen, membantu mereka menyelam lama.</div></div>
    </div>
  </div>
  ${bottom('Contoh dari video kami')}
</div>`,

// 5. Ide 2: Indonesia sehebat itu
`<div class="bg-dots"></div><div class="glow" style="right:-350px;top:-300px"></div>
<div class="wrap">${top(5)}
  <div style="margin-top:80px">
    <div class="kicker">Ide #2</div>
    <h2 style="margin-top:36px">Indonesia ternyata <span class="y">sekeren itu</span>.</h2>
    <div style="display:flex;flex-direction:column;gap:22px;margin-top:48px">
      <div class="card" style="display:flex;gap:30px;align-items:center"><div style="font-size:64px;font-weight:900;color:#FFC83D;min-width:250px;letter-spacing:-2px">67.800</div><div><div class="t" style="font-size:34px">tahun, usia minimal cap tangan di gua Pulau Muna</div></div></div>
      <div class="card" style="display:flex;gap:30px;align-items:center"><div style="font-size:64px;font-weight:900;color:#FFC83D;min-width:250px;letter-spacing:-2px">74.000</div><div><div class="t" style="font-size:34px">tahun lalu, letusan super yang membentuk Danau Toba</div></div></div>
      <div class="card" style="display:flex;gap:30px;align-items:center"><div style="font-size:64px;font-weight:900;color:#FFC83D;min-width:250px;letter-spacing:-2px">1997</div><div><div class="t" style="font-size:34px">ikan purba coelacanth &ldquo;ditemukan&rdquo; di pasar Manado</div></div></div>
    </div>
  </div>
  ${bottom('Banyak yang belum kita tahu')}
</div>`,

// 6. Ide 3: jujur & bersumber
`<div class="bg-dots"></div><div class="glow" style="left:-400px;bottom:-400px"></div>
<div class="wrap">${top(6)}
  <div style="margin:auto 0;padding-bottom:40px">
    <div class="kicker">Ide #3</div>
    <h2 style="margin-top:40px">Heran boleh, <span class="y">hoaks jangan</span>.</h2>
    <div style="display:flex;flex-direction:column;gap:30px;margin-top:52px">
      <p><b class="y">&#10003;</b>&nbsp; Setiap fakta dicek ke sumber tepercaya: jurnal ilmiah, lembaga riset, media kredibel.</p>
      <p><b class="y">&#10003;</b>&nbsp; Sumbernya selalu kami tulis di caption.</p>
      <p><b class="y">&#10003;</b>&nbsp; Angka yang masih perkiraan kami sebut perkiraan. Tidak dilebih-lebihkan.</p>
    </div>
  </div>
  ${bottom('Fakta dulu, viral belakangan')}
</div>`,

// 7. CTA
`<div class="bg-dots"></div><div class="glow" style="left:90px;top:200px"></div>
<div class="wrap">${top(7)}
  <div style="margin-top:120px;text-align:center;display:flex;flex-direction:column;align-items:center">
    <div class="dot" style="width:70px;height:70px;box-shadow:0 0 70px rgba(255,200,61,.8)"></div>
    <h2 style="margin-top:56px;font-size:96px">Siap dibikin <span class="y">heran</span> terus?</h2>
    <p style="margin-top:40px;max-width:900px">Follow <b style="color:#F4F1E8">@titikheran</b> dan simpan postingan ini</p>
    <div class="card" style="margin-top:56px;max-width:860px;text-align:left">
      <div class="tag">Kamu yang pilih</div>
      <div class="t">Fakta apa yang paling pengin kamu tahu? Tulis di komentar, bisa jadi video berikutnya!</div>
    </div>
  </div>
  ${bottom('@titikheran', false)}
</div>`,
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  for (let i = 0; i < slides.length; i++) {
    await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${slides[i]}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    const f = path.join(OUT, `titik-heran-perkenalan-${String(i + 1).padStart(2, '0')}.png`);
    await page.screenshot({ path: f });
    console.log(f);
  }
  await browser.close();
})();
