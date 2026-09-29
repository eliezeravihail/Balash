"""The harness runtime: turns a folder (instructions, schema, settings) into a block.

A harness block folder contains:

* ``block.yaml``: name, version, purpose, model, effort, max_tokens;
* ``prompt.md``: the fixed instructions, written like a brief for a new employee;
* ``schema.json``: the exact output shape, sent as a structured-output schema
  and checked again in code.

The Python subclass supplies only three things: how inputs become model calls
(``build_units``), which consistency checks run after the model
(``check``), and how the validated output becomes records (``to_records``).
Caching, validation, one retry, refusal handling and the call log are here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar

import jsonschema
import yaml

from ..core.block import Block, Context, log
from ..core.record import Record
from .llm import LLMRequest

HARNESS_DIR = Path(__file__).resolve().parent.parent / "harness_blocks"


@dataclass
class HarnessSpec:
    name: str
    version: int
    purpose: str
    model: str
    effort: str
    max_tokens: int
    prompt: str
    schema: dict[str, Any]

    @classmethod
    def load(cls, folder: Path) -> "HarnessSpec":
        meta = yaml.safe_load((folder / "block.yaml").read_text(encoding="utf-8"))
        return cls(
            name=meta["name"],
            version=int(meta["version"]),
            purpose=meta["purpose"],
            model=meta.get("model", "default"),
            effort=meta.get("effort", "medium"),
            max_tokens=int(meta.get("max_tokens", 16000)),
            prompt=(folder / meta.get("prompt", "prompt.md")).read_text(encoding="utf-8"),
            schema=json.loads((folder / meta.get("schema", "schema.json")).read_text(encoding="utf-8")),
        )

    @property
    def fingerprint(self) -> str:
        blob = json.dumps(
            [self.name, self.version, self.prompt, self.schema, self.effort], sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


@dataclass
class Unit:
    """One model call: the content to send, a stable digest of that content
    for the cache, and the records it came from."""

    content: list[dict[str, Any]]
    digest: str
    cites: list[str]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessResult:
    status: str  # ok | uncertain | failed (bad output) | refused | error (call did not complete)
    output: dict[str, Any] | None
    issues: list[str]
    cached: bool = False


class HarnessBlock(Block):
    kind = "harness"
    folder: ClassVar[str] = ""

    @cached_property
    def spec(self) -> HarnessSpec:
        return HarnessSpec.load(HARNESS_DIR / (self.folder or self.name))

    # ---- to override -----------------------------------------------------

    def build_units(self, inputs: list[Record], ctx: Context) -> list[Unit]:
        raise NotImplementedError

    def check(self, output: dict[str, Any], unit: Unit) -> list[str]:
        """Consistency checks in code. Return human-readable issues; they do
        not trigger a retry, they mark the result uncertain."""
        return []

    def to_records(self, result: HarnessResult, unit: Unit, ctx: Context) -> list[Record]:
        raise NotImplementedError

    # ---- runtime ---------------------------------------------------------

    def model_for(self, ctx: Context) -> str:
        return ctx.config.default_model if self.spec.model == "default" else self.spec.model

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out: list[Record] = []
        for unit in self.build_units(inputs, ctx):
            out.extend(self.to_records(self.call(unit, ctx), unit, ctx))
        return out

    def cache_key(self, unit: Unit, model: str) -> str:
        blob = json.dumps([self.spec.fingerprint, model, unit.digest], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def call(self, unit: Unit, ctx: Context) -> HarnessResult:
        model = self.model_for(ctx)
        key = self.cache_key(unit, model)
        cached = ctx.store.cache_get(key)
        if cached is not None:
            issues = self.check(cached, unit)
            return HarnessResult("uncertain" if issues else "ok", cached, issues, cached=True)
        if ctx.llm is None:
            return HarnessResult("error", None, ["no model client configured"])

        content = list(unit.content)
        last_error = ""
        for attempt in range(2):
            request = LLMRequest(
                block=self.spec.name,
                model=model,
                system=self.spec.prompt,
                content=content,
                schema=self.spec.schema,
                effort=self.spec.effort,
                max_tokens=self.spec.max_tokens,
            )
            try:
                response = ctx.llm.complete(request)
            except Exception as exc:  # network, auth, rate limit after SDK retries
                log.warning("harness %s call failed: %s", self.spec.name, exc)
                ctx.store.log_llm_call(block=self.spec.name, model=model, ok=0, error=str(exc)[:500])
                return HarnessResult("error", None, [f"model call failed: {type(exc).__name__}"])
            ok, output, last_error = self._parse(response.text, response.stop_reason)
            ctx.store.log_llm_call(
                block=self.spec.name,
                model=response.model,
                stop_reason=response.stop_reason,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cache_read_tokens=response.cache_read_tokens,
                latency_ms=response.latency_ms,
                ok=int(ok),
                error=last_error or None,
            )
            if response.stop_reason == "refusal":
                return HarnessResult("refused", None, [f"model declined ({response.refusal_category or 'no category'})"])
            if ok:
                assert output is not None
                ctx.store.cache_put(key, self.spec.name, output)
                issues = self.check(output, unit)
                return HarnessResult("uncertain" if issues else "ok", output, issues)
            content = content + [
                {
                    "type": "text",
                    "text": f"The previous answer did not match the required output schema: {last_error}. "
                    "Answer again, following the schema exactly.",
                }
            ]
        return HarnessResult("failed", None, [f"invalid output after retry: {last_error}"])

    def _parse(self, text: str, stop_reason: str) -> tuple[bool, dict[str, Any] | None, str]:
        if stop_reason == "refusal":
            return False, None, "refusal"
        if stop_reason == "max_tokens":
            return False, None, "output truncated at max_tokens"
        try:
            output = json.loads(text)
        except json.JSONDecodeError as exc:
            return False, None, f"not JSON: {exc}"
        try:
            jsonschema.validate(output, self.spec.schema)
        except jsonschema.ValidationError as exc:
            return False, None, f"{exc.message} at {'/'.join(map(str, exc.absolute_path))}"
        return True, output, ""
