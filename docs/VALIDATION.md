# Local validation

Validation date: 2026-10-16. The checks ran in a cloud workspace with headless Chromium through Playwright, Python 3.13 and ffmpeg. They are an implementation review, not user research, a listening test or an accessibility certification.

## Build and file integrity

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check site/site.js
```

The integrity check covers local HTML links and fragments, shipped Markdown destinations, unique IDs, local CSS dependencies, the source textarea, the `SKILL.md` download and every file in the ZIP bundle, byte for byte. It also checks the skill contract (frontmatter keys, the name `sizzle`, a description under 1,024 characters, a body under 500 lines, and that every `tools/` and `references/` path the skill names exists) and scans every shipped text file for email addresses, home directory paths, credential-like strings and em dashes, and every image for embedded metadata. The page reads the creative gate and the technical gates from `SKILL.md`, and the tool and provider tables from `tools/README.md`, when it is built.

## The site in a browser

- The film's audit reports six findings in 420 frames on the first cut (two READ, one MOTION, one SIZE, one HIT, one SAFE) and none after the checks, with no page errors.
- Each finding's time control moves the film to that frame. The overlay draws the safe area and every string the hook records, with flagged strings marked.
- Frame sequences across every transition of the checked cut were inspected: the question, the turn into the window, the headline's exit, the three list moments and the window closing into the full stop. The light was changed to arrive before the last line rises, so it never crosses the type.
- Layouts at 320 × 800, 390 × 844, 768 × 1024 and 1384 × 1119: the document width matched the viewport each time. On phones the film stacks above the audit panel, and overlay labels are drawn at about 11 px on screen.
- Not done: a screen-reader session, a cross-browser suite, or testing the clipboard and downloads in a real browser. Reduced-motion rules and the no-JavaScript fallback were inspected in source.

## The tools

- `tools/fixture.html`: the lint reports the four planted problems (SIZE, READ, SAFE, HIT) and nothing for the masked reveal, the wipe, or the string the wipe covers. The motion audit flags only the dot that jumps from rest; the burst inside its marked window passes. With a rules file, a role excuses the fine print and the copy list catches the one string left out of it.
- A 66-second production film from the skill's sixth round, rendered earlier with the same rules: the new `lint.mjs` and `motion.mjs` reproduced that round's recorded results exactly (no issues and eight exceptions named in the brief; the same photo glides, at 10 to 13 px a frame of speed change). `pops.py` found no pops and no black segments, `vo_over_bed.py` reported the same lowest line at 8.5 LU, and `extend_score.py` rebuilt that round's score with the same length and sample differences under 0.0001.
- `asr_check.py` on the same film recognized 92 of 93 scripted words (98.9 per cent); the one miss was a name spelled differently, which a variants file covers. `voice_words.py` flagged the one breathy word the earlier measurements found, passed the emphasis word, and drew the spectrogram with the pitch track and word marks.
- `tts.py`: the `command` provider voiced lines with a local engine (ffmpeg's flite), wrote two takes and converted to MP3. Each HTTP provider (ElevenLabs, OpenAI, Azure, Google) was pointed at a local stand-in that accepted a request only with the right path, key header and body; all four were accepted, a wrong key produced a clear refusal with no retry, special characters were escaped in the Azure SSML, and the generation logs contained no keys. The live services were not called.

## Security scan

`make scan` installs the skill package into `.work/scan/` and runs [SkillSpector](https://github.com/NVIDIA/skillspector) on it with static analysis only, against the reviewed baseline in `.skillspector-baseline.yaml`. Scan the package, not the repository: the repository also holds `.git/`, the built site, the films and local caches, none of which a user installs, and they made up most of the findings when the whole folder was scanned.

- Result: 0 of 100, severity low, recommendation "caution" (SkillSpector 2.12.0). The caution is coverage: the scanner's parser stops at a function call inside a template-literal expression, so it inspects `tools/lint.mjs` and `tools/motion.mjs` only in part.
- Fixed: the description now names the checks the skill ships and where voice text is sent, and that it stops before generating any media; `references/demo-video.md` pins HyperFrames per video in a lockfile and runs it with `npx --no-install`, instead of fetching an unpinned version on each run.
- Accepted, each with its reason in the baseline: `subprocess` calls that pass an argument list with no shell; `tts.py` calling the voice provider the user configures, and running the local engine the user names in `SIZZLE_TTS_COMMAND`; the append-only generation log; and no `allowed-tools` field, which would only preapprove tools.
- Not run here: the scanner's LLM analyzers, which send the files to a model provider. A run with them reported description and behavior mismatches for the tools, which the new description answers, and English-only defaults in `asr_check.py` and `voice_words.py`, which are a limitation rather than a risk.

## Screenshots

The images show only the product page. They exclude browser chrome, addresses, desktop content and private files, and carry no metadata.

- [Desktop film and audit](screenshots/desktop-film.jpg)
- [Tablet](screenshots/tablet-film.jpg)
- [Phone](screenshots/phone-film.jpg)
- [Narrow phone](screenshots/narrow-film.jpg)

## Privacy review

Before publication, every source, documentation, tool and asset file was checked three ways: the integrity check's patterns (above); a search outside the repository for the names, places, products and events of the two productions the lessons come from, which are described here without them; and an independent read of every file and image by a reviewer who had not seen the work. Client names, real people's names, distinctive brand details, script lines, local paths, session identifiers and keys were removed or never written; the few single words still quoted from the productions are common words. The only personal identifier left is the GitHub account name in the repository and site addresses. Generated output, logs and test copies are excluded from Git.
