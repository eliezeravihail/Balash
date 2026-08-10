"""The load-bearing test: state written by one process invocation must be readable by
a later, separate one.

Each step runs `python -m taskcli ...` as its own OS process against a shared data
directory. Nothing is held in memory between steps -- the only thing connecting them
is what landed on disk -- so a pass here is real evidence that the persistence seam
survives a full application restart, not just object reuse within one interpreter.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RestartSurvivalTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._dir.name)
        self.repo_root = Path(__file__).resolve().parent.parent

    def tearDown(self):
        self._dir.cleanup()

    def run_cli(self, *args):
        """Run the CLI as a brand-new process. Returns stdout (stripped)."""
        result = subprocess.run(
            [sys.executable, "-m", "taskcli", "--data-dir", str(self.data_dir), *args],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"command {args} failed: {result.stderr}",
        )
        return result.stdout.strip()

    def run_cli_expecting_failure(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "taskcli", "--data-dir", str(self.data_dir), *args],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        return result.stderr.strip()

    def _created_id(self, output):
        # "created task <id>"
        return output.split()[-1]

    def test_full_lifecycle_survives_across_separate_processes(self):
        # Process 1: build the team.
        self.run_cli("add-member", "--id", "alice", "--name", "Alice Ng")
        self.run_cli("add-member", "--id", "bob", "--name", "Bob Reyes")

        # Process 2: create a task.
        created = self.run_cli("create", "--title", "Design the seam", "--description", "first slice")
        task_id = self._created_id(created)

        # Process 3: assign it.
        self.run_cli("assign", task_id, "--to", "alice")

        # Process 4: move it along.
        self.run_cli("status", task_id, "in progress")

        # Process 5 (a fresh process that shared nothing in memory with the above):
        # read it back and confirm every change persisted.
        detail = self.run_cli("show", task_id)
        self.assertIn("Design the seam", detail)
        self.assertIn("in progress", detail)
        self.assertIn("Alice Ng", detail)  # resolved display name, not the raw id

        listing = self.run_cli("list")
        self.assertIn(task_id, listing)
        self.assertIn("Alice Ng", listing)

    def test_reassign_and_reopen_persist(self):
        self.run_cli("add-member", "--id", "alice", "--name", "Alice Ng")
        self.run_cli("add-member", "--id", "bob", "--name", "Bob Reyes")
        task_id = self._created_id(self.run_cli("create", "--title", "t", "--description", "d"))

        self.run_cli("assign", task_id, "--to", "alice")
        self.run_cli("status", task_id, "done")
        # ... restart ... reassign and reopen in later processes
        self.run_cli("assign", task_id, "--to", "bob")
        self.run_cli("status", task_id, "todo")

        detail = self.run_cli("show", task_id)
        self.assertIn("Bob Reyes", detail)
        self.assertIn("todo", detail)

    def test_prerequisites_persist_and_block_until_done_across_processes(self):
        # Process 1 & 2: a task, then a second task that depends on it.
        dep = self._created_id(self.run_cli("create", "--title", "groundwork", "--description", ""))
        main = self._created_id(
            self.run_cli("create", "--title", "the feature", "--description", "", "--needs", dep)
        )

        # A fresh process reads the dependent back as blocked, naming its prerequisite.
        detail = self.run_cli("show", main)
        self.assertIn("blocked", detail)
        self.assertIn(dep, detail)  # the prerequisite id survived the restart

        # Finish the prerequisite; a later, separate process now sees it as ready.
        self.run_cli("status", dep, "done")
        self.assertIn("ready", self.run_cli("show", main))

    def test_creating_with_an_unknown_prerequisite_is_rejected_across_processes(self):
        stderr = self.run_cli_expecting_failure(
            "create", "--title", "x", "--description", "", "--needs", "ghost"
        )
        self.assertIn("ghost", stderr)
        # the rejection created nothing, verified by a fresh process
        self.assertIn("no tasks yet", self.run_cli("list"))

    def test_assign_to_unknown_member_is_rejected_across_processes(self):
        task_id = self._created_id(self.run_cli("create", "--title", "t", "--description", "d"))
        stderr = self.run_cli_expecting_failure("assign", task_id, "--to", "ghost")
        self.assertIn("ghost", stderr)
        # and the rejection left the task unassigned, verified by a fresh process
        detail = self.run_cli("show", task_id)
        self.assertIn("unassigned", detail)


if __name__ == "__main__":
    unittest.main()
