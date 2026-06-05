Appendix. The things to keep at hand.

This last part isn't a chapter to be walked through. It's a reference — the things you'll want within reach once you're actually working in the code. Think of it as the drawer you keep open beside you. I won't read it all aloud; that would defeat its purpose. Let me just tell you what's in the drawer, and why it's there.

The first half is the glossary — the vocabulary of this masterclass, gathered in one place. An instance: the unit of work. A resolver: a pluggable strategy. The platform: the daemon that owns lifecycle, isolation, transport, and validation. The worker container, the event vocabulary, the interaction format, the viewport, the Dev Test Unit. Every term you've met, defined in a sentence, each pointing back to the chapter where it earned that definition. When a word goes slippery on you, this is where you firm it up.

Alongside it, two small anchors worth memorizing. The eight statuses an instance can hold — created, starting, running, then completing or failing or being cancelled, with side-trips into awaiting-input and paused. And the required event chain: created, then phase, then artifact, then completed. Four events, in that order, every single run.

But the part of this drawer you'll reach for most is the list of cross-repo invariants — and these deserve a word of respect. These are the traps that pass every unit test and break reality anyway. They live at the seams between repositories, exactly where a green test suite can't see them. The whole spirit of the list is this: the cheap bugs show up in your tests; the expensive ones hide at the integration boundaries. So write the boundaries down.

Let me name just a few of the sharpest, to give you their flavor. Emit the completion event at every exit path — success, failure, exception alike — because a single missed path is a silent hang that nothing will warn you about. Address the source server by the twin's own bridge address, never the host gateway, because the workers are siblings and the gateway points at the wrong machine — a bug that passes on your laptop and fails in the twin. Remember that mirroring your local code is a one-time snapshot taken at launch — edit afterward and re-launch, or you're testing the old version and proving nothing. And never bundle a second copy of React into a viewport; one copy, shared, or the whole interface crashes on the first hook.

You don't need to hold all of these in your head. You need to know they exist, and to know that this list is where they live — so that when something passes its tests and still breaks, your first instinct is to come here and read.

And one governing principle over all of it: when in doubt, the code wins over any document, including this one. The authoritative sources are listed at the end — the architecture notes, the event-vocabulary design, the per-repo guidance with its own pitfall lists. This appendix is a quick reference, nothing more. When the platform changes, the discipline is to update both the chapter and the invariant here, together, so this drawer never goes stale.

Keep it open. That's what it's for.
