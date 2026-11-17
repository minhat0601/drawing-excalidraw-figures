# Visual language: which shape for what, color, layout, arrows, text

Contents: [Shape vocabulary](#shape-vocabulary) · [Color](#color) · [Layout](#layout) · [Arrows and labels](#arrows-and-labels) · [Text](#text) · [Level of detail](#level-of-detail) · [Site constraints](#site-constraints)

Every rule here comes with a reason.
When two rules pull against each other, the reason is what helps you choose.

## Shape vocabulary

Keep to about six shapes per figure, each with exactly one meaning.
The source figure sets fail here most often: a diamond is a load balancer in one place, a cache in another, Elasticsearch in a third, so shape no longer carries information.

| Thing to draw | Use | Why |
|---|---|---|
| Service, process, processing step | rounded `box` | The default shape, needs no explanation |
| Place that holds data | `db` (cylinder) | Recognized as a "store" without reading the label. The Hello Interview source uses a circle for DB, cache, queue, CDN and lock alike, so you must read the label to tell them apart |
| Specific store kind | `db` with `kind` | One silhouette for the whole family, told apart by a mark inside: three disks is SQL, `{ }` is document, `k → v` is key-value |
| Queue | `queue` (flat box with messages) | Shows what the queue holds, and whether it is full or nearly empty |
| Stream, log, topic | `pipe` (horizontal tube) | A standing cylinder is a store, a lying cylinder is a flow: told apart by orientation |
| Gateway, load balancer, proxy | tall narrow `box` | A wall every request must pass through |
| Many identical instances | `stack` | Do not draw three separate boxes, and do not draw replicas for every store: write `×3` |
| Client with a UI | `window` | Separates end users from services calling each other |
| Human | `person` or the `user` icon | |
| Thing outside the system | `cloud`, or a `box` with a `dashed` border | Dashed means "not ours" or "does not exist yet" |
| Boundary, group | `frame` | Solid border is real containment (process, machine), dashed border is a logical group |
| Inner component | small `box` inside a large `box` or a `frame` | |
| Array, log, disk page, row | square-cornered `cells` | Square corners are for data, rounded corners are for things that run |
| Decision point | `diamond` | ONLY decision points |
| State | filled rounded `box` | |
| File, page, document | `doc` | |
| Schema | `entity`, or bare text next to the store | Name, then column lines, only columns relevant to the current point |
| Payload, command, config | `code` | The real thing is more convincing than a box named "Request" |
| Countable thing (token, request, event) | `ellipse` or small `box` filled `hachure` | Countable by eye |

Not every piece of text needs a box.
Titles, notes, units and axis names are bare text.
Box something only when it is a "thing" in the system, or when an arrow needs to bind to it.

## Color

Default: `ink` stroke, no fill.
Measured on 438 Hello Interview figures: half use a single color, 90% use at most four.
The karanpratapsingh set gives every service an arbitrary color, which looks nice but the color no longer says anything.

| Token | Its one meaning |
|---|---|
| `ink` | Everything normal |
| `muted` | Secondary notes, parts already explained in an earlier figure |
| `err` | Broken, rejected, lost, costly path |
| `node` | Correct result, good path (or `l3` if the lesson already uses `node` for Node.js) |
| `l4` | The thing under discussion, the thing NEWLY added at this step |
| `warn` | Affected region, thing that is waiting, thing being counted |
| `hot` | The path of exactly one request through the figure |
| `l2` | Neutral structure that must separate from the background: frames, buckets, unemphasized bars |
| `l6` `l7` `heap` | Only when the lesson has already assigned a meaning to that color |

Usage rules:

- At most three accent colors per figure. `ink` `muted` `l2` are neutral and do not count. Beyond three, no color stands out.
- An entity keeps one color everywhere it appears: when a cell in the array and a node in the tree share a color, the reader connects the two views unaided.
- Color must not be the only signal for something important. A broken thing is both red and dashed, or has an X mark, so it still reads in black-and-white print.
- Color by requirement: when a figure serves three requirements, write each requirement in one color, then color the components and arrows serving it the same.
- `hachure` for countable things and for "waste" (padding, waiting regions). `solid` for regions, states, bands.
- Red is always reserved for failure. The Everoot source uses red for "requirement 1" in one frame and "failure" in another, so the reader can no longer trust the color.
- Causal signs are not colors. In a causal loop or concept map, `+` and `-` go as text on the arrow (`+` same direction, `-` opposite), and every arrow stays `ink`. Color goes only on the one loop or path the idea is about (`l4`), and `err` only on a loop that ends in harm. Coloring every `-` red would tell the reader that every slowing effect is a failure, which is rarely what the writer meant.

## Layout

- **One flow direction per figure.** Requests go left to right: client, gateway, service, store. Layers and hierarchies go top to bottom.
- **The main axis lies on a straight line.** Side paths, bypasses and return paths curve above or below the axis.
- **Split the read path and the write path** into two lanes when they differ.
- **3 to 7 clusters.** A strip of 8 cells is one cluster. A summary figure has at most 10. Beyond that, split into an overview figure and a zoomed-in figure of the part under discussion.
- **The most important thing is the biggest and has the most empty space around it.**
- **Align.** Boxes with the same role have the same size and the same `y`. Use `row`/`col` to avoid computing by hand.
- **Draw only what affects the current point.** No load balancer in front of every service, no logging and monitoring, no replicas for every store.
- **A figure discussing a choice is cropped** to exactly the parts that differ between options, drawn large.

## Arrows and labels

- Every relation needs an arrow. Two boxes placed side by side say nothing.
- **One arrowhead, in the request direction.** A double-headed arrow hides the direction and hides what is flowing. When both directions matter, draw two arrows, each with its own label.
- **Solid is synchronous, dashed is asynchronous** or a reply. Use this consistently across the figure, and if the figure has both, add a one-line legend.
- **Labels are verbs or real names**: `POST /orders`, `CDC`, `getFareEstimate()`, `2. INSERT`. At most three words (measured on the sources: median two words per text line).
- **Number the steps** when order is the point: `1.` `2.` in the labels, or a `badge`, plus a `steps` list on the right if each step needs a sentence of explanation. This is the most effective technique and the one the sources use least.
- **A number on the edge** when it is the reason: `5ms`, `2GB`, `×1000`.
- A long bypass (direct upload to S3, SSE back to the client) is a curve going around above or below, not cutting across the figure.
- Arrows do not pass through boxes or over text. If one does, move the box, do not force a bend.
- A note pointing at something uses `note` with a thin dashed `muted` line, so it is not mistaken for data flow.

## Text

- A figure holds only labels, numbers and short phrases. Sentences belong in the lesson, not in the figure.
- A box label states responsibility and technology: `Feed Cache (Redis)`, not `Cache`.
- Detail inside a box is one or two `- ...` lines.
- Font sizes: 20 for main labels, 16 to 18 for notes and arrow labels, 14 to 15 for indexes and axis ticks. Use at most three sizes per figure.
- Vietnamese for explanations, with English terms kept as they appear in the lesson.
- Spell-check every label. The source figure sets are full of errors like "Messsages", "Inteventory": errors in a figure are harder to spot than errors in text, and nobody fixes them.

## Level of detail

Ask first: is this figure for grasping structure, or for learning details?

- **Conceptual figure**: abstract shapes are enough. Readable in 30 seconds.
- **Technical figure**: must contain real evidence. Real event names, real endpoints, real payloads, real measurements from the lesson's lab.

The "remove the text" test: delete all text, and does the remaining structure still suggest the idea?
A row of five equal boxes does not.
A bucket, a circle with a bold arc, two layer stacks of different heights do.

The "what is learned" test: does the reader learn one concrete thing from the figure, or does it only name the boxes?

## Default constraints

- The default reading column is 666px wide, the width of a typical article or docs column. A wider figure is scaled down, and its text with it. For a slide, a wiki page or a wide screen, preview with `--col N` and keep the same rule at that width.
- Keep width under about 800 units: size-16 text then stays above 13px on screen and the size-15 labels of the prebuilt macros at 12.5px. The source figures have a median width of 1,106, so their layouts cannot be copied as is.
- When short on room, stack vertically (height does not shrink text) or split into two figures.
- Colors come only from token names. Tokens invert their values in the dark theme, so the figure fits both themes automatically.
- Text renders in Patrick Hand (handwritten, full Vietnamese diacritics), code blocks in IBM Plex Mono.
- The output page loads nothing from the network: no external images, no raster vendor logos.
