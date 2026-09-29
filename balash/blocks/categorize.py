"""categorize_items: harness block, called only for product descriptions never seen before."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..core.block import Context, register
from ..core.record import Record
from ..core.store import utcnow
from ..harness.runtime import HarnessBlock, HarnessResult, Unit

BATCH = 80


@register
class CategorizeItems(HarnessBlock):
    """Input: ``stored_receipt`` records. Output: one ``categories`` record per
    model call, listing what was assigned. Every assignment is stored in the
    categories table and reused, so the model sees each description once."""

    name = "categorize_items"

    def build_units(self, inputs: list[Record], ctx: Context) -> list[Unit]:
        receipt_ids = [r.data["receipt_id"] for r in inputs if r.kind == "stored_receipt" and r.data.get("receipt_id")]
        if not receipt_ids:
            return []
        marks = ",".join("?" * len(receipt_ids))
        rows = ctx.store.query(
            f"SELECT DISTINCT l.norm_desc, l.description FROM lines l "
            f"LEFT JOIN categories c ON c.norm_desc = l.norm_desc "
            f"WHERE l.receipt_id IN ({marks}) AND c.norm_desc IS NULL ORDER BY l.norm_desc",
            tuple(receipt_ids),
        )
        seen: dict[str, str] = {}
        for row in rows:
            seen.setdefault(row["norm_desc"], row["description"])
        pending = list(seen.items())
        units = []
        for start in range(0, len(pending), BATCH):
            batch = pending[start : start + BATCH]
            listing = "\n".join(f"{i}. {desc}" for i, (_, desc) in enumerate(batch))
            units.append(
                Unit(
                    content=[{"type": "text", "text": f"Categorize these {len(batch)} product lines:\n{listing}"}],
                    digest=hashlib.sha256(json.dumps([k for k, _ in batch], ensure_ascii=False).encode()).hexdigest(),
                    cites=[r.id for r in inputs if r.kind == "stored_receipt"],
                    context={"batch": batch},
                )
            )
        return units

    def check(self, output: dict[str, Any], unit: Unit) -> list[str]:
        batch = unit.context["batch"]
        got = {item["index"] for item in output["items"]}
        missing = [i for i in range(len(batch)) if i not in got]
        return [f"items: no category for index {i}" for i in missing]

    def to_records(self, result: HarnessResult, unit: Unit, ctx: Context) -> list[Record]:
        batch = unit.context["batch"]
        assigned: dict[str, str] = {}
        if result.output:
            for item in result.output["items"]:
                if 0 <= item["index"] < len(batch):
                    assigned[batch[item["index"]][0]] = item["category"]
        with ctx.store.tx() as c:
            for norm_desc, category in assigned.items():
                c.execute(
                    "INSERT OR IGNORE INTO categories(norm_desc, category, source, created_at) VALUES(?,?,?,?)",
                    (norm_desc, category, "model", utcnow()),
                )
        return [Record("categories", {"status": result.status, "assigned": assigned}, cites=list(unit.cites))]
