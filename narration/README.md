# Narration scripts

These are the **spoken-word scripts** for the masterclass — one per chapter. They are
the source for the audio narration (TTS later, like the play-button "audio museum"
of the Amplifier Core masterclass). They are *not* meant to be shown as page text:
the chapters already carry the written prose. The script's job is the **ear**.

One file per chapter, matching the chapter id:

```
narration/01-introduction.md
narration/02-architecture-map.md
...
narration/appendix-glossary-and-invariants.md
```

## Voice

- **Second person, warm, an instructor walking beside the listener.** Not a lecture
  read aloud — a guided tour. "Let's start where the platform starts…"
- **Distilled from the page, not a re-reading.** Take the chapter's own ideas and say
  them plainly, in fewer words. The listener has the text if they want every clause;
  the audio is the throughline.
- **Timeless and unhurried.** Same register as the site: classy, no fluff, no hype.
- **Spoken, not written.** Short sentences. Say "the platform daemon," not "`amplifier-resolve`".
  Read symbols as words: "section seven," not "§7". Avoid code punctuation, brackets,
  and URLs. Numbers and acronyms get spoken out ("A-2-U-I", "the dot-graph resolver").
- **Length:** roughly 350–650 words per chapter — a few minutes of audio. Shorter is
  fine; never pad.

## The one addition the page doesn't have: diagram digests

This is the reason the audio exists for non-visual learners. Whenever a chapter shows a
diagram, the script must **describe it in words and teach the listener how to read it** —
because they cannot see it. Don't just name the boxes; convey the *shape of the idea* the
diagram encodes.

A digest has three beats:

1. **Orient** — "If you could see the diagram, here's its shape: work enters at the top,
   flows down through the platform, and fans out to the resolvers."
2. **Walk it** — follow the arrows in reading order, naming each node and what the arrow
   between them *means*.
3. **The lesson** — what the picture is really teaching. "Notice every consumer reaches
   the platform the same way. That sameness is the whole point."

Chapters with diagrams to digest: **02** (architecture map + the GitHub example),
**04** (the eight-status state machine), **12** (the DTU topology), **13** (the six-layer
stack). Chapters 7 and 9 have no figure but are concept-dense — narrate the key invariant
as if drawing it in the air.

## Format

Plain prose. No markdown headings inside the body, no bullet lists, no code fences — it is
read aloud start to finish. A single leading title line is fine. Paragraph breaks mark
breaths and beats.
