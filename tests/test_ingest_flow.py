from datetime import datetime
from zoneinfo import ZoneInfo

from conftest import image_bytes, line, receipt, tab

TZ = ZoneInfo("Asia/Jerusalem")


def test_supermarket_receipt_is_read_stored_and_categorized(h):
    replies = h.send(receipt(lines=[line("חלב תנובה 3%", 6.9), line("לחם אחיד", 7.5), line("במבה 80ג", 5.0)]))
    assert len(replies) == 1
    assert "שופרסל" in replies[0] and "19.40 ₪" in replies[0] and "3 פריטים" in replies[0]
    rows = h.service.store.query("SELECT account_key, total FROM receipts")
    assert [(r["account_key"], r["total"]) for r in rows] == [("שופרסל", 19.4)]
    cats = {r["norm_desc"]: r["category"] for r in h.service.store.query("SELECT * FROM categories")}
    assert cats["חלב תנובה 3%"] == "חלב וביצים"
    assert cats["במבה 80ג"] == "ממתקים וחטיפים"


def test_known_products_are_not_sent_to_the_model_again(h):
    h.send(receipt(lines=[line("חלב", 6.9)]))
    h.send(receipt(lines=[line("חלב", 6.9)], date="2026-09-05"))
    assert h.calls("categorize_items") == 1


def test_same_file_twice_is_not_counted(h):
    data = image_bytes(99)
    h.send(receipt(lines=[line("חלב", 6.9)]), caption="a", data=data)
    replies = h.send(receipt(lines=[line("חלב", 6.9)]), caption="a", data=data)
    assert "כבר קיבלתי" in replies[0]
    assert h.calls("receipt_to_records") == 1
    assert h.service.store.one("SELECT COUNT(*) n FROM receipts")["n"] == 1


def test_same_receipt_photographed_twice_is_not_counted(h):
    r = receipt(lines=[line("חלב", 6.9)], number="1234")
    h.send(r)
    replies = h.send(r)
    assert "כבר נקלטה" in replies[0]
    assert h.service.store.one("SELECT COUNT(*) n FROM receipts")["n"] == 1


def _slip(prev, charged, new, date, paid=None, store="מכולת יוסי"):
    return receipt(store=store, kind="grocery", date=date, lines=[line("חלב", charged)], tab=tab(prev, charged, paid, new),
                   payment="tab")


def test_consecutive_tab_slips_that_agree_raise_nothing(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    replies = h.send(_slip(150, 30, 180, "2026-09-04"))
    assert len(replies) == 1
    assert "180.00 ₪" in replies[0]
    assert h.service.store.one("SELECT COUNT(*) n FROM findings")["n"] == 0


def test_unexplained_increase_between_slips_alerts(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    h.send(_slip(150, 30, 180, "2026-09-04"))
    replies = h.send(_slip(230, 20, 250, "2026-09-08"))
    assert len(replies) == 2
    alert = replies[1]
    assert "אי התאמה" in alert and "50.00 ₪" in alert and "180.00 ₪" in alert
    f = h.service.store.one("SELECT * FROM findings")
    assert f["kind"] == "unexplained_increase" and f["severity"] == "high"


def test_alert_is_not_repeated(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    h.send(_slip(230, 20, 250, "2026-09-08"))
    replies = h.send(_slip(250, 10, 260, "2026-09-10"))
    assert len(replies) == 1  # only the acknowledgement, the old finding is not sent again


def test_reported_payment_explains_the_drop(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    replies = h.text("שילמתי 100 מכולת יוסי", now=datetime(2026, 9, 2, 12, 0, tzinfo=TZ))
    assert "100.00 ₪" in replies[0]
    replies = h.send(_slip(50, 20, 70, "2026-09-05"))
    assert len(replies) == 1
    assert h.service.store.one("SELECT COUNT(*) n FROM findings")["n"] == 0


def test_unreported_payment_is_flagged_softly(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    replies = h.send(_slip(50, 20, 70, "2026-09-05"))
    assert "שילמתי 100" in replies[1]
    f = h.service.store.one("SELECT * FROM findings")
    assert f["kind"] == "unexplained_decrease" and f["severity"] == "medium"


def test_slip_whose_own_math_is_wrong_alerts(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    replies = h.send(receipt(store="מכולת יוסי", kind="grocery", date="2026-09-03", lines=[line("לחם", 20)],
                             tab=tab(150, 20, None, 190), payment="tab"))
    kinds = [r["kind"] for r in h.service.store.query("SELECT kind FROM findings")]
    assert kinds == ["internal_mismatch"]
    assert any("לא מסתדר" in r for r in replies)


def test_handwritten_slip_without_store_goes_to_the_single_tab_account(h):
    h.send(receipt(store=None, kind="grocery", lines=[line("חלב", 20)], tab=tab(10, 20, None, 30), payment="tab"))
    row = h.service.store.one("SELECT account_key FROM receipts")
    assert row["account_key"] == "מכולת יוסי"


def test_store_alias_is_resolved(h):
    h.send(_slip(100, 50, 150, "2026-09-01", store="מינימרקט יוסי בע\"מ"))
    assert h.service.store.one("SELECT account_key FROM receipts")["account_key"] == "מכולת יוסי"


def test_statement_charge_without_a_slip_alerts(h):
    h.send(_slip(100, 50, 150, "2026-09-01"))
    h.send(_slip(150, 30, 180, "2026-09-04"))
    statement = receipt(
        store="מכולת יוסי", kind="grocery", doc_type="account_statement", lines=[], total=None, payment="other",
        statement=[
            {"date": "2026-09-01", "description": "קנייה", "amount": 50, "reference": None, "source_text": ""},
            {"date": "2026-09-04", "description": "קנייה", "amount": 30, "reference": None, "source_text": ""},
            {"date": "2026-09-06", "description": "קנייה", "amount": 45, "reference": None, "source_text": ""},
        ],
    )
    replies = h.send(statement)
    assert any("45.00 ₪" in r and "אין לו קבלה" in r for r in replies)
    kinds = [r["kind"] for r in h.service.store.query("SELECT kind FROM findings")]
    assert kinds == ["charge_without_receipt"]


def test_uncertain_fields_are_reported(h):
    replies = h.send(receipt(lines=[line("חלב", 6.9)], uncertain=["date", "lines[0].line_total"]))
    assert "לא קראתי בוודאות" in replies[0] and "תאריך" in replies[0]


def test_unreadable_document_asks_for_a_better_photo(h):
    r = receipt(lines=[], doc_type="unreadable", store=None, kind="unknown", payment="unknown")
    replies = h.send(r)
    assert "צילום חד יותר" in replies[0]
    assert h.service.store.one("SELECT COUNT(*) n FROM receipts")["n"] == 0


def test_run_log_records_every_step(h):
    h.send(receipt(lines=[line("חלב", 6.9)]))
    import json

    run = h.service.store.one("SELECT * FROM runs WHERE pipeline = 'groceries_ingest' ORDER BY started_at DESC")
    steps = [s["step"] for s in json.loads(run["log"])]
    assert steps == ["inbox", "ledger", "categories", "tab", "statement", "ack", "alerts", "send"]
    assert run["status"] == "ok"


def test_technical_error_can_be_retried_by_sending_again(h):
    data = image_bytes(77)
    llm = h.service.llm
    h.service.llm = None  # model unreachable
    replies = h.send(receipt(lines=[line("חלב", 6.9)]), caption="retry", data=data)
    assert "תקלה טכנית" in replies[0]
    h.service.llm = llm
    replies = h.send(receipt(lines=[line("חלב", 6.9)]), caption="retry", data=data)
    assert "נקלטה קבלה" in replies[0]
    assert h.service.store.one("SELECT COUNT(*) n FROM receipts")["n"] == 1


def test_same_slip_photographed_twice_without_number_is_not_counted(h):
    slip = receipt(store="מכולת יוסי", kind="grocery", date="2026-09-01", time="18:40", lines=[line("חלב", 50)],
                   tab=tab(100, 50, None, 150), payment="tab")
    h.send(slip)
    replies = h.send(slip)  # different photo, same slip
    assert "כבר נקלטה" in replies[0]
    assert h.service.store.one("SELECT COUNT(*) n FROM findings")["n"] == 0


def test_invalid_date_does_not_break_the_report(h):
    h.send(receipt(date="2026-09-3", lines=[line("חלב", 6.9)]))
    assert h.service.store.one("SELECT date FROM receipts")["date"] is None
    replies = h.text("דוח 9")
    assert "ספטמבר 2026" in replies[0]
