"""purchase_ledger: stores what the receipt block read, deterministically."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from ..core.block import Block, Context, register
from ..core.record import Record, new_id
from ..core.store import utcnow
from ..core.text import normalize_desc, normalize_store, resolve_account


def match_alias(text: str | None, aliases: dict[str, list[str]]) -> str:
    """Return a canonical store name only if the text mentions a configured one."""
    norm = normalize_store(text)
    if not norm:
        return ""
    for canon, names in aliases.items():
        for candidate in [canon, *names]:
            key = normalize_store(candidate)
            if key and key in norm:
                return canon
    return ""


def account_for(output: dict[str, Any], caption: str | None, ctx: Context) -> str:
    aliases = ctx.config.store_aliases
    printed = (output.get("store") or {}).get("name")
    if printed:
        return resolve_account(printed, aliases)
    from_caption = match_alias(caption, aliases)
    if from_caption:
        return from_caption
    if output.get("tab") and len(ctx.config.tab_accounts) == 1:
        return ctx.config.tab_accounts[0]
    return ""


def iso_date(value: str | None) -> str | None:
    """Only a valid YYYY-MM-DD goes into the date column; the raw value stays in the JSON."""
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return None


def spend_of(row: Any) -> float | None:
    """What a purchase cost: the printed total, or the tab charge when only that is printed."""
    if row["total"] is not None:
        return float(row["total"])
    if row["tab_charged"] is not None:
        return float(row["tab_charged"])
    return None


@register
class PurchaseLedger(Block):
    """Input: ``receipt`` records. Output: ``stored_receipt`` records.
    Guarantees: the same receipt (same store, number, date and total) is stored
    once; payment documents also land in the payments table; nothing is
    computed that the document did not print."""

    name = "purchase_ledger"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out: list[Record] = []
        for rec in inputs:
            if rec.kind != "receipt":
                continue
            d = rec.data
            output = d.get("output")
            if d["status"] in ("failed", "refused", "error") or not output:
                ctx.store.set_item_status(d["item_id"], d["status"])
                out.append(rec.derive("stored_receipt", {"status": d["status"], "item_id": d["item_id"], "issues": d["issues"]}))
                continue
            out.append(self._store(rec, output, ctx))
        return out

    def _store(self, rec: Record, o: dict[str, Any], ctx: Context) -> Record:
        d = rec.data
        store_info = o.get("store") or {}
        tab = o.get("tab") or {}
        account = account_for(o, d.get("caption"), ctx)
        uncertain = sorted(set(o.get("uncertain_fields") or []) | {i.split(":")[0] for i in d["issues"]})
        summary = {
            "status": d["status"],
            "item_id": d["item_id"],
            "doc_type": o["doc_type"],
            "account_key": account,
            "store_name": store_info.get("name") or account or None,
            "store_kind": store_info.get("kind"),
            "date": o.get("date"),
            "total": o.get("total"),
            "n_lines": len(o.get("lines") or []),
            "tab": tab or None,
            "uncertain": uncertain,
            "issues": d["issues"],
            "notes": o.get("notes"),
        }

        day = iso_date(o.get("date"))
        dup = None
        if o.get("receipt_number") and account:
            dup = ctx.store.one(
                "SELECT id, item_id FROM receipts WHERE account_key = ? AND receipt_number = ? "
                "AND IFNULL(date,'') = IFNULL(?, '') AND IFNULL(total, -1) = IFNULL(?, -1)",
                (account, o["receipt_number"], day, o.get("total")),
            )
        elif account and day and (o.get("time") or tab.get("new_balance") is not None):
            # no receipt number (typical for a grocery slip): same store, day, time,
            # total and printed balance means the same slip photographed again
            dup = ctx.store.one(
                "SELECT id, item_id FROM receipts WHERE account_key = ? AND receipt_number IS NULL AND date = ? "
                "AND IFNULL(time,'') = IFNULL(?, '') AND IFNULL(total, -1) = IFNULL(?, -1) "
                "AND IFNULL(tab_new_balance, -1) = IFNULL(?, -1) AND doc_type = ?",
                (account, day, o.get("time"), o.get("total"), tab.get("new_balance"), o["doc_type"]),
            )
        if dup is not None:
            ctx.store.set_item_status(d["item_id"], "duplicate")
            return rec.derive("stored_receipt", {**summary, "duplicate_of": dup["id"], "receipt_id": dup["id"]})

        receipt_id = new_id("rcpt")
        with ctx.store.tx() as c:
            c.execute(
                "INSERT INTO receipts(id, item_id, doc_type, account_key, store_name, store_kind, receipt_number, date, time, "
                "total, discount_total, payment_method, tab_customer, tab_previous_balance, tab_charged, tab_paid, "
                "tab_new_balance, uncertain, data, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    receipt_id, d["item_id"], o["doc_type"], account, store_info.get("name"), store_info.get("kind"),
                    o.get("receipt_number"), day, o.get("time"), o.get("total"), o.get("discount_total"),
                    o.get("payment_method"), tab.get("customer_ref"), tab.get("previous_balance"), tab.get("charged"),
                    tab.get("paid"), tab.get("new_balance"), json.dumps(uncertain, ensure_ascii=False),
                    json.dumps(o, ensure_ascii=False), utcnow(),
                ),
            )
            for i, ln in enumerate(o.get("lines") or []):
                c.execute(
                    "INSERT INTO lines(receipt_id, idx, description, norm_desc, barcode, quantity, unit, unit_price, line_total) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        receipt_id, i, ln["description"], normalize_desc(ln["description"]), ln.get("barcode"),
                        ln.get("quantity"), ln.get("unit"), ln.get("unit_price"), ln.get("line_total"),
                    ),
                )
            for i, sl in enumerate(o.get("statement_lines") or []):
                c.execute(
                    "INSERT INTO statement_lines(receipt_id, idx, date, description, amount, reference) VALUES(?,?,?,?,?,?)",
                    (receipt_id, i, sl.get("date"), sl.get("description"), sl.get("amount"), sl.get("reference")),
                )
            if o["doc_type"] == "payment" and account:
                amount = tab.get("paid") if tab.get("paid") is not None else o.get("total")
                if amount is not None:
                    c.execute(
                        "INSERT INTO payments(id, account_key, date, time, amount, source, ref, created_at) VALUES(?,?,?,?,?,?,?,?)",
                        (new_id("pay"), account, day or "", o.get("time"), float(amount), "receipt", receipt_id, utcnow()),
                    )
            c.execute(
                "UPDATE items SET status = ? WHERE id = ?",
                ("uncertain" if d["status"] == "uncertain" else "stored", d["item_id"]),
            )
        return rec.derive("stored_receipt", {**summary, "receipt_id": receipt_id})
