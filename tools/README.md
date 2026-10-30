# Sizzle tools

The checks behind `SKILL.md`, as small command-line tools. Copy the ones a film needs into its project's `tools/` folder. Each prints a short report and exits with code 1 when a check fails, so a build script can stop on it.

| Tool | Checks | Skill section |
| --- | --- | --- |
| `audit-hook.js` | Records every string and image the canvas draws, cut to masks, clips and covers | 6.4 |
| `lint.mjs` | Copy, type size, reading time, collisions, safe area, photo scale, optional contrast | 6.4 |
| `motion.mjs` | Starts from rest and sudden speed changes outside marked bursts and cuts | 8.3 |
| `pops.py` | Single-frame pops and black segments in the rendered film | 8.3, 8.4 |
| `tts.py` | Voices a line with the configured text-to-speech provider and logs the request | 0.2, 5 |
| `voice_words.py` | Word timing, level, voicing and pitch of each take; emphasis checks; spectrograms | 5.3 |
| `vo_over_bed.py` | Voice over music and effects, line by line | 7.2 |
| `asr_check.py` | Speech recognition on the final mix against the script | 8.4 |
| `extend_score.py` | Lengthens or rearranges a score by whole bars, with clean joins | 5.2 |
| `fixture.html` | A five-second page with known problems, to try the page contract and the audit tools | |

## Requirements

- Node.js 18 or later with Playwright for `lint.mjs` and `motion.mjs` (`npm i playwright`; or set `NODE_PATH` or `PLAYWRIGHT_MODULE` to an existing install).
- Python 3.9 or later. `tts.py` needs only the standard library. The audio tools need numpy, soundfile, librosa, pyloudnorm and faster-whisper, and matplotlib for spectrograms.
- ffmpeg and ffprobe.

## The page contract

The composition is one HTML page that draws frame `t` (in seconds) as a pure function of `t`. The tools need three functions on `window`:

```js
window.renderAt = async t => { await ready; drawFrame(t); return canvas.toDataURL('image/png'); };
window.auditAt  = async t => { await ready; return auditFrame(drawFrame, t); };   // from audit-hook.js
window.getMarks = () => [[t0, t1], ...];   // bursts and cuts, where a fast start is the design
```

Load `audit-hook.js` (or paste it in), call `auditInstall(ctx, W, H)` once, and mark what the viewer cannot see:

```js
ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.clip(); auditClip(x, y, r);   // every circular clip ...
ctx.restore(); auditUnclip();                                        // ... and its restore
auditMask(x0, y0, x1, y1); drawText(...); auditUnmask();             // a masked reveal's text
ctx.fillRect(0, 0, W, H); auditCover(ctx.globalAlpha);               // an opaque full-frame field
```

The hook does nothing unless the URL contains `audit`, so renders are untouched. `fixture.html` shows all of it in about fifty lines.

## Layout and motion

```sh
python3 -m http.server 8768 --bind 127.0.0.1 --directory web &      # note the PID; stop it by PID
node tools/lint.mjs "http://127.0.0.1:8768/index.html?audit=1" 47.5 --rules edit/lint-rules.json --json work/lint.json
node tools/motion.mjs "http://127.0.0.1:8768/index.html?audit=1" 47.5 --skip "person-" --json work/motion.json
```

- `lint.mjs` judges a string only while it is settled (the same box for three frames, fully opaque), and follows a run while its box drifts less than 2 px a frame.
  - Reading time: 0.3 s a word plus 0.5 s.
  - Size by role: story lines 72 px, other read strings 36 px, fine print 24 px.
  - Safe area: 5 per cent of each edge.
  - Photos: never drawn above 1.5 times their source pixels.
- The rules file names the brief's exceptions, the role of each string and, optionally, the exact on-screen copy:

  ```json
  { "exceptions": { "THIS WEEK": "ornamental kicker, repeats the spoken line" },
    "roles": { "Open late on Fridays.": "story", "THIS WEEK": "fine" },
    "copy": ["Open late on Fridays.", "THIS WEEK"] }
  ```

- `--contrast` estimates each string's contrast from its rendered box, comparing the darkest and lightest 5 per cent of its pixels. Antialiased small type reads low, so confirm any flag by eye.
- `--from` and `--to` limit either tool to a time range, for checking a revision.
- `motion.mjs` skips masked reveals, full-frame layers and any image source matching `--skip` (swarms such as a crowd of icons, which are judged by eye). Marked windows come from `window.getMarks()`, or from `--marks marks.json`.

## Voice

The text-to-speech provider is the user's choice. Set it in the environment the agent's shell inherits. Keys belong in environment variables only: not in project files, `.env` files or chat.

| Provider | `SIZZLE_TTS_PROVIDER` | Keys | `SIZZLE_TTS_VOICE` |
| --- | --- | --- | --- |
| ElevenLabs | `elevenlabs` | `ELEVENLABS_API_KEY` | a voice ID |
| OpenAI, or a compatible endpoint | `openai` | `OPENAI_API_KEY`; `OPENAI_BASE_URL` for another endpoint | a voice name |
| Azure AI Speech | `azure` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | a voice name such as `en-US-AvaMultilingualNeural` |
| Google Cloud Text-to-Speech | `google` | `GOOGLE_API_KEY` | a voice name such as `en-US-Chirp3-HD-Aoede` |
| Any local engine or command line | `command` | `SIZZLE_TTS_COMMAND` | whatever the command expects |

`SIZZLE_TTS_MODEL` picks a model where the provider has one. `--style` passes a style instruction to OpenAI or a style name to Azure.

```sh
python3 tools/tts.py --check                                    # what is set; never prints a key
python3 tools/tts.py "Fridays, the library stays open late." takes/L1.wav --takes 4
python3 tools/tts.py --lines edit/lines.json --dir takes/ --takes 4   # [{"id": "L1", "text": "..."}]
```

For `command`, `SIZZLE_TTS_COMMAND` is a command line with `{out}` and, optionally, `{text}`, `{text_file}` and `{voice}`. It runs without a shell. Without `{text}` or `{text_file}`, the text goes to standard input. `SIZZLE_TTS_COMMAND_EXT` names the format it writes (default `.wav`). **`SIZZLE_TTS_COMMAND` is trusted configuration:** it runs on your machine with your privileges, so set it only in your own environment, never from a project file, a script someone sent you, or text you did not write. The command is killed after `SIZZLE_TTS_COMMAND_TIMEOUT` seconds (default 120; `--command-timeout` overrides). For example:

```sh
SIZZLE_TTS_COMMAND='say -v {voice} -f {text_file} -o {out}' SIZZLE_TTS_COMMAND_EXT=.aiff   # macOS
SIZZLE_TTS_COMMAND='espeak-ng -v {voice} -f {text_file} -w {out}'                           # eSpeak NG
SIZZLE_TTS_COMMAND='piper --model {voice} --output_file {out}'                              # Piper, text on stdin
SIZZLE_TTS_COMMAND='aws polly synthesize-speech --engine neural --output-format mp3 --voice-id {voice} --text {text} {out}' SIZZLE_TTS_COMMAND_EXT=.mp3
```

With `--lines`, each `id` becomes a file name inside `--dir`, so it must be a plain name: ids containing `/`, `\`, `..`, an absolute path or a NUL byte are refused before any request is made. Existing files are overwritten by default; pass `--no-overwrite` to refuse instead.

Each take is one request, and the tool never retries on its own: a repeated request spends credits again. A provider that returns the same audio for the same text gives one distinct take, so vary the punctuation or the style instead. Every request is appended to `generation-log.jsonl` beside the output (or `--log`), without the key.

Then measure every take:

```sh
python3 tools/voice_words.py takes/L1_t*.wav --emphasis late --json work/takes.json --spectrogram work/L1.png --from 1.5 --to 4
```

The report lists each word's start, end, peak level, share of voiced frames and pitch against the take's median, and flags words under 35 per cent voiced (`whisper?`). Some flags are only unvoiced consonants, so check them on the spectrogram: harmonics mean voiced, and formants over noise mean breath. An emphasis word passes with a pause of 0.3 s or more before it, a peak 3 semitones or more over the median, a level at or above the line's, and its voicing.

For a bass voice, add `--fmin 40`: its falls dip under the default 60 Hz pitch floor and read as unvoiced. The longer analysis frame this needs blurs short words, so judge those on the spectrogram.

## Mix and delivery

```sh
python3 tools/vo_over_bed.py --edit edit/edit.json --voice audio/stem_voice.wav --music audio/stem_music.wav --fx audio/stem_fx.wav
python3 tools/pops.py out/v3/film.mp4
python3 tools/asr_check.py out/v3/film.mp4 out/v3/script.txt --variants edit/name-variants.json
```

- `vo_over_bed.py` reads the voice lines from `edit.json` as `{"vo": [{"id": "L1", "start": 0.5, "words": [[0.0, 0.42, "Fridays"], ...]}]}`, with word times relative to the line's start. The gate is 8 LU.
- `pops.py` lists frames that flash for one frame and fails on black segments of 0.08 s or longer. Designed cuts appear as pops too, so compare them with the beat sheet.
- `asr_check.py` aligns letters, not words, so "follow-ups" heard as "follow ups" still counts. Names the recognizer spells another way go in the variants file. The gate is 97 per cent. Whisper can end a long file's window early after a music gap and skip the speech that follows; when the full pass misses words, the tool hears the film again in 30 s windows every 15 s and counts a word that either pass heard.

## Score

```sh
python3 tools/extend_score.py music/score.wav music/score_long.wav --segments "0:5.876,1.8187:5.876,5.876:end" --snap --markers edit/markers.json
```

Segments are source ranges in seconds, cut at downbeats. Neighbors in the source join without a seam. Other joins sit 10 ms before the downbeat transient, with a 25 ms equal-power crossfade. `--snap` moves each seam to the strongest onset within 40 ms. The report gives each segment's place in the output and maps the markers, so later cues can move by the inserted length.
