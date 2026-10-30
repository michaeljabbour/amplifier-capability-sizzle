# Another approach: a narrated product demo in HyperFrames

Sizzle's main path draws the whole film on one HTML canvas (`SKILL.md`). This reference is a second way to make a short film, for when the film is a promotional or demo video of a software product: real screen recordings, scenes laid out as HTML and animated with GSAP in [HyperFrames](https://github.com/heygen-com/hyperframes), narration, music and an MP4 export.

**Choose it when** the product has to be seen working (screen recordings carry the proof), the person wants to edit the script as a document and watch changes live in a preview, or two agents will build parts of one film at the same time. **Stay on the canvas path when** the film is kinetic type and one motif with no footage, or when you need the layout and motion audits (`tools/lint.mjs`, `tools/motion.mjs`), which read the canvas page contract and do not run on HyperFrames compositions.

**What stays the same.** The order and the hard rule in `SKILL.md` hold here too. Find the idea (`SKILL.md`, 2), write the film on paper, pass the creative gate (4) and get a person's approval of the script before any generation call (narration, music, sound effects, images, video) and before any render or snapshot. Script for the ear (3.1), keep keys out of chat and logs (0.2), never ship font files (0.4), and record what you measured.

## Harness and models

Run this in any coding agent harness with a shell, using a frontier model at a high reasoning effort. Concept art needs a harness with image generation. Two harnesses can work on one video at the same time, one per part of the film (see "Sharing a video with another agent"). One chat per video keeps each context focused.

## Tools

```
HyperFrames            HTML + GSAP compositions, Studio preview, render
Gemini TTS             narration, one take per section (or any provider through tools/tts.py)
Lyria                  instrumental background music
Gemini Flash           advisory listening QC of music (vocals, gaps)
ffmpeg / ffprobe       reference frames, footage encode, loudness checks
faster-whisper         word timings for narration
uv                     runs the PEP 723 scripts in video/scripts/
```

Use the newest version of each. Look them up at the start of a video instead of trusting the IDs in an earlier video or in this reference:

```bash
npm view hyperframes version                     # newest HyperFrames
curl -s "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000" \
  -H "x-goog-api-key: $GEMINI_API_KEY" | jq -r '.models[].name' | grep -Ei 'tts|lyria|flash' | sort -V
```

Pin HyperFrames per video instead of fetching it on every run: install the version you looked up into the video folder with an exact version (step 5), so its lockfile records the version and its hash, and run it with `npx --no-install`, which never downloads. Move to a newer version on purpose, by installing it, never by accident.

Pick the newest TTS, Lyria and Flash model from the list, read each model's page in the Gemini API docs for changes to the request shape, and record the IDs in SCRIPT.md `## Audio`. Use the newest English faster-whisper models.

All Google calls read `GEMINI_API_KEY` from the environment. Never print or log it, and never retry a paid request automatically. Try the API before you tell the user to use a web UI.

Before writing compositions, load the HyperFrames skills: `hyperframes` first, then `hyperframes-cli`, `hyperframes-registry` and `media-use` as needed. Install them from `heygen-com/hyperframes` (path `skills/<name>`) if they are missing, and refresh them with `npx --no-install hyperframes skills update` once the video's HyperFrames is installed.

**Sizzle's own tools that apply here** (commands in `tools/README.md`):

- `tools/tts.py` voices lines with whichever provider the user configured, if they prefer one to Gemini TTS.
- `tools/voice_words.py` measures each narration take: word timings, emphasis, whispers and silence inside a phrase.
- `tools/extend_score.py` lengthens or rearranges the chosen music by whole bars, with clean joins.
- `tools/pops.py` and `tools/asr_check.py` check the exported MP4: single-frame pops, black segments, and speech recognition against the script.

## Workspace layout

```
<workspace>/
  reference/                    shallow clones of product repos (gitignored)
  tmp/                          scratch: frame grabs, voice auditions, clones (gitignored)
  YYYY-MM-DD-<product>-video/
    AGENTS.md                   video-specific rules, e.g. the export filename
    package.json, package-lock.json   the pinned HyperFrames version (node_modules/ gitignored)
    SCRIPT.md                   the source of truth for story, narration, on-screen text, audio
    .gitignore                  raw recordings and large reference MP4s
    references/                 quality bar and messaging: stills, films, decks, prior scripts
    concepts/                   optional concept art + the exact prompts (prompts.txt)
    assets/RawRecordings/       user screen recordings (.mkv), gitignored
    assets/music/options/       Lyria candidates, each with a .json record
    video/                      the HyperFrames project
      index.html                root timeline: scene hosts, music, narration
      compositions/<scene>.html one file per scene
      DESIGN.md                 frontmatter tokens (colors, fonts) + the motion grammar
      REVIEW.md                 timeline, creative calls, beat timings against narration
      scripts/                  narrate.py, align-narration.py, generate-music.py, build-*.py
      assets/{fonts,marks,music,sfx,footage,audio/narration}/
      renders/                  exports (gitignored)
```

The scripts in `video/scripts/` are small and specific to each film. Copy them from the newest earlier video if there is one; otherwise write them as you need them, one job each, with the request and its output file appended to a generation log.

## References

Read every reference the user gives, and record what you took from each one.

```
Launch film stills and films        the visual quality bar; study frames, write the grammar to DESIGN.md
Newest earlier video                SCRIPT.md shape, timings, DESIGN.md family, fonts, SFX, scripts
Product repo in reference/          product facts, the real product mark, install prompt
Decks and earlier scripts           messaging and narration lines (strip HTML to text to read)
Articles the user links             scenario inspiration only; turn it into a fictional scenario
```

## Process

### 1. Set up the video folder

1. Create `YYYY-MM-DD-<product>-video/` with `AGENTS.md`, `references/` and `SCRIPT.md`.
2. Clone the product repo into `reference/` (main branch, `--depth 1`). Product facts come from its README and docs, never from memory. They are the claims ledger (`SKILL.md`, 1).
3. Put the user's references in `references/`.

### 2. Write SCRIPT.md

The user owns SCRIPT.md. Co-write it when asked, starting from the newest earlier script or `references/demo-video-script.md` in the skill folder. The user also edits it directly: re-read it before each change and keep their edits.

- A `Premise:` line names the product URL and the audience.
- `## Audio` sets the narration model, voice and per-section style, and the music brief.
- `## Scene N` sections hold on-screen text in code blocks with size hints ("big bold", "smaller italics"), pills as bullets with one `*italic*` accent each, and `Narration:` lines. The narration script reads these lines literally, so keep only spoken words on them.
- For a big change, propose a plan, make a light SCRIPT.md edit for review, then build after the user says go.

Length guide: about 150 words per minute of narration, about 5.3 s per caption pill.

### 3. Find the look

1. Study the references. Make a contact sheet of each film and pull stills at the moments that set the bar:

   ```bash
   ffmpeg -i film.mp4 -vf "fps=1,scale=480:-1,tile=6x5" -frames:v 1 tmp/contact.png
   ffmpeg -ss 12.5 -i film.mp4 -frames:v 1 tmp/still-12.5.png
   ```

   Look at them, and at frames from the newest earlier render. Sample exact colors from the pixels, not by eye.
2. Gather real parts: licensed fonts, the product's own mark, licensed third-party marks, registry patterns. Record where each mark came from in `sources.json`.
3. Write `video/DESIGN.md` before any composition: frontmatter tokens for colors and fonts, then the motion grammar in words (how things enter, hold and leave; easing; pace). Use the same family as the earlier videos, a new palette, and one motif from the product's idea.

### 4. The gate

Before anything is generated or rendered:

1. Run the creative gate (`SKILL.md`, 4) against SCRIPT.md and DESIGN.md. Points about the canvas, such as the motif's states or craft moves, apply to the scenes as written.
2. Show the person SCRIPT.md as the storyboard, scene by scene, with the overview from `references/storyboard.md`: purpose, audience, what the viewer will understand afterwards, the full narration and the open questions. Add two or three questions.
3. Wait for their approval, and record it at the end of SCRIPT.md with their message quoted word for word. A later change to the narration reopens the gate.

Concept art from an image model is optional and comes after approval. Keep it flat and buildable, and save the exact prompts in `concepts/prompts.txt`.

### 5. Scaffold the HyperFrames project

```bash
cd YYYY-MM-DD-<product>-video
npm init -y
npm install --save-dev --save-exact hyperframes@<version>   # the version you looked up
npx --no-install hyperframes init video --example blank --non-interactive --skip-skills
```

Then:

- To move an existing project to a newer HyperFrames, install that version the same way, then run `npx --no-install hyperframes upgrade --project .`
- Copy `video/.gitignore`, `assets/fonts/` and `assets/sfx/` from the newest earlier video, if any. Fonts are licensed files: never publish them.

### 6. Build the first scenes, then stop

Build Scenes 1 and 2 only, snapshot every beat, fix what you see, and hand them to the user for review. The user wants to nail the feel before the rest of the film exists. Then continue scene by scene.

### 7. Audio

**Narration.**

1. Audition two or three voices on one script line, and let the user choose.
2. Generate one take per section, with the section's style from `## Audio`. Each take is one request; never retry automatically.
3. Measure every take with `tools/voice_words.py --text "<the words sent>"`, and re-voice a section that fails, after fixing its text (`SKILL.md`, 5.3).
4. Master: compress lightly and normalize each section to about -18 LUFS (`SKILL.md`, 5.4).
5. Align: take word timings with faster-whisper, write them beside the audio, and time each visual beat to the word it belongs to. Record the beat timings in `REVIEW.md`.

**Music.**

1. Write a timed Lyria brief: the feel, instrumental only, where it stays sparse, where it lifts, and how it resolves under "Get started".
2. Generate two or three options into `assets/music/options/`, each with a `.json` record of the prompt, model and settings.
3. Listen-check each one with Gemini Flash as advice only, then let the user pick.
4. Fit the pick to the film with bar-aligned edits (`tools/extend_score.py`) and volume automation: low under the narration, up where nobody speaks.

**Sound effects.** Subtle: pop, click, whoosh, key-press. Each peak near -10 dBFS after volume.

### 8. Screen recordings

Prepare the demo environment before recording: a practice run off camera, no visible setup prompts, unique folder names. Encode each cut for the browser and place it in `video/assets/footage/`:

```bash
ffmpeg -ss 00:01:04 -to 00:01:31 -i assets/RawRecordings/take3.mkv \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an -movflags +faststart video/assets/footage/scene3-run.mp4
```

Cut footage at regular speed; do not speed it up a lot. Label what is on screen with a pill rather than asking the viewer to find it.

### 9. Review loop

After every change:

```bash
npx --no-install hyperframes check --json            # 0 errors before you reply
npx --no-install hyperframes snapshot --at 3.2,7.5   # look at the frames you changed
```

Read the PNGs, fix what you see, then give the user the Studio URL (`http://localhost:3002/#project/video`). Keep one preview running with `preview --background`. Studio updates live: do not render an MP4 for review.

### 10. Export

Only when the user says export. Use the filename in the video's `AGENTS.md` (`renders/YYYY-MM-DD-<product>-promo.mp4`). Then verify the file:

- ffprobe: duration, size, frame rate.
- Loudness: `ffmpeg -i <file> -af loudnorm=print_format=summary -f null -` reads about -16 LUFS integrated, true peak at or under -1 dBTP (`SKILL.md`, 7.2).
- `tools/pops.py` and `tools/asr_check.py` pass, and a few frames pulled from the file look right.

Then offer a cleanup pass: gitignore or delete unused takes, options and artifacts. Never stage anything.

## Sharing a video with another agent

Two agents often edit the same `video/` at once.

- "Insert and shift. Do not let the other ongoing work distract you, but do not intentionally break it."
- Run `npx --no-install hyperframes history --limit 10` before editing. "Changed outside the app" means the other agent.
- Never edit files, music or scenes the other agent owns. When you add a scene, shift the later ones and refit music and SFX to the new root duration.

## Audience and content rules

- Say why before showing how: why would the viewer want this product at all?
- Label what is on screen ("Have you ever run into *this*?").
- Example scenarios are fictional and illustrative. Pick a domain the audience knows (sports coaching, a small business website, a personal assistant), then review it as a domain expert would and cut anything they would not do. Name no real organization, customer or person.
- Use real product marks with a `sources.json`. Never invent a logo.
- Promote only the product in the film. No false ending before the last argument. Mark a clear break before the "Get started" or install section.
- Install sections are one prompt the viewer pastes into their agent.

## Pitfalls

- One hot SFX makes the renderer turn the whole mix down. Keep each SFX peak (file peak + 20·log10(volume)) near -10 dBFS.
- Lyria can add voices, speech or a "tropical" feel despite the prompt. Listen to every option, run the Gemini QC as advice only and let the user decide.
- Music edits jump by whole bars, and by an even bar count inside 2-bar phrases.
- `check` and `preview` stamp `data-hf-id` attributes into files, so exact-string edits fail. Re-read before editing, or match on ids.
- Gradient text on transformed children fails. Give each letter its own gradient slice.
