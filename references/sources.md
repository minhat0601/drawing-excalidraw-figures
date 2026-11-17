# Sources and licenses

## Where the rules come from

| Source | Count | Used to derive | License | How it is used |
|---|---|---|---|---|
| Hello Interview "System Design in a Hurry" (the site owner's saved HTML copy) | 438 Excalidraw figures, 56 pages | Figure type table, color as meaning, progressive build sequences, the exemplary figures (token bucket, hash ring, Flink windows, two-view R-tree) | Paid content | Learn the drawing style only |
| karanpratapsingh/system-design | 43 `.excalidraw` files | Sequence with lifelines, event beads on arrows, row color following the row when sharding, dotted regions with a label below | CC BY-NC-ND 4.0 | Learn the drawing style only, do not copy figures |
| Prakash-sa/system-design-ultimatum | 65 files | Numbered arrows with a step list, standing and lying cylinders, note cards, color by section | MIT (code), CC BY 4.0 (content) | Learn the drawing style |
| Everoot/System-Design | 29 files | Color linking requirements to components, black background with new things in color, a frame per phase | No license | Learn the drawing style only |
| enkr1/..._excalidraw_examples | 15 files | Consistent icon set, underlined note cards, API in monospace text boxes | No license | Learn the drawing style only |
| sanket7474/system-design-lab | 6 files | Clear ER boxes | No license | Learn the drawing style only |
| DeKinci/sysdeslib | 84 shapes | "One silhouette for the whole family, told apart by a mark inside": every store is a cylinder, the store kind is a small mark on the body | No license | Learn the idea, rebuild from primitives (`db` with `kind`) |
| Dinesh-Sunny/excalidraw-system-design-kit | 4,458 items | Color by group, prebuilt patterns | MIT | Load with `--lib` when needed, not bundled because it weighs 9.8MB |
| excalidraw/excalidraw-libraries | 20 libraries reviewed | Icons, UML and flowchart symbols, data structures | MIT | 188 icons bundled, see below |
| coleam00/excalidraw-diagram-skill | 1 skill | The "remove the text" test, the "what is learned" test, real evidence, not boxing every text, the render-then-fix loop | No license | Learn the idea |
| github/awesome-copilot `excalidraw-diagram-generator` | 1 skill | Table for choosing diagram type by intent, element count limits | MIT | Learn the idea |
| algomaster.io, formation.dev, handbook-hld, plus.excalidraw.com | 4 articles | Left to right, one arrowhead, dashed is asynchronous, labels include technology, about six shapes, the stranger test | Public articles | Learn the idea |

Three pages in the original list could not be opened during research: designgurus (404), tryexponent (redirect blocked), teamblind (402).

## Where the sources conflict and what the skill chooses

| Question | The sources say | The skill chooses | Why |
|---|---|---|---|
| Shape for a data store | Hello Interview: circle. The rest: cylinder | Cylinder | The circle is also used for cache, queue, CDN and lock, so you must read the label to tell them apart |
| Clean or hand-drawn strokes | coleam00: `roughness 0`. Most real files: `roughness 1` | Hand-drawn (1) | Matches the site's 2,900 existing diagrams |
| Double-headed arrows | Hello Interview uses them for request and response. handbook-hld treats them as an error | One arrowhead | Two heads hide the direction and what is flowing |
| Label on every arrow | handbook-hld: always. algomaster: when unclear | When unclear, but always when more than one arrow joins two shapes | Figures for a lesson come with accompanying text |
| Detail in the figure | coleam00: code and JSON in the figure. algomaster: strip everything | By purpose: strip a conceptual figure, give a technical figure real evidence | The site teaches mechanisms, and real evidence is what makes a figure teach |
| Amount of color | karanpratapsingh: one color per service. Hello Interview: almost black and white | At most three accent colors, one meaning each | Decorative color carries no information |
| Marking new things in a progressive build sequence | Hello Interview: no marking. Everoot: colors new things | Color new things `l4`, drop old things to `muted` | Hello Interview's most-cited weakness is that the delta is not visible |

## Icons bundled in `assets/icons.json`

188 icons taken from the excalidraw/excalidraw-libraries repo, MIT license (copy at `assets/ICONS-LICENSE.txt`).
The `aws-` icons draw AWS Architecture Icons, which are AWS trademarks; AWS permits them in architecture diagrams, so always keep the service name as the label.
The `azure-` and `gcp-` icons draw Microsoft Azure and Google Cloud product icons, and `db-` / `tech-` draw database and tool logos (PostgreSQL, MySQL, Redis, Kafka and so on). All are trademarks of their owners and are used here only to name the product in an architecture diagram, so keep the product name as the label.

| Library author | Library | Name prefix | Icon count |
|---|---|---|---|
| mateuszbaransanok | it-icons | (none) | 48 |
| dwelle | network-topology-icons | `net-` | 10 |
| dhtoran | stick-people | (none) | 7 |
| finfin | flow-chart-symbols | `flow-` | 15 |
| anna-pastushko | architecture-diagram-components | `arch-` | 11 |
| childishgirl | aws-architecture-icons (39 of 249, chosen list in `build_icons.py`) | `aws-` | 39 |
| youritjang | azure-cloud-services (12 of 19) | `azure-` | 12 |
| rockssk | microsoft-azure-cloud-icons (7 of 19) | `azure-` | 7 |
| mguidoti | google-icons (29 of 139) | `gcp-` | 29 |
| mwc360 | microsoft-fabric-architecture-icons (Postgres, MySQL, Snowflake) | `db-` | 3 |
| chuqbach | data-platform (Cassandra, Elasticsearch, Kafka) | `db-` | 3 |
| maeddes | technology-logos (old format, picked by index: Kubernetes, Terraform, Neo4j, Redis) | `tech-` | 4 |

Rebuild with `python3 scripts/build_icons.py <path-to-excalidraw-libraries/libraries>`.
The script drops text, drops the original colors (the tool recolors by token) and drops the libraries' invisible click regions.

## Measurements used in the skill

Measured on 438 Hello Interview figures:

- Figure width: median 1,106, 90th percentile 1,938. Median width-to-height ratio 2.0.
- Text lines per figure: median 17, 90th percentile 40.
- Words per text line: median 2, 90th percentile 3.
- Font size: 20 accounts for 74%, 16 for 18%, 28 and 36 for titles.
- Stroke width: 2 accounts for 67%, 1 for 27%.
- Colors per figure: median 1, 90th percentile 4.
- 141 of 439 figures have dashed lines.

Measured on 158 `.excalidraw` files from five other authors: arrows bound to shapes at both ends range from 24% to 83% depending on the author (three of the five authors above 75%), right-angle elbow arrows under 2%, arrows with a bound label from 0% to 30%.

## Business diagrams and the learning pack

Added from the owner's pack `~/Downloads/excalidraw-learning-pack` (guide plus 19 self-made samples generated from PlantUML with excaliplant, and 176 downloaded scenes).

| Source | What the skill took | License |
|---|---|---|
| Owner's 19 samples (`excalidraw-samples/*.puml`) | Templates 21 to 25 are redrawn from samples 01, 08, 09, 13, 14 with site tokens and Vietnamese labels. The rules in figure-types sections 21 to 25 come from the "lessons" and "errors met" lists of the guide: one end node per terminal state, converge before branching again, a loop must hold real messages, round brackets in group titles, number one flow and letter the other, zones per path | Owner's own work |
| plus.excalidraw.com use-case guides (sequence, UML, flowchart) | Fragment vocabulary (`alt` `opt` `loop`), fewer return messages, one goal per diagram | Read only |
| `@grethel-labs/excaliplant` | Not a dependency. Its output shows the standard layouts; `ve.py` draws the same structures natively so colors stay tokens and text stays legible at 666px | MIT |
| swaymun/system-design-excalidraws, kranthiraju/system-design-docs | Looked at only (complete designs, LLD class and state diagrams) | No license: learning only, nothing copied |
| nv-minh/dev-ba-kit (`rules/diagram-selection.md`, `skills/sequence`) | The fact list before drawing and the coverage check after it, the size limits (15 messages, 8 actors, nesting 2), "when not to use" lines for sequence, state and activity, and the rule that sequence and state stay out of business-level text | MIT, owner's own repo |

The samples in the pack are 1,400 units wide and would show 7px text in the site column.
That is why the templates here keep four lifelines or four lanes and stack vertically.

## Reference samples in `references/samples/`

Kept for looking at, not for loading whole into context: each `.excalidraw` is 5 to 200 KB of JSON.
See `references/samples/README.md` for the list and when to open one.

| Folder | Content | License |
|---|---|---|
| `owner/` | The owner's 19 PlantUML sources and the guide `excalidraw-master-guide.md` (Vietnamese) | Owner's own work |
| `prakash-sa/` | 43 scenes from Prakash-sa/system-design-ultimatum (commit 859c8de), copied unchanged except the file names; scenes with embedded images or over 200 KB left out | CC BY 4.0, `LICENSE.md` beside them; credit "Prakash Saini, system-design-ultimatum" when reusing a scene |
