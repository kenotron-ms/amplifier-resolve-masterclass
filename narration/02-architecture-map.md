Chapter two. The architecture map.

Before we walk the streets, let's look at the map. You don't need every building yet — just the neighborhoods and the roads between them.

Let me describe the main diagram, because if you're listening, you can't see it — and its shape is the whole lesson. Picture the page divided top to bottom into three bands. Work enters at the top, flows down through the center, and fans out below.

Across the very top sits a row of consumers — four small boxes, side by side. A browser. An agent or script. A command-line tool. And a continuous-integration bridge, the kind that turns a GitHub event into a request. Here's the thing to notice: every one of those boxes has an arrow pointing down to the same place, and every arrow carries the same label — "post slash instances." Four different callers, one identical way in. That sameness is the point. Resolve doesn't have a favorite consumer.

Follow those arrows down and they all arrive at the center of the map: a single wide box, the platform daemon. This is the still center of the whole picture. Everything above it is just "how work arrives." Everything below it is "how work gets done and shown." The daemon depends on neither — it simply exposes contracts and lets the edges move.

Now the arrows continue downward and fan out — one to each resolver. Three boxes, side by side: the dot-graph resolver, the orchestrator resolver, the understudy resolver. The arrow from the platform to each one means "launch a sealed container." Read that carefully: each instance gets its own box, its own container. No two runs share memory, or processes, or files. The only thread connecting any two runs is a parent link — nothing more.

From each resolver, a thin arrow runs further down to a viewport — the little user interface that shows what that particular resolver is doing. And those viewports point, finally, into the last box at the bottom: the single-page web application, the shell that a person actually looks at. Off to one side, a dashed arrow feeds the whole stack from a provisioning box — that's the development harness that stands everything up, and we'll get to it near the end.

So the lesson of the map, in one breath: consumers on top, all entering the same way; the platform as the unmoving center; resolvers and their views below, each sealed off from the others.

Now, a worked example — and I want to be careful with the word "example," because it's easy to mistake it for the architecture itself. One common way to drive Resolve is a GitHub loop: an issue is opened, a triage step decides what to do, it posts a "resolve" command, the platform runs a resolver, a pull request comes out, and a review step comments on it. There's a second small diagram for this, and it's a simple vertical chain — issue, to triage, to the resolve command, to the resolver, to the pull request, to review, top to bottom, each step feeding the next.

That loop is one integration. It is not what Resolve is. Swap GitHub for any other event source and the platform doesn't change a line. The seam between the pieces is just a line of text — a command in a comment — which is the loosest possible coupling. Anything that can post that text can drive the platform, and the platform never needs to know who asked.

Hold the map in mind. From here, every chapter walks one neighborhood of it in full.
