"""The one place that talks to the model.

Harness blocks never call the SDK directly. They hand a request to an
``LLMClient``; tests and offline runs use ``FakeLLM`` with the same interface.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass
class LLMRequest:
    block: str
    model: str
    system: str
    content: list[dict[str, Any]]
    schema: dict[str, Any]
    effort: str = "medium"
    max_tokens: int = 16000


@dataclass
class LLMResponse:
    text: str
    stop_reason: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    latency_ms: int = 0
    refusal_category: str | None = None


class LLMClient(Protocol):
    def complete(self, request: LLMRequest) -> LLMResponse: ...


class AnthropicLLM:
    """Claude through the official SDK: structured output, prompt caching on
    the block instructions, and server-side fallback on a refusal."""

    FALLBACK_BETA = "server-side-fallback-2026-07-01"

    def __init__(self, client: Any | None = None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self.client = client

    def complete(self, request: LLMRequest) -> LLMResponse:
        started = time.monotonic()
        response = self.client.beta.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            betas=[self.FALLBACK_BETA],
            fallbacks="default",
            system=[{"type": "text", "text": request.system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": request.content}],
            output_config={
                "effort": request.effort,
                "format": {"type": "json_schema", "schema": request.schema},
            },
        )
        text = ""
        if response.stop_reason != "refusal":
            text = next((b.text for b in response.content if b.type == "text"), "")
        usage = response.usage
        details = getattr(response, "stop_details", None)
        return LLMResponse(
            text=text,
            stop_reason=response.stop_reason or "",
            model=response.model,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            latency_ms=int((time.monotonic() - started) * 1000),
            refusal_category=getattr(details, "category", None) if details else None,
        )


@dataclass
class FakeLLM:
    """Returns scripted outputs per block. ``responses[block]`` is either a
    list consumed in order or a function ``request -> dict | str``."""

    responses: dict[str, list[Any] | Callable[[LLMRequest], Any]] = field(default_factory=dict)
    calls: list[LLMRequest] = field(default_factory=list)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        source = self.responses.get(request.block)
        if source is None:
            raise AssertionError(f"FakeLLM has no response for block {request.block}")
        value = source(request) if callable(source) else source.pop(0)
        if isinstance(value, LLMResponse):
            return value
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        return LLMResponse(text=text, stop_reason="end_turn", model=request.model)
