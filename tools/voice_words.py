#!/usr/bin/env python3
"""Measure voice takes word by word (SKILL.md 5.3): timing, level, voicing and pitch, with emphasis checks.

    python3 tools/voice_words.py take1.mp3 [take2.mp3 ...] [--prompt "Names. Terms."]
        [--emphasis yours,bigger] [--json takes.json] [--spectrogram takes.png] [--from s] [--to s] [--fmin 40]

For each take: Whisper word times (faster-whisper, fed a 16 kHz float array), and for each word its peak
level, the share of voiced frames (pYIN) and its pitch against the take's median. A mostly voiced word under
about 35 per cent voiced frames is a whisper. A bass voice whose falls dip under 60 Hz reads as unvoiced
there: pass --fmin 40, whose longer frame blurs short words (judge those on the spectrogram). pYIN also misses breathy and creaky voice, so --spectrogram
draws each take with its pitch track and word marks: harmonics mean voiced, formants over noise mean breath.
Whisper drifts by up to 0.2 s on short words, so the energy islands are listed too, for onsets.
--emphasis checks each named word: a pause of 0.3 s or more before it (measured on the energy islands, since
Whisper's word edges stretch across silence; a line's first word counts its lead-in), a peak 3 semitones or more over the
take's median, and a level at or above the rest of the line. A word that Whisper stretches across a silence
prints LISTEN: the pause cannot be measured, so judge it by ear. Exit code 1 when an emphasis check fails or
needs a listen.
Needs numpy, librosa and faster-whisper; matplotlib for --spectrogram.
"""
import argparse
import json
import re
import sys
import warnings

import numpy as np

warnings.filterwarnings('ignore')
SR, HOP = 24000, 240
FMIN = 60.0   # pitch floor for pYIN; --fmin lowers it for bass voices, whose falls dip under 60 Hz and read as unvoiced


def frame_len():
    return 1024 if FMIN >= 47 else 2048   # the longest period must fit the frame


def norm(word):
    return re.sub(r"[^a-z0-9']", '', word.lower())


def islands(db, vprob, sr, hop, floor=30.0, gap=0.035, shortest=0.03):
    """Speech segments: frames within `floor` dB of the take's peak, merged across gaps under `gap` s."""
    on = db > db.max() - floor
    t = np.arange(len(db)) * hop / sr
    segs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            if segs and (i - segs[-1][1]) * hop / sr < gap:
                segs[-1][1] = j
            else:
                segs.append([i, j])
            i = j
        else:
            i += 1
    return [(round(float(t[i]), 3), round(float(t[j - 1]), 3), round(float(db[i:j].max()), 1), round(float(np.mean(vprob[i:j] > 0.3)), 2))
            for i, j in segs if (j - i) * hop / sr >= shortest]


def pause_before(a, b, isl, snap=0.15):
    """Silence before a word Whisper places at a..b, measured on the energy islands, not on Whisper's edges.

    Whisper stretches words across silence and drifts by up to 0.2 s. The word's onset is the island it
    starts in (when it starts within `snap` s of that island's start) or the next island (when Whisper starts
    it in the silence before, or in the last 0.05 s of the speech before). A word that starts later inside an
    island runs on from the speech before it: no pause. A line's first word counts its lead-in. A quiet,
    unvoiced island (a breath) is part of the pause, not speech. When the word spans a silence of 0.3 s or
    more, Whisper cannot say which side it lies on: returns None, and the pause must be judged by ear."""
    top = max((q[2] for q in isl), default=0.0)
    isl = [q for q in isl if q[3] >= 0.1 or q[2] >= top - 10]
    for k in range(len(isl) - 1):
        if isl[k + 1][0] - isl[k][1] >= 0.3 and a < isl[k][1] - 0.05 and b > isl[k + 1][0] + 0.05 and a > isl[k][0] + snap:
            return None
    for k, (s0, e0, _, _) in enumerate(isl):
        if e0 <= a + 0.05:
            continue
        if s0 < a - snap:
            return 0.0
        return s0 - (isl[k - 1][1] if k else 0.0)
    return 0.0


def measure(path, model, prompt, emphasis):
    import librosa
    y, _ = librosa.load(path, sr=SR, mono=True)
    y16 = librosa.resample(y, orig_sr=SR, target_sr=16000).astype(np.float32)
    segments, _ = model.transcribe(y16, word_timestamps=True, language='en', initial_prompt=prompt or None, vad_filter=False)
    words = [(w.start, w.end, w.word.strip(), w.probability) for s in segments for w in (s.words or [])]
    f0, vflag, vprob = librosa.pyin(y, fmin=FMIN, fmax=1000, sr=SR, frame_length=frame_len(), hop_length=HOP)
    rms = librosa.feature.rms(y=y, frame_length=960, hop_length=HOP)[0]
    n = min(len(rms), len(f0))
    f0, vflag, vprob, db = f0[:n], vflag[:n], vprob[:n], 20 * np.log10(rms[:n] + 1e-9)
    t = np.arange(n) * HOP / SR
    med = float(np.nanmedian(f0)) if np.any(~np.isnan(f0)) else float('nan')
    rows = []
    for a, b, w, p in words:
        m = (t >= a) & (t <= b)
        if not m.any():
            continue
        loud = m & (db > db[m].max() - 20)
        fz = f0[loud]
        fz = fz[~np.isnan(fz)]
        rows.append({'w': w, 'a': round(a, 3), 'b': round(b, 3), 'p': round(p, 2), 'db': round(float(db[m].max()), 1),
                     'voiced': round(float(np.mean(vflag[loud])), 2) if loud.any() else 0.0,
                     'st': round(float(12 * np.log2(np.median(fz) / med)), 1) if len(fz) else None,
                     'peak_st': round(float(12 * np.log2(np.percentile(fz, 90) / med)), 1) if len(fz) else None})
    fall = rows[-1]['st'] if rows else None   # the last word's pitch against the take's median: a statement falls 2 st or more
    isl = islands(db, vprob, SR, HOP)
    checks = []
    for target in emphasis:
        for i, r in enumerate(rows):
            if not norm(r['w']).startswith(target):
                continue
            pause = pause_before(r['a'], r['b'], isl)
            others = [q['db'] for j, q in enumerate(rows) if j != i]
            level_ok = not others or r['db'] >= float(np.median(others))
            rest = (r['peak_st'] or -99) >= 3 and level_ok and r['voiced'] >= 0.35
            ok = rest and pause is not None and pause >= 0.3
            checks.append({'word': r['w'], 'at': r['a'], 'pause': None if pause is None else round(pause, 2), 'peak_st': r['peak_st'], 'db': r['db'],
                           'line_db': round(float(np.median(others)), 1) if others else None, 'voiced': r['voiced'], 'ok': bool(ok),
                           'listen': bool(rest and pause is None)})
    return {'dur': round(len(y) / SR, 3), 'f0_median': round(med, 1), 'final_fall_st': fall, 'words': rows,
            'islands': isl, 'emphasis': checks}


def spectrogram(paths, results, out, start, end):
    import librosa
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(paths), 1, figsize=(16, 3.2 * len(paths)), squeeze=False)
    for ax, path in zip(axes[:, 0], paths):
        a = start or 0.0
        y, _ = librosa.load(path, sr=SR, mono=True, offset=a, duration=(end - a) if end else None)
        b = a + len(y) / SR
        S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=1024, hop_length=120)), ref=np.max)
        top = int(4000 / (SR / 1024))
        ax.imshow(S[:top], origin='lower', aspect='auto', extent=[a, b, 0, top * SR / 1024], cmap='magma', vmin=-80, vmax=0)
        f0, _, _ = librosa.pyin(y, fmin=FMIN, fmax=1000, sr=SR, frame_length=frame_len(), hop_length=120)
        level = 20 * np.log10(librosa.feature.rms(y=y, frame_length=1024, hop_length=120)[0] + 1e-9)[:len(f0)]
        f0 = np.where(level[:len(f0)] > level.max() - 40, f0[:len(level)], np.nan)   # no pitch dots in silence
        ax.plot(a + np.arange(len(f0)) * 120 / SR, f0, 'c.', ms=2)
        for w in results[path]['words']:
            if a <= w['a'] <= b:
                ax.axvline(w['a'], color='w', lw=0.6)
                ax.text(w['a'] + 0.01, 3700, w['w'], color='w', fontsize=9)
        ax.set_ylim(0, 4000)
        ax.set_ylabel('Hz')
        ax.set_title(f"{path}  (cyan: pitch; harmonics above it mean voiced, formants over noise mean breath)", loc='left', fontsize=10)
    plt.tight_layout()
    plt.savefig(out, dpi=70)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('takes', nargs='+')
    ap.add_argument('--prompt', default='', help='names and terms to prime Whisper with')
    ap.add_argument('--emphasis', default='', help='comma-separated emphasis words (prefix match)')
    ap.add_argument('--model', default='small.en')
    ap.add_argument('--json')
    ap.add_argument('--spectrogram')
    ap.add_argument('--from', dest='start', type=float)
    ap.add_argument('--to', dest='end', type=float)
    ap.add_argument('--fmin', type=float, default=60.0, help='pitch floor in Hz (default 60; about 40 for a bass voice)')
    args = ap.parse_args()
    global FMIN
    FMIN = args.fmin
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device='cpu', compute_type='int8')
    emphasis = [norm(w) for w in args.emphasis.split(',') if norm(w)]
    results, failed = {}, False
    for path in args.takes:
        r = results[path] = measure(path, model, args.prompt, emphasis)
        print(f"== {path}  {r['dur']:.2f} s, median pitch {r['f0_median']:.0f} Hz, final fall {r['final_fall_st']} st")
        print(f"   {'word':<14}{'start':>7}{'end':>7}{'level':>8}{'voiced':>8}{'pitch':>7}")
        for w in r['words']:
            flag = '   whisper?' if w['voiced'] < 0.35 else ''
            st = '' if w['st'] is None else f"{w['st']:+.1f}"
            print(f"   {w['w'][:13]:<14}{w['a']:7.2f}{w['b']:7.2f}{w['db']:8.1f}{w['voiced']:8.2f}{st:>7}{flag}")
        for c in r['emphasis']:
            failed |= not c['ok']
            pause = 'unclear (the word spans a silence)' if c['pause'] is None else f"{c['pause']:.2f} s"
            verdict = 'ok' if c['ok'] else 'LISTEN' if c['listen'] else 'FAIL'
            print(f"   EMPHASIS {c['word']!r} at {c['at']:.2f}: pause {pause}, peak {c['peak_st']} st, level {c['db']} vs line {c['line_db']} dB, voiced {c['voiced']:.2f}  {verdict}")
        print('   islands: ' + '  '.join(f'{a:.2f}-{b:.2f}({p},v{v})' for a, b, p, v in r['islands']))
    if args.json:
        with open(args.json, 'w') as fh:
            json.dump(results, fh, indent=1)
    if args.spectrogram:
        spectrogram(args.takes, results, args.spectrogram, args.start, args.end)
        print('spectrogram:', args.spectrogram)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
