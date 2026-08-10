"""Behavioral tests for the task manager.

The stage 1-2 behavior (create, assign human/agent, status workflow, execution
history, restart durability) is written once as backend-agnostic mixins and run
against BOTH storage backends -- JSON file and SQLite -- by generating a concrete
TestCase per (behavior, backend) pair. Restart is simulated by building a fresh
manager over the same data file; the CLI tests additionally prove it across
genuinely separate OS processes.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Make the package importable when run as `python -m unittest` from the repo.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tasktool.manager import (  # noqa: E402
    AgentNotFoundError,
    PrerequisiteError,
    TaskManager,
    TaskNotFoundError,
    _reaches,
)
from tasktool.models import AgentAssignee, HumanAssignee, Status, Task  # noqa: E402
from tasktool.sqlite_store import SqliteTaskStore  # noqa: E402
from tasktool.store import JsonTaskStore  # noqa: E402


# --------------------------------------------------------------------------
# Backend fixtures: each provides a temp data file and a make_manager() that
# reopens the same store (i.e. a "restart").
# --------------------------------------------------------------------------


class _ManagerBackend(unittest.TestCase):
    filename = "tasks.data"

    def make_store(self):  # pragma: no cover - overridden
        raise NotImplementedError

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data_file = Path(self._tmp.name) / self.filename
        self.addCleanup(self._tmp.cleanup)

    def make_manager(self) -> TaskManager:
        return TaskManager(self.make_store())


class JsonManagerBackend(_ManagerBackend):
    filename = "tasks.json"

    def make_store(self):
        return JsonTaskStore(self.data_file)


class SqliteManagerBackend(_ManagerBackend):
    filename = "tasks.db"

    def make_store(self):
        return SqliteTaskStore(self.data_file)


_MANAGER_BACKENDS = [("Json", JsonManagerBackend), ("Sqlite", SqliteManagerBackend)]


def _failing_runner(agent, task):
    return False, f"{agent.model} could not complete task {task.id}"


# --------------------------------------------------------------------------
# Backend-agnostic behavior mixins. They rely only on self.make_manager()
# and unittest assertions; they never mention a concrete store.
# --------------------------------------------------------------------------


class CreateAndListMixin:
    def test_create_task_starts_todo_and_unassigned(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Prepare weekly report", "Cover last week's metrics")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.status, Status.TODO)
        self.assertIsNone(task.assignee)
        self.assertEqual(task.description, "Cover last week's metrics")

    def test_ids_increment(self) -> None:
        mgr = self.make_manager()
        first = mgr.create_task("A")
        second = mgr.create_task("B")
        self.assertEqual((first.id, second.id), (1, 2))

    def test_empty_title_rejected(self) -> None:
        mgr = self.make_manager()
        with self.assertRaises(ValueError):
            mgr.create_task("   ")

    def test_list_is_ordered_by_id(self) -> None:
        mgr = self.make_manager()
        for title in ("A", "B", "C"):
            mgr.create_task(title)
        self.assertEqual([t.title for t in mgr.list_tasks()], ["A", "B", "C"])


class AssignmentMixin:
    def test_assign_records_member_id_and_display_name(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Prepare weekly report")
        mgr.assign(task.id, member_id="m-42", display_name="Dana")
        self.assertEqual(task.assignee.member_id, "m-42")
        self.assertEqual(task.assignee.display_name, "Dana")

    def test_display_name_is_snapshotted_at_assignment(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        mgr.assign(task.id, "m-1", "Danny")
        mgr.assign(task.id, "m-1", "Daniel")
        self.assertEqual(task.assignee.display_name, "Daniel")

    def test_reassign_to_different_member(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        mgr.assign(task.id, "m-1", "Alice")
        mgr.assign(task.id, "m-2", "Bob")
        self.assertEqual(task.assignee.member_id, "m-2")
        self.assertEqual(task.assignee.display_name, "Bob")

    def test_assign_missing_task_raises(self) -> None:
        mgr = self.make_manager()
        with self.assertRaises(TaskNotFoundError):
            mgr.assign(999, "m-1", "Nobody")

    def test_blank_display_name_rejected(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        with self.assertRaises(ValueError):
            mgr.assign(task.id, "m-1", "  ")


class StatusWorkflowMixin:
    def test_advance_through_full_workflow(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        self.assertEqual(task.status, Status.TODO)
        mgr.advance(task.id)
        self.assertEqual(task.status, Status.IN_PROGRESS)
        mgr.advance(task.id)
        self.assertEqual(task.status, Status.DONE)

    def test_cannot_advance_past_done(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        mgr.advance(task.id)
        mgr.advance(task.id)
        with self.assertRaises(ValueError):
            mgr.advance(task.id)


class PersistenceMixin:
    def test_state_survives_restart(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Prepare weekly report", "desc")
        mgr.assign(task.id, "m-7", "Eli")
        mgr.advance(task.id)

        reloaded = self.make_manager()  # fresh store over the same file == restart
        again = reloaded.get(task.id)
        self.assertEqual(again.title, "Prepare weekly report")
        self.assertEqual(again.description, "desc")
        self.assertEqual(again.status, Status.IN_PROGRESS)
        self.assertEqual(again.assignee.member_id, "m-7")
        self.assertEqual(again.assignee.display_name, "Eli")

    def test_next_id_persists_so_ids_do_not_collide(self) -> None:
        mgr = self.make_manager()
        mgr.create_task("A")
        mgr.create_task("B")
        reloaded = self.make_manager()
        third = reloaded.create_task("C")
        self.assertEqual(third.id, 3)


class AgentMixin:
    def test_create_agent_gets_stable_id_and_properties(self) -> None:
        mgr = self.make_manager()
        agent = mgr.create_agent(provider="openai", model="gpt-4o")
        self.assertEqual(agent.id, "agent-1")
        self.assertEqual(agent.provider, "openai")
        self.assertEqual(agent.model, "gpt-4o")

    def test_agent_survives_restart(self) -> None:
        mgr = self.make_manager()
        agent = mgr.create_agent("anthropic", "claude-3")
        reloaded = self.make_manager()
        again = reloaded.get_agent(agent.id)
        self.assertEqual((again.provider, again.model), ("anthropic", "claude-3"))

    def test_agent_ids_do_not_collide_after_restart(self) -> None:
        mgr = self.make_manager()
        mgr.create_agent("openai", "gpt-4o")
        reloaded = self.make_manager()
        second = reloaded.create_agent("openai", "gpt-4o-mini")
        self.assertEqual(second.id, "agent-2")

    def test_blank_provider_or_model_rejected(self) -> None:
        mgr = self.make_manager()
        with self.assertRaises(ValueError):
            mgr.create_agent("", "gpt-4o")
        with self.assertRaises(ValueError):
            mgr.create_agent("openai", " ")


class AgentAssignmentMixin:
    def test_assign_task_to_agent(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Draft blog post")
        agent = mgr.create_agent("openai", "gpt-4o")
        mgr.assign_agent(task.id, agent.id)
        self.assertIsInstance(task.assignee, AgentAssignee)
        self.assertEqual(task.assignee.agent_id, agent.id)

    def test_assign_agent_requires_existing_agent(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        with self.assertRaises(AgentNotFoundError):
            mgr.assign_agent(task.id, "agent-nope")

    def test_agent_assignment_survives_restart(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("anthropic", "claude-3")
        mgr.assign_agent(task.id, agent.id)

        reloaded = self.make_manager()
        again = reloaded.get(task.id)
        self.assertIsInstance(again.assignee, AgentAssignee)
        self.assertEqual(again.assignee.agent_id, agent.id)

    def test_human_and_agent_assignment_are_mutually_exclusive(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        mgr.assign(task.id, "m-1", "Alice")
        mgr.assign_agent(task.id, agent.id)
        self.assertIsInstance(task.assignee, AgentAssignee)
        mgr.assign(task.id, "m-2", "Bob")  # switching back replaces the agent
        self.assertIsInstance(task.assignee, HumanAssignee)


class ExecutionMixin:
    def test_execute_success_records_result(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        result = mgr.execute(task.id, agent.id)
        self.assertTrue(result.success)
        self.assertEqual(result.task_id, task.id)
        self.assertEqual(result.agent_id, agent.id)
        self.assertTrue(result.output)

    def test_execute_failure_records_result(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        result = mgr.execute(task.id, agent.id, runner=_failing_runner)
        self.assertFalse(result.success)
        self.assertIn("could not complete", result.output)

    def test_repeated_executions_accumulate_as_history(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        mgr.execute(task.id, agent.id)
        mgr.execute(task.id, agent.id, runner=_failing_runner)
        mgr.execute(task.id, agent.id)
        self.assertEqual(len(task.executions), 3)
        self.assertEqual([e.success for e in task.executions], [True, False, True])

    def test_execute_requires_existing_task_and_agent(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        with self.assertRaises(TaskNotFoundError):
            mgr.execute(999, agent.id)
        with self.assertRaises(AgentNotFoundError):
            mgr.execute(task.id, "agent-nope")

    def test_execution_history_survives_restart(self) -> None:
        mgr = self.make_manager()
        task = mgr.create_task("Task")
        agent = mgr.create_agent("openai", "gpt-4o")
        mgr.execute(task.id, agent.id)
        mgr.execute(task.id, agent.id, runner=_failing_runner)

        reloaded = self.make_manager()
        again = reloaded.get(task.id)
        self.assertEqual(len(again.executions), 2)
        self.assertEqual([e.success for e in again.executions], [True, False])
        self.assertEqual(again.executions[0].agent_id, agent.id)


class PrerequisiteMixin:
    def test_create_with_prerequisites_records_them(self) -> None:
        mgr = self.make_manager()
        a = mgr.create_task("A")
        b = mgr.create_task("B")
        c = mgr.create_task("C", prerequisites=[a.id, b.id])
        self.assertEqual(c.prerequisites, [a.id, b.id])

    def test_task_without_prerequisites_is_ready(self) -> None:
        mgr = self.make_manager()
        self.assertTrue(mgr.is_ready(mgr.create_task("solo")))

    def test_unknown_prerequisite_rejected(self) -> None:
        mgr = self.make_manager()
        with self.assertRaises(PrerequisiteError):
            mgr.create_task("X", prerequisites=[999])

    def test_blocked_until_all_prerequisites_done(self) -> None:
        mgr = self.make_manager()
        a = mgr.create_task("A")
        b = mgr.create_task("B")
        c = mgr.create_task("C", prerequisites=[a.id, b.id])
        self.assertFalse(mgr.is_ready(c))
        self.assertEqual(mgr.unmet_prerequisites(c), [a.id, b.id])

        mgr.advance(a.id)  # todo -> in progress
        mgr.advance(a.id)  # in progress -> done
        self.assertEqual(mgr.unmet_prerequisites(c), [b.id])
        self.assertFalse(mgr.is_ready(c))

        mgr.advance(b.id)
        mgr.advance(b.id)
        self.assertTrue(mgr.is_ready(c))

    def test_self_dependency_rejected(self) -> None:
        mgr = self.make_manager()
        # The new task's id will be 1; depending on itself is a direct cycle.
        with self.assertRaises(PrerequisiteError):
            mgr.create_task("loop", prerequisites=[1])

    def test_indirect_cycle_rejected(self) -> None:
        mgr = self.make_manager()
        a = mgr.create_task("A")
        b = mgr.create_task("B", prerequisites=[a.id])
        # The public API cannot build an indirect cycle (prereqs reference only
        # existing tasks and are immutable), so force a back-edge to prove the
        # guard is transitive: make A depend on C's future id (3).
        mgr.get(a.id).prerequisites.append(3)
        with self.assertRaises(PrerequisiteError):
            mgr.create_task("C", prerequisites=[b.id])  # 3->2->1->3

    def test_prerequisites_persist_and_readiness_recomputed_after_restart(
        self,
    ) -> None:
        mgr = self.make_manager()
        a = mgr.create_task("A")
        c = mgr.create_task("C", prerequisites=[a.id])

        reloaded = self.make_manager()  # restart
        again = reloaded.get(c.id)
        self.assertEqual(again.prerequisites, [a.id])
        self.assertFalse(reloaded.is_ready(again))  # A still todo
        reloaded.advance(a.id)
        reloaded.advance(a.id)  # A -> done (persisted)

        final = self.make_manager()  # restart again; readiness from stored status
        self.assertEqual(final.get(c.id).prerequisites, [a.id])
        self.assertTrue(final.is_ready(final.get(c.id)))


_BEHAVIOR_MIXINS = [
    CreateAndListMixin,
    AssignmentMixin,
    StatusWorkflowMixin,
    PersistenceMixin,
    AgentMixin,
    AgentAssignmentMixin,
    ExecutionMixin,
    PrerequisiteMixin,
]

# Generate one concrete TestCase per (behavior, backend): e.g. ExecutionSqlite.
for _mixin in _BEHAVIOR_MIXINS:
    for _suffix, _backend in _MANAGER_BACKENDS:
        _name = _mixin.__name__.replace("Mixin", "") + _suffix
        globals()[_name] = type(_name, (_mixin, _backend), {})


# --------------------------------------------------------------------------
# Backend-specific and pure-model tests (not parametrized).
# --------------------------------------------------------------------------


class JsonFormatTests(JsonManagerBackend):
    def test_on_disk_format_is_readable_json(self) -> None:
        mgr = self.make_manager()
        mgr.create_task("A")
        raw = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(raw["version"], 2)
        self.assertEqual(len(raw["tasks"]), 1)


class SqliteFormatTests(SqliteManagerBackend):
    def test_data_lands_in_real_tables(self) -> None:
        import sqlite3

        mgr = self.make_manager()
        task = mgr.create_task("A")
        agent = mgr.create_agent("openai", "gpt-4o")
        mgr.assign_agent(task.id, agent.id)
        mgr.execute(task.id, agent.id)

        conn = sqlite3.connect(self.data_file)
        try:
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 1
            )
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0], 1
            )
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0], 1
            )
        finally:
            conn.close()


class ModelSerializationTests(unittest.TestCase):
    def test_task_round_trips_through_dict(self) -> None:
        task = Task(id=5, title="T", description="d", status=Status.DONE)
        task.assign_human("m-9", "Zoe")
        restored = Task.from_dict(task.to_dict())
        self.assertEqual(restored, task)

    def test_unassigned_task_round_trips(self) -> None:
        task = Task(id=1, title="T")
        self.assertIsNone(Task.from_dict(task.to_dict()).assignee)


class ReachabilityTests(unittest.TestCase):
    """The pure graph helper that backs indirect-cycle detection."""

    def test_direct_reach(self) -> None:
        self.assertTrue(_reaches([1], 2, {1: [2]}))

    def test_indirect_reach(self) -> None:
        self.assertTrue(_reaches([1], 3, {1: [2], 2: [3]}))

    def test_no_reach(self) -> None:
        self.assertFalse(_reaches([1], 9, {1: [2], 2: [3]}))

    def test_terminates_on_existing_cycle(self) -> None:
        # Must not loop forever even if the graph itself contains a cycle.
        self.assertFalse(_reaches([1], 9, {1: [2], 2: [1]}))


class LegacyDataTests(unittest.TestCase):
    """A stage-1 JSON data file (no agents, assignee without 'kind') must load."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data_file = Path(self._tmp.name) / "tasks.json"
        self.addCleanup(self._tmp.cleanup)

    def test_v1_file_loads_and_human_assignee_survives(self) -> None:
        legacy = {
            "version": 1,
            "next_id": 2,
            "tasks": [
                {
                    "id": 1,
                    "title": "Old task",
                    "description": "",
                    "status": "todo",
                    "assignee": {"member_id": "m-1", "display_name": "Legacy Lee"},
                }
            ],
        }
        self.data_file.write_text(json.dumps(legacy), encoding="utf-8")
        mgr = TaskManager(JsonTaskStore(self.data_file))
        task = mgr.get(1)
        self.assertIsInstance(task.assignee, HumanAssignee)
        self.assertEqual(task.assignee.display_name, "Legacy Lee")
        self.assertEqual(mgr.create_agent("openai", "gpt-4o").id, "agent-1")


# --------------------------------------------------------------------------
# CLI tests in genuinely separate OS processes, run against both backends.
# --------------------------------------------------------------------------


class _CliBackend(unittest.TestCase):
    backend = "json"
    filename = "tasks.json"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data_file = Path(self._tmp.name) / self.filename
        self.addCleanup(self._tmp.cleanup)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        env = dict(
            os.environ,
            TASKTOOL_DATA=str(self.data_file),
            TASKTOOL_BACKEND=self.backend,
        )
        return subprocess.run(
            [sys.executable, "-m", "tasktool", *args],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
        )


class CliJsonBackend(_CliBackend):
    backend = "json"
    filename = "tasks.json"


class CliSqliteBackend(_CliBackend):
    backend = "sqlite"
    filename = "tasks.db"


class CliMixin:
    def test_full_flow_across_separate_processes(self) -> None:
        self.assertEqual(self.run_cli("add", "Prepare weekly report").returncode, 0)
        self.assertEqual(
            self.run_cli(
                "assign", "1", "--member-id", "m-3", "--name", "Dana"
            ).returncode,
            0,
        )
        self.assertEqual(self.run_cli("advance", "1").returncode, 0)

        listed = self.run_cli("list")
        self.assertEqual(listed.returncode, 0)
        self.assertIn("Prepare weekly report", listed.stdout)
        self.assertIn("Dana", listed.stdout)
        self.assertIn("in progress", listed.stdout)

    def test_unassigned_task_shown_as_unassigned(self) -> None:
        self.run_cli("add", "Lonely task")
        listed = self.run_cli("list")
        self.assertIn("(unassigned)", listed.stdout)

    def test_error_exit_code_for_missing_task(self) -> None:
        result = self.run_cli("advance", "42")
        self.assertEqual(result.returncode, 1)
        self.assertIn("No task with id 42", result.stderr)

    def test_agent_flow_across_separate_processes(self) -> None:
        self.assertEqual(self.run_cli("add", "Draft blog post").returncode, 0)
        created = self.run_cli(
            "add-agent", "--provider", "openai", "--model", "gpt-4o"
        )
        self.assertIn("agent-1", created.stdout)
        self.assertEqual(
            self.run_cli("assign-agent", "1", "--agent-id", "agent-1").returncode, 0
        )
        # Execute twice; --agent-id omitted the second time -> uses assigned agent.
        self.assertEqual(
            self.run_cli("execute", "1", "--agent-id", "agent-1").returncode, 0
        )
        self.assertEqual(self.run_cli("execute", "1").returncode, 0)

        listed = self.run_cli("list")
        self.assertIn("agent-1 [openai/gpt-4o]", listed.stdout)
        self.assertIn("execs:2", listed.stdout)

        agents = self.run_cli("list-agents")
        self.assertIn("agent-1: openai/gpt-4o", agents.stdout)

    def test_prerequisites_flow_across_separate_processes(self) -> None:
        self.assertEqual(self.run_cli("add", "Design").returncode, 0)  # task 1
        created = self.run_cli("add", "Build", "--depends-on", "1")  # task 2
        self.assertIn("depends on 1", created.stdout)

        blocked = self.run_cli("list")
        self.assertIn("BLOCKED(needs 1)", blocked.stdout)

        self.run_cli("advance", "1")  # todo -> in progress
        self.run_cli("advance", "1")  # in progress -> done

        ready = self.run_cli("list")
        self.assertIn("READY", ready.stdout)
        self.assertNotIn("BLOCKED", ready.stdout)

        shown = self.run_cli("show", "2")
        self.assertIn("prerequisites: [1] -> ready", shown.stdout)

    def test_unknown_prerequisite_rejected_via_cli(self) -> None:
        result = self.run_cli("add", "X", "--depends-on", "999")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown prerequisite", result.stderr)


for _suffix, _backend in [("Json", CliJsonBackend), ("Sqlite", CliSqliteBackend)]:
    _name = "Cli" + _suffix
    globals()[_name] = type(_name, (CliMixin, _backend), {})


if __name__ == "__main__":
    unittest.main()
