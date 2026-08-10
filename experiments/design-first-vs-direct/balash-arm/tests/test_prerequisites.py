"""Prerequisites as a first-class concept: the domain rules (readiness, and the
existence-at-creation gate that guarantees acyclicity) exercised directly, and the same
rules driven through the service end to end over real repositories.

The cycle case is the interesting one: because prerequisites may only reference tasks
that already exist and are fixed at creation, a cycle cannot be constructed at all. The
tests pin that -- a task cannot depend on itself, nor on a not-yet-existing task -- which
is the whole of the invariant at this scale.
"""

import tempfile
import unittest
from pathlib import Path

from taskcli.cli import build_service
from taskcli.domain import (
    Prerequisites,
    Readiness,
    Status,
    Task,
    TaskId,
    UnknownPrerequisiteError,
)


class PrerequisitesDomainTests(unittest.TestCase):
    def test_empty_prerequisites_are_vacuously_ready(self):
        self.assertEqual(Prerequisites.none().readiness(set()), Readiness.READY)

    def test_ready_only_when_every_prerequisite_is_done(self):
        prereqs = Prerequisites.of([TaskId("a"), TaskId("b")])
        self.assertEqual(prereqs.readiness({TaskId("a")}), Readiness.BLOCKED)
        self.assertEqual(
            prereqs.readiness({TaskId("a"), TaskId("b")}), Readiness.READY
        )

    def test_of_deduplicates_and_preserves_first_seen_order(self):
        prereqs = Prerequisites.of([TaskId("b"), TaskId("a"), TaskId("b")])
        self.assertEqual([t.value for t in prereqs], ["b", "a"])

    def test_require_all_known_rejects_a_reference_to_a_nonexistent_task(self):
        prereqs = Prerequisites.of([TaskId("a"), TaskId("ghost")])
        with self.assertRaises(UnknownPrerequisiteError) as ctx:
            prereqs.require_all_known({TaskId("a")})
        self.assertIn("ghost", str(ctx.exception))

    def test_require_all_known_passes_when_all_exist(self):
        prereqs = Prerequisites.of([TaskId("a"), TaskId("b")])
        prereqs.require_all_known({TaskId("a"), TaskId("b")})  # does not raise

    def test_task_delegates_readiness_to_its_prerequisites(self):
        task = Task.create(
            title="t", description="", prerequisites=Prerequisites.of([TaskId("dep")])
        )
        self.assertEqual(task.readiness(set()), Readiness.BLOCKED)
        self.assertEqual(task.readiness({TaskId("dep")}), Readiness.READY)

    def test_a_task_created_without_prerequisites_has_none_and_is_ready(self):
        task = Task.create(title="t", description="")
        self.assertTrue(task.prerequisites.is_empty)
        self.assertEqual(task.readiness(set()), Readiness.READY)


class PrerequisitesServiceTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.service = build_service(Path(self._dir.name))

    def tearDown(self):
        self._dir.cleanup()

    def test_task_with_unmet_prerequisite_is_blocked_then_ready_when_done(self):
        dep = self.service.create_task("dep", "").value
        blocked = self.service.create_task("main", "", needs=[dep]).value

        self.assertEqual(self.service.show_task(blocked).readiness, "blocked")
        self.assertEqual(self.service.show_task(blocked).prerequisites, (dep,))

        self.service.change_status(dep, "done")
        self.assertEqual(self.service.show_task(blocked).readiness, "ready")

    def test_task_without_prerequisites_is_ready(self):
        task_id = self.service.create_task("free", "").value
        self.assertEqual(self.service.show_task(task_id).readiness, "ready")
        self.assertEqual(self.service.show_task(task_id).prerequisites, ())

    def test_readiness_needs_all_prerequisites_done(self):
        a = self.service.create_task("a", "").value
        b = self.service.create_task("b", "").value
        main = self.service.create_task("main", "", needs=[a, b]).value

        self.service.change_status(a, "done")
        self.assertEqual(self.service.show_task(main).readiness, "blocked")
        self.service.change_status(b, "done")
        self.assertEqual(self.service.show_task(main).readiness, "ready")

    def test_creating_with_a_nonexistent_prerequisite_is_refused(self):
        with self.assertRaises(UnknownPrerequisiteError):
            self.service.create_task("main", "", needs=["does-not-exist"])
        # nothing was created
        self.assertEqual(self.service.list_tasks(), [])

    def test_a_task_cannot_depend_on_itself_because_its_id_does_not_exist_yet(self):
        # There is no way to name the new task's id at creation -- it is minted inside
        # create -- and even a forged one would not be among the existing tasks. So a
        # self-cycle is unconstructible; the only way to try is a bogus id, which the
        # existence gate rejects. This is the acyclicity invariant, enforced by that one
        # rule rather than by any cycle-detection pass.
        with self.assertRaises(UnknownPrerequisiteError):
            self.service.create_task("main", "", needs=["main-guessed-id"])

    def test_no_cycle_can_form_because_prereqs_point_only_at_older_tasks(self):
        # a exists first; b may depend on a. a can never be made to depend on b, because
        # a's prerequisites were fixed at a's creation, when b did not yet exist -- and
        # there is no command to add one afterward. Every edge points strictly backward
        # in creation order, so the graph is acyclic by construction.
        a = self.service.create_task("a", "").value
        b = self.service.create_task("b", "", needs=[a]).value
        self.assertEqual(self.service.show_task(b).prerequisites, (a,))
        # The service exposes no way to give `a` a prerequisite after the fact.
        self.assertFalse(hasattr(self.service, "add_prerequisite"))

    def test_duplicate_needs_are_deduplicated(self):
        dep = self.service.create_task("dep", "").value
        main = self.service.create_task("main", "", needs=[dep, dep]).value
        self.assertEqual(self.service.show_task(main).prerequisites, (dep,))


if __name__ == "__main__":
    unittest.main()
