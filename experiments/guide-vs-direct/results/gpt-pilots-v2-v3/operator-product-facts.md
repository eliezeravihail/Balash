# Operator-only product facts

**Never place this file in either agent's repository. Never reveal future-stage facts early.**

The product owner is non-technical. Answers should be short and concrete.

## Facts available from stage 1 onward

- This is initially for a small team, roughly 3–10 people.
- One person runs the CLI on one machine for the first version.
- Team members can be represented by a stable ID plus a display name; login/authentication is not required.
- Tasks need a stable ID, title, description, assignee (which may initially be empty), and status.
- Deleting tasks, due dates, priorities, notifications, multi-user networking, permissions, and a GUI are not required.
- Reliability matters enough that normal application restart must not lose data.
- The owner does not have an opinion about architecture patterns or the concrete local persistence format.

## Additional facts available only after stage 2 is revealed

- AI agents and humans are both things that can be assigned work, but only AI agents can execute through the application.
- An AI execution result only needs: task ID, agent ID, success/failure, and text output.
- Re-running an AI task may create another execution record; retaining execution history is acceptable.
- Provider/model configuration belongs to the AI agent, not to each task.
- No real provider authentication, billing, streaming, or network retry behavior is needed.

## Additional facts available only after stage 3 is revealed

- The user chooses storage when launching the CLI; runtime switching inside one process is not needed.
- Existing users should not lose the current storage option.
- The second backend should be meaningfully different from the first; the experiment does not care whether SQLite or JSON came first.
- Automatic migration between storage formats is not required.
- Equivalent observable task behavior across both backends is important.

## Additional facts available only after stage 4 is revealed

- Dependency graphs are expected to be small.
- Direct or indirect dependency cycles are invalid and should be rejected.
- A blocked task stays in `todo`.
- Changing a prerequisite back from `done` after a dependent task has already started does not need special handling in this experiment.
