---
name: demo-video
description: >-
  Make a short promotional or demo video for a software product in the demo-video workspace:
  scaffold the video folder, write SCRIPT.md, study the user's references and set the look, build scenes
  in HyperFrames, generate narration with Gemini TTS and music with Lyria, cut screen
  recordings with ffmpeg, review in HyperFrames Studio and export an MP4. Use when starting a new
  video, adding or changing scenes, narration, music or footage in an existing one, or exporting.
  Triggers on "demo video", "promo video", "SCRIPT.md", "new video", "export the video".
---

# Demo videos

Each video is a standalone folder at the workspace root. Videos borrow look, scripts and fixes from
earlier ones, so read the newest video folder, if any, before you start a new one.

## Agent harness and models

Run this skill in a coding agent harness such as GitHub Copilot, Claude Code, Amplifier or Codex,
with a frontier model at a high or extra high reasoning effort. These worked:

```
Claude Opus 5.5 (claude-opus-5-5), effort xhigh   in a harness that offers it, e.g. Claude Code
GPT-6 Astra (gpt-6-astra), effort high            in a harness that offers it, e.g. Codex
```

Use the newest successor of these models when one exists. Concept art needs a harness with built-in
image generation.

Two harnesses can work on one video at the same time, one per part of the film (see "Sharing a video
with another agent"). Running one chat per video keeps each context focused.

## Tools

```
HyperFrames            HTML + GSAP compositions, Studio preview, render
Gemini TTS             narration, one take per section
Lyria                  instrumental background music
Gemini Flash           advisory listening QC of music (vocals, gaps)
ffmpeg / ffprobe       reference frames, footage encode, loudness checks
faster-whisper         word timings for narration
uv                     runs the PEP 723 scripts in video/scripts/
```

Use the newest version of each. Look them up at the start of a video instead of trusting the IDs
in an earlier video or in this skill:

```bash
npm view hyperframes version                     # newest HyperFrames
npx --yes hyperframes skills update              # refresh the HyperFrames skills
curl -s "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000" \
  -H "x-goog-api-key: $GEMINI_API_KEY" | jq -r '.models[].name' | grep -Ei 'tts|lyria|flash' | sort -V
```

Pick the newest TTS, Lyria and Flash model from the list, read each model's page in the Gemini API docs
for changes to the request shape, and record the IDs in SCRIPT.md `## Audio`. Use the newest English
faster-whisper models.

All Google calls use `GEMINI_API_KEY` from the environment. Try the API before you tell the user to use
a web UI.

Before writing compositions, load the HyperFrames skills: `hyperframes` first, then `hyperframes-cli`,
`hyperframes-registry` and `media-use` as needed. Install them from `heygen-com/hyperframes` (path
`skills/<name>`) if they are missing.

## Workspace layout

```
<workspace>/
  AGENTS.md                     workspace rules (never edit)
  reference/                    shallow clones of product repos (gitignored)
  tmp/                          scratch: frame grabs, voice auditions, clones (gitignored)
  YYYY-MM-DD-<product>-video/
    AGENTS.md                   video-specific rules, e.g. the export filename
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
2. Clone the product repo into `reference/` (main branch, `--depth 1`). Product facts come from its
   README and docs, never from memory.
3. Put the user's references in `references/`.

### 2. Write SCRIPT.md

The user owns SCRIPT.md. Co-write it when asked, starting from the newest earlier script or
[templates/SCRIPT.md](templates/SCRIPT.md). The user also edits it directly: re-read it before
each change and keep their edits.

- A `Premise:` line names the product URL and the audience.
- `## Audio` sets the narration model, voice and per-section style, and the music brief.
- `## Scene N` sections hold on-screen text in code blocks with size hints ("big bold", "smaller
  italics"), pills as bullets with one `*italic*` accent each, and `Narration:` lines.
  `narrate.py` reads these lines literally, so keep only spoken words on them.
- For a big change, propose a plan, make a light SCRIPT.md edit for review, then build after the user
  says go.

Length guide: about 150 words per minute of narration, about 5.3 s per caption pill.

### 3. Scaffold the HyperFrames project

```bash
cd YYYY-MM-DD-<product>-video
npx --yes hyperframes@latest init video --example blank --non-interactive --skip-skills
```

Then:
- To move an existing project to a newer HyperFrames: `npx --yes hyperframes@latest upgrade --project .`
- Copy `video/.gitignore`, `assets/fonts/` and `assets/sfx/` from the newest earlier video, if any.
  Fonts are licensed files from the machine: never publish them.

### 4. Find the look

Details, commands and a brief to hand off: [references/look.md](references/look.md).

1. Study the references: contact sheets and stills from the films, the reference images, frames
   from the newest earlier render. Sample exact colours.
2. Gather real parts: licensed fonts, the product's own mark, licensed third-party marks, registry
   patterns.
3. Write `DESIGN.md` before any composition: same family, a new palette, one motif from the product's
   idea.
4. Concept art from an image model is optional. Keep it flat and buildable.

### 5. Build the first scenes, then stop

Build Scenes 1 and 2 only, snapshot every beat, fix what you see, and hand them to the user for
review. The user wants to nail the feel before the rest of the film exists. Then continue scene by
scene.

### 6. Audio

Details and commands: [references/audio.md](references/audio.md).

- Narration: audition voices on one script line, generate one take per section, master, align and
  time the visual beats to the word timings.
- Music: write a timed Lyria brief, generate 2 or 3 options, the user picks one, then fit it to the
  film with bar-aligned edits and volume automation.
- SFX: subtle (pop, click, whoosh, key-press). Peak near -10 dBFS after volume.

### 7. Screen recordings

Details: "Footage" in [references/hyperframes.md](references/hyperframes.md).
Prepare the demo environment before recording: a practice run off camera, no visible setup prompts,
unique folder names. Cut footage at regular speed; do not speed it up a lot.

### 8. Review loop

After every change:

```bash
npx --yes hyperframes check --json            # 0 errors before you reply
npx --yes hyperframes snapshot --at 3.2,7.5   # look at the frames you changed
```

Read the PNGs, fix what you see, then give the user the Studio URL
(`http://localhost:3002/#project/video`). Keep one preview running with `preview --background`.
Studio updates live: do not render an MP4 for review.

### 9. Export

Only when the user says export. Use the filename in the video's `AGENTS.md`
(`renders/YYYY-MM-DD-<product>-promo.mp4`). Verify the MP4 with ffprobe, loudness and a few frames
pulled from the file. Then offer a cleanup pass: gitignore or delete unused takes, options and
artifacts. Never stage anything.

## Sharing a video with another agent

Two agents often edit the same `video/` at once.

- "Insert and shift. Do not let the other ongoing work distract you, but do not intentionally break it."
- Run `npx --yes hyperframes history --limit 10` before editing. "Changed outside the app"
  means the other agent.
- Never edit files, music or scenes the other agent owns. When you add a scene, shift the later ones
  and refit music and SFX to the new root duration.

## Audience and content rules

- Say why before showing how: why would the viewer want this product at all?
- Label what is on screen ("Have you ever run into *this*?").
- Example scenarios are fictional and illustrative. Pick a domain the audience knows (sports
  coaching, a small business website, a personal assistant), then review it as a domain expert would
  and cut anything they would not do. Name no real organization, customer or person.
- Use real product marks with a `sources.json`. Never invent a logo.
- Promote only the product in the film. No false ending before the last argument. Mark a clear break
  before the "Get started" or install section.
- Install sections are one prompt the viewer pastes into their agent.

## Pitfalls

- One hot SFX makes the renderer turn the whole mix down. Keep each SFX peak
  (file peak + 20·log10(volume)) near -10 dBFS.
- Lyria can add voices, speech or a "tropical" feel despite the prompt. Listen to every option, run the
  Gemini QC as advice only and let the user decide.
- Music edits jump by whole bars, and by an even bar count inside 2-bar phrases.
- `check` and `preview` stamp `data-hf-id` attributes into files, so exact-string edits fail. Re-read
  before editing, or match on ids.
- Gradient text on transformed children fails. Give each letter its own gradient slice.
