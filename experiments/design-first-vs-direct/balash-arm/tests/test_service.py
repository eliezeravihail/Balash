"""The service composed over real (temp-dir) repositories: use cases end to end within
one process, including the assign-to-unknown-member decision."""

import tempfile
import unittest
from pathlib import Path

from taskcli.cli import build_service
from taskcli.domain import TaskNotFoundError, UnknownMemberError


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.service = build_service(Path(self._dir.name))

    def tearDown(self):
        self._dir.cleanup()

    def test_create_and_show(self):
        task_id = self.service.create_task("Ship it", "the first slice")
        view = self.service.show_task(task_id.value)
        self.assertEqual(view.title, "Ship it")
        self.assertEqual(view.status, "todo")
        self.assertEqual(view.assignee, "unassigned")

    def test_assign_resolves_display_name_in_listing(self):
        self.service.add_member("alice", "Alice Ng")
        task_id = self.service.create_task("t", "")
        self.service.assign_task(task_id.value, "alice")
        view = self.service.show_task(task_id.value)
        self.assertEqual(view.assignee, "Alice Ng")

    def test_assign_to_unknown_member_is_rejected_and_changes_nothing(self):
        task_id = self.service.create_task("t", "")
        with self.assertRaises(UnknownMemberError):
            self.service.assign_task(task_id.value, "ghost")
        # the task is untouched
        self.assertEqual(self.service.show_task(task_id.value).assignee, "unassigned")

    def test_unassign(self):
        self.service.add_member("bob", "Bob")
        task_id = self.service.create_task("t", "")
        self.service.assign_task(task_id.value, "bob")
        self.service.unassign_task(task_id.value)
        self.assertEqual(self.service.show_task(task_id.value).assignee, "unassigned")

    def test_status_change_including_reopen(self):
        task_id = self.service.create_task("t", "")
        self.service.change_status(task_id.value, "in progress")
        self.service.change_status(task_id.value, "done")
        self.service.change_status(task_id.value, "todo")  # reopen
        self.assertEqual(self.service.show_task(task_id.value).status, "todo")

    def test_show_missing_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.service.show_task("nope")

    def test_list_returns_all(self):
        self.service.create_task("a", "")
        self.service.create_task("b", "")
        self.assertEqual(len(self.service.list_tasks()), 2)


if __name__ == "__main__":
    unittest.main()
