"""Command-line interface for the task manager.

Commands:
    add           create a task (optionally with prerequisites)
    assign        assign a task to a human member (id + display name given now)
    advance       move a task forward: todo -> in progress -> done
    list          list all tasks with assignee, status, and readiness
    show          show one task in detail (prerequisites and readiness)
    add-agent     register an AI agent (provider + model)
    list-agents   list registered AI agents
    assign-agent  assign a task to an AI agent
    execute       have an agent execute a task (appends to task history)

Backend selection (--backend / $TASKTOOL_BACKEND): "json" (default) or "sqlite".
The two backends are independent stores; there is no migration between them.

Data location resolves in this order: --data-file, then $TASKTOOL_DATA, then a
backend-specific default under ~/.tasktool/ (tasks.json or tasks.db).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Sequence

from .manager import AgentNotFoundError, TaskManager, TaskNotFoundError
from .models import AgentAssignee
from .sqlite_store import SqliteTaskStore
from .store import JsonTaskStore, TaskStore

ENV_DATA_FILE = "TASKTOOL_DATA"
ENV_BACKEND = "TASKTOOL_BACKEND"
DATA_DIR = Path.home() / ".tasktool"
DEFAULT_BACKEND = "json"
DEFAULT_FILENAMES = {"json": "tasks.json", "sqlite": "tasks.db"}


def resolve_backend(cli_value: Optional[str]) -> str:
    backend = cli_value or os.environ.get(ENV_BACKEND) or DEFAULT_BACKEND
    if backend not in DEFAULT_FILENAMES:
        raise ValueError(f"Unknown backend: {backend!r}")
    return backend


def resolve_data_file(cli_value: Optional[str], backend: str) -> Path:
    if cli_value:
        return Path(cli_value)
    env_value = os.environ.get(ENV_DATA_FILE)
    if env_value:
        return Path(env_value)
    return DATA_DIR / DEFAULT_FILENAMES[backend]


def build_store(backend: str, data_file: Path) -> TaskStore:
    if backend == "sqlite":
        return SqliteTaskStore(data_file)
    return JsonTaskStore(data_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasktool", description="Single-machine task manager."
    )
    parser.add_argument(
        "--backend",
        choices=sorted(DEFAULT_FILENAMES),
        help=f"Storage backend (default: ${ENV_BACKEND} or {DEFAULT_BACKEND}).",
    )
    parser.add_argument(
        "--data-file",
        help=f"Path to the data file (default: ${ENV_DATA_FILE} or a "
        f"backend-specific file under {DATA_DIR}).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Create a new task.")
    p_add.add_argument("title", help="Short title, e.g. 'Prepare weekly report'.")
    p_add.add_argument("-d", "--description", default="", help="Longer description.")
    p_add.add_argument(
        "--depends-on",
        type=int,
        nargs="*",
        default=[],
        metavar="TASK_ID",
        help="Ids of tasks that must be done first (prerequisites).",
    )

    p_assign = sub.add_parser("assign", help="Assign a task to a human member.")
    p_assign.add_argument("task_id", type=int)
    p_assign.add_argument("--member-id", required=True, help="Stable member id.")
    p_assign.add_argument(
        "--name", required=True, dest="display_name", help="Member display name."
    )

    p_advance = sub.add_parser(
        "advance", help="Advance a task: todo -> in progress -> done."
    )
    p_advance.add_argument("task_id", type=int)

    sub.add_parser("list", help="List all tasks.")

    p_show = sub.add_parser("show", help="Show one task in detail.")
    p_show.add_argument("task_id", type=int)

    p_add_agent = sub.add_parser("add-agent", help="Register an AI agent.")
    p_add_agent.add_argument("--provider", required=True, help="e.g. openai, anthropic.")
    p_add_agent.add_argument("--model", required=True, help="e.g. gpt-4o, claude-3.")

    sub.add_parser("list-agents", help="List registered AI agents.")

    p_assign_agent = sub.add_parser(
        "assign-agent", help="Assign a task to an AI agent."
    )
    p_assign_agent.add_argument("task_id", type=int)
    p_assign_agent.add_argument("--agent-id", required=True)

    p_execute = sub.add_parser(
        "execute", help="Have an agent execute a task (appends to history)."
    )
    p_execute.add_argument("task_id", type=int)
    p_execute.add_argument(
        "--agent-id",
        help="Agent to run it. Defaults to the task's assigned agent, if any.",
    )

    return parser


def _readiness_label(manager: TaskManager, task) -> str:
    """Empty for tasks with no prerequisites; otherwise ready/blocked."""
    if not task.prerequisites:
        return ""
    unmet = manager.unmet_prerequisites(task)
    if unmet:
        return " BLOCKED(needs " + ",".join(map(str, unmet)) + ")"
    return " READY"


def _format_task_line(manager: TaskManager, task) -> str:
    assignee = manager.assignee_label(task)
    execs = f" execs:{len(task.executions)}" if task.executions else ""
    readiness = _readiness_label(manager, task)
    return (
        f"[{task.id}] {task.status.value:<12} {assignee:<28} "
        f"{task.title}{execs}{readiness}"
    )


def _cmd_add(manager: TaskManager, args: argparse.Namespace) -> int:
    task = manager.create_task(args.title, args.description, args.depends_on)
    suffix = (
        f" (depends on {', '.join(map(str, task.prerequisites))})"
        if task.prerequisites
        else ""
    )
    print(f"Created task {task.id}: {task.title}{suffix}")
    return 0


def _cmd_assign(manager: TaskManager, args: argparse.Namespace) -> int:
    task = manager.assign(args.task_id, args.member_id, args.display_name)
    print(
        f"Task {task.id} assigned to {task.assignee.display_name} "
        f"({task.assignee.member_id})"
    )
    return 0


def _cmd_advance(manager: TaskManager, args: argparse.Namespace) -> int:
    task = manager.advance(args.task_id)
    print(f"Task {task.id} is now '{task.status.value}'")
    return 0


def _cmd_list(manager: TaskManager, args: argparse.Namespace) -> int:
    tasks = manager.list_tasks()
    if not tasks:
        print("No tasks yet.")
        return 0
    for task in tasks:
        print(_format_task_line(manager, task))
    return 0


def _cmd_show(manager: TaskManager, args: argparse.Namespace) -> int:
    task = manager.get(args.task_id)
    print(f"Task {task.id}: {task.title}")
    print(f"  status:      {task.status.value}")
    print(f"  assignee:    {manager.assignee_label(task)}")
    if task.description:
        print(f"  description: {task.description}")
    if task.prerequisites:
        unmet = manager.unmet_prerequisites(task)
        readiness = "ready" if not unmet else f"blocked (needs {unmet})"
        print(f"  prerequisites: {task.prerequisites} -> {readiness}")
    else:
        print("  prerequisites: none -> ready")
    if task.executions:
        print(f"  executions:  {len(task.executions)}")
    return 0


def _cmd_add_agent(manager: TaskManager, args: argparse.Namespace) -> int:
    agent = manager.create_agent(args.provider, args.model)
    print(f"Created agent {agent.id}: {agent.provider}/{agent.model}")
    return 0


def _cmd_list_agents(manager: TaskManager, args: argparse.Namespace) -> int:
    agents = manager.list_agents()
    if not agents:
        print("No agents yet.")
        return 0
    for agent in agents:
        print(f"{agent.id}: {agent.provider}/{agent.model}")
    return 0


def _cmd_assign_agent(manager: TaskManager, args: argparse.Namespace) -> int:
    task = manager.assign_agent(args.task_id, args.agent_id)
    print(f"Task {task.id} assigned to agent {args.agent_id}")
    return 0


def _cmd_execute(manager: TaskManager, args: argparse.Namespace) -> int:
    agent_id = args.agent_id
    if agent_id is None:
        task = manager.get(args.task_id)
        if isinstance(task.assignee, AgentAssignee):
            agent_id = task.assignee.agent_id
        else:
            print(
                "Error: no --agent-id given and task has no assigned agent",
                file=sys.stderr,
            )
            return 1
    result = manager.execute(args.task_id, agent_id)
    status = "succeeded" if result.success else "failed"
    print(f"Execution by {result.agent_id} on task {result.task_id} {status}")
    print(result.output)
    return 0


_COMMANDS = {
    "add": _cmd_add,
    "assign": _cmd_assign,
    "advance": _cmd_advance,
    "list": _cmd_list,
    "show": _cmd_show,
    "add-agent": _cmd_add_agent,
    "list-agents": _cmd_list_agents,
    "assign-agent": _cmd_assign_agent,
    "execute": _cmd_execute,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        backend = resolve_backend(args.backend)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    store = build_store(backend, resolve_data_file(args.data_file, backend))
    manager = TaskManager(store)

    handler = _COMMANDS[args.command]
    try:
        return handler(manager, args)
    except (TaskNotFoundError, AgentNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
