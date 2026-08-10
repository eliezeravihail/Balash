"""The command-line interface.

Its whole job is translation: turn the words a person typed into a call on a service,
and turn what comes back into lines a person reads. It makes no product decisions and
it never touches storage or the domain's rules directly -- it goes through the services
and prints TaskViews. Where the store lives on disk, and which single provider runs
agent work, are chosen here (the composition root), because choosing concrete wiring is
exactly what an entry point is for.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from .domain import DomainError
from .execution import ExecutionService, LocalProvider
from .service import TaskService, TaskView
from .storage import JsonStorage, SqliteStorage, StorageBackend

DEFAULT_DATA_DIR = ".taskcli-data"
DATA_DIR_ENV = "TASKCLI_DATA_DIR"
DEFAULT_BACKEND = "json"
SQLITE_DB_NAME = "taskcli.db"


def build_backend(kind: str, data_dir: Path) -> StorageBackend:
    """The one and only place a backend name is interpreted. From here on everything
    downstream holds a ``StorageBackend`` or a repository port, never the string
    'json'/'sqlite', so the choice cannot leak past composition. A future third backend
    is one more branch here and a new subpackage -- nothing else changes."""
    if kind == "sqlite":
        # SQLite reuses --data-dir: the db lives at data_dir/taskcli.db, so a user picks
        # a directory once for either backend. Opening it ensures the schema once.
        return SqliteStorage(data_dir / SQLITE_DB_NAME)
    return JsonStorage(data_dir)  # DEFAULT -- the four *.json files, today's behavior


def build_service(data_dir: Path, backend: Optional[StorageBackend] = None) -> TaskService:
    """Compose the task/roster service over a storage backend. When no explicit backend
    is passed it defaults to a JSON backend built from ``data_dir`` -- byte-for-byte
    today's behavior, so existing ``build_service(Path(...))`` call sites are unchanged.
    An explicitly passed backend supersedes ``data_dir`` (the backend already owns its
    own location)."""
    backend = backend or JsonStorage(data_dir)
    return TaskService(
        tasks=backend.tasks(), members=backend.members(), agents=backend.agents()
    )


def build_execution_service(
    data_dir: Path, backend: Optional[StorageBackend] = None
) -> ExecutionService:
    """Compose the execution service, wiring the single local provider. Same backend
    contract as ``build_service``: default JSON from ``data_dir``, or an explicit backend
    that supersedes it."""
    backend = backend or JsonStorage(data_dir)
    return ExecutionService(
        tasks=backend.tasks(),
        agents=backend.agents(),
        results=backend.results(),
        provider=LocalProvider(),
    )


def _resolve_data_dir(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit)
    return Path(os.environ.get(DATA_DIR_ENV, DEFAULT_DATA_DIR))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskcli", description="A small task tracker for one team."
    )
    parser.add_argument(
        "--data-dir",
        help=f"where state is stored (default: ${DATA_DIR_ENV} or ./{DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--backend",
        choices=("json", "sqlite"),
        default=DEFAULT_BACKEND,
        help=(
            "which storage backend to use (default: json). sqlite keeps state in a "
            f"single {SQLITE_DB_NAME} under --data-dir"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-member", help="add someone to the team")
    p.add_argument("--id", required=True, dest="member_id")
    p.add_argument("--name", required=True, dest="name")

    sub.add_parser("members", help="list the team")

    p = sub.add_parser("add-agent", help="register an AI agent")
    p.add_argument("--id", required=True, dest="agent_id")
    p.add_argument("--name", required=True, dest="name")
    p.add_argument("--provider", required=True, dest="provider")
    p.add_argument("--model", required=True, dest="model")

    sub.add_parser("agents", help="list the registered agents")

    p = sub.add_parser("create", help="create a task")
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument(
        "--needs",
        action="append",
        default=None,
        dest="needs",
        metavar="TASK_ID",
        help=(
            "id of a task this one depends on; repeat for several. The task is blocked "
            "until every one of them is done. Each must already exist."
        ),
    )

    p = sub.add_parser("assign", help="assign a task to a member")
    p.add_argument("task_id")
    p.add_argument("--to", required=True, dest="member_id")

    p = sub.add_parser("assign-agent", help="assign a task to an AI agent")
    p.add_argument("task_id")
    p.add_argument("--to", required=True, dest="agent_id")

    p = sub.add_parser("unassign", help="remove a task's assignee")
    p.add_argument("task_id")

    p = sub.add_parser("execute", help="run an agent-assigned task")
    p.add_argument("task_id")

    p = sub.add_parser("history", help="show a task's execution history")
    p.add_argument("task_id")

    p = sub.add_parser("status", help="change a task's status")
    p.add_argument("task_id")
    p.add_argument("value", help="todo | in progress | done")

    sub.add_parser("list", help="list all tasks")

    p = sub.add_parser("show", help="show one task")
    p.add_argument("task_id")

    return parser


def _format_task_line(view: TaskView) -> str:
    return (
        f"{view.id}  [{view.status}]  {view.title}  "
        f"-- {view.assignee}  ({view.readiness})"
    )


def _format_task_detail(view: TaskView) -> str:
    prerequisites = ", ".join(view.prerequisites) if view.prerequisites else "none"
    return "\n".join(
        [
            f"id:            {view.id}",
            f"title:         {view.title}",
            f"description:   {view.description}",
            f"status:        {view.status}",
            f"assignee:      {view.assignee}",
            f"prerequisites: {prerequisites}",
            f"readiness:     {view.readiness}",
        ]
    )


def _format_result_line(index: int, result) -> str:
    outcome = "ok" if result.succeeded else "failed"
    return f"{index}. [{outcome}] {result.agent_id.value}: {result.output}"


def _run(
    args: argparse.Namespace,
    service: TaskService,
    data_dir: Path,
    backend: StorageBackend,
    out,
) -> None:
    command = args.command
    if command == "add-member":
        member = service.add_member(args.member_id, args.name)
        print(f"added member {member.id.value} ({member.display_name})", file=out)
    elif command == "members":
        roster = service.roster()
        if not roster:
            print("no team members yet; add one with add-member", file=out)
        for member in roster:
            print(f"{member.id.value}  {member.display_name}", file=out)
    elif command == "add-agent":
        agent = service.add_agent(args.agent_id, args.provider, args.model, args.name)
        print(
            f"registered agent {agent.id.value} ({agent.display_name}) "
            f"on {agent.provider_name}/{agent.model_name}",
            file=out,
        )
    elif command == "agents":
        agents = service.agents()
        if not agents:
            print("no agents registered yet; add one with add-agent", file=out)
        for agent in agents:
            print(
                f"{agent.id.value}  {agent.display_name}  "
                f"({agent.provider_name}/{agent.model_name})",
                file=out,
            )
    elif command == "create":
        task_id = service.create_task(args.title, args.description, args.needs or [])
        print(f"created task {task_id.value}", file=out)
    elif command == "assign":
        service.assign_task(args.task_id, args.member_id)
        print(f"assigned task {args.task_id} to {args.member_id}", file=out)
    elif command == "assign-agent":
        service.assign_task_to_agent(args.task_id, args.agent_id)
        print(f"assigned task {args.task_id} to agent {args.agent_id}", file=out)
    elif command == "unassign":
        service.unassign_task(args.task_id)
        print(f"unassigned task {args.task_id}", file=out)
    elif command == "execute":
        result = build_execution_service(data_dir, backend).execute(args.task_id)
        outcome = "succeeded" if result.succeeded else "failed"
        print(f"execution {outcome}", file=out)
        print(result.output, file=out)
    elif command == "history":
        results = build_execution_service(data_dir, backend).history(args.task_id)
        if not results:
            print("no executions yet for this task", file=out)
        for index, result in enumerate(results, start=1):
            print(_format_result_line(index, result), file=out)
    elif command == "status":
        service.change_status(args.task_id, args.value)
        print(f"task {args.task_id} status changed", file=out)
    elif command == "list":
        views = service.list_tasks()
        if not views:
            print("no tasks yet; create one with create", file=out)
        for view in views:
            print(_format_task_line(view), file=out)
    elif command == "show":
        print(_format_task_detail(service.show_task(args.task_id)), file=out)


def main(argv: Optional[List[str]] = None, out=None) -> int:
    out = out or sys.stdout
    parser = _build_parser()
    args = parser.parse_args(argv)
    data_dir = _resolve_data_dir(args.data_dir)
    backend = build_backend(args.backend, data_dir)  # the ONE selection point
    service = build_service(data_dir, backend)
    try:
        _run(args, service, data_dir, backend, out)
    except DomainError as error:
        # The domain speaks in the user's concepts; relay that, don't dump a traceback.
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0
