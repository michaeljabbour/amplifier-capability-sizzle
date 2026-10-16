#!/usr/bin/env python3
"""Voice over the bed, line by line (SKILL.md 7.2): the voice stem's loudness minus music plus effects, in LU.

    python3 tools/vo_over_bed.py --edit edit/edit.json --voice stem_voice.wav --music stem_music.wav
        [--fx stem_fx.wav] [--gate 8] [--json report.json]

edit.json holds the voice lines as {"vo": [{"id": "L1", "start": 0.5, "words": [[a, b, "word"], ...]}, ...]},
with word times relative to the line's start. Each line is measured from its first word's start to its last
word's end. Run it after every change to the effects. Exit code 1 when any line is under the gate (8 LU).
Needs numpy, soundfile and pyloudnorm.
"""
import argparse
import json
import sys

import numpy as np
import pyloudnorm as pyln
import soundfile as sf


def load(path, channels=None):
    y, sr = sf.read(path, always_2d=True)
    if channels and y.shape[1] != channels:
        y = np.repeat(y.mean(axis=1, keepdims=True), channels, axis=1)
    return y, sr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--edit', required=True)
    ap.add_argument('--voice', required=True)
    ap.add_argument('--music', required=True)
    ap.add_argument('--fx')
    ap.add_argument('--gate', type=float, default=8.0)
    ap.add_argument('--json')
    args = ap.parse_args()
    voice, sr = load(args.voice)
    bed, sr_m = load(args.music, voice.shape[1])
    if args.fx:
        fx, _ = load(args.fx, voice.shape[1])
        n = max(len(bed), len(fx))
        bed = np.pad(bed, ((0, n - len(bed)), (0, 0))) + np.pad(fx, ((0, n - len(fx)), (0, 0)))
    if sr_m != sr:
        sys.exit('The stems must share one sample rate.')
    n = max(len(voice), len(bed))
    voice, bed = np.pad(voice, ((0, n - len(voice)), (0, 0))), np.pad(bed, ((0, n - len(bed)), (0, 0)))
    meter = pyln.Meter(sr, block_size=0.2)
    rows = []
    for line in json.load(open(args.edit))['vo']:
        a, b = line['start'] + line['words'][0][0], line['start'] + line['words'][-1][1]
        i, j = int(a * sr), max(int(b * sr), int(a * sr) + int(0.4 * sr))
        lu = meter.integrated_loudness(voice[i:j]) - meter.integrated_loudness(bed[i:j])
        rows.append({'id': line['id'], 'from': round(a, 2), 'to': round(b, 2), 'lu': round(float(lu), 1)})
        print(f"{line['id']:<6}{a:7.2f}-{b:6.2f}  voice over bed {lu:5.1f} LU{'' if lu >= args.gate else '   under the gate'}")
    low = min(r['lu'] for r in rows)
    print(f'lowest {low:.1f} LU (gate {args.gate:g} LU)')
    if args.json:
        with open(args.json, 'w') as fh:
            json.dump(rows, fh, indent=1)
    sys.exit(0 if low >= args.gate else 1)


if __name__ == '__main__':
    main()
