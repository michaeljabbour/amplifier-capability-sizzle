/* The invented film, drawn as a pure function of time, audited with the skill's own hook (assets/audit-hook.js),
   and linted in the browser with the rules of tools/lint.mjs and tools/motion.mjs. Plus honest copy buttons. */
'use strict';

const W = 1920, H = 1080, FPS = 30;
const film = document.getElementById('film');
const overlay = document.getElementById('film-audit');
const ctx = film.getContext('2d');
const octx = overlay.getContext('2d');
const slider = document.getElementById('film-time');
const clock = document.getElementById('film-clock');
const playButton = document.getElementById('film-play');
const overlayToggle = document.getElementById('film-overlay');
const cutButtons = [...document.querySelectorAll('[data-cut]')];
const C = { night: '#1C2420', paper: '#F4F1EA', ink: '#252823', light: '#E9B44C', glow: 'rgba(233, 180, 76, 0.16)' };
let data = { duration: 14, roles: {}, cuts: [] };
let cut = 'first', frameIndex = Number(slider.value), playing = false, startedAt = 0, startFrame = 0;
const cache = {};

AUDIT = [];               // the shipped hook records only when asked; this page always audits its film
auditInstall(ctx, W, H);

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const prog = (t, a, d) => clamp((t - a) / d);
const easeOut = x => 1 - Math.pow(1 - x, 3);
const easeInOut = x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const serif = px => `${px}px Georgia, "Times New Roman", serif`;

function text(s, x, y, px, color, align = 'center') {
  ctx.font = serif(px); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = color;
  ctx.fillText(s, x, y);
}

// A masked reveal: the line rises into place through a window and drops out of it.
function reveal(s, x, y, px, color, t, tIn, tOut, dIn = 0.3, dOut = 0.2) {
  if (t < tIn || t >= tOut + dOut) return;
  const up = easeOut(prog(t, tIn, dIn)), down = easeInOut(prog(t, tOut, dOut));
  ctx.font = serif(px);
  const w = ctx.measureText(s).width, x0 = x - w / 2 - 12, top = y - px * 1.02, bottom = y + px * 0.32;
  ctx.save(); ctx.beginPath(); ctx.rect(x0, top, w + 24, bottom - top); ctx.clip();
  auditMask(x0, top, x0 + w + 24, bottom);
  text(s, x, y + (1 - up) * px * 1.35 + down * px * 1.35, px, color);
  auditUnmask(); ctx.restore();
}

function windowLight(cx, cy, w, h, r) {
  const halo = ctx.createRadialGradient(cx, cy, Math.min(w, h) * 0.3, cx, cy, Math.max(w, h) * 1.1);
  halo.addColorStop(0, C.glow); halo.addColorStop(1, 'rgba(233, 180, 76, 0)');
  ctx.fillStyle = halo; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = C.light; ctx.beginPath(); ctx.roundRect(cx - w / 2, cy - h / 2, w, h, r); ctx.fill();
}

const WIN = { cx: 960, cy: 430, w: 560, h: 340 };
const END = { s: 'Fridays, open until midnight', y: 520, px: 84 };

function drawChecked(t) {
  reveal('Where do you go after nine?', 960, 500, 84, C.paper, t, 0.1, 2.85);
  ctx.font = serif(END.px);
  const stopX = 960 + ctx.measureText(END.s).width / 2 + 16, stopY = END.y - 9;
  if (t < 3.0) windowLight(960, 720, 32, 32, 16);
  else if (t < 11.05) {
    const k = easeInOut(prog(t, 3.0, 0.5));
    windowLight(960, 720 + (WIN.cy - 720) * k, 32 + (WIN.w - 32) * k, 32 + (WIN.h - 32) * k, 16 - 8 * k);
  } else {
    const k = easeInOut(prog(t, 11.05, 0.5));                  // the window closes into a dot that waits as the full stop
    const w = WIN.w + (18 - WIN.w) * Math.min(1, k * 1.6), h = WIN.h + (18 - WIN.h) * Math.min(1, k * 1.6);
    windowLight(WIN.cx + (stopX - WIN.cx) * k, WIN.cy + (stopY - WIN.cy) * k, w, h, Math.min(w, h) / 2);
  }
  reveal('The library stays open.', 960, 820, 84, C.paper, t, 3.5, 5.75);
  reveal('Study rooms.', 960, 455, 72, C.ink, t, 5.95, 7.5);
  reveal('Late coffee.', 960, 455, 72, C.ink, t, 7.75, 9.35);
  reveal('Quiet.', 960, 455, 72, C.ink, t, 9.6, 10.85);
  reveal(END.s, 960, END.y, END.px, C.paper, t, 11.55, 99);   // the line rises to meet its full stop
  if (t >= 12.0) {
    ctx.save(); ctx.globalAlpha = easeOut(prog(t, 12.0, 0.3));
    text('Anytown Library', 960, 640, 44, C.light);
    ctx.restore();
  }
}

function drawFirst(t) {
  if (t >= 0.6 && t < 1.6) text('Where do you go after nine?', 960, 500, 84, C.paper);
  if (t < 3.0) windowLight(960, 720, 32, 32, 16);
  else if (t < 10.0) windowLight(WIN.cx, WIN.cy, WIN.w, WIN.h, 8);        // snaps open, and later cuts away
  if (t >= 3.2) {
    const x = t < 5.3 ? 960 : 960 - (t - 5.3) * FPS * 50;             // jumps from a standstill into a slide
    if (x > -700) text('The library stays open.', x, 820, 84, C.paper);
  }
  if (t >= 6.0 && t < 6.9) text('Study rooms · Late coffee · Quiet', 960, 445, 30, C.ink);
  if (t >= 10.0) {
    text('Open until midnight.', 900, 520, 84, C.paper);
    text('Fridays', 1240, 548, 64, C.light, 'left');
    text('Anytown Library', 1895, 1055, 44, C.paper, 'right');
  }
}

function drawFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.fillStyle = C.night; ctx.fillRect(0, 0, W, H); auditCover(1);
  if (cut === 'checked') drawChecked(t); else drawFirst(t);
}

// ---------- the lint, as tools/lint.mjs and tools/motion.mjs apply it ----------
const MIN_PX = { story: 72, read: 36, fine: 24 };
const area = b => (b[2] - b[0]) * (b[3] - b[1]);
const overlap = (a, c) => Math.max(0, Math.min(a[2], c[2]) - Math.max(a[0], c[0])) * Math.max(0, Math.min(a[3], c[3]) - Math.max(a[1], c[1]));
const quote = s => `“${s}”`;
const wordsIn = n => ['', 'one word', 'two words', 'three words', 'four words', 'five words', 'six words', 'seven words'][n] || `${n} words`;

function audit() {
  const frames = [];
  const total = Math.round(data.duration * FPS);
  for (let f = 0; f < total; f++) frames.push(auditFrame(drawFrame, f / FPS));
  const same = (a, c) => a.s === c.s && a.box.every((v, i) => Math.abs(v - c.box[i]) <= 1);
  const near = (a, c, d) => a.every((v, i) => Math.abs(v - c[i]) <= d);
  const runs = []; let open = [];
  for (let f = 2; f < total; f++) {
    const alive = [];
    for (const r of frames[f]) {
      if (r.type !== 'text' || r.alpha < 0.9 || !r.s.trim()) continue;
      if (![frames[f - 1], frames[f - 2]].every(fr => fr.some(q => q.type === 'text' && same(q, r)))) continue;
      const o = open.find(q => q.run.s === r.s && q.f1 === f - 1 && near(q.box, r.box, 2) && !alive.includes(q));
      if (o) { o.run.f1 = f; o.run.px = Math.min(o.run.px, r.px); o.run.boxes.push([f, r.box]); o.f1 = f; o.box = r.box; alive.push(o); }
      else { const run = { s: r.s, f0: f, f1: f, px: r.px, boxes: [[f, r.box]] }; runs.push(run); alive.push({ run, f1: f, box: r.box }); }
    }
    open = alive;
  }
  const findings = [];
  const byText = new Map();
  for (const run of runs) byText.set(run.s, (byText.get(run.s) || []).concat([run]));
  for (const [s, list] of byText) {
    const words = s.trim().split(/\s+/).length, need = 0.3 * words + 0.5;
    const best = list.reduce((a, b) => (b.f1 - b.f0 > a.f1 - a.f0 ? b : a));
    const held = (best.f1 - best.f0 + 3) / FPS, role = data.roles[s] || 'read';
    const mid = (best.f0 + best.f1) / 2 / FPS;
    if (held < need) findings.push({ kind: 'READ', s, t: mid, msg: `${quote(s)} is readable for ${held.toFixed(1)} s; ${wordsIn(words)} need ${need.toFixed(1)} s.` });
    const px = Math.min(...list.map(r => r.px));
    if (px < MIN_PX[role] - 0.5) findings.push({ kind: 'SIZE', s, t: mid, msg: `${quote(s)} is ${Math.round(px)} px; a ${role === 'story' ? 'story line' : 'line to read'} needs ${MIN_PX[role]} px.` });
    for (const run of list) {
      const hit = run.boxes.find(([, b]) => b[0] < 0.05 * W || b[2] > 0.95 * W || b[1] < 0.05 * H || b[3] > 0.95 * H);
      if (hit) { findings.push({ kind: 'SAFE', s, t: hit[0] / FPS, msg: `${quote(s)} runs into the outer 5 per cent of the frame.` }); break; }
    }
  }
  const seen = new Set();
  for (let f = 2; f < total; f++) {
    const T = frames[f].filter(r => r.type === 'text' && r.alpha >= 0.9 && r.s.trim());
    for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
      const key = T[i].s + '|' + T[j].s;
      if (overlap(T[i].box, T[j].box) > 4 && !seen.has(key)) { seen.add(key); findings.push({ kind: 'HIT', s: T[i].s, also: T[j].s, t: f / FPS, msg: `${quote(T[i].s)} and ${quote(T[j].s)} overlap.` }); }
    }
  }
  // Motion: follow each element and flag a start from rest or a sudden change of speed.
  let tracks = [];
  const flagged = new Set();
  for (let f = 0; f < total; f++) {
    const next = [];
    for (const r of frames[f]) {
      if (r.alpha < 0.5 || r.masked || area(r.box) > 0.6 * W * H) continue;
      const id = r.type + ':' + (r.s || r.src), c = [(r.box[0] + r.box[2]) / 2, (r.box[1] + r.box[3]) / 2];
      let best = null, bd = 1e9;
      for (const q of tracks) { if (q.id !== id || q.f !== f - 1 || q.used) continue; const d = Math.hypot(q.c[0] - c[0], q.c[1] - c[1]); if (d < bd) { bd = d; best = q; } }
      if (best && bd < 220) {
        best.used = true;
        const v = [c[0] - best.c[0], c[1] - best.c[1]], sp = Math.hypot(...v), sp0 = Math.hypot(...best.v), dv = Math.hypot(v[0] - best.v[0], v[1] - best.v[1]);
        const fromRest = best.age >= 2 && sp0 < 2 && sp > 25;
        if ((fromRest || (best.age >= 2 && dv > 10)) && !flagged.has(id)) {
          flagged.add(id);
          findings.push({ kind: 'MOTION', s: r.s, t: f / FPS, msg: fromRest ? `${quote(r.s)} jumps from rest to ${Math.round(sp)} px a frame.` : `${quote(r.s)} changes speed by ${Math.round(dv)} px a frame.` });
        }
        next.push({ id, c, v, f, age: best.age + 1 });
      } else next.push({ id, c, v: [0, 0], f, age: 0 });
    }
    tracks = next;
  }
  findings.sort((a, b) => a.t - b.t);
  return { frames, findings, total };
}

function result() {
  if (!cache[cut]) cache[cut] = audit();
  return cache[cut];
}

// ---------- drawing a frame and what the audit sees in it ----------
function show(f) {
  const { frames, findings, total } = result();
  frameIndex = Math.max(0, Math.min(total - 1, Math.round(f)));
  const t = frameIndex / FPS;
  const seen = auditFrame(drawFrame, t);
  slider.value = String(frameIndex);
  clock.textContent = `${t.toFixed(2)} s`;
  slider.setAttribute('aria-valuetext', `${t.toFixed(2)} seconds`);
  octx.clearRect(0, 0, W, H);
  if (!overlayToggle.checked) return;
  octx.setLineDash([10, 10]); octx.lineWidth = 2; octx.strokeStyle = 'rgba(244, 241, 234, 0.45)';
  octx.strokeRect(0.05 * W, 0.05 * H, 0.9 * W, 0.9 * H);
  octx.setLineDash([]); octx.font = '30px Arial, Helvetica, sans-serif'; octx.textBaseline = 'bottom';
  octx.fillStyle = 'rgba(244, 241, 234, 0.7)'; octx.fillText('safe area', 0.05 * W + 8, 0.05 * H - 6);
  const flagged = new Map();
  for (const k of findings) for (const s of [k.s, k.also]) if (s) flagged.set(s, (flagged.get(s) || []).concat(k.kind));
  for (const r of seen) {
    if (r.type !== 'text') continue;
    const kinds = flagged.get(r.s), b = r.box;
    octx.lineWidth = kinds ? 4 : 2;
    octx.strokeStyle = kinds ? '#F07A4F' : 'rgba(150, 214, 190, 0.9)';
    octx.strokeRect(b[0] - 4, b[1] - 4, b[2] - b[0] + 8, b[3] - b[1] + 8);
    const label = `${Math.round(r.px)} px` + (kinds ? ' · ' + [...new Set(kinds)].join(' · ') : '');
    const size = Math.max(34, Math.round(11 * W / Math.max(1, overlay.clientWidth)));   // about 11 px on screen
    octx.font = `bold ${size}px Arial, Helvetica, sans-serif`;
    const lw = octx.measureText(label).width + size * 0.7, lh = size * 1.35;
    const ly = b[1] - 8 > lh + 8 ? b[1] - 8 : b[3] + lh + 12, lx = Math.max(4, Math.min(b[0] - 4, W - lw - 8));
    octx.fillStyle = kinds ? '#F07A4F' : 'rgba(150, 214, 190, 0.95)';
    octx.fillRect(lx, ly - lh, lw, lh);
    octx.fillStyle = '#1C2420'; octx.fillText(label, lx + size * 0.35, ly - size * 0.18);
  }
}

function renderPanel() {
  const { findings, total } = result();
  const info = data.cuts.find(c => c.id === cut) || { label: cut, summary: '', changes: [] };
  document.getElementById('film-stamp').textContent = info.label;
  document.getElementById('cut-summary').textContent = info.summary;
  document.getElementById('audit-count').textContent = findings.length
    ? `${findings.length} finding${findings.length > 1 ? 's' : ''} in ${total} frames` : `No findings in ${total} frames`;
  const list = document.getElementById('audit-findings');
  list.replaceChildren(...findings.map(k => {
    const li = document.createElement('li');
    const tag = document.createElement('span'); tag.className = 'finding-kind'; tag.textContent = k.kind;
    const msg = document.createElement('span'); msg.className = 'finding-text'; msg.textContent = k.msg;
    const go = document.createElement('button'); go.type = 'button'; go.className = 'finding-time';
    go.textContent = `${k.t.toFixed(2)} s`; go.setAttribute('aria-label', `Show the frame at ${k.t.toFixed(2)} seconds`);
    go.addEventListener('click', () => { pause(); show(k.t * FPS); });
    li.append(tag, msg, go);
    return li;
  }));
  const changes = document.getElementById('cut-changes');
  changes.hidden = !info.changes.length;
  document.getElementById('cut-change-list').replaceChildren(...info.changes.map(c => Object.assign(document.createElement('li'), { textContent: c })));
  for (const b of cutButtons) b.setAttribute('aria-pressed', String(b.dataset.cut === cut));
}

function pause() { playing = false; playButton.textContent = 'Play'; playButton.setAttribute('aria-pressed', 'false'); }
function tick(now) {
  if (!playing) return;
  const f = startFrame + (now - startedAt) / 1000 * FPS;
  if (f >= result().total - 1) { show(result().total - 1); pause(); return; }
  show(f);
  requestAnimationFrame(tick);
}
playButton.addEventListener('click', () => {
  if (playing) { pause(); return; }
  playing = true; playButton.textContent = 'Pause'; playButton.setAttribute('aria-pressed', 'true');
  startFrame = frameIndex >= result().total - 1 ? 0 : frameIndex; startedAt = performance.now();
  requestAnimationFrame(tick);
});
slider.addEventListener('input', () => { pause(); show(Number(slider.value)); });
overlayToggle.addEventListener('change', () => show(frameIndex));
cutButtons.forEach(b => b.addEventListener('click', () => { pause(); cut = b.dataset.cut; renderPanel(); show(frameIndex); }));

async function start() {
  try {
    const response = await fetch('./assets/film.json');
    if (!response.ok) throw new Error('film data unavailable');
    data = await response.json();
  } catch {
    document.getElementById('cut-summary').textContent = 'The film’s notes could not load, so every string is held to the 36 px rule. Preview the page over HTTP for the full audit.';
  }
  const ready = document.fonts ? document.fonts.ready : Promise.resolve();
  await ready;
  renderPanel();
  show(frameIndex);
}

// ---------- the source and copy buttons ----------
function openSkillSource() {
  if (location.hash === '#skill-source') document.querySelector('#skill-source').open = true;
}
window.addEventListener('hashchange', openSkillSource);
window.addEventListener('resize', () => show(frameIndex));
openSkillSource();

document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copy);
    const content = target instanceof HTMLTextAreaElement ? target.value : target.textContent;
    const status = document.getElementById(button.dataset.copy === 'skill-text' ? 'skill-copy-status' : 'copy-status');
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(content);
      status.textContent = button.dataset.copy === 'skill-text' ? 'SKILL.md copied.' : 'Starting prompt copied.';
    } catch {
      // Keep a manual path when a browser denies clipboard access. Do not claim success.
      if (target instanceof HTMLTextAreaElement) { target.focus(); target.select(); }
      else {
        const range = document.createRange(); range.selectNodeContents(target);
        const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      }
      status.textContent = 'Clipboard unavailable. The text is selected; use your browser’s Copy command.';
    }
  });
});

start();
