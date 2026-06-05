Chapter one. Introduction.

If you've used Amplifier, you've run a single session. You type a request, a loop turns, tools fire, an answer comes back. One process, one conversation, and when it ends, it ends.

Resolve asks a different question. What if the request didn't come from a person at a keyboard, but from somewhere else entirely — a browser form, another program, a scheduled job, a continuous-integration event? What if the work took an hour instead of a minute? What if it had to run somewhere sealed, where a runaway process couldn't touch anything that mattered? And what if you wanted to watch the whole thing happen, from a distance, without ever interrupting it?

That is Resolve. It takes a unit of work, runs a pluggable strategy inside a sealed container, narrates every step through a fixed contract, relays a human in and out, and hands back an artifact at the end. Often a pull request — but just as easily a review, a report, a verdict, or a set of files.

Here's the analogy to carry with you. Amplifier Core is like a small operating-system kernel: a tiny center that provides mechanisms, while everything specific plugs in from the outside. Resolve sits one layer up and borrows the same shape. Where the kernel runs a single program, Resolve runs many — under isolation — on behalf of the outside world.

Two words anchor everything. The first is "instance." An instance is the unit of work: one run, of one strategy, against one request. Think of it the way an operating system thinks of a process. It has a lifecycle, an isolation boundary, a status you can read, and a parent it can be linked to. Everything in this masterclass orbits the instance. And notice the deliberate choice here — the unit of work is the instance, not the session. A session is one AI conversation. An instance is a governed run that might use many sessions, span hours, pause for a human, spawn workers, and survive a restart.

The second word is "resolver." A resolver is a strategy for resolving a request. Fix this bug. Implement this feature. Review this pull request. The resolver decides how that gets done: what to ask for, what to clone, what phases to move through, how to verify the result, when to stop. Three resolvers ship today, and they could not be more different in temperament. One treats the work as a compiled pipeline. One treats it as live delegation, a manager spawning workers. One treats it as a governed contract — align on intent, commit to verifiable success, then prove it. We'll meet all three later.

And here is the line that makes the whole thing hold together: the platform never knows what a resolver means. It checks that inputs are well-formed, and it routes events and responses to the right place. It never interprets what a field, or a phase, or an artifact actually signifies. That single restraint is what lets a wildly different new resolver appear without changing the platform at all.

Keep that idea close. The platform provides mechanism; the resolver provides policy. Everything that follows — the lifecycle, the sealed container, the event vocabulary, the interaction surfaces, the resolvers, their views — is a consequence of holding that one line. Let's begin.
