# The storyboard gate

The storyboard is the film on paper, drawn. It lets a person see the whole plan in a few minutes and change it while change is free. Nothing is generated or rendered until they approve it (`SKILL.md`, 4.1).

Why it exists: one film passed every technical gate (every word recognized, the layout lint clean, loudness on target) and was rejected on first viewing. The script never said what the product was for, the words were insider words, and the motion carried more than the meaning. A storyboard would have shown all three before a credit was spent.

## Make it fast

Aim to show the storyboard within minutes of the brief. Draw the sketches with plain HTML and CSS shapes (rectangles, rules, a few words of type in the right fonts), never with generated images, and never with the film's own renderer. A sketch answers "what is on screen and where", not "how good does it look".

## What it contains

**An overview card,** read first:

- Purpose: what the product is for and the problem it solves, in plain words.
- Who it is for, where they watch, and what they already know.
- What the viewer will understand, or be able to do, afterwards.
- The key terms in plain words, the way the film will define them.
- How the film teaches or persuades: the example, the contrast, the turns, the takeaway.
- The two ahas (one in a film under 30 s): for each, its time, what the viewer believes just before and just after, the word, image or sound that flips it, and the earlier plant it changes. Mark their times, the pose and the button on a clock strip above the first act.
- The full narration, line by line.
- The open questions.

**One card per frame,** grouped into acts, each act labeled with its timecodes:

- A sketch of the picture.
- Number, title and timecode.
- The exact voice line, as it will be spoken.
- Role: pose, plant, hold, flip (aha 1 or aha 2), settle, proof or button. Draw a flip's sketch as two small panels, before and after.
- Picture: what is on screen.
- Teaches (or Point): what the viewer knows or feels now that they did not before.
- Motion: what moves and why. Every move should help the viewer understand.
- Sound: music section, effects, silence.

**Two or three questions** for the reviewer, each one a real choice: the length (a 60 s lesson and a 15 s cut, or 45 s), the example, the feel of voice and music. Recommend an answer for each. Ask the reviewer to show the storyboard to one or two people outside the field, who have not seen the brief, and have them say back in two sentences what the film says; record what they said. Add one test: "Cover the flip frames and say what you expect next." A correct guess means the flip confirms rather than surprises.

## Where it lives

1. **A native canvas.** If the host offers a canvas, design board or storyboard artifact (for example a design-type artifact), put the overview and one artboard per frame there, laid out in rows by act.
2. **One HTML page.** Otherwise copy `storyboard-template.html`, replace its sample frames, and give the user the file. It is self-contained (inline CSS, no scripts, no external requests beyond optional web fonts), lays the frames out as a responsive grid, and prints one act per page. The user can open it in any browser and annotate the printout or reply with frame numbers.
3. **Text only.** In a host without files or rendering, send the overview as a short list and each act as a Markdown table with the columns Frame, Time, Role, Voice, Picture, Teaches, Motion, Sound.

## Check the sketches

Screenshot every frame card and look at it, or, if you have no eyes, measure the sketches in the page (each element's box with `getBoundingClientRect`, and overlaps between text and shapes); `tools/lint.mjs` reads the film's canvas page, not the storyboard. In particular:

- No icon, doodle or motif sits on text. A small sun drawn on a sign once landed on the date line; it moved to the sign's top corner.
- A recurring motif keeps the same place and size from frame to frame, so the viewer can follow it.
- Every word the viewer must read is large enough on the sketch to be read in the film.

## Record the approval

Write this in `BRIEF.md` before the first generation call. Quote the person's approving message word for word; if there is none to quote (or, where the host approves with a button, its recorded approval), the gate has not passed.

```
## Storyboard approval
Version: storyboard v2 (11 frames, 62 s)
Approved by: the client, in chat, 2026-10-17
Approving message, verbatim: "Approved. Move the sun off the date line and keep the yard sale."
Ahas approved: aha 1 at 0:19 (before: one sign is good and one is bad; after: where a sign sits on the map says which way to move it); aha 2 at 0:44 (before: this is about signs; after: it is how I should write anything people skim)
Changes asked for: move the sun off the date line; keep the yard-sale example
Answers: length 60 s plus a 15 s cut; voice and music as proposed
```

Any later change to the script, the example or the order of frames reopens the gate: update the storyboard, mark the new version, and ask again. Changes to timing, sound mix or polish that leave the story as approved do not.
