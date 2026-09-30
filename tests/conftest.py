from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from balash.channels.whatsapp import ConsoleSender
from balash.config import Config
from balash.harness.llm import FakeLLM, LLMRequest
from balash.service import Service

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_RULES = [
    ("חלב", "חלב וביצים"), ("גבינה", "חלב וביצים"), ("ביצים", "חלב וביצים"),
    ("לחם", "לחם ומאפים"), ("עגבני", "ירקות ופירות"), ("מלפפון", "ירקות ופירות"),
    ("במבה", "ממתקים וחטיפים"), ("אקונומיקה", "ניקיון"), ("הנחה", "פיקדון והנחות"),
]


def image_bytes(seed: int) -> bytes:
    img = Image.new("RGB", (240, 360), color=(seed % 256, (seed * 7) % 256, (seed * 13) % 256))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def line(desc: str, total: float, qty: float | None = 1, unit_price: float | None = None) -> dict[str, Any]:
    return {
        "description": desc, "barcode": None, "quantity": qty, "unit": "יח'" if qty else None,
        "unit_price": unit_price if unit_price is not None else (total / qty if qty else None),
        "line_total": total, "source_text": f"{desc} {total}",
    }


def receipt(
    store: str | None = "שופרסל דיל",
    date: str = "2026-09-03",
    lines: list[dict] | None = None,
    total: float | None = None,
    kind: str = "supermarket",
    tab: dict | None = None,
    doc_type: str = "purchase",
    number: str | None = None,
    payment: str = "card",
    statement: list[dict] | None = None,
    uncertain: list[str] | None = None,
    time: str | None = "10:00",
) -> dict[str, Any]:
    lines = lines if lines is not None else []
    if total is None and doc_type == "purchase" and lines:
        total = round(sum(ln["line_total"] for ln in lines), 2)
    return {
        "doc_type": doc_type,
        "store": {"name": store, "branch": None, "kind": kind, "business_id": None},
        "receipt_number": number, "date": date, "time": time, "currency": "ILS",
        "lines": lines, "discount_total": None, "total": total, "payment_method": payment,
        "tab": tab, "statement_lines": statement or [], "uncertain_fields": uncertain or [], "notes": None,
    }


def tab(prev=None, charged=None, paid=None, new=None, customer=None) -> dict[str, Any]:
    return {"customer_ref": customer, "previous_balance": prev, "charged": charged, "paid": paid, "new_balance": new}


def caption_of(request: LLMRequest) -> str:
    text = next(b["text"] for b in request.content if b["type"] == "text")
    m = re.search(r"Caption typed by the sender: (\S+)", text)
    return m.group(1) if m else ""


def fake_categorize(request: LLMRequest) -> dict[str, Any]:
    text = request.content[0]["text"]
    items = []
    for row in text.splitlines()[1:]:
        idx, desc = row.split(". ", 1)
        category = next((c for key, c in CATEGORY_RULES if key in desc), "אחר")
        items.append({"index": int(idx), "description": desc, "category": category})
    return {"items": items}


class Harness:
    """A service wired to a fake model, with receipts keyed by caption."""

    def __init__(self, tmp_path: Path):
        self.outputs: dict[str, Any] = {}
        self.llm = FakeLLM(
            responses={
                "receipt_to_records": lambda req: self.outputs[caption_of(req)],
                "categorize_items": fake_categorize,
            }
        )
        self.config = Config(
            root=tmp_path,
            data_dir=tmp_path / "data",
            pipelines_dir=ROOT / "config" / "pipelines",
            owners=["972500000001"],
            store_aliases={"מכולת יוסי": ["יוסי מרקט", "מינימרקט יוסי"], "שופרסל": ["שופרסל דיל"]},
            tab_accounts=["מכולת יוסי"],
        )
        self.service = Service(self.config, self.llm)
        self.out = ConsoleSender(echo=False)
        self._seed = 0

    def send(self, output: Any, caption: str | None = None, data: bytes | None = None) -> list[str]:
        """Send one document whose model output is ``output``; return the texts sent back."""
        self._seed += 1
        caption = caption or f"doc{self._seed}"
        self.outputs[caption] = output
        before = len(self.out.sent)
        self.service.ingest(data or image_bytes(self._seed), "image/jpeg", self.out, "972500000001", "test", caption=caption)
        return [body for _, kind, body in self.out.sent[before:] if kind == "text"]

    def text(self, message: str, now=None) -> list[str]:
        before = len(self.out.sent)
        self.service.handle_text(message, self.out, "972500000001", now)
        return [body for _, kind, body in self.out.sent[before:] if kind == "text"]

    def calls(self, block: str) -> int:
        return sum(1 for c in self.llm.calls if c.block == block)


@pytest.fixture
def h(tmp_path: Path) -> Harness:
    return Harness(tmp_path)
