"""receipt_to_records: the harness block that reads shopping documents."""

from __future__ import annotations

import base64
import hashlib
import io
from datetime import date
from pathlib import Path
from typing import Any

from ..core.block import Context, register
from ..core.record import Record
from ..harness.runtime import HarnessBlock, HarnessResult, Unit

MAX_EDGE = 2600
MAX_BYTES = 4_500_000


def prepare_image(raw: bytes) -> bytes:
    """Upright, RGB, bounded size JPEG. Deterministic for the same input."""
    from PIL import Image, ImageOps

    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img).convert("RGB")
    if max(img.size) > MAX_EDGE:
        img.thumbnail((MAX_EDGE, MAX_EDGE))
    for quality in (88, 80, 70, 60):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= MAX_BYTES:
            break
    return buf.getvalue()


def _close(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


@register
class ReceiptToRecords(HarnessBlock):
    """Input: ``item`` records (photo or PDF).
    Output: ``receipt`` {item_id, status, issues, output}, one per item.
    Status is ok, uncertain, failed or refused. The model transcribes; the
    checks below verify the printed numbers agree with each other."""

    name = "receipt_to_records"

    def build_units(self, inputs: list[Record], ctx: Context) -> list[Unit]:
        units: list[Unit] = []
        for rec in inputs:
            if rec.kind != "item":
                continue
            raw = Path(rec.data["path"]).read_bytes()
            if rec.data["media_type"] == "application/pdf":
                payload, media_type, block_type = raw, "application/pdf", "document"
            else:
                payload, media_type, block_type = prepare_image(raw), "image/jpeg", "image"
            content: list[dict[str, Any]] = [
                {
                    "type": block_type,
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64.standard_b64encode(payload).decode("ascii"),
                    },
                }
            ]
            caption = (rec.data.get("caption") or "").strip()
            note = f"Caption typed by the sender: {caption}" if caption else "No caption."
            content.append({"type": "text", "text": f"Transcribe this document. {note}"})
            digest = hashlib.sha256(payload + caption.encode()).hexdigest()
            units.append(Unit(content=content, digest=digest, cites=[rec.id], context={"item": rec.data}))
        return units

    def check(self, output: dict[str, Any], unit: Unit) -> list[str]:
        issues: list[str] = []
        for field_name in ("date",):
            value = output.get(field_name)
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    issues.append(f"{field_name}: not a valid date '{value}'")
        doc_type = output.get("doc_type")
        total = output.get("total")
        if doc_type == "purchase":
            if total is None:
                tab = output.get("tab") or {}
                if tab.get("charged") is None:
                    issues.append("total: missing")
            lines = output.get("lines") or []
            amounts = [ln.get("line_total") for ln in lines]
            if total is not None and lines and all(a is not None for a in amounts):
                expected = sum(amounts) - (output.get("discount_total") or 0)
                if not _close(expected, total, max(1.0, abs(total) * 0.01)):
                    issues.append(f"total: lines add up to {expected:.2f} but the printed total is {total:.2f}")
        tab = output.get("tab")
        if tab:
            prev, charged, paid, new = (tab.get(k) for k in ("previous_balance", "charged", "paid", "new_balance"))
            if prev is not None and new is not None and (charged is not None or paid is not None):
                expected = prev + (charged or 0) - (paid or 0)
                if not _close(expected, new, 0.5):
                    issues.append(
                        f"tab.new_balance: {prev:.2f} + {charged or 0:.2f} - {paid or 0:.2f} = {expected:.2f}, printed {new:.2f}"
                    )
        return issues

    def to_records(self, result: HarnessResult, unit: Unit, ctx: Context) -> list[Record]:
        status = result.status
        if result.output and result.output.get("uncertain_fields") and status == "ok":
            status = "uncertain"
        if result.output and result.output.get("doc_type") == "unreadable":
            status = "failed"
        item = unit.context["item"]
        return [
            Record(
                "receipt",
                {
                    "item_id": item["id"],
                    "caption": item.get("caption"),
                    "status": status,
                    "issues": result.issues,
                    "output": result.output,
                    "cached": result.cached,
                },
                cites=list(unit.cites),
            )
        ]
