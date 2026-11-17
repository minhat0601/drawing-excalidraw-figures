---
name: drawing-excalidraw-figures
description: Draws hand-drawn Excalidraw figures (real .excalidraw scenes plus themed SVG) that explain a technical mechanism, a business flow, or a rough idea written only in words - architecture and request flows, system design with read/write paths, sequence diagrams with alt/opt/loop, business processes in swimlanes, state machines and lifecycles, ER and class diagrams, data-structure anatomy, byte layouts, timelines, hash rings, decision trees, charts, layer stacks, before/after pairs, failure paths, causal loops, 2x2 matrices, funnels, concept maps, physical metaphors. Use this whenever a lesson, doc, note, pitch or answer needs a picture, when a page is a wall of text, when someone has a half-formed idea and wants to see its shape, when an existing figure is only generic boxes and arrows, or when asked to "vẽ hình", "vẽ sơ đồ", "vẽ Excalidraw", "vẽ sequence", "vẽ luồng nghiệp vụ", "vẽ swimlane", "vẽ state", "vẽ kiến trúc hệ thống", "minh hoạ cơ chế", "thêm hình cho bài", "mô hình hoá ý tưởng", "vẽ ý tưởng này", "biến note thành sơ đồ", "giải thích bằng hình", "diagram this", "visualize this idea", even if Excalidraw is not named.
---

# Drawing Excalidraw figures

Turn one idea into a hand-drawn figure, the kind someone who understands the problem sketches on a whiteboard for someone who does not yet.
The idea can be a technical mechanism, a business process, a concept to teach, or a rough thought that so far exists only as text.
Output is a real `.excalidraw` file (opens and edits on excalidraw.com) plus an SVG that uses color tokens and works in both light and dark themes.

Text inside figures follows the source it is for: Vietnamese explanations, English technical terms as the source writes them.
The skill docs are English; the labels in `examples/` are Vietnamese on purpose.

## The load-bearing rule

**Draw the SHAPE of the idea, not the list of components.**
A row of boxes joined by arrows says "A calls B", which one sentence already says.
A good figure turns time into length, data into cells holding real values, a limit into a line, a failure into a red stroke.

The rules come from about 600 real Excalidraw figures, 20 shape libraries, and the owner's pack of sequence, swimlane, state and system-design samples.
Sources and licenses: `references/sources.md`.

## Workflow

Do all six steps in order.
Steps 1, 2 and 6 are skipped most often, and they decide whether the figure is usable.

### 1. Write one sentence before drawing

Write exactly one sentence: **"Looking at this figure, the reader SEES ... that the paragraph does not show."**
If you cannot write it, do not draw: a needless figure is worse than no figure.
The sentence picks the figure type in step 3 and later becomes the caption.

When the source is a rough idea (a note, a pitch, a paragraph of thinking out loud) rather than a worked-out text, write one more sentence first: **"This idea really says that ..."**, in at most 20 words.
Rough ideas often say three things at once; this sentence picks the one the figure is about.
If the idea genuinely holds two claims, that is two figures.

### 2. List the facts the figure must carry

There are two kinds of source, and each has its own fact list.
A technical or process source (a lesson, lab numbers, a spec, code, a procedure) uses the list right below.
A rough idea uses the idea list after it.

Read the source and write a short fact list in your working notes, not in a file:

- **Things**: every actor, component, state or table that must appear.
- **Main steps** in order, each with its real name: endpoint, command, event, status code.
- **Branches**: every alternative, error, timeout and cancel path, each with an id (A1, A2).
  "Has an error branch" is not a fact; "A2: payment times out after 30s, order goes to FAILED" is.
- **Real values**: numbers from the lab, key names, sizes, limits.
  Copy them from the source, never from memory.

When the source does not say who acts, what triggers a step, or what happens on failure, ask the person who gave the task before drawing.
Do not invent a branch or a number: a figure with a made-up value teaches something false.
Placeholder rows that only show structure (ids 1, 2, 3 in a join table) are allowed when the source gives a schema and no data; say in the hand-off that they are examples.
A value you derive (12 - 8 = 4 byte) is fine when the subtraction is visible in the figure.
When nobody can be asked (you run as a subagent or in a batch), draw the most literal reading of the source and list every assumption in your hand-off.
If the input already is structured (a Mermaid or PlantUML block, a use case, an SRS flow, output of the `dev-ba-kit` skills), take the fact list from it instead of re-deriving it.

**Idea list**, for a rough idea:

- **Concepts**: every noun the idea leans on, in the writer's own words. Do not rename them into jargon.
- **Relations**: how each pair connects, as a verb: causes, slows, trades off against, is part of, comes before, needs.
  Mark the direction and, for causes, the sign: more A gives more B (`+`) or less B (`-`).
- **Tension**: the conflict or trade-off that makes the idea worth saying. Most ideas worth a figure have one.
- **The claim**: what the writer wants the reader to believe or do after seeing it.

The no-invention rule holds here too: a concept or relation the writer did not state is an assumption, so ask or list it.
A rough idea rarely has numbers, and the figure does not need any: it is a conceptual figure (see "Level of detail" in `references/visual-language.md`).
Keep a number only when the writer gave it.

This list is the checklist for step 6.

### 3. Pick the figure type by what must be seen

For a rough idea, first name the structure of the idea from the idea list, then take the type it points to:

| The idea is shaped like | Figure type | Template in `examples/` |
|---|---|---|
| A causes B causes C, and C feeds back | Causal loop | `26-causal-loop` |
| Two forces pull against each other, options sit between them | 2x2 matrix | `27-matrix-2x2` |
| Many enter, fewer pass each stage | Funnel | `28-funnel` |
| Several concepts and how they relate | Concept map | `29-concept-map` |
| A foundation that holds up what is above | Layer stack | `18-layer-stack` |
| Life before and after one change | Before and after | `06-before-after` |
| A choice between options | Decision tree | `10-decision-tree` |
| Who does which step | Swimlane | `22-swimlane` |
| Something abstract that needs intuition | Physical metaphor | `08-metaphor-token-bucket` |
| A trend or a point of no return | Curve or threshold | `19-curve`, `05-threshold` |

For a technical source, or when the table above does not fit, pick from the full table:

| The reader needs to see | Figure type | Template in `examples/` |
|---|---|---|
| Who calls whom, in what order | Request flow | `01-request-flow` |
| What is inside a thing | Anatomy, nested frames | `02-anatomy` |
| How data lies on disk or in RAM | Byte cells | `03-byte-cells` |
| What happens over time | Timeline | `04-timeline` |
| A limit being crossed | Bars against a threshold | `05-threshold` |
| What changes when one thing is fixed | Before and after | `06-before-after` |
| One structure, two ways to look | Two views, same colors | `07-two-views` |
| Intuition before the mechanism | Physical metaphor | `08-metaphor-token-bucket` |
| The plan and where it can break | Happy path and failure branch | `09-failure-branch` |
| Which one to choose | Decision tree | `10-decision-tree` |
| Message order between parties, no branches | Sequence | `11-sequence` |
| How a thing changes state | State machine | `12-state-machine` |
| How data relates | ER and tables with real rows | `13-er-table` |
| Partitioning on a ring | Hash ring | `14-hash-ring` |
| A real payload, command, config | Annotated code block | `15-code-evidence` |
| Which layer does the work | Layer lanes | `16-layer-lanes` |
| A system growing step by step | Progressive series | `17a-progressive-1` and `17b-progressive-2` |
| Layers stacked on each other | Layer stack | `18-layer-stack` |
| Distribution, trend, long tail | Curve on axes | `19-curve` |
| Familiar components | Library icons | `20-icon` |
| A flow that branches: success, failure, retry | Sequence with `alt`/`opt`/`loop` | `21-sequence-frames` |
| Which role does which step of a process | Business flow in swimlanes | `22-swimlane` |
| A lifecycle with nested and terminal states | Composite state | `23-composite-state` |
| Cardinality between tables, or classes | ER with crow's foot | `24-er-crowfoot` |
| One architecture, two paths (write/read) | System design with two flows | `25-system-two-flows` |
| A feedback loop that amplifies or balances itself | Causal loop | `26-causal-loop` |
| Where options sit on two trade-off axes | 2x2 matrix | `27-matrix-2x2` |
| How much survives each stage | Funnel | `28-funnel` |
| Concepts joined by named relations | Concept map | `29-concept-map` |

`references/figure-types.md` describes each type: when to use it, when not to, how to build it, where it breaks.
Read the section of the chosen type before writing the spec.
Then run the seven-line pre-render checklist in `references/lessons-from-runs.md`: it removes the mistakes that cost the most rounds in testing.
A lesson about the mechanism inside a technology almost never wants a plain request flow.
Interaction over time is a sequence, the life of one entity is a state diagram, who does what is a swimlane: do not mix two of those three in one figure.
Supporting pieces are fine: a timeline may carry a small `plot`, an ER figure a `table` of rows, any figure a `code` block.

### 4. Write the spec

Copy the template of the chosen type and edit it; do not start from a blank file.
A spec is short JSON: coordinates, text, colors by token name.
Full syntax of every element: `references/spec.md`.
Conventions for shapes, color, layout, arrows: `references/visual-language.md`.

Three things to remember even before opening those files:

- **Real values beat generic names.** `user:1`, `1 023`, `429`, `POST /orders` instead of "key", "n", "error", "request".
  A figure with real values teaches; a figure of generic labels only names things.
- **Color is meaning.** Default is `ink` stroke, no fill.
  At most three accent colors per figure: `err` broken, `node` correct, `l4` the thing under discussion or the new thing, `warn` the affected region, `hot` the path of one request.
- **The default reading column is 666px** (a typical article column; `--col N` previews another width). Keep the figure under about 800 units wide (the width the tool reports, which includes 20 units of padding); it is a guide, the tool enforces text size.
  Out of room: stack vertically or split the figure, never shrink the text.

Name the spec after the lesson slug plus what the figure shows, lowercase ASCII with hyphens: `mvcc-snapshot-hai-transaction.json`.
A file name given by the person who asked wins.

### 5. Render

```bash
python3 .claude/skills/drawing-excalidraw-figures/scripts/ve.py <spec.json> [--out dir] [--col N]
```

The tool prints one summary line per figure, then the paths of the two PNGs to open.
A `✗` line is a hard error to fix (text overflow, shape grown by Excalidraw, text too small).
A `•` line is a nudge: read each one, fix it or know exactly why you keep it.
`--col N` previews at another column width, only for a figure that will not sit in the site column.

### 6. Open the images, check, fix

Open both `<name>-light.png` and `<name>-dark.png` with the image reader.
A valid spec and a silent tool do not mean the figure reads well: the tool cannot know whether the figure says the right thing.
Go through `references/review.md`, which starts with the coverage check against the fact list of step 2, then fix the spec and render again.
Expect 2 to 4 rounds.
Stop when the figure says the sentence of step 1 with the caption covered.

For a rough idea with a person to ask, show the first clean render before polishing and ask one question: "Is this what you meant?"
Name the one relation or tension you were least sure of, so the answer is about the idea and not the colors.
Writers often see their idea more clearly in the draft and change it; that is the figure doing its job, so redraw rather than defend the first version.
With nobody to ask, list the relations you assumed in the hand-off instead.

## When no type fits

The table covers the common cases, not all of them.
`references/figure-types.md` has a "Rare figure types" table (DFD, use case, deployment, journey, org chart, roadmap and more).
For a truly new idea ask: what does this resemble in the real world (a bucket, a funnel, an assembly line, a ledger, a queue of people)?
Then build it from primitives (`box` `ellipse` `diamond` `line` `arrow` `text`) and free polygons (`line` with `closed`), following "Building a new figure from primitives" in the same file.

## Where files go

The four output files (`.excalidraw`, `.svg`, `-light.png`, `-dark.png`) land next to the spec unless `--out` is given.
Keep the `.json` spec with the outputs: it is the source for later edits.
Which file to hand over depends on where the figure goes:

| Destination | Use |
|---|---|
| Markdown on GitHub, a chat, a slide, a doc tool | `-light.png` (or `-dark.png` for a dark slide) |
| A web page you control | `.svg` plus `dist/assets/tokens.css`, which defines the color tokens for both themes |
| Someone who will keep editing by hand | `.excalidraw`, opens on excalidraw.com |

A site that already has its own figure pipeline and checker (for example a docs site that embeds token SVG through a fence and runs a contrast check) keeps its own rules: follow them, and run its checker after copying the SVG in.
When the destination is unclear, ask the person who gave the task; when nobody can be asked, leave the files next to the spec and say so.
The skill stops at producing correct files; it does not edit the site's engine or source code.

## Bundled references

| File | Read when |
|---|---|
| `references/figure-types.md` | After picking the type, before writing the spec |
| `references/spec.md` | You need the exact syntax of an element |
| `references/visual-language.md` | Unsure which shape for what, color, layout, arrow labels |
| `references/lessons-from-runs.md` | Before the first render (checklist), and when a figure needs more than three rounds |
| `references/review.md` | After every render |
| `references/sources.md` | You need to know where a rule comes from, or an icon's license |
| `references/samples/README.md` | You want a real example of a whole system-design scene or a business diagram source to look at |
| `examples/*.json` | Always: copy one as the starting point |
