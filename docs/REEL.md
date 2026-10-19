# The Sizzle reel

The film at the top of [the site](../README.md) was made with this skill, in the order the skill sets out: the film on paper first, then the creative gate, then voice, score and sound, then the build and the audits. It runs 60 seconds (1,800 frames at 30 fps), with a 15-second cut.

## The idea

- **Insight:** agents can make a video in minutes now, and it looks finished. Nobody decided anything, and nobody checked a frame.
- **Proposition:** Sizzle makes your agent direct the film first, then prove every frame.
- **Shape:** noise to proof. The film opens as the kind of video it argues against, stops itself, rebuilds as the thing it describes, and ends by auditing itself.
- **Turn:** made before the skill asked for two ahas, the reel has one clear turn, "Stop." The stock music slows to a halt, the frame freezes and loses its color, and the audit flags every failure on screen.
- **Hero line:** Direct the film. Measure every frame.
- **Ending:** the name in a viewfinder, then a line of type in silence: "This film passed its own audit." The last line explains the opening.

The motif is the audit's own dashed box. It is absent while nobody checks, ember on the turn, mint while the film is made, a frame around the hero line, and a viewfinder around the name.

## The script

Every agent can make a video now. It looks finished. Nobody checked a single frame. / Stop. / Sizzle makes your agent a director first. / Ideas before assets. / It writes the film on paper, beat by beat. / Nothing is generated until it passes fifteen checks. / Then voice, score and sound. / Then it checks every word, and every beat. / Direct the film. Measure every frame. / Sizzle.

Sixty-three words in sixty seconds. The joke at the end plays in type, without a voice.

## How the choices were made

- **Voice:** three voices read the turn line four times each. Each take was measured word by word with `tools/voice_words.py`: whether "Stop." was voiced, and how far "director" rose above the rest of the line. The chosen voice then read every line four times, and each line was picked by the same measurements and its spectrogram.
- **Recasting:** after the first cut came a note asking for a different male voice. Three more voices were cast the same way, with an audition that put each read on the film's own sync points over the real music and picture, and the pick voiced the whole script. Then an alto read it in one pass. Neither beat the first narrator, so the film kept him. Measurement rejects a bad take; only a listener can say a voice is right. Two lessons went back into the tools: a bass voice needs a lower pitch floor in `tools/voice_words.py` (`--fmin 40`), and `tools/asr_check.py` now hears the film again in 30 s windows when Whisper's full pass skips speech after a long music gap.
- **Score:** four candidates from two briefs, all instrumental. The one chosen had the structure the film needed: a groove for the making, a breakdown under the proof, and a big chord to land on "Measure". It was rearranged by whole bars with `tools/extend_score.py`, so the same chord returns for the name.
- **Sound:** the stock loop at the start, its tape stop, the gate's ticks, the sub drops and the final click are synthesized. The shutter clicks, card slaps, stamps, gate slam, projector and typewriter are generated effects, each placed on the frame its cue names.
- **Picture:** one HTML canvas drawn as a pure function of time, rendered frame by frame. Type: Instrument Serif, JetBrains Mono and Inter Display, all under the SIL Open Font License.

Voice, score and the generated effects came from ElevenLabs. Nothing in the film is a quote, an endorsement or a claim the skill's documents do not make.

## The audit

| Check | Tool | Result |
| --- | --- | --- |
| Layout: type size, reading time, collisions, safe area, image scale, contrast | `tools/lint.mjs` | 0 issues on 1,800 frames, outside the exceptions named below |
| Motion: starts from rest and sudden speed changes | `tools/motion.mjs` | 0 flagged outside 12 marked windows |
| Single-frame pops and black segments | `tools/pops.py` | none |
| Voice over music and effects | `tools/vo_over_bed.py` | every line 8 LU or more; lowest 8.5 LU |
| Speech recognition against the script | `tools/asr_check.py` | 63 of 63 words (primed with the name, 62 of 63: "Stop." is the most fragile word) |
| Loudness | ffmpeg `ebur128` | -16.0 LUFS integrated, -1.2 dBTP true peak |
| Smallest type outside the exceptions | the audit hook | 28 px (the tags on the audit boxes) |

The brief named two exceptions before the audit ran. The opening's stock-video words are unreadable by design: they are the parody, and the audit's own tags call them out on screen. The gate's counter runs up from 00/15 on eighth notes; only 15/15 is meant to be read, and it holds.

The four numbers the film shows during its proof scene, and the "0 issues" in its last frame, are the measured values from these checks.

The poster is the end card. Captions come from the measured word times, one cue per line.
