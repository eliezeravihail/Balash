# Guide question log

Record only user-facing discovery questions and answers.

| Run | Stage | # | Guide question | Operator answer | Was the answer architecture-relevant? |
|---|---:|---:|---|---|---|
| guide-1 | 1 | 1 | Will more than one person need to use this at the same time, possibly on different machines, or is one person on one machine enough for this first version? | One person runs the CLI on one machine for the first version. | yes — rules out concurrent-write handling / network service for v1 |
| guide-1 | 2 | 1 | Should assigning a task to an AI agent automatically start execution, or should a person separately tell the AI agent to run it? | I don't know; choose a simple sensible technical approach. | yes — decides whether "assign" and "execute" are one action or two |
| guide-1 | 3 | 1 | If someone switches which storage option the application uses, should existing data automatically move over to the new option, or is that not needed for now? | Automatic migration between storage formats is not required. | yes — removes a whole migration-tooling scope from this stage |
| guide-1 | 4 | 1 | Should the system stop someone from creating a cycle of prerequisites (task A needs B, B needs A, directly or through others), or is that not a concern yet? | Direct or indirect dependency cycles are invalid and should be rejected. | yes — requires cycle detection at the point a dependency is declared |
| guide-1 | 4 | 2 | If a prerequisite that was already "done" gets moved back to an earlier status after a dependent task already started, should the dependent automatically become blocked again? | Changing a prerequisite back from done after a dependent task has already started does not need special handling in this experiment. | yes — scopes out a re-blocking/cascade feature |
