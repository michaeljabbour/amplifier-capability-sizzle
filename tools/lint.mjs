// Sizzle layout lint (SKILL.md 6.4): audit every frame of a composition, then check copy, type size,
// reading time, collisions, safe area and photo scale (and, with --contrast, an estimate of contrast).
//
//   node tools/lint.mjs <url> <seconds> [--fps 30] [--size 1920x1080] [--rules rules.json]
//                       [--from s] [--to s] [--contrast] [--canvas css-selector] [--json report.json]
//
// <url> is the composition opened with ?audit=1 (for example http://127.0.0.1:8768/index.html?audit=1).
// The page must expose window.auditAt(t), as tools/audit-hook.js describes.
// rules.json (all keys optional):
//   { "exceptions": { "<string or image file>": "reason from the brief" },
//     "roles": { "<string>": "story" | "read" | "fine" },      // minimum size 72, 36 or 24 px; default "read"
//     "copy": [ "<every on-screen string, exactly as drawn>" ] }  // anything else drawn is a COPY issue
// A plain { "<string>": "reason" } object is read as exceptions. Exit code 1 when issues remain.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);

const argv = process.argv.slice(2), pos = [], opt = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { const k = argv[i].slice(2); opt[k] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true; }
  else pos.push(argv[i]);
}
const [url, durS] = pos;
if (!url || !durS) { console.error('usage: node tools/lint.mjs <url?audit=1> <seconds> [--fps 30] [--size 1920x1080] [--rules rules.json] [--from s] [--to s] [--contrast] [--json report.json]'); process.exit(2); }
let chromium;
try { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')); }
catch { console.error('Playwright is not installed here. Run "npm i playwright", or point NODE_PATH or PLAYWRIGHT_MODULE at it.'); process.exit(2); }

const FPS = parseFloat(opt.fps || 30);
const [W, H] = String(opt.size || '1920x1080').split('x').map(Number);
const F0 = Math.round(parseFloat(opt.from || 0) * FPS), N = Math.round(parseFloat(opt.to || durS) * FPS);
let rules = opt.rules ? JSON.parse(fs.readFileSync(opt.rules, 'utf8')) : {};
if (!rules.exceptions && !rules.roles && !rules.copy) rules = { exceptions: rules };
const EXC = rules.exceptions || {}, ROLE = rules.roles || {}, COPY = rules.copy ? new Set(rules.copy) : null;
const MIN_PX = { story: 72, read: 36, fine: 24 };

const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
const errors = []; page.on('pageerror', e => errors.push(e.message));
await page.goto(url, { waitUntil: 'load' });
if (!(await page.evaluate(() => typeof window.auditAt === 'function'))) { console.error('The page has no window.auditAt(t). See tools/audit-hook.js.'); process.exit(2); }

// Sample every frame, in batches to keep round trips low.
const frames = [];
for (let f = F0; f < N; f += 30) {
  const ts = []; for (let g = f; g < Math.min(N, f + 30); g++) ts.push(g / FPS);
  frames.push(...await page.evaluate(async ts => { const out = []; for (const t of ts) out.push(await window.auditAt(t)); return out; }, ts));
}
const at = f => frames[f - F0];

// Settled runs: the same string with the same box (within 1 px) for three frames, fully opaque.
// A run follows its string while the box drifts less than 2 px a frame, so a slow camera push stays one run.
const same = (a, c) => a.s === c.s && a.box.every((v, i) => Math.abs(v - c.box[i]) <= 1);
const near = (a, c, d) => a.every((v, i) => Math.abs(v - c[i]) <= d);
const runs = new Map(); let open = [];
for (let f = F0 + 2; f < N; f++) {
  const alive = [];
  for (const r of at(f)) {
    if (r.type !== 'text' || r.alpha < 0.9 || !r.s.trim()) continue;
    if (![at(f - 1), at(f - 2)].every(fr => fr.some(q => q.type === 'text' && same(q, r)))) continue;
    const o = open.find(q => q.s === r.s && q.f1 === f - 1 && near(q.box, r.box, 2) && !alive.includes(q));
    if (o) { const run = runs.get(o.id); run.f1 = f; run.px = Math.min(run.px, r.px); run.boxes.push(r.box); o.f1 = f; o.box = r.box; alive.push(o); }
    else { const id = r.s + '|' + r.box.map(Math.round).join(',') + '|' + f; runs.set(id, { s: r.s, f0: f, f1: f, px: r.px, boxes: [r.box] }); alive.push({ id, s: r.s, f1: f, box: r.box }); }
  }
  open = alive;
}

const issues = [], excused = [];
const push = (kind, key, msg) => (EXC[key] ? excused : issues).push({ kind, key, msg: `${kind.padEnd(8)}${msg}` + (EXC[key] ? `   [exception: ${EXC[key]}]` : '') });
const q = s => JSON.stringify(s);
const byText = new Map();
for (const run of runs.values()) byText.set(run.s, (byText.get(run.s) || []).concat([run]));
for (const [s, list] of byText) {
  const words = s.trim().split(/\s+/).length, need = 0.3 * words + 0.5;
  const held = Math.max(...list.map(r => (r.f1 - r.f0 + 3) / FPS));   // +3: the two frames it took to settle, plus this one
  const px = Math.min(...list.map(r => r.px)), role = ROLE[s] || 'read';
  if (COPY && !COPY.has(s)) push('COPY', s, `${q(s)} is drawn but is not in the on-screen copy`);
  if (held < need) push('READ', s, `${q(s)} held ${held.toFixed(2)} s, needs ${need.toFixed(2)} s`);
  if (px < MIN_PX[role] - 0.5) push('SIZE', s, `${q(s)} ${px.toFixed(0)} px, needs ${MIN_PX[role]} px as ${role}`);
  const out = list.flatMap(r => r.boxes).find(b => b[0] < 0.05 * W || b[2] > 0.95 * W || b[1] < 0.05 * H || b[3] > 0.95 * H);
  if (out) push('SAFE', s, `${q(s)} box ${out.map(v => v.toFixed(0)).join(',')} leaves the 5 per cent safe area`);
}

// Collisions between opaque strings, strings over photos and icons (not full-frame layers), and enlarged photos.
const area = b => (b[2] - b[0]) * (b[3] - b[1]);
const ov = (a, c) => Math.max(0, Math.min(a[2], c[2]) - Math.max(a[0], c[0])) * Math.max(0, Math.min(a[3], c[3]) - Math.max(a[1], c[1]));
const name = src => (src || 'canvas').split('/').pop();
const seen = new Set(), once = (k, fn) => { if (!seen.has(k)) { seen.add(k); fn(); } };
for (let f = F0 + 2; f < N; f++) {
  const T = at(f).filter(r => r.type === 'text' && r.alpha >= 0.9 && r.s.trim());
  const I = at(f).filter(r => r.type === 'image' && r.alpha >= 0.5 && area(r.box) < 0.5 * W * H);
  const t = (f / FPS).toFixed(2);
  for (let i = 0; i < T.length; i++) {
    for (let j = i + 1; j < T.length; j++) if (ov(T[i].box, T[j].box) > 4) once('HIT' + T[i].s + '|' + T[j].s, () => push('HIT', T[i].s, `${q(T[i].s)} overlaps ${q(T[j].s)} at ${t} s`));
    for (const im of I) if (ov(T[i].box, im.box) > 0.02 * area(T[i].box)) once('OVER' + T[i].s + '|' + im.src, () => push('OVER', T[i].s, `${q(T[i].s)} over image ${name(im.src)} at ${t} s`));
  }
  for (const im of at(f)) if (im.type === 'image' && im.scale > 1.5 && (im.box[2] - im.box[0]) < W) once('PHOTO' + im.src, () => push('PHOTO', name(im.src), `${name(im.src)} drawn at ${im.scale.toFixed(2)}x its source at ${t} s`));
}

// Optional contrast estimate: at the middle of each run, compare the darkest and lightest 5 per cent of the
// pixels in the string's box. Antialiased small type reads low; confirm any flag by eye.
if (opt.contrast) {
  const sel = typeof opt.canvas === 'string' ? opt.canvas : 'canvas';
  for (const run of runs.values()) {
    const f = Math.round((run.f0 + run.f1) / 2), b = run.boxes[Math.floor(run.boxes.length / 2)];
    const ratio = await page.evaluate(async ([t, b, sel]) => {
      await window.auditAt(t);
      const c = document.querySelector(sel), g = c.getContext('2d');
      const x0 = Math.max(0, Math.floor(b[0])), y0 = Math.max(0, Math.floor(b[1])), x1 = Math.min(c.width, Math.ceil(b[2])), y1 = Math.min(c.height, Math.ceil(b[3]));
      if (x1 - x0 < 2 || y1 - y0 < 2) return null;
      const d = g.getImageData(x0, y0, x1 - x0, y1 - y0).data, L = [];
      const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      for (let i = 0; i < d.length; i += 4) L.push(0.2126 * lin(d[i]) + 0.7152 * lin(d[i + 1]) + 0.0722 * lin(d[i + 2]));
      L.sort((a, c) => a - c);
      const lo = L[Math.floor(0.05 * (L.length - 1))], hi = L[Math.floor(0.95 * (L.length - 1))];
      return (hi + 0.05) / (lo + 0.05);
    }, [f / FPS, b, sel]);
    if (ratio !== null && ratio < 4.5) push('CONTRAST', run.s, `${q(run.s)} about ${ratio.toFixed(1)}:1 at ${(f / FPS).toFixed(2)} s, needs 4.5:1`);
  }
}
await browser.close();

console.log(`lint: ${N - F0} frames, ${byText.size} strings (${runs.size} placements), ${issues.length} issues, ${excused.length} exceptions` + (errors.length ? `, page errors: ${errors.join(' | ')}` : ''));
for (const i of issues) console.log('  ' + i.msg);
for (const i of excused) console.log('  ' + i.msg);
if (opt.json) fs.writeFileSync(opt.json, JSON.stringify({ frames: N - F0, strings: byText.size, placements: runs.size, issues, exceptions: excused, pageErrors: errors }, null, 1));
process.exit(issues.length || errors.length ? 1 : 0);
