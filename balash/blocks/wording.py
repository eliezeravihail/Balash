"""All user-facing Hebrew wording in one place. Pure functions, no I/O."""

from __future__ import annotations

from typing import Any

from ..core.text import fmt_date, money

FIELD_LABELS = {
    "total": 'סה"כ',
    "date": "תאריך",
    "time": "שעה",
    "store": "שם החנות",
    "store.name": "שם החנות",
    "receipt_number": "מספר קבלה",
    "discount_total": "הנחות",
    "tab": "פרטי החשבון",
    "tab.previous_balance": "יתרה קודמת",
    "tab.charged": "סכום החיוב",
    "tab.paid": "תשלום",
    "tab.new_balance": "יתרה חדשה",
    "lines": "שורות פריטים",
    "items": "סיווג פריטים",
}

DOC_LABELS = {
    "purchase": "נקלטה קבלה",
    "payment": "נקלטה קבלה על תשלום",
    "account_statement": "נקלט פירוט חשבון",
    "other": "נקלט מסמך",
    "unreadable": "נקלט מסמך",
}


def field_label(path: str) -> str:
    if path in FIELD_LABELS:
        return FIELD_LABELS[path]
    if path.startswith("lines"):
        return "שורת פריט"
    if path.startswith("statement_lines"):
        return "שורה בפירוט"
    head = path.split(".")[0].split("[")[0]
    return FIELD_LABELS.get(head, path)


def receipt_ack(d: dict[str, Any]) -> str:
    status = d.get("status")
    if status == "failed":
        return "לא הצלחתי לקרוא את המסמך. אפשר לשלוח צילום חד יותר, ישר ומואר, שבו כל הקבלה בתמונה?"
    if status == "error":
        return "המסמך נשמר, אבל לא הצלחתי לעבד אותו כרגע בגלל תקלה טכנית. אפשר לשלוח אותו שוב בעוד כמה דקות."
    if status == "refused":
        return "לא הצלחתי לעבד את המסמך הזה. אם זו קבלה, אפשר לנסות לשלוח אותה שוב."
    doc = d.get("doc_type")
    if doc == "other":
        return "המסמך נשמר, אבל הוא לא נראה כמו קבלה, קבלה על תשלום או פירוט חשבון."
    store = d.get("store_name") or "חנות לא מזוהה"
    parts = [f"{DOC_LABELS.get(doc, 'נקלט מסמך')}: {store}, {fmt_date(d.get('date'))}"]
    if doc == "purchase":
        total = d.get("total")
        if total is None and d.get("tab"):
            total = d["tab"].get("charged")
        parts[0] += f", {money(total)}, {d.get('n_lines', 0)} פריטים."
    elif doc == "payment":
        tab = d.get("tab") or {}
        paid = tab.get("paid") if tab.get("paid") is not None else d.get("total")
        parts[0] += f", תשלום של {money(paid)}."
    else:
        parts[0] += "."
    tab = d.get("tab") or {}
    if tab.get("new_balance") is not None:
        parts.append(f"יתרה בחשבון אחרי המסמך: {money(tab['new_balance'])}.")
    if d.get("duplicate_of"):
        parts = [f"הקבלה הזו כבר נקלטה קודם ({store}, {fmt_date(d.get('date'))}). לא נספרה שוב."]
    elif d.get("uncertain"):
        labels = sorted({field_label(p) for p in d["uncertain"]})
        parts.append("שים לב, לא קראתי בוודאות: " + ", ".join(labels) + ". הרשומה סומנה לבדיקה.")
    if not d.get("account_key") and doc in ("purchase", "payment") and not d.get("duplicate_of"):
        parts.append("לא זיהיתי את שם החנות. אפשר לשלוח שוב עם כיתוב של שם החנות.")
    return "\n".join(parts)


def duplicate_item(received_at: str) -> str:
    return "את הקובץ הזה כבר קיבלתי קודם, הוא לא נספר שוב."


def unsupported_item(media_type: str) -> str:
    return "אני מקבל רק תמונות או קבצי PDF של קבלות."


def finding_message(kind: str, d: dict[str, Any]) -> str:
    store = d.get("store") or "החנות"
    if kind == "unexplained_increase":
        return (
            f"⚠️ אי התאמה בחשבון ב{store}.\n"
            f"בקבלה מ-{fmt_date(d['date'])} היתרה הקודמת היא {money(d['printed_previous'])}, "
            f"אבל לפי המסמכים ששלחת היתרה הייתה {money(d['expected_previous'])} "
            f"(אחרי {d['last_label']} מ-{fmt_date(d['last_date'])}).\n"
            f"נוספו {money(d['delta'])} שלא מופיעים באף קבלה שלך. ייתכן שמישהו נרשם על החשבון שלך בטעות, "
            f"או שקבלה לא נשלחה אליי."
        )
    if kind == "unexplained_decrease":
        return (
            f"אי התאמה בחשבון ב{store}: בקבלה מ-{fmt_date(d['date'])} היתרה הקודמת היא {money(d['printed_previous'])}, "
            f"ולפי המסמכים ששלחת היא הייתה {money(d['expected_previous'])}. "
            f"היתרה ירדה ב-{money(d['delta'])} בלי תשלום רשום. אם שילמת, אפשר לשלוח: שילמתי {abs(d['delta']):g}"
        )
    if kind == "internal_mismatch":
        return (
            f"⚠️ החישוב בקבלה מ-{fmt_date(d['date'])} ב{store} לא מסתדר: "
            f"{money(d['previous'])} + {money(d['charged'])} - {money(d['paid'])} = {money(d['expected'])}, "
            f"אבל היתרה החדשה המודפסת היא {money(d['printed_new'])}."
        )
    if kind == "charge_without_receipt":
        return (
            f"⚠️ בפירוט החשבון של {store} יש חיוב של {money(d['amount'])} מ-{fmt_date(d['date'])}"
            f"{' (' + d['description'] + ')' if d.get('description') else ''} שאין לו קבלה ששלחת."
        )
    if kind == "receipt_missing_from_statement":
        return (
            f"קבלה מ-{fmt_date(d['date'])} על {money(d['amount'])} ב{store} לא מופיעה בפירוט החשבון ששלחת."
        )
    return f"ממצא: {kind}"


def payment_ack(d: dict[str, Any]) -> str:
    if d.get("error") == "no_amount":
        return 'לא הבנתי את הסכום. לדוגמה: "שילמתי 250 מכולת יוסי".'
    if d.get("error") == "no_account":
        known = d.get("known") or []
        hint = f" החשבונות שאני מכיר: {', '.join(known)}." if known else ""
        return f'לאיזה חשבון התשלום? לדוגמה: "שילמתי {d.get("amount", 0):g} מכולת יוסי".{hint}'
    return f"נרשם תשלום של {money(d['amount'])} לחשבון ב{d['account_key']}, {fmt_date(d['date'])}."


HELP = (
    "*בלש, מעקב קניות*\n"
    "• שלח צילום או PDF של קבלה מהסופר או מהמכולת, קבלה על תשלום, או פירוט חשבון.\n"
    "• *דוח*: סיכום החודש הנוכחי. *דוח 9* או *דוח 2026-09*: חודש מסוים.\n"
    "• *יתרה*: היתרה בחשבונות המכולת.\n"
    "• *שילמתי 250 מכולת יוסי*: רישום תשלום על החשבון.\n"
    "בסוף כל חודש יישלח אליך סיכום עם גרפים."
)
