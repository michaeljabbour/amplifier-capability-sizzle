# A worked example: the library film

This is an **invented example**, the same film the site draws and audits in the browser. The library, its town and its hours are fictional. No voice, music or video was generated for it, and nobody reviewed it but the audits. It shows the order the skill works in, and what each step writes down.

## The ask

> Make a short film for the library's screens and socials: we're open until midnight on Fridays now, and we want students to know.

The skill decides rather than waiting to be directed, and records each choice with its reason in `BRIEF.md`:

- **Length:** 14 seconds for the screens, because it is a feed-length message with one proposition. A 15-second cut is the film itself.
- **Room:** lobby screens without sound, and phones with sound off by default. So every word that matters is on screen and held long enough to read, and the voice is a bonus.
- **Voice:** a warm peer, cast for the students' own accent, from whichever text-to-speech provider is configured.

## The idea, on paper

- **Insight:** after nine, students who need a quiet table have nowhere obvious to go.
- **Proposition:** the library is that place on Friday nights.
- **Shape:** a question in the dark, answered by a lit window.
- **Turn:** on "library", the waiting dot of light opens into the window.
- **Aha:** one, because the film is 14 seconds (3.2). Before: after nine there is nowhere to go. After: there is, and it was the lit window the whole time. It flips on "library" at 3.0 s, planted by the waiting light in the first frame, after the question holds in silence. In the viewer's words: "Oh, the library is still open." The hours that follow are proof, not a second turn.
- **Hero line:** "Fridays, open until midnight."
- **Ending:** the window closes back into a dot, and the hero line rises to meet it as its full stop, with the library's name under it.

In one breath: we open on a question in the dark, turn when the light becomes a window, and leave on the hours, punctuated by that light.

## Beat sheet

| Time | Picture | On screen | Motif | Role | Job |
| --- | --- | --- | --- | --- | --- |
| 0.0 to 2.9 s | Night field, one small light | "Where do you go after nine?" | Waiting | Pose, plant | Pose the question within three seconds |
| 3.0 to 6.0 s | The light opens into a window | "The library stays open." | The answer | Flip, settle | The turn, held three seconds |
| 6.0 to 11.1 s | Inside the window, one moment each | "Study rooms." "Late coffee." "Quiet." | The room | Proof | What is there, each read in its own moment |
| 11.1 to 14.0 s | The window closes into the full stop | "Fridays, open until midnight" and "Anytown Library" | The statement | Button | The hours, then the name |

The list is the classic risk: three items arriving at once with no voice cannot be read. Each gets its own moment instead, at 72 px, held at least 0.3 s a word plus 0.5 s.

## The creative gate

A separate pass reads the brief as a stranger would. Most points pass. A few need a word:

- **Point 4 (the first frame moves, and a question is posed within three seconds):** pass, as long as the question is held long enough to read. The first cut fails it in practice; see below.
- **Points 5 and 6 (the aha, its plant):** pass. One aha, as a 14-second film should have, named with its time, its before and after, and the light as its plant. Cold read: not run, since no fresh reviewer read it.
- **Point 13 (type sizes and reading times):** pass on paper. The audit has to confirm it on the frames.
- **Weakest beat:** the list. Cut it to three items, never more.

## The first cut, audited

The first cut is what a quick pass produces: every element is on screen, and almost nothing can be read. The layout and motion audits find six problems across 420 frames:

| Rule | Finding |
| --- | --- |
| READ | "Where do you go after nine?" is readable for about 1 s; six words need 2.3 s. |
| MOTION | "The library stays open." jumps from rest to 50 px a frame. |
| SIZE | "Study rooms · Late coffee · Quiet" is 30 px; a story line needs 72 px. |
| READ | The same line is on screen for 0.9 s; seven words need 2.6 s. |
| HIT | "Open until midnight." and "Fridays" overlap. |
| SAFE | "Anytown Library" runs into the outer 5 per cent of the frame. |

## After the checks

One round of fixes, each answering a finding:

- The question is revealed through a mask and holds 2.4 s.
- The headline leaves through its mask instead of jumping into a slide.
- The list became three moments of its own, at 72 px, inside the window.
- The day joined the hero line, and the light becomes its full stop.
- The library's name moved inside the safe area, under the hero line.

The audit then reports no findings in 420 frames. That does not make the film good. On a real job, the next steps are the director's pass on the frames, a second critic, the voice and mix measurements, and the user's own eyes and ears.

## What this example does not show

No voice, score or sound was generated, so sections 5 and 7 of the skill, the voice-over-bed check and the speech check did not run. The audit sees what the canvas draws through `fillText` and `drawImage`; the window and the light are shapes, so their motion was judged by eye. Try it yourself on the site: scrub to any finding's time with the audit shown.
