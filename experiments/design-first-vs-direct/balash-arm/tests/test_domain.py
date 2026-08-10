"""The task and team own their rules -- these tests exercise that directly, with no
storage or CLI involved."""

import unittest

from taskcli.domain import (
    InvalidStatusError,
    InvalidTitleError,
    Member,
    MemberId,
    Status,
    Task,
    Team,
    UnknownMemberError,
)


class TaskBehaviourTests(unittest.TestCase):
    def test_new_task_starts_todo_and_unassigned(self):
        task = Task.create(title="Write spec", description="the first draft")
        self.assertEqual(task.status, Status.TODO)
        self.assertIsNone(task.assignee)
        self.assertFalse(task.is_assigned)

    def test_task_requires_a_title(self):
        with self.assertRaises(InvalidTitleError):
            Task.create(title="   ", description="d")

    def test_title_is_trimmed(self):
        task = Task.create(title="  hello  ", description="")
        self.assertEqual(task.title, "hello")

    def test_assign_then_unassign(self):
        task = Task.create(title="t", description="")
        task.assign_to(MemberId("alice"))
        self.assertEqual(task.assignee, MemberId("alice"))
        self.assertTrue(task.is_assigned)
        task.unassign()
        self.assertIsNone(task.assignee)

    def test_every_status_transition_is_allowed_including_reopening(self):
        task = Task.create(title="t", description="")
        for target in (Status.IN_PROGRESS, Status.DONE, Status.TODO, Status.DONE):
            task.change_status(target)
            self.assertEqual(task.status, target)

    def test_change_status_rejects_non_status(self):
        task = Task.create(title="t", description="")
        with self.assertRaises(InvalidStatusError):
            task.change_status("done")  # the string, not the Status


class StatusParsingTests(unittest.TestCase):
    def test_parses_natural_spellings(self):
        self.assertEqual(Status.parse("in progress"), Status.IN_PROGRESS)
        self.assertEqual(Status.parse("in-progress"), Status.IN_PROGRESS)
        self.assertEqual(Status.parse("DONE"), Status.DONE)

    def test_rejects_unreal_status_with_helpful_message(self):
        with self.assertRaises(InvalidStatusError) as ctx:
            Status.parse("archived")
        self.assertIn("in progress", str(ctx.exception))

    def test_label_is_human_readable(self):
        self.assertEqual(Status.IN_PROGRESS.label, "in progress")


class TeamTests(unittest.TestCase):
    def test_resolves_known_member_to_display_name(self):
        team = Team([Member(MemberId("m1"), "Alice")])
        self.assertEqual(team.display_name_for(MemberId("m1")), "Alice")

    def test_unknown_member_is_refused(self):
        team = Team([Member(MemberId("m1"), "Alice")])
        self.assertFalse(team.knows(MemberId("ghost")))
        with self.assertRaises(UnknownMemberError):
            team.member(MemberId("ghost"))


class ValueObjectTests(unittest.TestCase):
    def test_member_id_cannot_be_blank(self):
        with self.assertRaises(ValueError):
            MemberId("  ")

    def test_member_needs_a_display_name(self):
        with self.assertRaises(ValueError):
            Member(MemberId("m1"), "  ")


if __name__ == "__main__":
    unittest.main()
