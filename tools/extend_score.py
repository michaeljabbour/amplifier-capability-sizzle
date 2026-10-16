#!/usr/bin/env python3
"""Lengthen or rearrange a score by whole bars (SKILL.md 5.2).

    python3 tools/extend_score.py score.wav out.wav --segments "0:5.876,1.8187:5.876,5.876:end"
        [--snap] [--markers markers.json] [--json map.json]

Each segment is a range of the source in seconds ("end" for its end), played in order. Cut at downbeats, so
every segment is a whole number of bars: confirm the beat phase first, so beat one carries the strongest onsets.
Where one segment follows another in the source, they join without a seam. Otherwise the join sits 10 ms
before the downbeat transient with a 25 ms equal-power crossfade. --snap moves each seam to the strongest onset
within 40 ms and reports the change. To add a bar without a new kind of join, repeat a segment that already
follows itself. --markers maps source times to output times ({"turn": 6.373}), so later markers can be shifted
by the inserted length. Needs numpy and soundfile; librosa for --snap.
"""
import argparse
import json

import numpy as np
import soundfile as sf


def snap_time(y, sr, t, reach=0.040):
    import librosa
    mono = y.mean(axis=1) if y.ndim > 1 else y
    hop = 64
    env = librosa.onset.onset_strength(y=mono.astype(np.float32), sr=sr, hop_length=hop)
    i0, i1 = max(0, int((t - reach) * sr / hop)), min(len(env), int((t + reach) * sr / hop) + 1)
    return (i0 + int(np.argmax(env[i0:i1]))) * hop / sr if i1 > i0 else t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('score')
    ap.add_argument('out')
    ap.add_argument('--segments', required=True, help='comma-separated a:b source ranges in seconds')
    ap.add_argument('--snap', action='store_true')
    ap.add_argument('--markers')
    ap.add_argument('--json')
    args = ap.parse_args()
    y, sr = sf.read(args.score, always_2d=True)
    total = len(y) / sr
    segs = [[float(a), total if b == 'end' else float(b)] for a, b in (p.split(':') for p in args.segments.split(','))]
    if args.snap:
        for k in range(len(segs) - 1):
            if abs(segs[k][1] - segs[k + 1][0]) > 1e-6:
                for side, idx in ((k, 1), (k + 1, 0)):
                    old = segs[side][idx]
                    segs[side][idx] = round(snap_time(y, sr, old), 4)
                    if abs(segs[side][idx] - old) > 0.0005:
                        print(f'snapped {old:.4f} s to {segs[side][idx]:.4f} s')
    pre, h = int(0.010 * sr), int(0.0125 * sr)
    fade_out = np.cos(np.linspace(0, np.pi / 2, 2 * h))[:, None]
    fade_in = np.sin(np.linspace(0, np.pi / 2, 2 * h))[:, None]
    out = y[int(round(segs[0][0] * sr)):int(round(segs[0][1] * sr))].copy()
    starts = [0.0]
    for (a0, a1), (b0, b1) in zip(segs, segs[1:]):
        starts.append(len(out) / sr)
        ja, jb = int(round(a1 * sr)), int(round(b0 * sr))
        if ja == jb:
            out = np.concatenate([out, y[jb:int(round(b1 * sr))]])
            continue
        if ja - pre - h < 0 or jb - pre - h < 0 or ja - pre + h > len(y):
            raise SystemExit(f'join at {a1} s / {b0} s is too close to the edge of the source')
        xf = y[ja - pre - h:ja - pre + h] * fade_out + y[jb - pre - h:jb - pre + h] * fade_in
        out = np.concatenate([out[:len(out) - pre - h], xf, y[jb - pre + h:int(round(b1 * sr))]])
    sf.write(args.out, out, sr, subtype=sf.info(args.score).subtype)
    length = len(out) / sr
    print(f'{args.out}: {length:.3f} s from {total:.3f} s ({length - total:+.3f} s)')
    table = []
    for (a, b), s in zip(segs, starts):
        table.append({'out_from': round(s, 4), 'out_to': round(s + b - a, 4), 'source_from': a, 'source_to': b})
        print(f'  out {s:8.3f} - {s + b - a:8.3f}   source {a:8.3f} - {b:8.3f}')
    mapped = {}
    if args.markers:
        for name, t in json.load(open(args.markers)).items():
            mapped[name] = [round(r['out_from'] + t - r['source_from'], 4) for r in table if r['source_from'] <= t < r['source_to']]
            print(f'  marker {name}: source {t} s -> output {mapped[name]} s')
    if args.json:
        with open(args.json, 'w') as fh:
            json.dump({'length': round(length, 4), 'inserted': round(length - total, 4), 'segments': table, 'markers': mapped}, fh, indent=1)


if __name__ == '__main__':
    main()
