"""The instance: config, store, model client and pipelines, wired together.

Channels (the WhatsApp webhook, the command line) call these methods. The
methods only build trigger records and run the pipelines named in config;
the work itself happens in blocks.
"""

from __future__ import annotations

import re
import threading
from datetime import datetime
from pathlib import Path

from .config import Config
from .core.block import Context, MessageSender
from .core.pipeline import Pipeline
from .core.record import Record
from .core.store import Store
from .harness.llm import LLMClient

INGEST = "groceries_ingest"
PAYMENT = "groceries_payment"
MONTHLY = "groceries_monthly"
BALANCES = "groceries_balances"


class Service:
    def __init__(self, config: Config, llm: LLMClient | None, store: Store | None = None):
        self.config = config
        self.store = store or Store(config.db_path)
        self.llm = llm
        self.media = None  # set by a channel that can download attachments (WhatsApp)
        self._pipelines: dict[str, Pipeline] = {}
        # One run at a time: runs read and then write the same ledger.
        self._run_lock = threading.Lock()

    def pipeline(self, name: str) -> Pipeline:
        if name not in self._pipelines:
            self._pipelines[name] = Pipeline.load(Path(self.config.pipelines_dir) / f"{name}.yaml")
        return self._pipelines[name]

    def context(self, sender: MessageSender, recipient: str | None, now: datetime | None = None) -> Context:
        return Context(
            config=self.config, store=self.store, llm=self.llm, sender=sender, recipient=recipient,
            now_override=now, media=self.media,
        )

    def run(self, name: str, records: list[Record], sender: MessageSender, recipient: str | None,
            label: str = "", now: datetime | None = None) -> dict[str, list[Record]]:
        with self._run_lock:
            return self.pipeline(name).run(records, self.context(sender, recipient, now), label)

    # ---- entry points ----------------------------------------------------

    def ingest(self, data: bytes, media_type: str, sender: MessageSender, recipient: str | None,
               source: str, caption: str = "", filename: str = "") -> dict[str, list[Record]]:
        incoming = Record(
            "incoming",
            {"bytes": data, "media_type": media_type, "source": source, "sender": recipient,
             "caption": caption, "filename": filename},
        )
        return self.run(INGEST, [incoming], sender, recipient, label=source)

    def ingest_whatsapp(self, message: dict, sender: MessageSender) -> dict[str, list[Record]]:
        """Hand a WhatsApp message to the ingest pipeline exactly as it arrived.
        The receipt_inbox block decides whether the sender is allowed."""
        return self.run(INGEST, [Record("whatsapp_message", message)], sender, message.get("sender"), label="whatsapp")

    def handle_text(self, text: str, sender: MessageSender, recipient: str | None,
                    now: datetime | None = None) -> dict[str, list[Record]] | None:
        text = (text or "").strip()
        now = now or datetime.now(self.context(sender, recipient).now().tzinfo)
        if text.startswith("שילמתי"):
            return self.run(PAYMENT, [Record("command", {"text": text})], sender, recipient, "text", now)
        if text in ("יתרה", "יתרות", "חשבון"):
            return self.run(BALANCES, [Record("command", {"text": text})], sender, recipient, "text", now)
        month = parse_report_request(text, now)
        if month:
            return self.monthly(month, sender, recipient)
        from .blocks.wording import HELP

        if recipient:
            sender.send_text(recipient, HELP)
        return None

    def monthly(self, month: str, sender: MessageSender, recipient: str | None) -> dict[str, list[Record]]:
        return self.run(MONTHLY, [Record("month", {"month": month})], sender, recipient, label=f"report {month}")

    def due_monthly_report(self, now: datetime) -> str | None:
        """The previous month, from the configured day and hour and for one week after
        (so a server that was down still catches up), unless it was already sent."""
        if (now.day, now.hour) < (self.config.report_day, self.config.report_hour):
            return None
        if now.day >= self.config.report_day + 7:
            return None
        month = f"{now.year - 1}-12" if now.month == 1 else f"{now.year}-{now.month - 1:02d}"
        if self.store.kv_get("last_report_month") == month:
            return None
        return month


def parse_report_request(text: str, now: datetime) -> str | None:
    m = re.fullmatch(r"(?:דוח|דו\"ח|דו״ח|סיכום)(?:\s+(\d{4})-(\d{1,2})|\s+(\d{1,2}))?", text.strip())
    if not m:
        return None
    if m.group(1):
        return f"{int(m.group(1))}-{int(m.group(2)):02d}"
    if m.group(3):
        month = int(m.group(3))
        if not 1 <= month <= 12:
            return None
        year = now.year if month <= now.month else now.year - 1
        return f"{year}-{month:02d}"
    return f"{now.year}-{now.month:02d}"
