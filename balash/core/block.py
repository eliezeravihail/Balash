"""The block contract shared by software blocks and harness blocks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Protocol
from zoneinfo import ZoneInfo

from .record import Record

if TYPE_CHECKING:
    from ..config import Config
    from ..harness.llm import LLMClient
    from .store import Store

log = logging.getLogger("balash")


class MessageSender(Protocol):
    def send_text(self, to: str, body: str) -> None: ...

    def send_image(self, to: str, path: str, caption: str | None = None) -> None: ...


@dataclass
class Context:
    """Everything a block may use while running. Blocks get nothing else."""

    config: "Config"
    store: "Store"
    llm: "LLMClient | None"
    sender: MessageSender
    recipient: str | None
    run_id: str = ""
    log: list[dict[str, Any]] = field(default_factory=list)
    now_override: datetime | None = None

    def now(self) -> datetime:
        if self.now_override is not None:
            return self.now_override
        return datetime.now(ZoneInfo(self.config.timezone))


class Block:
    """A block does one whole thing, with a defined input and output.

    Subclasses set ``name`` and ``kind`` and implement ``run``. Everything that
    varies between customers arrives in ``params`` from the pipeline file.
    """

    name: ClassVar[str] = ""
    kind: ClassVar[str] = "software"  # "software" or "harness"

    def __init__(self, params: dict[str, Any] | None = None):
        self.params = params or {}

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        raise NotImplementedError


_REGISTRY: dict[str, type[Block]] = {}


def register(cls: type[Block]) -> type[Block]:
    if not cls.name:
        raise ValueError(f"{cls.__name__} has no name")
    if cls.name in _REGISTRY and _REGISTRY[cls.name] is not cls:
        raise ValueError(f"duplicate block name {cls.name}")
    _REGISTRY[cls.name] = cls
    return cls


def get_block(name: str) -> type[Block]:
    from .. import blocks  # noqa: F401  (import registers all blocks)

    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown block '{name}'. Known: {', '.join(sorted(_REGISTRY))}") from None


def all_blocks() -> dict[str, type[Block]]:
    from .. import blocks  # noqa: F401

    return dict(_REGISTRY)
