#!/usr/bin/env python3
"""Single-frame pops and black segments in a rendered film (SKILL.md 8.3 and 8.4).

    python3 tools/pops.py film.mp4 [--black 0.08] [--save lumadiff.npy]

A pop is a frame whose luma change from the previous frame is over 6 levels (of 255) and over three times the
change on either side: something flashed for one frame. Designed cuts and bursts also show here, so compare each
pop with the beat sheet's marked cuts. Black segments of --black seconds or longer always fail.
Exit code 1 when there is a black segment. Needs numpy, ffmpeg and ffprobe.
"""
import argparse
import re
import subprocess
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('film')
    ap.add_argument('--black', type=float, default=0.08, help='shortest black segment to report, in seconds')
    ap.add_argument('--save', help='write the per-frame luma change as a .npy array')
    args = ap.parse_args()
    rate = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                           '-of', 'csv=p=0', args.film], capture_output=True, text=True).stdout.strip()
    num, den = (rate.split('/') + ['1'])[:2]
    fps = float(num) / float(den)
    w, h = 480, 270
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', args.film, '-vf', f'scale={w}:{h},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)
    d = np.abs(np.diff(y, axis=0)).mean(axis=(1, 2))
    pops = []
    for i in range(1, len(d) - 1):
        around = max(d[i - 1], d[i + 1], 0.5)
        if d[i] > 6 and d[i] > 3 * around:
            pops.append((round((i + 1) / fps, 2), round(float(d[i]), 1), round(float(around), 1)))
    print(f'{len(y)} frames at {fps:g} fps; largest change {d.max():.1f} levels at {(int(d.argmax()) + 1) / fps:.2f} s')
    print('single-frame pops (time s, change, around):', pops if pops else 'none')
    log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', args.film, '-vf', f'blackdetect=d={args.black}:pix_th=0.10',
                          '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
    black = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', log)
    print(f'black segments of {args.black:g} s or longer:', [f'{a}-{b} s' for a, b in black] if black else 'none')
    if args.save:
        np.save(args.save, d)
    sys.exit(1 if black else 0)


if __name__ == '__main__':
    main()
