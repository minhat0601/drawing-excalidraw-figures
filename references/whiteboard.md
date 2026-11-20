# Whiteboard scenes, storyboards and wireframes

| What the reader should see | Start from |
|---|---|
| Where people and objects sit in one moment, and what is happening between them | `examples/38-whiteboard-scene.json` |
| How the experience changes from one moment to the next | `examples/39-storyboard.json` |
| What the user sees on each screen and which action or condition moves to the next state | `examples/40-wireframe-prototype.json` |

## Reuse editable parts

Open `assets/whiteboard-parts.json` and copy the group by its `id`. Set its `dx` and `dy` for the new position. If you copy a part containing element IDs, give each copy its own `prefix`. You can also open `docs/images/examples/whiteboard-parts.excalidraw` and copy shapes on the canvas. Each shape remains editable.

| Part | Group ID |
|---|---|
| Standing person | `standing-person` |
| Seated person | `seated-person` |
| Two people | `people-group` |
| Phone frame | `phone` |
| Desktop frame | `desktop` |
| Button | `button` |
| Text input | `input` |
| Modal | `modal` |
| Figure in a colored outfit | `actor` |
| Parcel | `parcel` |
| Status indicators | `status` |

## Draw the scene or interaction

- **Scene.** Use pose and placement to show the action. Draw the relevant setting around the people, then label only the props or roles the viewer needs. A line at the floor or an object in front of someone helps show where they stand.
- **Storyboard.** Keep the same character and object shapes across panels. Give each panel one visible moment and a short caption. Use a screen close-up when the next action depends on what the person sees.
- **Wireframe.** Keep repeated screen chrome and controls aligned. Give each frame a distinct state. Label the action or condition that causes a transition. Use the simplest UI elements that show the interaction. The arrows document the intended behavior in an editable sketch.
- **Fictional states.** Labels such as A-042 and A-043 and the QR-shaped marks in these demos are illustrative. For a real product or workflow, take copy and transitions from the source and flag any proposal.
- **Render review.** Open the light and dark PNGs. Check that the pose or transition reads without the caption, and that the text and controls remain legible at the intended width.

## Adapt the parts to other briefs

| Brief | How to lay it out |
|---|---|
| Review an interface with the team | Put one screen in the middle, add numbered callouts beside the controls, and place a proposed revision next to it. |
| Show a service across roles and screens | Align customer actions, screens, staff actions and background steps in lanes. Use a scene or screen close-up at important handoffs. |
| Plan a physical space or event | Draw a simple plan, put people and objects at the relevant places, then mark entrances, queues and movement. Use distances only when the source supplies them. |
| Set up a workshop board | Give each exercise its own region, put prompts above blank cards, and leave room for participants to move or add cards. |
