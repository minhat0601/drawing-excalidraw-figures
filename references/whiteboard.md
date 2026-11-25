# Whiteboard scenes, prototypes and collaborative boards

| What the reader should see | Start from |
|---|---|
| Where people and objects sit in one moment, and what is happening between them | `examples/38-whiteboard-scene.json` |
| How the experience changes from one moment to the next | `examples/39-storyboard.json` |
| What the user sees on each screen and which action or condition moves to the next state | `examples/40-wireframe-prototype.json` |
| What customers see and who works behind each handoff | `examples/41-service-blueprint.json` |
| What is wrong in the current UI, the proposed fix, and how to verify it | `examples/42-ui-review-board.json` |
| How a group collects observations, votes and commits to a next step | `examples/43-workshop-board.json` |

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

## Compose a board with several regions

- **Service blueprint.** Align all lanes to the same customer stages. Include the evidence a customer sees, their actions, the frontstage, backstage work, and supporting systems. Put the line of visibility between frontstage and backstage. Annotate a failure or handoff, such as selecting a delivery slot that fills up before confirmation.
- **UI review.** Use the same scenario on both sides of the current/proposed pair. Anchor numbered findings to specific controls or states and pair them with acceptance checks. Recreate the relevant portion of a screenshot with editable shapes when needed. Label proposals and assumptions.
- **Workshop.** Put the question and available time up front. Give each activity its own region and leave space to add input. Use blank cards or labelled examples on a live board. Add actual votes to a recap when supplied. End with a decision or experiment, an owner, and when and how to read the result.
- **Space or event plan.** Place people and props in an overhead sketch, then mark entrances, queues and movement. Use distances only when the source supplies them.
