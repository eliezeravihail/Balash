"""Stage-2 service tests: agent registration and roster, assigning a task to an agent,
the display path for agents, read-tolerance for a removed agent, kind changes, and
back-compat with a stage-1 bare-string assignee row."""

import json
import tempfile
import unittest
from pathlib import Path

from taskcli.cli import build_service
from taskcli.domain import UnknownAgentError


class AgentServiceTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self._dir.name)
        self.service = build_service(self.data_dir)

    def tearDown(self):
        self._dir.cleanup()

    def test_register_and_list_agents(self):
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        agents = self.service.agents()
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0].id.value, "gpt")
        self.assertEqual(agents[0].display_name, "Assistant")
        self.assertEqual(agents[0].provider_name, "openai")
        self.assertEqual(agents[0].model_name, "gpt-4")

    def test_assign_to_agent_resolves_agent_display_name(self):
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        task_id = self.service.create_task("t", "").value
        self.service.assign_task_to_agent(task_id, "gpt")
        self.assertEqual(self.service.show_task(task_id).assignee, "Assistant")

    def test_assign_to_unknown_agent_is_rejected_and_changes_nothing(self):
        task_id = self.service.create_task("t", "").value
        with self.assertRaises(UnknownAgentError):
            self.service.assign_task_to_agent(task_id, "ghost")
        self.assertEqual(self.service.show_task(task_id).assignee, "unassigned")

    def test_assignee_may_change_between_kinds(self):
        self.service.add_member("alice", "Alice Ng")
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        task_id = self.service.create_task("t", "").value

        self.service.assign_task(task_id, "alice")
        self.assertEqual(self.service.show_task(task_id).assignee, "Alice Ng")

        self.service.assign_task_to_agent(task_id, "gpt")
        self.assertEqual(self.service.show_task(task_id).assignee, "Assistant")

        self.service.assign_task(task_id, "alice")
        self.assertEqual(self.service.show_task(task_id).assignee, "Alice Ng")

        self.service.unassign_task(task_id)
        self.assertEqual(self.service.show_task(task_id).assignee, "unassigned")

    def test_removed_agent_renders_unknown_agent_without_crashing(self):
        self.service.add_agent("gpt", "openai", "gpt-4", "Assistant")
        task_id = self.service.create_task("t", "").value
        self.service.assign_task_to_agent(task_id, "gpt")
        # The agent vanishes from the registry after assignment.
        (self.data_dir / "agents.json").write_text("[]\n", encoding="utf-8")
        # A read must tolerate it rather than crash.
        self.assertEqual(self.service.show_task(task_id).assignee, "gpt (unknown agent)")
        self.assertEqual(len(self.service.list_tasks()), 1)

    def test_stage1_bare_string_assignee_reads_as_a_member(self):
        # Hand-write a task row in the stage-1 shape: "assignee" is a bare id string.
        self.service.add_member("alice", "Alice Ng")
        tasks_path = self.data_dir / "tasks.json"
        tasks_path.write_text(
            json.dumps(
                [
                    {
                        "id": "t1",
                        "title": "legacy",
                        "description": "",
                        "status": "todo",
                        "assignee": "alice",
                    }
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        # It reads as a member assignment, resolving the member's display name.
        self.assertEqual(self.service.show_task("t1").assignee, "Alice Ng")


if __name__ == "__main__":
    unittest.main()
