/* Sizzle layout audit hook (SKILL.md 6.4).
 *
 * Records every string and image the canvas draws, with its size and on-screen box, and
 * resolves each frame against what the viewer can actually see: masked reveals, circular
 * clips (wipes, irises) and opaque fields that cover what lies under them.
 *
 * Use it in the composition page, after the canvas context exists. Paste it inline, or load it
 * as a classic script before your drawing code:
 *
 *   const ctx = canvas.getContext('2d');
 *   auditInstall(ctx, W, H);
 *   ...
 *   ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.clip(); auditClip(x, y, r);   // beside every circular clip
 *   ctx.restore(); auditUnclip();                                        // and beside its restore
 *   auditMask(x0, y0, x1, y1); text(...); auditUnmask();                 // around a masked reveal's text
 *   ctx.fillRect(0, 0, W, H); auditCover(ctx.globalAlpha);               // after an opaque full-frame fill
 *   ...
 *   window.auditAt = async t => { await ready; return auditFrame(drawFrame, t); };
 *   window.getMarks = () => [[t0, t1], ...];   // bursts and cuts, for tools/motion.mjs
 *
 * The hook stays inert unless the page URL contains "audit" (index.html?audit=1), so renders
 * are untouched. Give offscreen canvases an id, so photos can be told apart from texture.
 */
var AUDIT = (typeof location !== 'undefined' && location.search.includes('audit')) ? [] : null;
var AUD_CLIPS = [], AUD_RECT = null, auditBox = null, AUD_W = 1920, AUD_H = 1080;

function auditClip(x, y, r) { if (AUDIT) AUD_CLIPS.push([x, y, r]); }
function auditUnclip() { if (AUDIT) AUD_CLIPS.pop(); }
function auditCover(alpha) {
  // An opaque field hides what was drawn under it. Inside a clip, it covers only the clip's circle.
  if (AUDIT && alpha >= 0.9) AUDIT.push({ type: 'cover', c: AUD_CLIPS.length ? AUD_CLIPS.slice() : [[AUD_W / 2, AUD_H / 2, 1e6]] });
}
function auditMask(x0, y0, x1, y1) { if (AUDIT && auditBox) AUD_RECT = auditBox(x0, y0, x1, y1); }   // in the current transform
function auditUnmask() { AUD_RECT = null; }

function auditInstall(ctx, width, height) {
  AUD_W = width || ctx.canvas.width; AUD_H = height || ctx.canvas.height;
  if (!AUDIT) return;
  const fillText = ctx.fillText.bind(ctx), drawImage = ctx.drawImage.bind(ctx);
  // Axis-aligned box of a rectangle under the current transform.
  const box = (x0, y0, x1, y1) => {
    const m = ctx.getTransform();
    const p = [[x0, y0], [x1, y0], [x0, y1], [x1, y1]].map(([x, y]) => [m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f]);
    const xs = p.map(q => q[0]), ys = p.map(q => q[1]);
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  };
  ctx.fillText = function (s, x, y, ...rest) {
    const k = this.measureText(s), m = this.getTransform();
    const px = parseFloat(/([\d.]+)px/.exec(this.font)[1]) * Math.hypot(m.a, m.b);
    AUDIT.push({ type: 'text', s: String(s), px, alpha: this.globalAlpha, clips: AUD_CLIPS.slice(), rect: AUD_RECT,
      box: box(x - k.actualBoundingBoxLeft, y - k.actualBoundingBoxAscent, x + k.actualBoundingBoxRight, y + k.actualBoundingBoxDescent) });
    return fillText(s, x, y, ...rest);
  };
  ctx.drawImage = function (img, ...a) {
    const natural = img.naturalWidth || img.videoWidth || img.width;
    const [dx, dy, dw, dh] = a.length >= 8 ? a.slice(4) : a.length === 4 ? a : [a[0], a[1], natural, img.naturalHeight || img.videoHeight || img.height];
    const b = box(dx, dy, dx + dw, dy + dh), sw = a.length >= 8 ? a[2] : natural;
    AUDIT.push({ type: 'image', src: img.currentSrc || img.src || img.id || 'canvas', alpha: this.globalAlpha,
      clips: AUD_CLIPS.slice(), rect: AUD_RECT, box: b, scale: (b[2] - b[0]) / sw });
    return drawImage(img, ...a);
  };
  auditBox = box;
}

// What the viewer can see: each box cut to its mask and clips, dropped if nothing is left
// or if a later opaque field covers it completely.
function auditResolve(list) {
  const out = [];
  const isect = (b, r) => [Math.max(b[0], r[0]), Math.max(b[1], r[1]), Math.min(b[2], r[2]), Math.min(b[3], r[3])];
  const inside = (b, c) => [[b[0], b[1]], [b[2], b[1]], [b[0], b[3]], [b[2], b[3]]].every(([x, y]) => Math.hypot(x - c[0], y - c[1]) <= c[2]);
  list.forEach((e, i) => {
    if (e.type === 'cover') return;
    let b = e.box;
    if (e.rect) b = isect(b, e.rect);
    for (const c of e.clips || []) b = isect(b, [c[0] - c[2], c[1] - c[2], c[0] + c[2], c[1] + c[2]]);
    if (b[2] - b[0] < 1 || b[3] - b[1] < 1) return;
    if (list.slice(i + 1).some(q => q.type === 'cover' && q.c.every(c => inside(b, c)))) return;
    out.push({ type: e.type, s: e.s, src: e.src, px: e.px, alpha: e.alpha, scale: e.scale, masked: !!e.rect, box: b });
  });
  return out;
}

// One audited frame: clear the record, draw frame t, return what the viewer sees.
function auditFrame(drawFrame, t) {
  if (!AUDIT) throw new Error('Open the page with ?audit=1 to audit it.');
  AUDIT.length = 0; AUD_CLIPS = []; AUD_RECT = null;
  drawFrame(t);
  return auditResolve(AUDIT);
}
