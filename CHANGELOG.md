# Changelog

## 2026-10-28: Public first use

- Add a complete public clone/install path beside the first useful outcome, with prerequisites, safe updates and a full-folder ZIP alternative. Preserve the existing method, films and interactive examples.


## Unreleased

- Security scan. `make scan` runs SkillSpector on the installed package against a reviewed baseline (`.skillspector-baseline.yaml`). A scan of the whole repository folder had scored 100 of 100, mostly on files no user installs; with every remaining finding fixed or reviewed, the package scores 0. The description names the shipped checks and where voice text goes, the demo-video reference pins HyperFrames per video and never fetches it unpinned, and each accepted finding carries its reason (`docs/VALIDATION.md`).
- Add a second approach for narrated demos of software products (`references/demo-video.md`, with a script template in `references/demo-video-script.md`): scenes built in HyperFrames from a script the person owns, real screen recordings, narration, music and an MP4 export. It runs under the skill's order and hard rule: the creative gate and the person's approval of the script come before any generation or render, and the narration and the export are measured with the skill's voice, pop and speech tools.
- When the person wrote the source, ask them first what two things they most want a viewer to realize, and build the ahas on their words.
- Keep the energy. A sizzle defaults to rousing; the brief names the feeling the viewer should leave with; the storyboard states the energy so a mismatch surfaces before generation; the first-time panel also reports how the film made each viewer feel and whether they would watch it again; and clarity fixes must not slow a beat into a lecture. A trial film that the panel understood was called robotic and a little depressing.
- `tools/voice_words.py`: measure the pause before an emphasis word on the energy islands, not on Whisper's word edges, which stretch across silence and made almost every pause read as zero; a line's first word counts its lead-in, a quiet unvoiced breath counts as part of the pause, and a word that Whisper stretches across a silence prints LISTEN instead of a guessed number. On a 13-line film the old check failed 12 words; the fixed check fails the 5 that an independent measurement of the audio also fails.
- Check that a newcomer understands the film. A first-time panel of at least four simulated viewers (no background; second language with the sound off; busy and barely interested; not a user of the technology shown) retells the film, names its point, its ask and its hero line, and rates understanding; it gates the storyboard and the render. Every idea the story needs is shown as well as said, and real people outside the field say the storyboard back before generation. A research teaser that passed every other gate scored 2, 2, 3 and 2 out of 5 on this check (`references/lessons.md`).
- Design for two ahas: two moments, each earned, when the viewer's belief changes, the second turning on the first, both inside the first 60 s (one in a film under 30 s). `SKILL.md` adds an aha clock per length, a breath before and a settle after each flip, plant and pay, pose-guess-break, the viewer's-sentence test, a role column in the beat sheet, cut-downs that keep a whole plant and flip, a music arc with a different gesture for each flip, a cold read at the creative gate, and a second critic asked where its belief changed. Creative gate points 3 to 12 are rewritten to check them; there are still fifteen. The storyboard adds a clock strip, a role row, before-and-after sketches for flips, and a cover-the-flip test.
- A trial on a 60 s research teaser tightened the new rules: the flip is the word where the old belief breaks, not the line that explains it; no line or move points at a plant, and a plant is seen, not read; the cold read gets only per-beat time, picture, voice and on-screen words, with no wording that marks a callback, pause or change of state; picture, voice and music may change with a flip's one trigger; read aloud at the casting pace with a second of slack; a cut-down may join up to four ranges; storyboard sketches without eyes are checked by measuring their boxes. In that trial the cold read missed the first draft's aha 1 and found both ahas in the revision.
- The creative gate judges the film on paper; styleframes come after approval, as the hard rule already required.
- The storyboard approval quotes the person's approving message word for word, and every pass in `verification.txt` is a tool's output or a reviewer's verdict, never a line the author wrote.
- Name the skill folder: `tools/` and `references/` sit beside `SKILL.md`, not in the project, so run tools by that path (Amplifier reports it as `skill_directory`) or copy them in once.
- Frontmatter adds `license`, `compatibility`, `user-invocable` and `metadata.version`. Amplifier needs `user-invocable` to offer `/sizzle`; the strict reference validator rejects that one field, a trade-off made on purpose. The description now says when to use the skill. `scripts/check.py` keeps the version in step with `project.json`.
- Move the craft-move table to `references/craft-moves.md`, and replace the audit-hook sketch with a pointer to `tools/audit-hook.js`.
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

- Kept pasted credentials out of files and preserved environment-only provider configuration. Added the MIT notice to the portable bundle and a conflict-preserving local installer.
