"""End-to-end evidence that ``--backend sqlite`` and the default JSON produce identical
observable output.

The same representative flow -- create, assign a member, register and assign an agent,
execute, list, show, history -- is driven through the real CLI as separate processes
once per backend, in its own data directory. The only thing that legitimately differs
between the two runs is the randomly minted task id, so it is normalized to ``<ID>``;
after that the two transcripts must be byte-identical. If any command produced different
output on one backend, this test fails.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BackendParityTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def _cli(self, data_dir, backend, *args):
        result = subprocess.run(
            [
                sys.executable, "-m", "taskcli",
                "--data-dir", str(data_dir),
                "--backend", backend,
                *args,
            ],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=f"[{backend}] command {args} failed: {result.stderr}",
        )
        return result.stdout

    def _run_flow(self, backend):
        """Run one representative flow and return a normalized transcript (task id
        replaced by <ID>), so two backends can be compared for identical output."""
        with tempfile.TemporaryDirectory() as name:
            data_dir = Path(name)
            transcript = []

            transcript.append(self._cli(data_dir, backend, "add-member", "--id", "alice", "--name", "Alice Ng"))
            transcript.append(self._cli(data_dir, backend, "add-agent", "--id", "gpt", "--name", "Assistant", "--provider", "openai", "--model", "gpt-4"))

            created = self._cli(data_dir, backend, "create", "--title", "Ship it", "--description", "write the code")
            task_id = created.split()[-1].strip()
            transcript.append(created)

            transcript.append(self._cli(data_dir, backend, "assign", task_id, "--to", "alice"))
            transcript.append(self._cli(data_dir, backend, "show", task_id))
            transcript.append(self._cli(data_dir, backend, "assign-agent", task_id, "--to", "gpt"))
            transcript.append(self._cli(data_dir, backend, "status", task_id, "in progress"))
            transcript.append(self._cli(data_dir, backend, "execute", task_id))
            transcript.append(self._cli(data_dir, backend, "execute", task_id))

            # A dependent task, so the prerequisite/readiness path is exercised through
            # the real CLI on BOTH backends (SQLite's join table included).
            dependent = self._cli(data_dir, backend, "create", "--title", "Follow up", "--description", "after", "--needs", task_id)
            dependent_id = dependent.split()[-1].strip()
            transcript.append(dependent)
            transcript.append(self._cli(data_dir, backend, "show", dependent_id))  # blocked
            transcript.append(self._cli(data_dir, backend, "status", task_id, "done"))
            transcript.append(self._cli(data_dir, backend, "show", dependent_id))  # now ready

            transcript.append(self._cli(data_dir, backend, "list"))
            transcript.append(self._cli(data_dir, backend, "show", task_id))
            transcript.append(self._cli(data_dir, backend, "history", task_id))

            # Normalize the two legitimately-different tokens: the random task ids.
            return [
                chunk.replace(task_id, "<ID>").replace(dependent_id, "<ID2>")
                for chunk in transcript
            ]

    def test_json_and_sqlite_produce_identical_observable_output(self):
        json_transcript = self._run_flow("json")
        sqlite_transcript = self._run_flow("sqlite")
        self.assertEqual(json_transcript, sqlite_transcript)


if __name__ == "__main__":
    unittest.main()
