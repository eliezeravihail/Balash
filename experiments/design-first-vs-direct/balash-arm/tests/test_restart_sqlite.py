"""SQLite restart survival -- the same load-bearing check the JSON restart tests make,
but with ``--backend sqlite``.

Each step runs ``python -m taskcli --backend sqlite ...`` as its own OS process against
a shared data directory. Nothing is held in memory between steps; the only thing
connecting them is the ``taskcli.db`` file on disk. A pass here is real evidence that
the SQLite persistence seam survives a full application restart -- a genuine relational
store created on first use, reopened by every later process.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SqliteRestartSurvivalTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._dir.name)
        self.repo_root = Path(__file__).resolve().parent.parent

    def tearDown(self):
        self._dir.cleanup()

    def run_cli(self, *args):
        result = subprocess.run(
            [
                sys.executable, "-m", "taskcli",
                "--data-dir", str(self.data_dir),
                "--backend", "sqlite",
                *args,
            ],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0, msg=f"command {args} failed: {result.stderr}"
        )
        return result.stdout.strip()

    def run_cli_expecting_failure(self, *args):
        result = subprocess.run(
            [
                sys.executable, "-m", "taskcli",
                "--data-dir", str(self.data_dir),
                "--backend", "sqlite",
                *args,
            ],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        return result.stderr.strip()

    def _created_id(self, output):
        return output.split()[-1]

    def test_full_lifecycle_survives_across_separate_processes(self):
        # Process 1 and 2: build the team and register an agent.
        self.run_cli("add-member", "--id", "alice", "--name", "Alice Ng")
        self.run_cli("add-agent", "--id", "gpt", "--name", "Assistant",
                     "--provider", "openai", "--model", "gpt-4")

        # The db file exists after first use -- a real store on disk.
        self.assertTrue((self.data_dir / "taskcli.db").exists())

        # Process 3: create a task; Process 4: assign to a member; Process 5: move it.
        task_id = self._created_id(
            self.run_cli("create", "--title", "Design the seam", "--description", "first slice")
        )
        self.run_cli("assign", task_id, "--to", "alice")
        self.run_cli("status", task_id, "in progress")

        # Process 6 (shared nothing in memory): every change persisted.
        detail = self.run_cli("show", task_id)
        self.assertIn("Design the seam", detail)
        self.assertIn("in progress", detail)
        self.assertIn("Alice Ng", detail)  # resolved display name, not the raw id

        # Reassign to the agent and execute twice, each its own process.
        self.run_cli("assign-agent", task_id, "--to", "gpt")
        self.assertIn("succeeded", self.run_cli("execute", task_id))
        self.assertIn("succeeded", self.run_cli("execute", task_id))

        # Process N: append-only history survives, oldest-first, across restarts.
        history = self.run_cli("history", task_id)
        self.assertIn("1.", history)
        self.assertIn("2.", history)
        self.assertIn("first slice", history)

    def test_assign_to_unknown_member_is_rejected_across_processes(self):
        task_id = self._created_id(
            self.run_cli("create", "--title", "t", "--description", "d")
        )
        stderr = self.run_cli_expecting_failure("assign", task_id, "--to", "ghost")
        self.assertIn("ghost", stderr)
        # The rejection left the task unassigned, verified by a fresh process.
        self.assertIn("unassigned", self.run_cli("show", task_id))


if __name__ == "__main__":
    unittest.main()
