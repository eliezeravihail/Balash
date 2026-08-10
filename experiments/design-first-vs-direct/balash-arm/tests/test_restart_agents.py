"""Stage-2 restart survival: an agent registered in one process, and execution results
written in one process, must be readable by a later, separate process. Same
separate-process style as the stage-1 restart test -- each step is its own OS process
against a shared data directory, so a pass is real evidence the new persistence seams
survive a full application restart."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AgentRestartSurvivalTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._dir.name)
        self.repo_root = Path(__file__).resolve().parent.parent

    def tearDown(self):
        self._dir.cleanup()

    def run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "taskcli", "--data-dir", str(self.data_dir), *args],
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
            [sys.executable, "-m", "taskcli", "--data-dir", str(self.data_dir), *args],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        return result.stderr.strip()

    def _created_id(self, output):
        return output.split()[-1]

    def test_agent_and_results_survive_across_separate_processes(self):
        # Process 1: register an agent.
        self.run_cli("add-agent", "--id", "gpt", "--name", "Assistant",
                     "--provider", "openai", "--model", "gpt-4")

        # Process 2: a fresh process still sees the agent.
        agents = self.run_cli("agents")
        self.assertIn("gpt", agents)
        self.assertIn("Assistant", agents)

        # Process 3: create a task and assign it to the agent.
        task_id = self._created_id(
            self.run_cli("create", "--title", "Ship it", "--description", "write the code")
        )
        self.run_cli("assign-agent", task_id, "--to", "gpt")

        # Process 4: a fresh process resolves the agent's display name.
        self.assertIn("Assistant", self.run_cli("show", task_id))

        # Process 5 and 6: execute twice, each its own process.
        self.assertIn("succeeded", self.run_cli("execute", task_id))
        self.assertIn("succeeded", self.run_cli("execute", task_id))

        # Process 7: a fresh process reads back the append-only history -- both runs.
        history = self.run_cli("history", task_id)
        self.assertIn("1.", history)
        self.assertIn("2.", history)
        self.assertIn("write the code", history)

    def test_execute_gate_rejections_persist_nothing_across_processes(self):
        task_id = self._created_id(
            self.run_cli("create", "--title", "t", "--description", "d")
        )
        # Unassigned: refused.
        self.run_cli_expecting_failure("execute", task_id)
        # And a fresh process sees no history.
        self.assertIn("no executions yet", self.run_cli("history", task_id))


if __name__ == "__main__":
    unittest.main()
