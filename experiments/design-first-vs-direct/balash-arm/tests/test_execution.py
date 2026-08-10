"""Stage-2 execution tests over real (temp-dir) repositories: registering agents,
assigning to them, running the local provider, the execute-gate rejections, and the
append-only history. End to end within one process."""

import tempfile
import unittest
from pathlib import Path

from taskcli.cli import build_execution_service, build_service
from taskcli.domain import TaskNotExecutableError, UnknownAgentError
from taskcli.execution import (
    ExecutionOutcome,
    ExecutionRequest,
    LocalProvider,
)


class LocalProviderTests(unittest.TestCase):
    def test_succeeds_with_instructions_and_is_network_free(self):
        outcome = LocalProvider().run(
            ExecutionRequest("openai", "gpt-4", "Ship it", "write the code")
        )
        self.assertIsInstance(outcome, ExecutionOutcome)
        self.assertTrue(outcome.succeeded)
        self.assertIn("write the code", outcome.output)

    def test_fails_deterministically_without_instructions(self):
        outcome = LocalProvider().run(ExecutionRequest("openai", "gpt-4", "t", "  "))
        self.assertFalse(outcome.succeeded)
        self.assertIn("no instructions", outcome.output)


class ExecutionServiceTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._dir.name)
        self.service = build_service(self.data_dir)
        self.execution = build_execution_service(self.data_dir)

    def tearDown(self):
        self._dir.cleanup()

    def _agent_task(self, description="do the work"):
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        task_id = self.service.create_task("Ship it", description).value
        self.service.assign_task_to_agent(task_id, "gpt")
        return task_id

    def test_execute_success_appends_a_result_with_four_fields(self):
        task_id = self._agent_task()
        result = self.execution.execute(task_id)
        self.assertEqual(result.task_id.value, task_id)
        self.assertEqual(result.agent_id.value, "gpt")
        self.assertTrue(result.succeeded)
        self.assertIn("do the work", result.output)

        history = self.execution.history(task_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].output, result.output)

    def test_rerun_appends_a_second_result_and_keeps_the_first_in_order(self):
        task_id = self._agent_task()
        first = self.execution.execute(task_id)
        second = self.execution.execute(task_id)
        history = self.execution.history(task_id)
        self.assertEqual(len(history), 2)  # nothing overwritten
        self.assertEqual(history[0].output, first.output)
        self.assertEqual(history[1].output, second.output)

    def test_executing_an_unassigned_task_is_refused_and_writes_nothing(self):
        task_id = self.service.create_task("t", "d").value
        with self.assertRaises(TaskNotExecutableError):
            self.execution.execute(task_id)
        self.assertEqual(self.execution.history(task_id), [])

    def test_executing_a_human_assigned_task_is_refused_and_writes_nothing(self):
        self.service.add_member("alice", "Alice")
        task_id = self.service.create_task("t", "d").value
        self.service.assign_task(task_id, "alice")
        with self.assertRaises(TaskNotExecutableError):
            self.execution.execute(task_id)
        self.assertEqual(self.execution.history(task_id), [])

    def test_executing_a_task_whose_agent_is_unknown_is_refused(self):
        # Assign to a real agent, then wipe the registry so the task points at an agent
        # id no longer known -- the gate must raise UnknownAgentError, not run anything.
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        task_id = self.service.create_task("t", "d").value
        self.service.assign_task_to_agent(task_id, "gpt")
        # Wipe the agents store so the assignee id is no longer a known agent.
        (self.data_dir / "agents.json").write_text("[]\n", encoding="utf-8")
        with self.assertRaises(UnknownAgentError):
            self.execution.execute(task_id)
        self.assertEqual(self.execution.history(task_id), [])


if __name__ == "__main__":
    unittest.main()
