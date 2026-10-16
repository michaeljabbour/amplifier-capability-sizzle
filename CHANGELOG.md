# Changelog

## 0.1.0 (2026-10-16)

- Publish the `sizzle` skill with the lessons of its sixth production round: keep the word that must land out of the last, unstressed place; confirm breathy voice on a spectrogram; teach the layout audit about masks, clips and covers; follow drifting strings; give the motion audit its marked windows; never double-expose a wipe or an iris; keep random sequences stable across versions; lengthen a score by whole bars; deliver a director's transcript on request.
- Make the text-to-speech provider configurable: `tools/tts.py` speaks to ElevenLabs, OpenAI or a compatible endpoint, Azure AI Speech, Google Cloud Text-to-Speech, or any local engine or command line. Keys come only from environment variables.
- Add the tools the skill names: the audit hook, the layout lint, the motion audit, pops and black segments, word-level voice measurement with spectrograms, voice over the bed, speech recognition against the script, whole-bar score extension, and a fixture page with known problems.
- Move the client-note history to `references/lessons.md`, and describe the two source productions without client or personal names.
- Add a static site with an invented film whose audit runs in the browser, built and checked with Python's standard library and published with GitHub Pages.

Sizzle grew out of an earlier kinetic brand film skill, which it replaces.
