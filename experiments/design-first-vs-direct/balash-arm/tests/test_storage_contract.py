"""The proof that the two backends behave identically.

One backend-agnostic contract suite, written purely against the ``StorageBackend`` port
and the four repository ports, with a single ``make_backend()`` hook. It is subclassed
once per backend (JSON and SQLite). Any behavioral divergence between the two stores
fails exactly one subclass -- that is the mechanical proof of behavior-identity, not a
promise of it.

Nothing in ``StorageContractTests`` mentions a file, a table, a column, or SQL: it
speaks only the ports and domain objects, exactly as the services do. The one place the
backends are named is the two tiny subclasses at the bottom.
"""

import tempfile
import unittest
from pathlib import Path

from taskcli.domain import (
    Agent,
    AgentId,
    AssigneeRef,
    ExecutionResult,
    Member,
    MemberId,
    Status,
    Task,
    TaskId,
    TaskNotFoundError,
    UnknownAgentError,
    UnknownMemberError,
)
from taskcli.storage import JsonStorage, SqliteStorage


class StorageContractTests:
    """Abstract -- no TestCase base, so it is not collected on its own. Each concrete
    subclass mixes in unittest.TestCase and overrides make_backend()."""

    def make_backend(self):
        raise NotImplementedError

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._tmp = Path(self._dir.name)
        self.backend = self.make_backend()

    def tearDown(self):
        self._dir.cleanup()

    # --- helpers ---

    @staticmethod
    def _a_task(task_id="t1", title="Ship it", description="do it", assignee=None):
        return Task(
            task_id=TaskId(task_id),
            title=title,
            description=description,
            status=Status.TODO,
            assignee=assignee,
        )

    def _assertSameTask(self, actual, expected):
        self.assertEqual(actual.id.value, expected.id.value)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.description, expected.description)
        self.assertEqual(actual.status, expected.status)
        self.assertEqual(actual.assignee, expected.assignee)  # AssigneeRef.__eq__ / None

    # --- tasks ---

    def test_add_then_get_returns_an_equal_task(self):
        tasks = self.backend.tasks()
        task = self._a_task()
        tasks.add(task)
        self._assertSameTask(tasks.get(TaskId("t1")), task)

    def test_get_unknown_task_raises_TaskNotFoundError(self):
        with self.assertRaises(TaskNotFoundError):
            self.backend.tasks().get(TaskId("nope"))

    def test_save_existing_task_persists_changes(self):
        tasks = self.backend.tasks()
        tasks.add(self._a_task())
        changed = self._a_task(title="Renamed", description="new", assignee=None)
        changed.change_status(Status.DONE)
        tasks.save(changed)
        reloaded = tasks.get(TaskId("t1"))
        self.assertEqual(reloaded.title, "Renamed")
        self.assertEqual(reloaded.description, "new")
        self.assertEqual(reloaded.status, Status.DONE)

    def test_save_absent_task_raises_TaskNotFoundError(self):
        with self.assertRaises(TaskNotFoundError):
            self.backend.tasks().save(self._a_task(task_id="ghost"))

    def test_all_returns_everything_added(self):
        tasks = self.backend.tasks()
        tasks.add(self._a_task(task_id="a", title="a"))
        tasks.add(self._a_task(task_id="b", title="b"))
        got = {t.id.value for t in tasks.all()}
        self.assertEqual(got, {"a", "b"})

    def test_assignee_roundtrips_for_all_three_forms(self):
        tasks = self.backend.tasks()
        forms = {
            "unassigned": None,
            "member": AssigneeRef.member(MemberId("alice")),
            "agent": AssigneeRef.agent(AgentId("gpt")),
        }
        for task_id, assignee in forms.items():
            tasks.add(self._a_task(task_id=task_id, assignee=assignee))
        for task_id, assignee in forms.items():
            self.assertEqual(tasks.get(TaskId(task_id)).assignee, assignee)

    # --- members ---

    def test_member_add_and_team_roundtrip(self):
        members = self.backend.members()
        members.add(Member(id=MemberId("alice"), display_name="Alice Ng"))
        team = members.team()
        self.assertTrue(team.knows(MemberId("alice")))
        self.assertEqual(team.display_name_for(MemberId("alice")), "Alice Ng")

    def test_member_add_is_upsert_by_id(self):
        members = self.backend.members()
        members.add(Member(id=MemberId("alice"), display_name="Alice Ng"))
        members.add(Member(id=MemberId("alice"), display_name="Alice Renamed"))
        team = members.team()
        self.assertEqual(len(team.roster()), 1)  # not two rows
        self.assertEqual(team.display_name_for(MemberId("alice")), "Alice Renamed")

    def test_unknown_member_raises_UnknownMemberError(self):
        with self.assertRaises(UnknownMemberError):
            self.backend.members().team().member(MemberId("ghost"))

    # --- agents ---

    def test_agent_add_and_registry_roundtrip_including_provider_and_model(self):
        agents = self.backend.agents()
        agents.add(
            Agent(
                id=AgentId("gpt"),
                display_name="Assistant",
                provider_name="openai",
                model_name="gpt-4",
            )
        )
        agent = self.backend.agents().registry().agent(AgentId("gpt"))
        self.assertEqual(agent.display_name, "Assistant")
        self.assertEqual(agent.provider_name, "openai")
        self.assertEqual(agent.model_name, "gpt-4")

    def test_agent_add_is_upsert_by_id(self):
        agents = self.backend.agents()
        agents.add(Agent(AgentId("gpt"), "Assistant", "openai", "gpt-4"))
        agents.add(Agent(AgentId("gpt"), "Renamed", "anthropic", "claude"))
        registry = agents.registry()
        self.assertEqual(len(registry.roster()), 1)
        again = registry.agent(AgentId("gpt"))
        self.assertEqual(again.display_name, "Renamed")
        self.assertEqual(again.provider_name, "anthropic")
        self.assertEqual(again.model_name, "claude")

    def test_unknown_agent_is_not_known_and_raises_UnknownAgentError(self):
        registry = self.backend.agents().registry()
        self.assertFalse(registry.knows(AgentId("ghost")))
        with self.assertRaises(UnknownAgentError):
            registry.agent(AgentId("ghost"))

    # --- results (append-only history) ---

    def _result(self, task_id="t1", agent_id="gpt", succeeded=True, output="ok"):
        return ExecutionResult(
            task_id=TaskId(task_id),
            agent_id=AgentId(agent_id),
            succeeded=succeeded,
            output=output,
        )

    def test_append_then_for_task_returns_the_result(self):
        results = self.backend.results()
        results.append(self._result(output="only"))
        got = results.for_task(TaskId("t1"))
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0].output, "only")
        self.assertTrue(got[0].succeeded)

    def test_multiple_appends_come_back_oldest_first(self):
        results = self.backend.results()
        results.append(self._result(output="first"))
        results.append(self._result(output="second"))
        results.append(self._result(output="third"))
        outputs = [r.output for r in results.for_task(TaskId("t1"))]
        self.assertEqual(outputs, ["first", "second", "third"])

    def test_reappend_never_overwrites_and_for_task_filters_by_id(self):
        results = self.backend.results()
        results.append(self._result(task_id="t1", output="a"))
        results.append(self._result(task_id="t1", output="b"))
        results.append(self._result(task_id="t2", output="other"))
        self.assertEqual(len(results.for_task(TaskId("t1"))), 2)  # count grew, no overwrite
        self.assertEqual([r.output for r in results.for_task(TaskId("t2"))], ["other"])

    def test_succeeded_flag_roundtrips_both_values(self):
        results = self.backend.results()
        results.append(self._result(output="win", succeeded=True))
        results.append(self._result(output="lose", succeeded=False))
        by_output = {r.output: r.succeeded for r in results.for_task(TaskId("t1"))}
        self.assertIs(by_output["win"], True)
        self.assertIs(by_output["lose"], False)

    # --- cross-cutting: read-tolerance parity (pins the no-FK decision, DS4) ---

    def test_task_with_dangling_member_assignee_still_loads(self):
        # A task assigned to a member id that is NOT present in the members table --
        # the exact situation a since-removed member leaves behind. With a foreign key
        # SQLite would reject this row; JSON tolerates it. The no-FK decision keeps them
        # identical: both backends must store and reload the dangling reference.
        tasks = self.backend.tasks()
        dangling = AssigneeRef.member(MemberId("removed-member"))
        tasks.add(self._a_task(task_id="d1", assignee=dangling))
        self.assertEqual(tasks.get(TaskId("d1")).assignee, dangling)
        self.assertEqual(self.backend.members().team().roster(), [])  # truly absent
        self.assertEqual(
            [t.assignee for t in tasks.all() if t.id.value == "d1"], [dangling]
        )

    def test_task_with_dangling_agent_assignee_still_loads(self):
        tasks = self.backend.tasks()
        dangling = AssigneeRef.agent(AgentId("removed-agent"))
        tasks.add(self._a_task(task_id="d2", assignee=dangling))
        self.assertEqual(tasks.get(TaskId("d2")).assignee, dangling)
        self.assertFalse(
            self.backend.agents().registry().knows(AgentId("removed-agent"))
        )


class JsonStorageContractTests(StorageContractTests, unittest.TestCase):
    def make_backend(self):
        return JsonStorage(self._tmp)


class SqliteStorageContractTests(StorageContractTests, unittest.TestCase):
    def make_backend(self):
        return SqliteStorage(self._tmp / "taskcli.db")


if __name__ == "__main__":
    unittest.main()
