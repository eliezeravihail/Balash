Tasks can now depend on other tasks.

A task may have zero or more prerequisite tasks. A task must not be moved to `in progress`, and an AI agent must not execute it, until all of its prerequisites are `done`.

The application should clearly report why a blocked task cannot start. Existing tasks with no prerequisites should continue to behave as before.
