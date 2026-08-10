I want to be able to choose how the application's data is stored.

Keep the persistent storage option you already built, and add a second persistent storage option using a different local format:
- if the current implementation uses JSON files, add SQLite;
- otherwise add a JSON-file storage option.

The user should be able to select either storage option when starting the application.

The task-management behavior should be the same whichever storage option is selected.
