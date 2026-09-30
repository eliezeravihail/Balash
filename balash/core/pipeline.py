"""Pipelines: YAML files that list blocks in order.

A pipeline holds no logic. Each step names a block, optionally names the
step(s) whose output it reads (``input``), and passes every other key to the
block as a parameter. The first step, and any step that says
``input: trigger``, reads the records that started the run.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .block import Context, get_block, log
from .record import Record, new_id

RESERVED = {"id", "block", "input"}


class PipelineError(RuntimeError):
    pass


@dataclass
class Step:
    id: str
    block: str
    inputs: list[str] | None
    params: dict[str, Any]


@dataclass
class Pipeline:
    name: str
    trigger: str
    steps: list[Step]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Pipeline":
        if "pipeline" not in raw or "steps" not in raw:
            raise PipelineError("a pipeline needs 'pipeline' and 'steps'")
        steps: list[Step] = []
        seen: set[str] = set()
        for i, s in enumerate(raw["steps"]):
            sid = s.get("id") or f"step{i + 1}"
            if sid in seen:
                raise PipelineError(f"duplicate step id '{sid}'")
            if "block" not in s:
                raise PipelineError(f"step '{sid}' has no block")
            inp = s.get("input")
            inputs = None if inp is None else ([inp] if isinstance(inp, str) else list(inp))
            for ref in inputs or []:
                if ref != "trigger" and ref not in seen:
                    raise PipelineError(f"step '{sid}' reads '{ref}', which is not an earlier step")
            get_block(s["block"])  # fail early on unknown blocks
            steps.append(Step(sid, s["block"], inputs, {k: v for k, v in s.items() if k not in RESERVED}))
            seen.add(sid)
        return cls(name=raw["pipeline"], trigger=raw.get("trigger", "manual"), steps=steps)

    @classmethod
    def load(cls, path: str | Path) -> "Pipeline":
        return cls.from_dict(yaml.safe_load(Path(path).read_text(encoding="utf-8")))

    def run(self, trigger_records: list[Record], ctx: Context, trigger_label: str = "") -> dict[str, list[Record]]:
        ctx.run_id = ctx.run_id or new_id("run")
        ctx.store.start_run(ctx.run_id, self.name, trigger_label or self.trigger)
        outputs: dict[str, list[Record]] = {"trigger": trigger_records}
        previous = "trigger"
        try:
            for step in self.steps:
                refs = step.inputs or [previous]
                records = [r for ref in refs for r in outputs[ref]]
                block = get_block(step.block)(step.params)
                started = time.monotonic()
                result = block.run(records, ctx)
                ctx.log.append(
                    {
                        "step": step.id,
                        "block": step.block,
                        "kind": block.kind,
                        "in": [r.id for r in records],
                        "out": [r.id for r in result],
                        "ms": int((time.monotonic() - started) * 1000),
                    }
                )
                outputs[step.id] = result
                previous = step.id
        except Exception as exc:
            ctx.log.append({"error": f"{type(exc).__name__}: {exc}"})
            ctx.store.finish_run(ctx.run_id, "failed", ctx.log)
            log.exception("pipeline %s failed", self.name)
            raise PipelineError(f"{self.name} failed: {exc}") from exc
        ctx.store.finish_run(ctx.run_id, "ok", ctx.log)
        return outputs
