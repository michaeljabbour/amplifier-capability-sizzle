---
name: "sizzle"
description: "Direct and produce a 15 to 90 s kinetic-typography brand film (sizzle reel, teaser, launch film or event opener) with narration, score and cut-downs, from an outline, deck, site, template or photos. Use when asked for a sizzle, a teaser, a brand or launch video, a narrated product demo, or an event opener; not for a single clip or image. Stops for a person to approve the storyboard before generating any media. Ships local command-line checks for layout, motion, voice, mix and speech recognition, and a text-to-speech adapter that sends script lines only to the provider the user configures."
license: "MIT"
compatibility: "Needs Node.js with Playwright, ffmpeg and ffprobe, and Python with numpy, scipy, soundfile, librosa, pyloudnorm and faster-whisper for the build and the checks. Voice needs a text-to-speech provider key or a local engine. Network use is limited to the voice, music and sound providers the user configures; keys are read from environment variables and never printed."
user-invocable: true
metadata:
  version: "0.1.1"
---

# Sizzle

You are the director first and the production team second. Sizzle makes a 15 to 90 second motion-graphics film in which type, one visual motif, a narrator and a score move on one timeline. The picture is drawn on an HTML canvas and rendered frame by frame, so picture and sound stay locked and every frame can be measured.

**The bar.** A film the room wants to watch twice and the client forwards without being asked. It comes from decisions made before any asset exists: an insight about the audience, a shape that acts out the client's own promise, two ahas that each change what the viewer believes and each turn on one word, a motif whose states carry the story, lines written for the ear, a score briefed as emotion, and one signature craft move per scene. Two films set this bar: a 60 s teaser for an executive education program (the teaser, below) and a company's internal event opener (the opener: six versions, 47 to 66 s, made twice in two harnesses). Their lessons are folded in below.

**Built to run anywhere.** Harnesses differ. Some agents can see images and some cannot; some have a voice connector, some an API key and some only a local engine; some carry a huge standing context. The film must not depend on luck with any of these. So Sizzle starts with a preflight, keeps its state in files, and turns every quality bar into something you can measure on the rendered frames and the mix, as well as something you look at.

**Another approach: a narrated product demo.** When the film has to show a software product working, from real screen recordings, `references/demo-video.md` gives a second path: scenes built in HyperFrames from a script the person owns and edits, previewed live, with narration, music and an MP4 export. It keeps this skill's order, its hard rule and its voice and delivery checks. The canvas path below stays the default for kinetic type with no footage.

## The order, and the hard rule

0. Preflight: learn what this harness gives you.
1. Absorb the source, the brand, the assets and the audience.
2. Find the idea.
3. Write the film on paper.
4. Pass the creative gate, then the storyboard gate: a person approves the plan.
5. Generate score, voice and sound.
6. Build the composition, auditing and looking as you go.
7. Render and mix.
8. Watch, review, verify.
9. Deliver and document, then take notes.

**Hard rule: no generation call (music, voice, sound effects, images or video) and no render before step 4 passes, and step 4 passes only when a person has approved the storyboard and script.** Generation spends credits and anchors the film: once a score exists, the edit bends to it. A film once passed every technical gate and was still rejected, because its script never said what the product was for. A storyboard shows that in minutes; a render shows it after an hour.

**Decide; don't wait to be directed.** A short ask ("make the event opener from this folder") is enough. Choose the length, shape, voice, music, treatment of people and cut-downs from the defaults below, record each choice and its reason in the brief, and ask only when a choice is expensive to undo and the source cannot settle it (which people to feature from a long list, for example). The story is the exception: the script and storyboard always go to a person before anything is generated.

Defaults when the user doesn't say:

- Length by job: event opener 30 to 50 s, teaser 30 to 60 s, feed 15 to 30 s. Always deliver a 15 s cut as well.
- A voice cast for the audience's own accent, warm and peer to peer.
- Energy: a sizzle is rousing and kinetic, a film that lifts the room, unless the user asks for something quieter. Even a sober subject gets an arc that ends higher than it starts.
- Jokes and taglines play in type, in silence.
- Every word the viewer must read is spoken while it is on screen, or held long enough to read (3.2).
- The people the source names get their own moment; everyone else is drawn, not photographed (3.7).
- Versioned folders, never overwritten, each with the film, the cut-down, captions, script, posters, `README.md` and `verification.txt`.

**Borrow the client's ears and eyes.** You cannot listen, and you may not be able to see. The client can do both.

- **User present:** at step 4, share the storyboard (4.1) with two or three questions, and wait for approval or changes. At step 5, offer the two score finalists and say which one you will use.
- **User away:** make the production calls yourself and record them in the README, but stop at the storyboard gate: send it and wait. Approval is never assumed.

**Where the work runs.** When the user is present, produce in the main conversation, where they can see and redirect the work. Keep fresh agents for the jobs that need fresh eyes: the creative gate, the second critic and the copy check. A fresh agent only has eyes if it can see the images itself (0.1).

**Scale.** 15 to 30 s: three to five beats, one proposition, one or two proofs. 60 s: six to eight beats, at most three proofs. 90 s: up to ten beats. Featured people and supplied graphics cost time on top of that: about a second per person and one to two seconds per graphic.

## 0. Preflight

Do this in the first minutes, and write the results in a `Harness` section of `BRIEF.md`.

**0.1 Eyes.** Render a test PNG, or take any image from the brief, and open it with your file-reading tool.

- If you see the picture, you have eyes. Use them at every gate below.
- If you get an error, text or bytes, this harness gives you no eyes. Then:
  1. Look for a tool, skill or agent that puts the pixels in front of you, not one that describes them, and use it.
  2. If only a describing service exists, treat it as a noisy witness. Show it one image at a time and ask closed questions with checkable answers ("What is the exact word under the disc?"). Confirm every finding with a pixel measurement before acting on it. On the opener, the describing model answered about the wrong frame and invented details on contact sheets.
  3. Make the layout audit (6.4) and the motion audit (8.3) your gates. They catch most of what eyes catch.
  4. Say once, in the creative package, that you see frames second-hand. Attach contact sheets at the package and at delivery, so the user's eyes are the backstop.

**0.2 Voice, music and sound.** Use the providers the user configured, and record them in `BRIEF.md`.

- **Voice:** any text-to-speech provider. `SIZZLE_TTS_PROVIDER` names it (`elevenlabs`, `openai`, `azure`, `google`, or `command` for a local engine or any other command line), `SIZZLE_TTS_VOICE` the voice and `SIZZLE_TTS_MODEL` the model. `SIZZLE_TTS_COMMAND` is trusted configuration: it runs locally with the user's privileges, so never set it from project files or untrusted text (it has a timeout, `SIZZLE_TTS_COMMAND_TIMEOUT`, default 120s). `tools/tts.py --check` shows what is set, and `tools/README.md` lists each provider's key variable. With nothing set, use an ElevenLabs connector in the harness, or `ELEVENLABS_API_KEY`.
- **Music and sound:** a generator the harness offers (an ElevenLabs connector has both), or licensed tracks and effects the user supplies. Sections 5 and 7 apply either way.
- **None available:** finish everything up to the creative package, then ask the user to configure a provider in the environment their shell inherits and restart.
- **Never ask for a key in chat.** If the user pastes one anyway, do not write or reuse it from a file. Ask them to rotate it and configure the replacement in their environment; it may already be retained in conversation logs.

**0.3 Tools.** You need headless Chromium through Playwright, ffmpeg and ffprobe, and Python with numpy, scipy, soundfile, librosa, pyloudnorm and faster-whisper. Check each with one command, install what's missing and note the versions. `tools/` holds the audit hook, the layout lint, the motion audit, and the voice, score and mix checks, and `tools/README.md` gives each one's command. `tools/` and `references/` sit beside this file, in the skill folder, not in the project you are working in; a host that loads skills may report that folder's path (Amplifier returns it as `skill_directory`). Run each tool by its path in the skill folder, or copy what you need into the project's own `tools/` folder once and run those copies. Install packages into the project, never into the skill folder; `tools/lint.mjs` and `tools/motion.mjs` look for Playwright beside themselves, so when you run them from the skill folder, set `PLAYWRIGHT_MODULE` to the project's `node_modules/playwright`.

**0.4 Fonts.** Use the brand's typeface if its license allows rendering. Otherwise use an open stand-in with matching metrics. Never ship font files with the deliverables.

**0.5 Memory you can trust.** Your context may be compacted, cut or handed to a new agent between rounds. Keep the film's state in files, not in the conversation:

- `BRIEF.md`: the film on paper, updated whenever the film changes.
- `edit/edit.json`: the timeline (voice lines with starts, gains and word timings, music markers, and every on-screen string that may change).
- `STATE.md`: what exists, which file is current, the command that last built each output, and the open notes.
- One build script that renders, mixes, muxes, encodes and verifies a version with fixed settings.

After any break, read `STATE.md` before touching anything. Never re-run a step from an older copy of the work: on the opener, a stale re-run overwrote the score edit, the voice cuts and the mix. Keep long outputs (logs, JSON, transcripts) in files and read summaries, so the conversation stays small.

## 1. Absorb

- **Earlier work:** read everything the client gave. Make a contact sheet of any earlier film and write down what to beat.
- **Claims ledger:** every fact, name, title, number and quote, verbatim, with its source. This is what the film may claim. It is not the script.
- **Never-claim list:** dates, fees, approvals, partnerships, rankings, results, and anything else the source does not say.
- **Leaders' words:** a paraphrase is not a quote. Show it without quote marks and don't voice it. Keep it in `edit.json` so the verbatim can replace it later without a new recording.
- **Assets:**
  - logos (official, unmodified), palette, typefaces and their licenses, imagery and supplied graphics;
  - photos: note each one's size and quality, and how large the face sits in it;
  - pronunciations.
  Match photos to people by file name or the user's word, never by recognizing a face.
- **Brand template** (PPTX, POTX or a design file): unpack it and take the system, not the slides. That means the theme colors as exact hex values, the fonts, master backgrounds, textures, icon sets, section and number styles, and the logo lockups. Use these elements as they are, so the film looks like the deck's next slide, moving.
- **Audience and room:** who watches, where (a stage screen, a feed, an email), with sound or without, what they already know, what they feel today, and which accent they hear as their own.
- **Tone:** serious, warm, rousing or playful. Tone decides casting, music, pace and how much space to leave. Write down the feeling the viewer should leave with, in one word, and check every later choice against it. A grim subject can still leave the viewer energized; find the part of the source that gives hope or a way to act, and end there.

## 2. Find the idea

Write each of these in one or two sentences before anything else. They are the spine; everything later is checked against them. When the person you are working with wrote the source, ask them first, in one question, what two things they most want a viewer to realize; their answer is the ahas, and your job is to make those land. Record their words verbatim.

- **Purpose:** what the product is for and the problem it solves, in plain words, with its core thesis in the source's own terms. Study the repo, site or deck until you can say it to a stranger. A script that never says this fails, however well it is made.
- **Insight:** a truth about the audience's situation, not about the product. The teaser: senior leaders hear answers all day from vendors, consultants and their own teams, and few get time away to work on their own question.
- **Proposition:** the one thing the viewer must believe at the end, in one sentence.
- **Shape:** the change the film puts the viewer through, ideally the client's own promise acted out.
  - The teaser's program promised leaders a new way to see their own question, so the film runs from noise in to a clear view out.
  - The opener: the company's frame, then into the team, then many people becoming one ring.
  - Other common shapes: question to answer, before to after, scattered to assembled, close-up to the big picture.
- **The turn and the two ahas:** a turn is where the film changes direction, usually where the viewer becomes the subject. Make each turn an aha: a moment when the viewer's belief changes, not only the picture. A film of 30 s or more has two, both inside the first 60 s. Aha 1 is the reframe: the viewer sees their own situation differently (the insight, made felt). Aha 2 turns on aha 1: it shows the reframe was part of something larger, and it lands the proposition. A film under 30 s keeps one. Design them first; picture, voice and music change on each, and every rule below that names the turn applies to each.
- **Hero line:** the sentence people repeat afterwards, true to the source, set big and given time. In a film of 30 s or more, it states aha 2 or follows it within three seconds.
- **Ending:** the payoff answers the opening, then come the brand and an invitation.

Test: tell the film in one breath. "We open on X, turn on Y, that turns again on Z, and we leave on W." Each turn comes from the one before it ("because of that"). If it needs "and also", cut.

**From source to film.** A film is not the source's table of contents. Choose the proofs that move this audience and leave the rest in the source. For an analysis or a report, the film is its trailer: the question, the most surprising finding, a reason to open the full thing. Find the human stakes even in technical material.

**Teach first when the product is a way of thinking** (a method, a framework, a skill). The viewer must leave able to use the idea; the product comes last, as the partner that helps. Write for a viewer with no insider knowledge: no jargon, and one everyday object anyone can judge in a second (a yard-sale sign seen from a passing car). Then teach with it: two cases that fail in different ways, shown before either failure is named; one change at a time; a question, a real silent pause, then the answer; a worked example, then the same idea on two or three other things; and a short habit or question the end card keeps on screen. Define each term on screen, shown on the example that lacks it.

**A frame from above.** When leadership has just set a company-wide frame, open on it: the leader's portrait and the phrases, one at a time, held and readable. Then move into the team, for example with a camera dive into one dot of a field that opens as the team's world.

**Humor.** Give a joke its own beat: set it up straight, then land it in a held moment or on a music stop. Never explain it. A tag line works in type alone, in silence: the setup, a held beat, the punchline, and one small sound as the motif lands.

## 3. Write the film on paper

All of this goes in `BRIEF.md`, written before any generation and updated whenever the film changes.

### 3.1 Script for the ear

- **The source supplies the claims; you write the lines.** Quote verbatim only names, titles, program names, taglines and legal lines.
- **Voice and grammar:** second person, present tense, short declaratives. Questions belong on screen; the voice makes statements.
- **Word count:** about 160 words a minute while speaking, with at least a third of the film free of voice, so music and picture can land things. A 30 s film takes 35 to 50 words.
- **Marks:** give each line its one emphasis word, its pauses (`/`) and each flip.
- **Write emphasis with punctuation, not typography.**
  - A full stop before the key word gives the held beat; an exclamation mark gives it lift.
  - Keep capitals and ellipses out of voice text. On eleven_v4 voices they often produce a whisper or a creak on exactly the word that must land. Across two runs of the opener in two harnesses they did this to "week", "bigger", "Yours" and "one". Re-voiced with plain punctuation and "!", the words measured as voiced; re-voiced with the capitals kept, "bigger" and "Yours" stayed creaky.
  - Measure every emphasis word (5.3), whatever you write.
- **Keep the word that must land out of the last, unstressed place.** A voice lets go of an utterance after its stress. On an eleven_v4 voice that came out breathy even with "!": the team's name when it ended a sentence, the last syllable of a two-word rallying cry in every take, and the last word of a slogan that ended on a repeated noun in all eight takes. A comma in place of the full stop, so the name ran on into one more word, kept it voiced and let that word lift. Put the key word where the stress falls, or let the line play in type.
- **Read it aloud** at the casting brief's pace against the beat sheet, and leave a second of slack, and cut any line the picture already says.
- **Names:** say a person's name together with their organization, and leave titles on screen. Put tricky names in a pronunciation table.

### 3.2 Beat sheet and legibility

One row per beat with these columns: time, music (section and hit), picture (the visual idea), voice, on-screen words, motif state, sound, the role (pose, plant, hold, flip, settle, proof or button), and the job (what the viewer believed before, and what they know or feel now that they did not two seconds ago).

- **The grid is for sync, not for structure.** Put entrances and cuts on beats, but let scene lengths follow the story: hold the beat that matters, compress a list into a burst, let one moment breathe. Equal blocks read as slides.
- **Every beat changes something.** If removing a beat loses nothing, remove it.
- **The aha clock.** Pose the question or the claim by 3 s in every cut. 15 s: one aha at 3 to 8 s. 30 s: aha 1 at 8 to 12 s, aha 2 at 20 to 24 s. 60 s: 15 to 24 s and 40 to 50 s. 90 s: 20 to 28 s and 45 to 58 s. Between rows, scale from the nearer one. The hero line and the brand card come after the last aha; a small brand mark may sit on screen earlier (9). No run of more than about 15 s of proof without a plant or a flip. These are starting defaults; tune them on the films you make.
- **Breath and settle.** The flip is the word where the old belief breaks, not the line that explains it afterwards; if the viewer could finish the line during the breath, the flip came earlier. Before it, 0.5 to 1.5 s with no voice and the score thinned or stopped. After it, at least 1 s with nothing new to read. Key each flip to one word, image or sound; picture, voice and music may change with it on the same frame, but nothing else new arrives.
- **Plant and pay.** Each flip has a plant shown or said earlier, at least 5 s earlier in a film of 30 s or more: a word, an object, a sound or a motif state that looks incidental and is not explained. It rides inside another beat and adds none; no voice line, caption or camera move points at it, or the viewer predicts the flip. A plant is seen, not read: it is not a line the narrator must carry (3.2). The flip changes what it meant. The brief names, for aha 2, the earlier line or image that now means something else.
- **Pose, guess, break.** Pose the question, leave room to guess, then break the guess. If a stranger can finish the line before the flip, it confirms; it is not an aha.
- **The viewer's aha.** Write each aha as the sentence a viewer would say to a friend ("Oh, so I can..."). If the sentence is about the product ("it does X"), rewrite the flip.
- **One idea per frame.** The most important words are the largest thing on screen.
- **Type sizes for a room, on a 1080-pixel frame:**
  - story lines (the words the film is saying): 72 px or more;
  - every other string meant to be read (names, roles, subtitles, the tag line): 36 px or more;
  - fine print, and ornamental kickers that repeat something larger or spoken: at least 24 px;
  - never more than about 12 words on screen at once.
- **Exceptions:** name each deliberate exception in the beat sheet, with its reason (a secondary label the narrator says aloud, a line a transition covers while it is spoken). The audit (6.4) holds the rest to these numbers.
- **Reading time.** Every string stays fully visible and still for at least 0.3 s per word plus 0.5 s. A line the narrator says stays up for as long as she says it, plus 0.3 s.
- **Lists and agendas.** This is the classic failure: six cards arriving in 2.5 s with no voice cannot be read. Give each item its own moment and say it, or cut items.
- **The narrator carries what matters on screen.** If a line must be read, she says it, or it gets a held moment of its own.
- **Show it as well as say it.** Anything the viewer needs to follow the story is on screen as words or picture, not only in the voice, so the film works with the sound off. Every idea the film relies on is shown happening at least once (what was done, to whom, and what changed), not only named; a term the audience does not already use is shown before it is named, or cut.
- **Cut-downs:** plan them now. A 15 s cut keeps one whole pair from the master, a plant and its flip, usually the pair that lands the proposition, with aha 1's setup folded into one line or frame so the flip still has something to turn. Never keep a flip without its plant, its breath and its settle. Name the master ranges, which aha each carries, which beats carry the hook, the offer and the brand, and whether the platform needs a square or vertical version.

### 3.3 The motif and its arc

Choose one motif drawn from the brand. Write its arc as states that change meaning with the story, not as moves.

- **The teaser:** a square cursor in the brand's color goes from waiting, to the noise, to ownership (every question mark takes the brand's color on "you"), to the opening, the work, the statement (it types the hero line and becomes its full stop), the frame and the brand.
- **The opener:** one gradient dot in the company's field becomes the dot the camera dives into, then the people, then the bullet of each moment, the padlock, the ring, and finally the joke's full stop.

Its largest changes land on the two flips. Never drain the motif to satisfy a copy check; change the words instead.

### 3.4 Casting and voice direction

- **Casting brief:** accent, age, register, warmth against authority and pace, matched to the audience, the room and the user's direction.
- **Cast every film for its own audience.** The opener first reused the teaser's voice, whose accent was not the staff audience's own, and that was the first note. Recast as a warm voice in the audience's accent, it landed.
- **Choose by measurement, then by ear:** shortlist two or three voices, generate the aha 1 line with each, and reject takes by measurement. Measurement cannot hear drama, so play the finalists to the client in context, on the film's sync points over the real bed, and start from voices the client has already approved. On the reel, two measured recasts lost to the first narrator.
- **Direct each line** through its attitude and its emphasis word, written as punctuation (3.1).
- **Audio tags:** use them sparingly and measure what they did. `[confident]` on a short title gave four whispered takes.

### 3.5 Music brief

Brief the music as you would a composer, then turn the brief into the generator prompt.

- **Its job and its arc,** mapped to the shape: a build under the opening, a breath and a hit on aha 1, a breakdown under the reflective beat where aha 2 is planted, a bigger swell or a stop on aha 2, a clean release. Give the two flips different gestures, so the second does not sound like an echo of the first.
- **Instrumentation for the subject's world:**
  - The teaser: piano, strings and pulse.
  - The opener: a marching drumline with brass.
  - A research film might want prepared piano and pizzicato strings.
- **Anti-references, every time:** no corporate electronica, stock tech arpeggios, glassy pads, generic inspirational piano, or elevator and stock-video music.
- **Tempo serves the edit:** at 120 BPM a beat is 0.5 s and a bar 2 s. Name the hit times, but write the feeling first.

### 3.6 Sound palette

Each sound belongs to something on screen, lands on its frame, and comes from the motif's material world. Prompt sounds tactile and specific, for example "Heavy paper card sliding across a wooden desk and stopping, soft and tactile". Add a riser into the release and a synthesized sub drop under the title. Nothing decorative.

### 3.7 People and crowds

- **Featured people get a beat.** Make the portrait large (about 45 per cent of frame height), with the name at 64 px or more and the role from the source under it. Hold it about a second, two beats at 120 BPM, while everyone else steps back. Names rippling past on eighth notes read as a list.
- **Never upscale small photos.**
  - Never draw a photo larger than 1.5 times its source pixels.
  - Never use AI super-resolution on a real person's face.
  - Instead, draw it as a vector halftone: each dot a circle on a fixed grid, 64 to 100 dots across. This holds a 120 px thumbnail at 480 px. Otherwise keep the photo small, or ask for a better one.
  - On the opener, 120 to 360 px photos drawn at up to 640 px drew a first note that some pictures looked low resolution. Four-times AI upscaling left them soft; new photos fixed them.
- **Treatment:** use one treatment for the set (halftone or duotone in the brand palette), cropped from the top of the head and framed alike. Never distort or retouch a face. Spell names exactly as given.
  - Duotone: map luminance from the person's color, deepened toward ink, to a warm white. Give each person their own step of the brand spectrum, and pad above the head so it clears the circle.
- **A tour of several people** (the opener's v6): run it on the beat grid, two beats a person. Each slot is a 0.5 s sine-eased glide to the next person, then a 0.5 s hold. Lay the strip of the others on one smooth curve (near neighbours about 470 px out, then about 250 px apart), because a curve with a corner makes every photo jerk as it passes. Hand names over without sharing a mask (out in 0.08 s, then in over 0.18 s); keep the role label still and let it take each person's color.
- **When the people aren't the point, draw them.** Show a crowd, a team coming together or "everyone else" with the brand's own people icons, in its colors, gathering into a shape. Only the people the source names get photos.

### 3.8 Supplied graphics: build, don't flash

When the client hands you an image to feature (a campaign mark, a diagram, a key visual), a hard cut to the still reads as an interruption. Take it apart and build it on the beat.

- **Take it apart:**
  - measure its geometry (dots, lines, shapes) and redraw those as vectors, so they stay sharp in motion;
  - keep its type and texture as the original pixels, with alpha extracted against the background color;
  - remove from the type layer anything that a redrawn element overlaps.
- **Build:** about one second, fast and on the music: background, then structure rippling out from where it entered, then type cascading up through a mask, then accents.
- **Enter and leave through the motif.** On the opener, the full stop of "bigger." grew and burst into the image's own color field. The finished picture then shrank into the empty place in the ring and became its dot on "one".
- **Verify fidelity:** compare the built frame with the original, fitted the same way. The mean difference should be under about 2 levels out of 255.

### 3.9 Craft moves

Give each scene one signature move that suits its idea, and never bring two scenes on the same way.

The moves that served the two films that set the bar, and what each is for, are in `references/craft-moves.md`.

**Restraint holds it together.** Motion should feel typeset, not effects-driven:

- slow pushes of 3.5 per cent at most, and a 3.5 per cent punch on big hits that decays over 0.5 s;
- no spins, flips or shake;
- at most one full-frame flash, one frame long;
- eases in and out on every camera move, never a move that starts at full speed;
- motion that explains, not motion that decorates: one idea per beat, edits drive the moves, and no kinetic type for its own sake.

### 3.10 Styleframes

Once the storyboard is approved, and before writing the whole composition, render the first frame, the frames just before and after each flip, the hero line and the end card at full resolution. Judge them as a designer: hierarchy, contrast, brand fidelity, and whether you would pause on them. Fix the look here, where it is cheap.

## 4. The creative gate and the storyboard

Before showing anyone the plan, review it against this rubric.

- **Who reviews:** on a long or unattended run, a fresh agent that has not seen the work. Give it the brief, the claims ledger and `BRIEF.md`; styleframes come after approval (3.10), so the gate judges the film on paper. When the user is waiting, or there is no agent tool, do a separate pass yourself, reading `BRIEF.md` as a stranger would, and mark the cold read not run; the person's cover-the-flip test at the storyboard gate stands in for it.
- **What it returns:** pass or fail with a reason on each point, naming any clause that fails, the weakest beat, and what to cut.
- **First-time panel:** give at least four fresh reviewers the same plain description as the cold read, each playing a different first-time viewer: one with no background in the subject; one reading in a second language with the sound off (the voice is unheard unless its words are on screen); one busy and barely interested; one who does not use the technology or setting the film shows. Each watches once at real speed, then, without rereading, retells the film in two sentences, names its main point, what it asks them to do and what the hero line means, lists where they got lost, and rates their understanding from 1 to 5, then says in one word how the film made them feel and rates from 1 to 5 how much they would want to watch it again or pass it on. It passes when at least three of four retell the proposition, nobody rates it below 3, and no moment loses two or more of them. A moment is lost when the confusion lasts: the retell or the answers are wrong or missing on that point. A puzzle the film resolves a few seconds later is a setup; note it, but it does not fail the panel. It also fails when the feelings named are not the brief's, or the want-to-watch-again ratings average under 3. On paper, the feeling answers are a weak signal: energy lives in the music, the voice and the cut, which a description cannot carry, so the person at the storyboard gate judges it. Clarity fixes must keep the energy: when making a beat clearer slows or flattens it, find a faster way to show it rather than adding words. Simulated viewers are a screen, not people: the storyboard also goes to real people outside the field (4.1).
- **Cold read:** first give the reviewer only time, picture, voice and on-screen words, in plain description: no role, job, motif-state or sound columns, no named ahas, and no wording that marks a callback, a pause or a change of state ("returns", "along the path it left", "nothing moves"), since each of those tells a stranger where to look. Give times per beat, not per event, for the same reason. It names the moments where a viewer's belief changes, and what changed. If they are not the declared flips, within 2 s, the ahas are not on the page: change the film, not the labels. A cold read shows structure, not felt effect; the person at the storyboard gate judges that.

1. The insight is about the audience, not the product.
2. The film says in plain words what the product is for, and there is one proposition, in one sentence.
3. The film can be told in one breath, and each turn comes from the one before it, never "and also".
4. The first frame moves, and by three seconds a question, or a claim the viewer will want tested, is posed; the brief says what the viewer will guess.
5. Aha 1 and aha 2 (one under 30 s) are named in the brief, each with its time on the 3.2 clock, what the viewer believed just before, what they believe just after, and the one word, image or sound that flips it; the cold read, if run, found the same moments; picture, voice and music change on each, in different ways.
6. Each flip has an unexplained plant earlier (at least 5 s in a film of 30 s or more), aha 2 changes what aha 1 meant when there are two, and each aha reads as the viewer's own sentence, not a product claim.
7. The motif's states carry meaning and change with the story, with its largest changes on the flips.
8. The ending answers the opening in a way the opening did not predict, then lands the brand with an invitation.
9. Every beat has a role and changes what the viewer knows or feels; no run of proof lasts more than about 15 s without a plant or a flip.
10. The script reads aloud in time, with a third of the film free of voice; it is written for the ear, with emphasis as punctuation; every claim traces to the ledger.
11. Scene lengths vary, with at least one held moment and one burst; each scene has a distinct craft move, and nothing reads as a slide.
12. The music brief names an arc, a breath and a hit for each flip, instrumentation for this subject, and the anti-references.
13. Type sizes and reading times meet 3.2, the narrator carries every line that must be read, every idea the story needs is shown as well as said, and the first-time panel passes.
14. The voice is cast for this audience and the brief's energy, the arc ends on the feeling the brief names, and every featured person gets a moment large and long enough to know them.
15. Supplied graphics are built, not flashed; leaders' paraphrases carry no quote marks; no photo is upscaled.

Fix every failure, then make the storyboard.

### 4.1 The storyboard gate

Within minutes of the brief, show a person the whole film as a storyboard, and generate nothing until they approve it. `references/storyboard.md` gives the full contents and the approval record.

- **Overview card:** purpose, who it is for, what the viewer will understand or be able to do afterwards, the key terms in plain words, how the film teaches or persuades, the two ahas on a clock strip (time, belief before and after, the flip, the plant), the full narration, and the open questions.
- **One card per frame,** grouped by act with timecodes: a quick sketch, title and timecode, the exact voice line, then Role, Picture, Teaches (or Point), Motion and Sound. A flip's card shows before and after.
- **Two or three questions** for the reviewer, such as length, the choice of example, and the feel of voice and music, with the energy you have chosen named plainly ("rousing, fast cuts, drums" or "quiet and reflective") so a mismatch surfaces before anything is generated. Ask too for one or two people outside the field, who have not seen the brief, to say back in two sentences what the film says; if they cannot, the story changes before anything is generated.
- **Where it lives:** the host's own canvas or design board if it has one; otherwise one self-contained HTML page (start from `references/storyboard-template.html`); in a text-only host, a Markdown table per act.
- **Sketches are schematic,** drawn with HTML and CSS shapes, never generated images. Screenshot them and check that no icon or doodle sits on text, and keep a recurring motif in the same place from frame to frame.
- **Record the approval** in `BRIEF.md`: who approved, the approving message quoted word for word, which storyboard version, the ahas approved, and the changes asked for. With no approving message to quote (or, where the host approves with a button, its recorded approval), the gate has not passed. Any later change to the script reopens it.

## 5. Generate score, voice and sound

**5.1 Ground rules.**

- **One record:** with a connector, keep everything on one project or flow. With an API or a local engine, keep a generation log in the project: prompt, voice, model, settings and output file (`tools/tts.py` appends one).
- **Four per call:** get four takes or candidates per line or prompt. A provider that returns the same audio for the same text gives one take; vary the punctuation or the style instruction instead.
- **No repeats:** never repeat a call because a result was slow or disliked; each call spends credits.
- **Download promptly:** signed links expire (two hours on ElevenLabs flows).

**5.2 Score.**

- **Choose:** generate four candidates from the brief and measure each for sync. Track the beat, the spread of beat intervals, and the onsets and level jumps at the planned hits. Among those that sync, choose the most distinctive, not the safest.
- **Build what's missing.** Generators follow a structure loosely, so add a stop, hit or breakdown in the mix (cut the band dead for one or two beats, add a riser or a sub drop) rather than regenerating.
- **Lengthen with whole bars** (`tools/extend_score.py`):
  - confirm the beat phase first, so beat one carries the strongest onsets;
  - find matching downbeat transients by cross-correlating the onset envelope;
  - join 10 ms before them with a 25 ms equal-power crossfade;
  - shift every later marker by the inserted length;
  - to add a bar without a new kind of join, repeat a segment that already follows itself (the opener's v6 played a three-bar groove loop four times instead of three times plus two bars).
- **Budget in bars.** When a revision adds a beat or a longer line, add whole bars rather than squeezing the gaps between lines below about 0.3 s.
- **Map the accents.** Run onset analysis on the final score and list its accents and silences. Key reveals land on accents, and a silence before a hit is the breath where the picture holds. Each flip lands on an accent, after its breath and before its settle (3.2).

**5.3 Voice.**

- **One pass first:** read the whole script in one pass, for a consistent tone.
- **Measure every take** (`tools/voice_words.py`):
  - transcribe with faster-whisper, passing a 16 kHz float array rather than a path;
  - take the onsets of the words the picture keys to from energy islands and the pitch contour, since Whisper drifts by up to 0.2 s on short words;
  - run pYIN for pitch and voicing. Under about 35 per cent voiced frames on a mostly voiced word is a whisper; reject it.
  - pYIN also misses breathy and creaky voice. Confirm on a spectrogram with the pitch track and the word marks drawn on it: harmonics mean voiced; formants over noise mean breath. Look at it if you have eyes.
  - a bass voice's falls dip under pYIN's 60 Hz floor and read as unvoiced: measure it with `--fmin 40`, and judge short words like "Stop." on the spectrogram, since the longer frame blurs them.
  - a statement's final fall should be at least 2 semitones.
- **Each emphasis word** needs a pause of at least 0.3 s before it, measured on the audio's energy rather than on Whisper's word edges, which stretch across silence (a line's first word counts its lead-in), a peak at least 3 semitones over the line median, and a level at or above the rest of the line.
- **Fixing a failing word:** re-voice that line alone, with its neighbors as context and plain punctuation.
- **The same failure in every take is the text, not luck.** Four takes of one script fail at the same place. Rewrite the line (punctuation, word order, which word ends it) instead of buying more takes.

**5.4 Level and edit.**

- **Compress and normalize:** compress lightly (about 3:1 above -26 dBFS), then normalize every line to about -18 LUFS. Write line files as 32-bit float WAV, because 24-bit clipped normalized peaks on the opener. Keep per-line gains within a few dB.
- **Prefer whole takes.** Prefer a whole natural take to a splice. Cut only in silence, keep breaths, and fade 6 to 12 ms in and 30 to 40 ms out. A pause can be lengthened in silence to put a word on the beat.
- **Store:** each line goes in `edit.json` with its word timings, start and gain.

**5.5 Sound effects.** Generate from the palette and trim each sample's pre-roll. Place each sample by its measured peak, not its start: a whoosh peaks 0.3 to 0.5 s in.

## 6. Build the composition

**6.1 One page.** One self-contained `index.src.html`, built to `index.html` by a script that injects `edit.json` and any measured geometry.

```js
const EDIT = /* injected */; const VO = {}; for (const v of EDIT.vo) VO[v.id] = v;
const wordFind = (id, w) => { const v = VO[id]; const i = v.words.findIndex(x => x[2].toLowerCase().replace(/[^a-z0-9']/g, '').startsWith(w)); return i < 0 ? v.start : v.start + v.words[i][0]; };
function drawFrame(t) { /* dispatch to scenes by time; every value derived from t */ }
window.renderAt = async t => { await ready; drawFrame(t); return canvas.toDataURL('image/png'); };
window.getCues = async () => { await ready; return cues(); };   // sound events from the same timeline
```

**6.2 Determinism.**

- Use seeded randomness (mulberry32), no `Date`, and no `requestAnimationFrame` state.
- Load fonts and images before the first frame.
- Keep grain static: grain that changes every frame cannot compress cleanly.

**6.3 Sync.**

- Key every on-screen beat to a spoken word with `wordFind`, or to a measured music accent, so the picture follows when a line moves.
- Put each flip's picture change on the word, image or sound that flips it.
- Write these helpers first: a masked reveal and its exit, a write-on, cover-fit images around a face anchor, and an easing set.

**6.4 Layout audit (works with or without eyes).** Instrument the canvas so every frame reports what it draws, then lint the whole film. Paste `tools/audit-hook.js` into the page and run `tools/lint.mjs`. The hook records each string and image the canvas draws, with its size, alpha, clips and mask rectangle; its header shows where each call goes (`auditInstall`, `auditClip`, `auditMask`, `auditCover`, `window.auditAt`).
Sample every frame; a 66 s film lints in about three minutes. Five rules keep the results honest:

- **Settled strings only.** Judge a string only while it is settled, meaning its box is unchanged for three frames, because masks and moves make strings partial in between.
- **Follow drift.** Link a string to its run while its box moves less than 2 px a frame. A slow camera push otherwise splits every run, and reading times look short.
- **Count by position.** Count a string by its text and its position, since the same words can appear twice at once (a title and a name label).
- **Layers and canvases.** Ignore full-frame layers such as grain and backgrounds. Give offscreen canvases an `id`, so photos can be told apart from texture.
- **Masks, clips and covers.** Resolve every frame against what the viewer can see: masked reveals share their rectangle, circular wipes register their clip, and an opaque field covers whatever lies wholly inside it. Without this, every wipe and iris reports collisions that nobody sees (49 false issues on the opener's v6 before, none after). Check text baked into a supplied graphic by eye or against the original.

Then check the following:

1. **Copy:** every drawn string appears in the beat sheet's on-screen copy, exactly, including case. Strays and near misses fail (a "you" where the script says "Yours", or a label left on).
2. **Size:** settled, opaque strings meet 3.2 for their role.
3. **Reading time:** each string's settled, opaque time meets 3.2.
4. **Collisions:** settled text boxes don't overlap each other or a photo, apart from overlays the beat sheet intends.
5. **Safe area:** settled text sits inside 5 per cent of every edge.
6. **Photos:** no photo is drawn at more than 1.5 times its source pixels.
7. **Contrast:** for each settled string, sample the rendered frame around its box. Text against its background should reach a contrast ratio of 4.5 or more.

Run the audit on every build, fix what fails, and put the numbers in `verification.txt`. Eyes and audit together beat either alone. On the opener's v5, after five rounds of looking, the audit still found a person icon crossing the title, two phrases overlapping at a handover, and a four-word hint card on screen for 0.9 s.

**6.5 Director's pass, with eyes.** For each scene's key frames and every transition:

- render them at full resolution, along with a contact sheet at 2 frames a second and frame-by-frame strips of every transition, and look twice;
- **as QA:** collisions, clipped type, widows and contrast;
- **as director:** is the most important thing the biggest, does the frame do its beat's job, is it beautiful, would you pause on it?
- **transitions:** nothing double-exposes during a wipe or an iris (clear the outgoing content before the next scene shows through), no handover puts two strings in one mask, and no closing move leaves a flat empty field on screen for more than a few frames;
- change the composition, not just the bugs.

## 7. Render and mix

```js
// node render.mjs out.mp4 [firstFrame lastFrame]
for (let f = f0; f < f1; f++) { const url = await page.evaluate(t => window.renderAt(t), f / 30); ffmpeg.stdin.write(Buffer.from(url.slice(url.indexOf(',') + 1), 'base64')); }
// ffmpeg: -f image2pipe -framerate 30 -c:v png -i - -vf scale=out_color_matrix=bt709:out_range=tv,format=yuv420p
//         -c:v libx264 -preset slow -crf 15 -g 60 -colorspace bt709 -color_primaries bt709 -color_trc bt709
```

**7.1 Rendering.**

- **Serving:** serve the page over HTTP. If renders fail with a refused connection, the server died; restart it detached.
- **Splitting:** split long renders into frame ranges with identical encoder settings and join them with the concat demuxer. Start the render, then write the docs while it runs.
- **Exact length:** mux with `-t <duration>`, never `-shortest`. Encode delivery copies with `-fps_mode passthrough`, and check the frame count with `ffprobe -count_frames`.
- **Fixed settings:** the build script holds the delivery encoder settings, and a revision uses the same settings as the version it replaces.
- **Processes:** record each background job's PID and stop it by PID. Never kill by a pattern that also matches your own command line.

**7.2 Mixing.**

- **Chain:**
  - high-pass the voice at 70 Hz;
  - duck the score under the voice with a smoothed envelope (about 120 ms look-ahead attack, 450 ms release) and a depth for each section (6 to 14 dB);
  - lift the score where nobody speaks;
  - sum into a look-ahead peak limiter at -2.5 dBFS;
  - finish with a two-pass `loudnorm` to -16 LUFS, TP -1.0, LRA 20. If the second pass reports `dynamic`, lower the limiter ceiling.
- **Stems:** write the voice, music and effects stems beside the mix.
- **Voice over the bed** (`tools/vo_over_bed.py`): measure each line's voice stem against music plus effects over its words, after every change to the effects. On the opener, a new whoosh under "bigger" took that line from 12.3 to 10.5 LU until it was moved and lowered.

## 8. Watch, review, verify

**8.1 Watch it as the audience.** Look at a contact sheet every 0.5 s and at every transition frame by frame; without eyes, read the audit's string timeline as the viewer would. Write the notes a demanding client would write before they have to ("flat on [word]", "this drags", "I can't read that", "who is this?"), act on each, and kill what repeats. Then check the aha clock against `edit.json` and the stems: measure the voice and score level around each flip (an `ffmpeg` `astats` or `silencedetect` window works) and paste that output in `verification.txt`, with each flip's time.

**8.2 Second critic.** Give a fresh agent the stills at 0.5 s, the script and the mix numbers, with the rubric from section 4. Run the first-time panel (4) again on the rendered frames and captions, with the same pass bar. Ask what it would cut, what it did not understand, and where its belief changed: the moments of realization, and what it believed before each. If they differ from the brief's ahas, the film is not doing what the brief says. It reviews only what it can actually see, and says which frames it saw second-hand.

**8.3 Motion audit.**

- **Single-frame pops:** compute the frame-to-frame luma difference to find them (`tools/pops.py`, which also finds black segments).
- **Speed:** track each element's speed from the audit boxes. Flag any element that jumps from rest to full speed in one frame, or whose speed changes by more than about 10 px a frame between frames, unless the beat sheet marks a cut or a burst.
  - Skip masked reveals (entrances by design) and swarms such as crowds, which nearest-box tracking cannot follow; judge those by eye.
  - Call a start "from rest" only after two frames of tracking, so elements entering the frame do not count.
  - Give the audit the marked bursts and cuts as a list of time windows (`tools/motion.mjs` reads them from `window.getMarks()`).
  - A 470 px glide needs about 0.5 s of sine easing to keep its speed changes near 10 px a frame; cubic easing over 0.32 s measured 60.

**8.4 Technical gates.** Pass all of these and record the measured numbers in `verification.txt`. Every result there is a tool's output pasted unedited beside the command that produced it, or a reviewer's returned verdict; a pass you wrote yourself with nothing behind it does not count.

1. Frame count, duration, size, frame rate and BT.709 tags as specified.
2. No page errors, no decode errors, and no black segment of 0.08 s or longer.
3. Loudness and true peak on target.
4. Speech recognition on the final mix matches the script at 97 per cent or better (`tools/asr_check.py`).
5. Voice at least 8 LU over music and effects on every line, and every marked emphasis word measures as emphasized.
6. The layout audit and the motion audit pass.
7. An independent copy check against the ledger, with verbatim evidence. Answer a flag by rewording the claim, not by adding labels.
8. Supplied graphics match their originals (3.8).

**8.5 Revisions.** Change only what the note asks, then prove it. Per-frame PSNR against the previous version should drop below 40 dB only inside the range you meant to change. Report that range.

- **A re-edit that moves everything** (new scenes, a longer score): place every line by a rule in a script, keep the unchanged scenes' code, and compare those scenes at their new offset.
- **Keep random sequences stable.** On the opener's v6, deleting one unused random call reshuffled the whole finale crowd. Only the PSNR comparison against v5 caught it.

Passing the gates does not make the film good: they measure craft, not meaning. It is done when the creative gate, the storyboard gate and both reviews have passed as well.

## 9. Deliver and document

- **Cut-downs** use the master's own frames and stems:
  - join two to four source ranges on beats, with a 25 ms score crossfade at each join;
  - bring the cut to -14 LUFS and remap the captions;
  - put a brand mark on screen within four seconds, and make every beat read with the sound off;
  - check that each cut keeps a plant, its flip, the breath before it and the settle after it.
- **Each version in its own folder:** H.264 web copy, master, cut-downs, SRT and VTT captions, script, posters, `BRIEF.md`, `README.md` and `verification.txt`. Never overwrite an earlier version.
- **`README.md`,** in this order:
  - the notes, and what changed in answer to each, with before and after numbers;
  - the director's notes: insight, audience, shape, motif, voice and sound;
  - which checks were seen and which were measured;
  - open items.
- **Director's transcript,** when asked for notes: every beat's voice, on-screen words, and its motion, timing and sound, taken from the composition's own timeline, with a frame for each act.
- **Handing over:** put files where the user works, and check the size and checksum after any transfer.

## 10. Lessons from client notes

Diagnose with measurement, fix the cause, and report before and after numbers. Treat every note as a chance to make the film sharper, not just to patch it. `references/lessons.md` lists each client note behind the rules above and what answered it. Read it when a note arrives: the fix that worked before is usually a rule here, applied earlier.

## 11. Anti-patterns

- Generating music and voice before the idea exists, or before a person has approved the storyboard.
- A script that never says what the product is for.
- Insider vocabulary, an idea said but never shown, and a product pitch where the viewer needed a lesson.
- Motion that decorates instead of explaining.
- Lifting the source's sentences as the script, or mirroring its sections as scenes.
- Scenes of equal length, one per hit.
- Corporate electronica.
- A motif that moves but never means anything.
- Small labels in a crowded scene; an agenda of cards nobody has time to read.
- A turn that changes the picture and the score but not what the viewer believes.
- A second turn that only adds ("and also"), or an aha that announces a feature.
- Capitals and ellipses in voice text, or a key word left last in its phrase, where the voice lets it go.
- Wipes and irises that double-expose the outgoing scene.
- Enlarging small photos, or sharpening faces with AI; a supplied graphic dropped in as a hard cut.
- Reviewing frames you never saw, or trusting a describing model before checking it against the pixels.
- Re-running a step from an older copy of the work.
- Asking for, or keeping, an API key in chat.
- Copy-check fixes that add labels or drain the metaphor.
- Calling the film done because the technical gates passed, or grading your own film: a pass recorded without a tool run or an independent reviewer.

## Writing for the client

- **Spelling:** British or American to match the client.
- **Your own copy:** no em dashes (quote the client's copy as it stands), and no superlatives or hype.
- **The README:** state what changed in answer to each note, then the thinking, then the open items, with numbers wherever a claim can be measured.