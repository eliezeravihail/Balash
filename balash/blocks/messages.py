"""Blocks that turn results into messages, and the block that sends them."""

from __future__ import annotations

from ..core.block import Block, Context, log, register
from ..core.record import Record
from ..core.text import money, month_label
from . import wording
from .tab import current_balances


@register
class ReceiptAck(Block):
    """Input: ``stored_receipt``, ``duplicate_item``, ``unsupported_item``.
    Output: one ``message`` per document, telling the sender what was read."""

    name = "receipt_ack"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out = []
        for rec in inputs:
            if rec.kind == "stored_receipt":
                out.append(rec.derive("message", {"text": wording.receipt_ack(rec.data)}))
            elif rec.kind == "duplicate_item":
                out.append(rec.derive("message", {"text": wording.duplicate_item(rec.data["received_at"])}))
            elif rec.kind == "unsupported_item":
                out.append(rec.derive("message", {"text": wording.unsupported_item(rec.data["media_type"])}))
        return out


@register
class FindingMessages(Block):
    """Input: ``finding``. Output: ``message``, high severity first.
    Params: ``min_severity`` (low | medium | high, default low)."""

    name = "finding_messages"
    ORDER = {"high": 0, "medium": 1, "low": 2}

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        floor = self.ORDER[self.params.get("min_severity", "low")]
        findings = [r for r in inputs if r.kind == "finding" and self.ORDER[r.data["severity"]] <= floor]
        findings.sort(key=lambda r: self.ORDER[r.data["severity"]])
        return [r.derive("message", {"text": r.data["message"]}) for r in findings]


@register
class PaymentAck(Block):
    """Input: ``payment``. Output: one ``message`` confirming the payment or asking what was missing."""

    name = "payment_ack"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        return [r.derive("message", {"text": wording.payment_ack(r.data)}) for r in inputs if r.kind == "payment"]


@register
class BalancesText(Block):
    """Input: any trigger. Output: one ``message`` with the balance of every tab account."""

    name = "balances_text"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        balances = current_balances(ctx.store, float(self.params.get("tolerance", 0.5)))
        if not balances:
            text = "עדיין אין חשבונות מכולת במעקב. שלח קבלה שמופיעה בה יתרה."
        else:
            rows = [f"• {acc}: {money(bal) if bal is not None else 'לא ידועה עדיין'}" for acc, bal in balances.items()]
            text = "*יתרות בחשבונות*\n" + "\n".join(rows)
        cites = [r.id for r in inputs]
        return [Record("message", {"text": text}, cites=cites)]


@register
class MonthlyReportText(Block):
    """Input: ``monthly_stats``. Output: one ``message`` with the monthly summary."""

    name = "monthly_report_text"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        return [rec.derive("message", {"text": self.render(rec.data)}) for rec in inputs if rec.kind == "monthly_stats"]

    @staticmethod
    def render(s: dict) -> str:
        label = month_label(s["month"])
        if not s["receipts"]:
            return f"*סיכום קניות, {label}*\nלא נקלטו קבלות בחודש הזה."
        lines = [f"*סיכום קניות, {label}*"]
        lines.append(f'סה"כ {money(s["total"])} ב-{s["receipts"]} קניות, ממוצע {money(s["average_basket"])} לקנייה.')
        if s["change_pct"] is not None:
            direction = "עלייה" if s["change_pct"] >= 0 else "ירידה"
            diff = s["total"] - s["previous_total"]
            lines.append(
                f"לעומת {month_label(s['previous_month'])}: {direction} של {abs(s['change_pct']) * 100:.0f}% ({money(diff)})."
            )
        lines.append("")
        lines.append("*לפי חנות*")
        lines += [f"• {k}: {money(v)}" for k, v in list(s["by_store"].items())[:6]]
        lines.append("")
        lines.append("*לפי קטגוריה*")
        lines += [f"• {k}: {money(v)}" for k, v in list(s["by_category"].items())[:6]]
        if s["top_items"]:
            lines.append("")
            lines.append("*המוצרים שעלו הכי הרבה*")
            lines += [
                f"• {it['description']}: {money(it['spend'])} ({'פעם אחת' if it['count'] == 1 else str(it['count']) + ' פעמים'})"
                for it in s["top_items"][:5]
            ]
        if s["price_changes"]:
            lines.append("")
            lines.append("*שינויי מחיר*")
            for c in s["price_changes"][:5]:
                sign = "+" if c["pct"] > 0 else ""
                lines.append(
                    f"• {c['description']} ב{c['store']}: {money(c['old'])} ← {money(c['new'])} ({sign}{c['pct'] * 100:.0f}%)"
                )
        balances = {k: v for k, v in s["tab_balances"].items() if v is not None}
        if balances:
            lines.append("")
            lines.append("*יתרות בחשבונות*")
            lines += [f"• {k}: {money(v)}" for k, v in balances.items()]
        alerts = [f for f in s["findings"] if f["severity"] in ("high", "medium")]
        if alerts:
            lines.append("")
            lines.append(f"החודש היו {len(alerts)} התראות על אי התאמה בחשבון.")
        if s["uncertain_receipts"]:
            lines.append(f"{s['uncertain_receipts']} קבלות סומנו כלא ודאיות, כדאי לבדוק אותן.")
        return "\n".join(lines)


@register
class Notify(Block):
    """Input: ``message`` {text} and ``image`` {path, caption}. Sends each to
    the run's recipient (the person who sent the document, or the owners for
    scheduled runs). Output: ``sent`` records. Params: ``to`` overrides the recipient."""

    name = "notify"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        recipients = self.params.get("to") or ([ctx.recipient] if ctx.recipient else ctx.config.owners)
        out = []
        for rec in inputs:
            for to in recipients:
                try:
                    if rec.kind == "message":
                        ctx.sender.send_text(to, rec.data["text"])
                    elif rec.kind == "image":
                        ctx.sender.send_image(to, rec.data["path"], rec.data.get("caption"))
                    else:
                        continue
                    out.append(rec.derive("sent", {"to": to, "kind": rec.kind}))
                except Exception as exc:  # a failed send must not lose the other messages
                    log.warning("send to %s failed: %s", to, exc)
                    out.append(rec.derive("sent", {"to": to, "kind": rec.kind, "error": str(exc)}))
        return out
