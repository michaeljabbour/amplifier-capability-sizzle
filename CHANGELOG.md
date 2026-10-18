# Changelog

## Unreleased

- Add the storyboard gate (`SKILL.md` 4.1, `references/storyboard.md`): within minutes of the brief, a person sees the whole film as an overview card and one sketched card per frame, with two or three questions, and nothing is generated or rendered until they approve it. It works in any host: a native canvas, a self-contained HTML page (`references/storyboard-template.html`), or Markdown tables. The approval is recorded in `BRIEF.md`, and any later script change reopens it.
- Add the lessons of a film that passed every technical gate and was still rejected: state the product's purpose in plain words; write for viewers with no insider knowledge, around one everyday example; teach first when the product is a way of thinking, with contrasting cases, a predict-then-reveal pause, transfer and a takeaway; define terms on screen; let motion explain rather than decorate; check storyboard sketches for doodles on text.
- The skill bundle now carries every file in `references/`, not only Markdown.

## 0.1.1 (2026-10-16)

- Open the homepage with a 60-second reel made with Sizzle, in the order the skill sets out, and audited with its own tools. It ships with captions, a poster and a 15-second cut, and [docs/REEL.md](docs/REEL.md) tells how it was made and what each check measured.
- `tools/voice_words.py --fmin`: a bass voice's falls dip under the default 60 Hz pitch floor and read as unvoiced; `--fmin 40` measures them.
- `tools/asr_check.py`: when Whisper's full pass skips speech after a long music gap, a second pass hears the film in 30 s windows and counts a word that either pass heard.
- The site check covers video posters and caption files, and fails on metadata inside MP4 files.

## 0.1.0 (2026-10-16)

- Publish the `sizzle` skill with the lessons of its sixth production round: keep the word that must land out of the last, unstressed place; confirm breathy voice on a spectrogram; teach the layout audit about masks, clips and covers; follow drifting strings; give the motion audit its marked windows; never double-expose a wipe or an iris; keep random sequences stable across versions; lengthen a score by whole bars; deliver a director's transcript on request.
- Make the text-to-speech provider configurable: `tools/tts.py` speaks to ElevenLabs, OpenAI or a compatible endpoint, Azure AI Speech, Google Cloud Text-to-Speech, or any local engine or command line. Keys come only from environment variables.
- Add the tools the skill names: the audit hook, the layout lint, the motion audit, pops and black segments, word-level voice measurement with spectrograms, voice over the bed, speech recognition against the script, whole-bar score extension, and a fixture page with known problems.
- Move the client-note history to `references/lessons.md`, and describe the two source productions without client or personal names.
- Add a static site with an invented film whose audit runs in the browser, built and checked with Python's standard library and published with GitHub Pages.

Sizzle grew out of an earlier kinetic brand film skill, which it replaces.
