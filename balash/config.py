"""Instance configuration: one YAML file per instance, with ${ENV} substitution."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_ENV = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


def _expand(value: Any) -> Any:
    if isinstance(value, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), value)
    if isinstance(value, list):
        return [_expand(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    return value


@dataclass
class WhatsAppConfig:
    phone_number_id: str = ""
    access_token: str = ""
    app_secret: str = ""
    verify_token: str = ""
    graph_version: str = "v23.0"

    @property
    def enabled(self) -> bool:
        return bool(self.phone_number_id and self.access_token)


@dataclass
class Config:
    root: Path
    instance: str = "personal"
    timezone: str = "Asia/Jerusalem"
    data_dir: Path = Path("data")
    pipelines_dir: Path = Path("config/pipelines")
    owners: list[str] = field(default_factory=list)
    default_model: str = "claude-opus-5-5"
    store_aliases: dict[str, list[str]] = field(default_factory=dict)
    tab_accounts: list[str] = field(default_factory=list)
    report_day: int = 1
    report_hour: int = 9
    whatsapp: WhatsAppConfig = field(default_factory=WhatsAppConfig)
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "balash.sqlite"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"


def load_config(path: str | Path | None = None) -> Config:
    """Load ``config/instance.yaml`` (or the given file). Missing file means defaults."""
    path = Path(path or os.environ.get("BALASH_CONFIG", "config/instance.yaml"))
    raw: dict[str, Any] = {}
    if path.exists():
        raw = _expand(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    root = path.parent.parent if path.parent.name == "config" else Path.cwd()

    def rel(p: str | None, default: str) -> Path:
        value = Path(p or default)
        return value if value.is_absolute() else (root / value)

    wa = raw.get("whatsapp") or {}
    stores = raw.get("stores") or {}
    report = raw.get("report") or {}
    return Config(
        root=root,
        instance=raw.get("instance", "personal"),
        timezone=raw.get("timezone", "Asia/Jerusalem"),
        data_dir=rel(raw.get("data_dir"), "data"),
        pipelines_dir=rel(raw.get("pipelines_dir"), "config/pipelines"),
        owners=[_digits(n) for n in raw.get("owners", []) if _digits(n)],
        default_model=(raw.get("llm") or {}).get("default_model", "claude-opus-5-5"),
        store_aliases={k: list(v or []) for k, v in (stores.get("aliases") or {}).items()},
        tab_accounts=list(stores.get("tab_accounts") or []),
        report_day=int(report.get("day_of_month", 1)),
        report_hour=int(report.get("hour", 9)),
        whatsapp=WhatsAppConfig(
            phone_number_id=str(wa.get("phone_number_id", "") or ""),
            access_token=str(wa.get("access_token", "") or ""),
            app_secret=str(wa.get("app_secret", "") or ""),
            verify_token=str(wa.get("verify_token", "") or ""),
            graph_version=str(wa.get("graph_version", "v23.0") or "v23.0"),
        ),
        raw=raw,
    )


def _digits(number: Any) -> str:
    return re.sub(r"\D", "", str(number or ""))
