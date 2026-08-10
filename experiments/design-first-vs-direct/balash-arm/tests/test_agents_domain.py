"""Stage-2 domain tests: the assignee reference, the agent registry, and the single
execute gate own their rules -- exercised directly, with no storage or CLI involved."""

import unittest

from taskcli.domain import (
    Agent,
    AgentId,
    AgentRegistry,
    AssigneeKind,
    AssigneeRef,
    ExecutionResult,
    MemberId,
    TaskId,
    TaskNotExecutableError,
    UnknownAgentError,
)


class AssigneeRefTests(unittest.TestCase):
    def test_member_ref_is_not_an_agent(self):
        ref = AssigneeRef.member(MemberId("alice"))
        self.assertFalse(ref.is_agent)
        self.assertEqual(ref.kind, AssigneeKind.MEMBER)

    def test_agent_ref_is_an_agent(self):
        ref = AssigneeRef.agent(AgentId("gpt"))
        self.assertTrue(ref.is_agent)
        self.assertEqual(ref.kind, AssigneeKind.AGENT)

    def test_as_member_id_raises_on_an_agent_ref(self):
        ref = AssigneeRef.agent(AgentId("gpt"))
        with self.assertRaises(ValueError):
            ref.as_member_id()

    def test_as_agent_id_raises_on_a_member_ref(self):
        ref = AssigneeRef.member(MemberId("alice"))
        with self.assertRaises(ValueError):
            ref.as_agent_id()

    def test_typed_accessors_return_the_right_id_for_the_right_kind(self):
        self.assertEqual(
            AssigneeRef.member(MemberId("alice")).as_member_id(), MemberId("alice")
        )
        self.assertEqual(
            AssigneeRef.agent(AgentId("gpt")).as_agent_id(), AgentId("gpt")
        )

    def test_ref_id_cannot_be_blank(self):
        with self.assertRaises(ValueError):
            AssigneeRef(kind=AssigneeKind.AGENT, id_value="   ")


class AgentTests(unittest.TestCase):
    def test_agent_needs_display_provider_and_model(self):
        with self.assertRaises(ValueError):
            Agent(AgentId("a"), "  ", "openai", "gpt-4")
        with self.assertRaises(ValueError):
            Agent(AgentId("a"), "Assistant", "  ", "gpt-4")
        with self.assertRaises(ValueError):
            Agent(AgentId("a"), "Assistant", "openai", "  ")

    def test_agent_id_cannot_be_blank(self):
        with self.assertRaises(ValueError):
            AgentId("  ")


class AgentRegistryGateTests(unittest.TestCase):
    def setUp(self):
        self.agent = Agent(AgentId("gpt"), "Assistant", "openai", "gpt-4")
        self.registry = AgentRegistry([self.agent])

    def test_resolves_known_agent_to_display_name(self):
        self.assertEqual(self.registry.display_name_for(AgentId("gpt")), "Assistant")

    def test_unknown_agent_is_refused(self):
        self.assertFalse(self.registry.knows(AgentId("ghost")))
        with self.assertRaises(UnknownAgentError):
            self.registry.agent(AgentId("ghost"))

    def test_require_executable_returns_the_agent_for_an_agent_assignment(self):
        agent = self.registry.require_executable(AssigneeRef.agent(AgentId("gpt")))
        self.assertEqual(agent.id, AgentId("gpt"))
        self.assertEqual(agent.provider_name, "openai")

    def test_require_executable_refuses_an_unassigned_task(self):
        with self.assertRaises(TaskNotExecutableError):
            self.registry.require_executable(None)

    def test_require_executable_refuses_a_human_assignment(self):
        with self.assertRaises(TaskNotExecutableError):
            self.registry.require_executable(AssigneeRef.member(MemberId("alice")))

    def test_require_executable_refuses_an_unknown_agent(self):
        with self.assertRaises(UnknownAgentError):
            self.registry.require_executable(AssigneeRef.agent(AgentId("ghost")))


class ExecutionResultTests(unittest.TestCase):
    def test_holds_its_four_facts(self):
        result = ExecutionResult(
            task_id=TaskId("t1"),
            agent_id=AgentId("gpt"),
            succeeded=True,
            output="done",
        )
        self.assertEqual(result.task_id, TaskId("t1"))
        self.assertEqual(result.agent_id, AgentId("gpt"))
        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "done")


if __name__ == "__main__":
    unittest.main()
