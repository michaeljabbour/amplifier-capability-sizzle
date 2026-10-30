# Sizzle

[Open the guide, watch an audit and get the skill](https://michaeljabbour.github.io/amplifier-skill-sizzle/).

A skill that helps agents direct and produce short kinetic brand films: 15 to 90 seconds of type, one visual motif, a narrator and a score on one timeline, with captions and a 15-second cut. It makes the creative decisions before anything is generated, then measures the work on every frame and in the mix. It does not replace a person's eyes and ears; it gets the film to them in better shape.

The picture is drawn on an HTML canvas as a pure function of time and rendered frame by frame, so picture and sound stay locked and every frame can be checked. The skill works in agent hosts that can see images and in hosts that cannot, because each quality bar is something to measure as well as something to look at.

This project pairs the reusable [`sizzle` skill](SKILL.md) with its [tools](tools/README.md), a [reference of client lessons](references/lessons.md) and an explanatory static website. The website opens with a 60-second reel made with the skill and audited with its own tools; [docs/REEL.md](docs/REEL.md) tells how.

## First use

Bring the audience, one proposition, source assets and a length. Start with a storyboard you can approve; production follows only after that approval and the creative gate.

```sh
git clone https://github.com/michaeljabbour/amplifier-skill-sizzle.git
cd amplifier-skill-sizzle
python3 scripts/capability.py install --dest ~/.agents/skills
```

Requires Git and Python 3.11+. Use the skills directory supported by your agent. Ask for Sizzle in a new session and supply one real task. The [install guide](docs/INSTALL.md) explains the complete ZIP alternative and safe updates.

## Use the skill

Install the skill as a folder named `sizzle` with `SKILL.md`, `references/` and `tools/` inside it, in your host's skills directory: for example `~/.amplifier/skills/sizzle` for Amplifier, `~/.claude/skills/sizzle` for Claude Code, or `~/.agents/skills/sizzle` for hosts that read the shared folder. The site's skill bundle is that folder, zipped.

Then give your agent the material and the job. Say who will watch, where, and whether they will hear it. A short ask is enough: the skill chooses length, voice, music and cut-downs from its defaults and writes each choice in the brief.

Example requests:

> Use the sizzle skill to make a 45-second opener for our all-hands from the deck in this folder. The audience is the whole company, on a stage screen, with sound. Show me the creative package before you generate anything.

> Make a 30-second teaser for our product launch from the launch deck and the site. Customers will watch it in an email, mostly with the sound off. Deliver a square 15-second cut as well.

> Here are the notes on version 4. Change only what they ask, prove that nothing else moved, and give me before and after numbers for each note.

A good run returns a storyboard first, within minutes: an overview of the purpose, the audience, the key terms and the narration, then one card per frame with its sketch, voice line, picture, point, motion and sound, and two or three questions. It uses the host's own canvas if there is one, a self-contained HTML page if not, or Markdown tables in a text-only host. Once you approve it, the run returns a versioned folder: the film, the 15-second cut, captions, script, posters, a `README.md` that answers each note, and `verification.txt` with every measured check.

## Voice, music and sound

The text-to-speech provider is yours to choose. Set `SIZZLE_TTS_PROVIDER` to `elevenlabs`, `openai`, `azure`, `google` or `command` (any local engine or command line), with `SIZZLE_TTS_VOICE` and, where it applies, `SIZZLE_TTS_MODEL`. Keys live only in environment variables; `python3 tools/tts.py --check` shows what is set without printing them. Music and sound effects come from a generator your host offers, or from licensed tracks and effects you supply. `SIZZLE_TTS_COMMAND` is trusted configuration (it runs locally with your privileges and is killed after `SIZZLE_TTS_COMMAND_TIMEOUT` seconds, default 120). See [the tools guide](tools/README.md#voice) for each provider's variables and command-line examples.

## How the checks work

Nothing is generated until a person has approved a storyboard of the whole film, and the film on paper has passed a fifteen-point creative gate: an insight about the audience, one proposition, two ahas, each a turn where the viewer's belief changes and picture, voice and music change with it, a motif that means something, a script written for the ear, and type that can be read. After the build, eight technical gates are measured and written down: frame count and color tags, black segments, loudness, speech recognition against the script, voice over the music, the layout and motion audits, an independent copy check, and fidelity to supplied graphics.

The layout audit records every string and image the canvas draws, cut to what the viewer can actually see, and checks size, reading time, collisions, safe area and photo scale on every frame. Passing the gates does not make a film good. The creative gate and the reviews decide that.

## Local development

The site follows the Taste × Elegance skill site's small Python static builder: HTML, CSS and JavaScript with no backend or runtime dependencies. Use Python 3.11 or later; the build needs no packages.

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check site/site.js   # optional JavaScript syntax check; needs Node.js
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Or `make check` and `make preview`. Open <http://127.0.0.1:8000>. Re-run the build after source changes and reload the page. `_site/` is generated output.

The check covers local links and fragments, shipped Markdown links, the skill contract (name, description, body under 500 lines, every named tool and reference present), byte-for-byte fidelity of the downloads and the ZIP bundle, and privacy patterns: no email addresses, home directory paths, credential-like strings, em dashes in prose, or image metadata. See [site details](site/README.md) and [validation evidence](docs/VALIDATION.md).

The tools have their own requirements (Playwright, ffmpeg, and Python audio packages); [tools/README.md](tools/README.md) lists them. `tools/fixture.html` is a five-second page with known problems for trying the audit tools.

The Pages workflow builds and checks `_site/` on pushes to `main`, then publishes only that static output. It uses GitHub's official actions pinned to fixed commits and needs no project secrets.

## Project contents

- `SKILL.md`: the skill, from preflight to delivery.
- `references/lessons.md`: the client notes behind the rules, and what answered each.
- `references/storyboard.md` and `references/storyboard-template.html`: what the storyboard contains, where it lives, how its approval is recorded, and a self-contained HTML page to start from.
- `references/craft-moves.md`: the signature moves that served the two source films, and what each is for.
- `references/demo-video.md` and `references/demo-video-script.md`: a second approach, for narrated demos of software products built in HyperFrames from screen recordings, and the script template it starts from.
- `tools/`: the audit hook, layout lint, motion audit, voice, mix, speech and score tools, the text-to-speech adapter, and a fixture page.
- `docs/EXAMPLES.md`: a worked, invented example, from brief to audited cut.
- `docs/VALIDATION.md`: what was checked, how, and what was not.
- `scripts/build.py` and `scripts/check.py`: the dependency-free build and checks.
- `site/`: the page template, metadata, styles, the invented film and its in-browser audit, and local assets.
- `_site/`: the generated website and the downloadable bundle.

## Limits

Sizzle is a set of instructions and tools for an agent with a shell, a headless browser and audio tools. It does not render films by itself, and it cannot listen: voice, music and mix checks are measurements, and a person still needs to hear the film. The layout audit sees only what the canvas draws through `fillText` and `drawImage`; shapes and text baked into images are checked by eye or against their originals. The contrast check is an estimate.

The text-to-speech adapters were checked against a local stand-in for each service and with a local engine, not against the live services. The site's film is invented for explanation, and its findings come from its own frames; they are not evidence about any real film. The homepage reel's narrator, score and most sound effects were generated with ElevenLabs. The lessons in `references/lessons.md` come from two real productions, described without client or personal names.

## License and provenance

MIT; see [LICENSE](LICENSE). The family theme snapshot keeps its own [MIT notice](site/theme/LICENSE). The page follows the Taste × Elegance skill site as a design and implementation reference.


## Portable capability and ownership

Direct the film before generating it, then check the picture and sound.

Read the [installation guide](docs/INSTALL.md) for the supported local path and [consolidation record](docs/CONSOLIDATION.md) for ownership and evidence limits. Canonical catalog name: **Sizzle**; repository: `amplifier-skill-sizzle`.
