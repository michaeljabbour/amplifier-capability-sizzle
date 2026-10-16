// Sizzle motion audit (SKILL.md 8.3): follow every drawn element from the layout audit and flag jerks
// outside the marked bursts and cuts.
//
//   node tools/motion.mjs <url> <seconds> [--fps 30] [--size 1920x1080] [--marks marks.json]
//                         [--skip regex] [--from s] [--to s] [--json report.json]
//
// <url> is the composition opened with ?audit=1. Marked windows, where a fast start is the design, come from
// window.getMarks() on the page ([[t0, t1], ...]) or from --marks (the same list, or [{"from":..,"to":..}]).
// --skip is a regular expression for image sources that move as a swarm (a crowd of icons): judge those by eye.
// A flag is a start from rest to more than 25 px a frame, or a change of speed of more than 10 px a frame
// between frames. Masked reveals and full-frame layers are skipped. Exit code 1 when anything is flagged.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);

const argv = process.argv.slice(2), pos = [], opt = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { const k = argv[i].slice(2); opt[k] = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true; }
  else pos.push(argv[i]);
}
const [url, durS] = pos;
if (!url || !durS) { console.error('usage: node tools/motion.mjs <url?audit=1> <seconds> [--fps 30] [--size 1920x1080] [--marks marks.json] [--skip regex] [--json report.json]'); process.exit(2); }
let chromium;
try { ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')); }
catch { console.error('Playwright is not installed here. Run "npm i playwright", or point NODE_PATH or PLAYWRIGHT_MODULE at it.'); process.exit(2); }

const FPS = parseFloat(opt.fps || 30);
const [W, H] = String(opt.size || '1920x1080').split('x').map(Number);
const F0 = Math.round(parseFloat(opt.from || 0) * FPS), N = Math.round(parseFloat(opt.to || durS) * FPS);
const SKIP = opt.skip ? new RegExp(opt.skip) : null;

const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.goto(url, { waitUntil: 'load' });
if (!(await page.evaluate(() => typeof window.auditAt === 'function'))) { console.error('The page has no window.auditAt(t). See tools/audit-hook.js.'); process.exit(2); }
let marks = opt.marks ? JSON.parse(fs.readFileSync(opt.marks, 'utf8'))
  : await page.evaluate(() => (typeof window.getMarks === 'function' ? window.getMarks() : []));
marks = (marks || []).map(m => Array.isArray(m) ? m : [m.from, m.to]);
const frames = [];
for (let f = F0; f < N; f += 30) {
  const ts = []; for (let g = f; g < Math.min(N, f + 30); g++) ts.push(g / FPS);
  frames.push(...await page.evaluate(async ts => { const out = []; for (const t of ts) out.push(await window.auditAt(t)); return out; }, ts));
}
await browser.close();

const marked = t => marks.some(([a, c]) => t >= a && t <= c);
const centre = b => [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2, b[2] - b[0]];
const idOf = r => r.type === 'text' ? 'text ' + JSON.stringify(r.s) : 'image ' + (r.src || 'canvas').split('/').pop();
let tracks = [];
const flags = new Map();
for (let f = F0; f < N; f++) {
  const t = f / FPS, next = [];
  for (const r of frames[f - F0]) {
    if (r.alpha < 0.5 || r.masked) continue;                                   // masked reveals are entrances by design
    if (r.type === 'image' && SKIP && SKIP.test(r.src || '')) continue;        // swarms: judged by eye
    if ((r.box[2] - r.box[0]) * (r.box[3] - r.box[1]) > 0.6 * W * H) continue; // full-frame layers
    const id = idOf(r), c = centre(r.box);
    let best = null, bd = 1e9;
    for (const q of tracks) {
      if (q.id !== id || q.f !== f - 1 || q.used) continue;
      const d = Math.hypot(q.last[0] - c[0], q.last[1] - c[1]);
      if (d < bd) { bd = d; best = q; }
    }
    if (best && bd < 220) {
      best.used = true;
      const v = [c[0] - best.last[0], c[1] - best.last[1]], sp = Math.hypot(...v), sp0 = Math.hypot(...best.v);
      const dv = Math.hypot(v[0] - best.v[0], v[1] - best.v[1]);
      const fromRest = best.age >= 2 && sp0 < 2 && sp > 25;                   // two frames of tracking first: entrances do not count
      if (!marked(t) && (fromRest || (best.age >= 2 && dv > 10))) {
        if (!flags.has(id)) flags.set(id, []);
        flags.get(id).push({ t: +t.toFixed(2), what: fromRest ? `from rest to ${sp.toFixed(0)} px/frame` : `speed change ${dv.toFixed(0)} px/frame` });
      }
      next.push({ id, last: c, v, f, age: best.age + 1 });
    } else next.push({ id, last: c, v: [0, 0], f, age: 0 });
  }
  tracks = next;
}
console.log(`motion audit: ${N - F0} frames, ${marks.length} marked windows, ${flags.size} elements flagged outside them`);
for (const [id, L] of flags) console.log(`  ${id}: ${L.length} frames, first ${L.slice(0, 4).map(x => `${x.t.toFixed(2)} s ${x.what}`).join('; ')}`);
if (opt.json) fs.writeFileSync(opt.json, JSON.stringify({ frames: N - F0, marks, flags: Object.fromEntries(flags) }, null, 1));
process.exit(flags.size ? 1 : 0);
