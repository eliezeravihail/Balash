from pathlib import Path

from balash.blocks.stats import compute, month_bounds, prev_month

from conftest import line, receipt, tab


def _fill(h):
    h.send(receipt(date="2026-08-20", lines=[line("חלב", 6.0), line("לחם", 7.0)]))  # August: 13
    h.send(receipt(date="2026-09-03", lines=[line("חלב", 6.9), line("לחם", 7.0), line("אקונומיקה", 12.0)]))
    h.send(receipt(date="2026-09-17", lines=[line("עגבניות", 9.5, qty=1.0), line("במבה", 5.0)]))
    h.send(receipt(store="מכולת יוסי", kind="grocery", date="2026-09-10", lines=[line("ביצים", 20.0)],
                   tab=tab(100, 20, None, 120), payment="tab"))


def test_month_helpers():
    assert prev_month("2026-01") == "2025-12"
    assert month_bounds("2026-02")[1].day == 28


def test_monthly_totals_categories_weeks_and_comparison(h):
    _fill(h)
    s = compute(h.service.store, "2026-09")
    assert s["receipts"] == 3
    assert s["total"] == 60.4
    assert s["by_store"] == {"שופרסל": 40.4, "מכולת יוסי": 20.0}
    assert s["by_category"]["חלב וביצים"] == 26.9
    assert s["by_category"]["ניקיון"] == 12.0
    assert sum(s["by_week"].values()) == 60.4
    assert s["previous_total"] == 13.0
    assert round(s["change_pct"], 2) == round((60.4 - 13) / 13, 2)
    assert s["tab_balances"] == {"מכולת יוסי": 120.0}


def test_price_change_same_product_same_store(h):
    _fill(h)
    s = compute(h.service.store, "2026-09")
    changes = {c["description"]: c for c in s["price_changes"]}
    assert "חלב" in changes
    assert changes["חלב"]["old"] == 6.0 and changes["חלב"]["new"] == 6.9
    assert "לחם" not in changes  # same price


def test_report_message_and_charts(h):
    _fill(h)
    before = len(h.out.sent)
    h.text("דוח 9")
    sent = h.out.sent[before:]
    texts = [b for _, k, b in sent if k == "text"]
    images = [b for _, k, b in sent if k == "image"]
    assert len(texts) == 1
    report = texts[0]
    assert "ספטמבר 2026" in report and "60.40 ₪" in report and "מכולת יוסי: 120.00 ₪" in report
    assert "שינויי מחיר" in report
    assert len(images) == 3
    for p in images:
        assert Path(p).exists() and Path(p).stat().st_size > 5000


def test_empty_month_report(h):
    before = len(h.out.sent)
    h.text("דוח 2026-03")
    texts = [b for _, k, b in h.out.sent[before:] if k == "text"]
    assert texts == ["*סיכום קניות, מרץ 2026*\nלא נקלטו קבלות בחודש הזה."]


def test_balances_command(h):
    _fill(h)
    replies = h.text("יתרה")
    assert "מכולת יוסי: 120.00 ₪" in replies[0]
