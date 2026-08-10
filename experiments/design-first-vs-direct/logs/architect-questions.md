# Architect question log (product-level discovery, same as prior pilots)

| Stage | # | Question | Operator answer |
|---:|---:|---|---|
| 1 | 1 | Give one concrete example of a user using this product from start to a useful result. | A team lead uses the CLI on one machine to create "Prepare weekly report" with a description, assigns it to team member u1 (display name Dana), moves it todo→in progress→done, and lists tasks to see Dana and the status. After restart, the task is still there. |
| 1 | 2 | How is a team member identified? | Stable member ID + display name, entered at assignment time; no roster command, no login. |
| 1 | 3 | May a task start unassigned? | Yes, may start unassigned and be assigned later. |
| 2 | 1 | Is an AI agent a separate persisted entity, or fields on the task? | Separate persisted entity with its own id; provider/model belong to the agent, not the task. |
| 2 | 2 | Does the execution result need success/failure, or just text? | Task id, agent id, success/failure, text output. |
| 2 | 3 | Repeated execution: append or overwrite? | Append; retaining history is acceptable. |
| 3 | 1 | Automatic migration between storage formats? | Not required; independent stores. |
| 4 | 1 | Cycles in prerequisites? | Direct or indirect cycles invalid, rejected. |
| 4 | 2 | Prerequisites at creation only, or editable later? | Creation-time only for this version. |
| 4 | 3 | Reopening a done prerequisite after a dependent started? | No automatic re-blocking needed. |

These are the same product facts used in the prior two pilots (same oracle). This run tests a
different variable: how the objective given to the Worker is *framed* — as a design/quality target
with behavior as a constraint, versus as a behavior target with quality checked afterward (the
guide-vs-direct and v3-vs-v3.1 pilots both used the latter framing for their Guide conditions).
