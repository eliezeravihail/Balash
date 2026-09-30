"""Grocery tab checks. Pure software: the model only read the slips.

A grocery tab is a running account. Each slip may print the previous
balance, this charge, a payment and the new balance. Walking the slips in
order, the previous balance printed on each slip must equal the balance after
the slip before it, adjusted by payments the person reported. A jump up means
charges that no slip the person holds explains, for example someone buying
on the wrong account.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from ..core.block import Block, Context, register
from ..core.record import Record, new_id
from ..core.store import Store, utcnow
from ..core.text import resolve_account
from . import wording
from .ledger import match_alias, spend_of


@dataclass
class TabEvent:
    kind: str  # receipt | payment
    id: str
    date: str
    time: str
    created_at: str
    doc_type: str = ""
    previous: float | None = None
    charged: float | None = None
    paid: float | None = None
    new: float | None = None
    amount: float | None = None

    @property
    def label(self) -> str:
        if self.kind == "payment":
            return "התשלום שרשמת"
        return "הקבלה על התשלום" if self.doc_type == "payment" else "הקבלה"


def tab_accounts(store: Store) -> list[str]:
    rows = store.query(
        "SELECT DISTINCT account_key FROM receipts WHERE account_key != '' AND ("
        "tab_previous_balance IS NOT NULL OR tab_new_balance IS NOT NULL OR tab_charged IS NOT NULL "
        "OR payment_method = 'tab' OR doc_type IN ('payment', 'account_statement')) "
        "UNION SELECT DISTINCT account_key FROM payments"
    )
    return sorted(r["account_key"] for r in rows)


def load_events(store: Store, account: str) -> list[TabEvent]:
    events: list[TabEvent] = []
    for r in store.query(
        "SELECT * FROM receipts WHERE account_key = ? AND doc_type IN ('purchase', 'payment') "
        "AND (tab_previous_balance IS NOT NULL OR tab_new_balance IS NOT NULL OR tab_charged IS NOT NULL "
        "OR tab_paid IS NOT NULL OR payment_method = 'tab' OR doc_type = 'payment')",
        (account,),
    ):
        charged = r["tab_charged"]
        paid = r["tab_paid"]
        if r["doc_type"] == "purchase" and charged is None and r["payment_method"] == "tab":
            charged = r["total"]
        if r["doc_type"] == "payment" and paid is None:
            paid = r["total"]
        events.append(
            TabEvent(
                kind="receipt", id=r["id"], date=r["date"] or "", time=r["time"] or "", created_at=r["created_at"],
                doc_type=r["doc_type"], previous=r["tab_previous_balance"], charged=charged, paid=paid,
                new=r["tab_new_balance"],
            )
        )
    for p in store.query("SELECT * FROM payments WHERE account_key = ? AND source = 'text'", (account,)):
        events.append(
            TabEvent(kind="payment", id=p["id"], date=p["date"], time=p["time"] or "", created_at=p["created_at"], amount=p["amount"])
        )
    events.sort(key=lambda e: (e.date, e.time, e.created_at))
    return events


def walk(events: list[TabEvent], tolerance: float) -> tuple[list[dict[str, Any]], float | None]:
    """Return (problems, balance after the last event). Deterministic."""
    problems: list[dict[str, Any]] = []
    balance: float | None = None
    last: TabEvent | None = None
    for ev in events:
        if ev.kind == "payment":
            if balance is not None and ev.amount is not None:
                balance -= ev.amount
            last = ev
            continue
        if ev.previous is not None and balance is not None and last is not None:
            delta = round(ev.previous - balance, 2)
            if abs(delta) > tolerance:
                problems.append(
                    {
                        "kind": "unexplained_increase" if delta > 0 else "unexplained_decrease",
                        "severity": "high" if delta > 0 else "medium",
                        "cites": [last.id, ev.id],
                        "data": {
                            "date": ev.date, "printed_previous": ev.previous, "expected_previous": round(balance, 2),
                            "delta": delta, "last_date": last.date, "last_label": last.label,
                        },
                    }
                )
        if ev.previous is not None and ev.new is not None and (ev.charged is not None or ev.paid is not None):
            expected = round(ev.previous + (ev.charged or 0) - (ev.paid or 0), 2)
            if abs(expected - ev.new) > tolerance:
                problems.append(
                    {
                        "kind": "internal_mismatch",
                        "severity": "high",
                        "cites": [ev.id],
                        "data": {
                            "date": ev.date, "previous": ev.previous, "charged": ev.charged or 0, "paid": ev.paid or 0,
                            "expected": expected, "printed_new": ev.new,
                        },
                    }
                )
        if ev.new is not None:
            balance = ev.new
        else:
            base = ev.previous if ev.previous is not None else balance
            if base is not None:
                balance = base + (ev.charged or 0) - (ev.paid or 0)
        last = ev
    return problems, (round(balance, 2) if balance is not None else None)


def current_balances(store: Store, tolerance: float = 0.5) -> dict[str, float | None]:
    return {acc: walk(load_events(store, acc), tolerance)[1] for acc in tab_accounts(store)}


def _save_findings(ctx: Context, account: str, problems: list[dict[str, Any]], source: Record | None) -> list[Record]:
    out: list[Record] = []
    for p in problems:
        data = {**p["data"], "store": account}
        message = wording.finding_message(p["kind"], data)
        finding = {
            "id": new_id("find"),
            "dedupe_key": f"{p['kind']}:{account}:{':'.join(p['cites'])}",
            "kind": p["kind"],
            "severity": p["severity"],
            "account_key": account,
            "message": message,
            "data": data,
            "cites": p["cites"],
        }
        if ctx.store.insert_finding(finding):
            out.append(Record("finding", {**finding, "created_at": utcnow()}, id=finding["id"], cites=p["cites"]))
    return out


@register
class TabContinuity(Block):
    """Input: records with ``account_key`` (stored receipts, payments).
    Output: new ``finding`` records only; findings already reported are not repeated.
    Params: ``tolerance`` in shekels (default 0.5)."""

    name = "tab_continuity"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        tolerance = float(self.params.get("tolerance", 0.5))
        accounts = sorted({r.data.get("account_key") for r in inputs if r.data.get("account_key")})
        out: list[Record] = []
        for account in accounts:
            problems, _ = walk(load_events(ctx.store, account), tolerance)
            out.extend(_save_findings(ctx, account, problems, None))
        return out


@register
class StatementReconcile(Block):
    """Input: ``stored_receipt`` records; acts on account statements among them.
    Every charge on the statement must match a slip the person sent (same
    account, amount within tolerance, date within the window). Output: new
    ``finding`` records. Params: ``date_window_days`` (1), ``amount_tolerance`` (0.5)."""

    name = "statement_reconcile"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        window = int(self.params.get("date_window_days", 1))
        tol = float(self.params.get("amount_tolerance", 0.5))
        out: list[Record] = []
        for rec in inputs:
            d = rec.data
            if rec.kind != "stored_receipt" or d.get("doc_type") != "account_statement" or not d.get("receipt_id"):
                continue
            if d.get("duplicate_of"):
                continue
            account = d.get("account_key")
            if not account:
                continue
            lines = ctx.store.query(
                "SELECT * FROM statement_lines WHERE receipt_id = ? ORDER BY idx", (d["receipt_id"],)
            )
            charges = [ln for ln in lines if ln["amount"] is not None and ln["amount"] > 0]
            dates = [date.fromisoformat(ln["date"]) for ln in charges if _valid(ln["date"])]
            if not dates:
                continue
            start, end = min(dates) - timedelta(days=window), max(dates) + timedelta(days=window)
            receipts = [
                r for r in ctx.store.query(
                    "SELECT * FROM receipts WHERE account_key = ? AND doc_type = 'purchase' AND date BETWEEN ? AND ?",
                    (account, start.isoformat(), end.isoformat()),
                )
            ]
            unmatched = {r["id"]: r for r in receipts}
            problems = []
            for ln in charges:
                match = None
                for rid, r in unmatched.items():
                    amount = r["tab_charged"] if r["tab_charged"] is not None else spend_of(r)
                    if amount is None or not _valid(r["date"]) or not _valid(ln["date"]):
                        continue
                    if abs(amount - ln["amount"]) <= tol and abs(
                        (date.fromisoformat(r["date"]) - date.fromisoformat(ln["date"])).days
                    ) <= window:
                        match = rid
                        break
                if match:
                    unmatched.pop(match)
                else:
                    problems.append(
                        {
                            "kind": "charge_without_receipt",
                            "severity": "high",
                            "cites": [d["receipt_id"], f"{d['receipt_id']}#{ln['idx']}"],
                            "data": {"date": ln["date"], "amount": ln["amount"], "description": ln["description"]},
                        }
                    )
            for r in unmatched.values():
                problems.append(
                    {
                        "kind": "receipt_missing_from_statement",
                        "severity": "low",
                        "cites": [d["receipt_id"], r["id"]],
                        "data": {"date": r["date"], "amount": r["tab_charged"] if r["tab_charged"] is not None else spend_of(r)},
                    }
                )
            out.extend(_save_findings(ctx, account, problems, rec))
        return out


def _valid(value: str | None) -> bool:
    if not value:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


PAY_RE = re.compile(r'^\s*שילמתי\s+([\d.,]+)\s*(?:₪|ש"ח|ש״ח|שח|שקלים|שקל)?\s*(?:ל|ב|על|עבור)?\s*(.*)$')


@register
class PaymentFromText(Block):
    """Input: ``command`` {text}. Output: ``payment`` records, stored in the
    payments table, or a ``payment`` record with an ``error`` to ask back."""

    name = "payment_from_text"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out: list[Record] = []
        for rec in inputs:
            if rec.kind != "command":
                continue
            m = PAY_RE.match(rec.data.get("text", ""))
            if not m:
                out.append(rec.derive("payment", {"error": "no_amount"}))
                continue
            try:
                amount = float(m.group(1).replace(",", ""))
            except ValueError:
                out.append(rec.derive("payment", {"error": "no_amount"}))
                continue
            name = m.group(2).strip()
            known = sorted(set(tab_accounts(ctx.store)) | set(ctx.config.tab_accounts))
            account = ""
            if name:
                account = match_alias(name, ctx.config.store_aliases) or resolve_account(name, ctx.config.store_aliases)
            elif len(known) == 1:
                account = known[0]
            if not account:
                out.append(rec.derive("payment", {"error": "no_account", "amount": amount, "known": known}))
                continue
            now = ctx.now()
            pay = {
                "id": new_id("pay"), "account_key": account, "date": now.date().isoformat(),
                "time": now.strftime("%H:%M"), "amount": amount, "source": "text", "ref": rec.id,
                "created_at": utcnow(),
            }
            with ctx.store.tx() as c:
                c.execute(
                    "INSERT INTO payments(id, account_key, date, time, amount, source, ref, created_at) "
                    "VALUES(:id, :account_key, :date, :time, :amount, :source, :ref, :created_at)",
                    pay,
                )
            out.append(Record("payment", pay, id=pay["id"], cites=[rec.id]))
        return out
