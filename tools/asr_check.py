#!/usr/bin/env python3
"""Speech recognition on the final mix against the script (SKILL.md 8.4): every scripted word, in order.

    python3 tools/asr_check.py film.mp4 script.txt [--variants variants.json] [--prompt "Names."]
        [--model small.en] [--gate 0.97]

script.txt is the voice script as plain text. Lines starting with # or ( are skipped (notes and directions),
and so are [bracketed] marks and (parenthesized) asides. The check aligns letters rather than words, so "Sunflower" heard as "Sun Flower"
or "follow-ups" as "follow ups" still counts. A scripted word is recognized when at least three quarters of
its letters line up. variants.json maps a scripted spelling to what the recognizer may write instead, for names:
{"zylo": ["xylo", "zilo"]}. Exit code 1 when the recognized share is under the gate (97 per cent).
Whisper decodes a long file window by window and can end a window early, skipping the speech after a long
music gap. When the full pass misses words, a second pass hears the film in 30 s windows every 15 s, each
word judged by the window it sits in the middle of; a word counts when either pass heard it.
Needs numpy, ffmpeg and faster-whisper.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import warnings

import numpy as np

warnings.filterwarnings('ignore')


def letters(word):
    return re.sub(r'[^a-z0-9]', '', word.lower())


def script_words(text):
    keep = [ln for ln in text.splitlines() if not re.sub(r'^\s*\[[^\]]*\]', '', ln).lstrip().startswith(('#', '('))]
    text = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', '\n'.join(keep))
    return [w for w in re.split(r'[\s\-–—/]+', text) if letters(w)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('film')
    ap.add_argument('script')
    ap.add_argument('--variants')
    ap.add_argument('--prompt', default='')
    ap.add_argument('--model', default='small.en')
    ap.add_argument('--gate', type=float, default=0.97)
    args = ap.parse_args()
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', args.film, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device='cpu', compute_type='int8')
    audio = np.frombuffer(raw, np.float32)
    variants = json.load(open(args.variants)) if args.variants else {}
    swap = {letters(v): letters(k) for k, vs in variants.items() for v in vs}
    want = script_words(open(args.script, encoding='utf-8').read())
    a = ''.join(letters(w) for w in want)

    def hits(heard):
        got = [swap.get(letters(w), letters(w)) for w in re.split(r'[\s\-]+', ' '.join(heard)) if letters(w)]
        h = np.zeros(len(a), bool)
        for block in difflib.SequenceMatcher(a=a, b=''.join(got), autojunk=False).get_matching_blocks():
            h[block.a:block.a + block.size] = True
        return h

    def listen(x, offset=0.0):
        segs, _ = model.transcribe(x, word_timestamps=True, language='en', initial_prompt=args.prompt or None, vad_filter=False)
        return [(offset + w.start, w.word.strip()) for s in segs for w in (s.words or [])]

    words = listen(audio)
    heard = [w for _, w in words]
    hit = hits(heard)
    if not all(hit[i:i + len(letters(w))].mean() >= 0.75 for i, w in zip(np.cumsum([0] + [len(letters(w)) for w in want])[:-1], want)):
        sr, W, H = 16000, 30.0, 15.0
        dur = len(audio) / sr
        second = []
        for s0 in np.arange(0.0, max(dur - W, 0.0) + H, H):
            lo = 0.0 if s0 == 0 else s0 + (W - H) / 2
            hi = dur if s0 + W >= dur else s0 + (W + H) / 2
            second += [(t, w) for t, w in listen(audio[int(s0 * sr):int((s0 + W) * sr)], s0) if lo <= t < hi]
        second.sort()
        hit |= hits([w for _, w in second])
        print('second pass (30 s windows):', ' '.join(w for _, w in second))
    missing, i = [], 0
    for w in want:
        n = len(letters(w))
        if hit[i:i + n].mean() < 0.75:
            missing.append(w)
        i += n
    share = 1 - len(missing) / max(1, len(want))
    print('heard:', ' '.join(heard))
    print(f'scripted words {len(want)}, recognized {len(want) - len(missing)} ({share:.1%}), gate {args.gate:.0%}')
    print('not recognized:', missing if missing else 'none')
    sys.exit(0 if share >= args.gate else 1)


if __name__ == '__main__':
    main()
