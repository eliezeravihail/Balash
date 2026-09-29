"""monthly_stats: deterministic statistics over the stored purchases."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from ..core.block import Block, Context, register
from ..core.record import Record
from ..core.store import Store
from .ledger import spend_of
from .tab import current_balances

UNCATEGORIZED = "לא מסווג"
UNITEMIZED = "ללא פירוט"


def prev_month(month: str) -> str:
    y, m = map(int, month.split("-"))
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def month_bounds(month: str) -> tuple[date, date]:
    y, m = map(int, month.split("-"))
    start = date(y, m, 1)
    end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    return start, end - timedelta(days=1)


def _purchases(store: Store, month: str) -> list[Any]:
    start, end = month_bounds(month)
    return store.query(
        "SELECT * FROM receipts WHERE doc_type = 'purchase' AND date BETWEEN ? AND ? ORDER BY date, time",
        (start.isoformat(), end.isoformat()),
    )


def _unit_price(row: Any) -> float | None:
    if row["unit_price"] is not None and row["unit_price"] > 0:
        return float(row["unit_price"])
    q, t = row["quantity"], row["line_total"]
    if q and t and q > 0 and t > 0:
        return float(t) / float(q)
    return None


def compute(store: Store, month: str, min_price_change: float = 0.03) -> dict[str, Any]:
    receipts = _purchases(store, month)
    start, end = month_bounds(month)
    total = 0.0
    by_store: dict[str, float] = defaultdict(float)
    by_kind: dict[str, float] = defaultdict(float)
    by_week: dict[str, float] = defaultdict(float)
    by_category: dict[str, float] = defaultdict(float)
    item_spend: dict[str, dict[str, Any]] = {}
    counted = 0
    uncertain = 0
    for r in receipts:
        spend = spend_of(r)
        if spend is None:
            uncertain += 1
            continue
        counted += 1
        total += spend
        name = r["account_key"] or r["store_name"] or "לא מזוהה"
        by_store[name] += spend
        by_kind[r["store_kind"] or "unknown"] += spend
        d = date.fromisoformat(r["date"])
        week_start = max(d - timedelta(days=(d.weekday() + 1) % 7), start)  # weeks start on Sunday
        by_week[week_start.isoformat()] += spend
        if r["uncertain"] and r["uncertain"] != "[]":
            uncertain += 1
        lines = store.query(
            "SELECT l.*, c.category FROM lines l LEFT JOIN categories c ON c.norm_desc = l.norm_desc "
            "WHERE l.receipt_id = ? ORDER BY l.idx",
            (r["id"],),
        )
        itemized = 0.0
        for ln in lines:
            if ln["line_total"] is None:
                continue
            itemized += ln["line_total"]
            by_category[ln["category"] or UNCATEGORIZED] += ln["line_total"]
            if ln["line_total"] > 0 and (ln["category"] or "") != "פיקדון והנחות":
                entry = item_spend.setdefault(ln["norm_desc"], {"description": ln["description"], "spend": 0.0, "count": 0})
                entry["spend"] += ln["line_total"]
                entry["count"] += 1
        residual = spend - itemized
        if abs(residual) >= 1.0:
            by_category[UNITEMIZED] += residual

    prev = prev_month(month)
    prev_total = sum(s for s in (spend_of(r) for r in _purchases(store, prev)) if s is not None)
    change_pct = ((total - prev_total) / prev_total) if prev_total else None

    return {
        "month": month,
        "total": round(total, 2),
        "receipts": counted,
        "average_basket": round(total / counted, 2) if counted else None,
        "by_store": _sorted(by_store),
        "by_store_kind": _sorted(by_kind),
        "by_category": _sorted(by_category),
        "by_week": {k: round(v, 2) for k, v in sorted(by_week.items())},
        "top_items": sorted(
            ({"description": v["description"], "spend": round(v["spend"], 2), "count": v["count"]} for v in item_spend.values()),
            key=lambda x: -x["spend"],
        )[:8],
        "price_changes": price_changes(store, month, min_price_change),
        "previous_month": prev,
        "previous_total": round(prev_total, 2),
        "change_pct": round(change_pct, 4) if change_pct is not None else None,
        "uncertain_receipts": uncertain,
        "tab_balances": current_balances(store),
        "findings": [
            dict(f) for f in store.query(
                "SELECT kind, severity, account_key, message FROM findings WHERE substr(created_at, 1, 7) = ? ORDER BY created_at",
                (month,),
            )
        ],
    }


def price_changes(store: Store, month: str, threshold: float) -> list[dict[str, Any]]:
    """Unit price of the same product at the same store, this month vs. its previous purchase."""
    start, end = month_bounds(month)
    rows = store.query(
        "SELECT l.*, r.account_key, r.date FROM lines l JOIN receipts r ON r.id = l.receipt_id "
        "WHERE r.doc_type = 'purchase' AND r.date <= ? AND r.account_key != '' ORDER BY r.date, r.time, l.idx",
        (end.isoformat(),),
    )
    last_seen: dict[tuple[str, str], tuple[float, str]] = {}
    changes: dict[tuple[str, str], dict[str, Any]] = {}
    for ln in rows:
        price = _unit_price(ln)
        if price is None:
            continue
        key = (ln["account_key"], ln["norm_desc"])
        if key in last_seen and ln["date"] >= start.isoformat():
            old, old_date = last_seen[key]
            pct = (price - old) / old if old else 0
            if abs(pct) >= threshold:
                changes[key] = {
                    "description": ln["description"], "store": ln["account_key"], "old": round(old, 2),
                    "new": round(price, 2), "pct": round(pct, 4), "old_date": old_date, "new_date": ln["date"],
                }
        last_seen[key] = (price, ln["date"])
    return sorted(changes.values(), key=lambda c: -abs(c["pct"]))[:10]


def _sorted(d: dict[str, float]) -> dict[str, float]:
    return {k: round(v, 2) for k, v in sorted(d.items(), key=lambda kv: -kv[1])}


@register
class MonthlyStats(Block):
    """Input: ``month`` {month: YYYY-MM}. Output: ``monthly_stats`` with totals by
    store, store kind, category and week; top items; price changes; comparison
    with the previous month; tab balances. Params: ``min_price_change`` (0.03)."""

    name = "monthly_stats"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        threshold = float(self.params.get("min_price_change", 0.03))
        return [
            rec.derive("monthly_stats", compute(ctx.store, rec.data["month"], threshold))
            for rec in inputs
            if rec.kind == "month"
        ]
