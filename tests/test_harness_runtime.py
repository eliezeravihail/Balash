from balash.core.record import Record
from balash.harness.llm import LLMResponse

from conftest import image_bytes, line, receipt


def _item(h, seed=1, caption="c1"):
    rec = Record("incoming", {"bytes": image_bytes(seed), "media_type": "image/jpeg", "source": "t", "caption": caption})
    from balash.blocks.intake import RawStore

    return RawStore().run([rec], h.service.context(h.out, "x"))[0]


def _block():
    from balash.blocks.receipts import ReceiptToRecords

    return ReceiptToRecords()


def test_valid_output_is_cached(h):
    item = _item(h)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    ctx = h.service.context(h.out, "x")
    first = _block().run([item], ctx)[0]
    second = _block().run([item], ctx)[0]
    assert first.data["status"] == "ok"
    assert second.data["cached"] is True
    assert h.calls("receipt_to_records") == 1


def test_schema_violation_is_retried_once(h):
    item = _item(h)
    good = receipt(lines=[line("חלב", 6.9)])
    answers = [{"doc_type": "purchase"}, good]
    h.llm.responses["receipt_to_records"] = lambda req: answers.pop(0)
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "ok"
    retry = h.llm.calls[-1]
    assert "did not match the required output schema" in retry.content[-1]["text"]


def test_schema_violation_twice_fails(h):
    item = _item(h)
    h.llm.responses["receipt_to_records"] = lambda req: {"doc_type": "purchase"}
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "failed"
    assert h.calls("receipt_to_records") == 2


def test_refusal_is_reported_not_retried(h):
    item = _item(h)
    h.llm.responses["receipt_to_records"] = lambda req: LLMResponse(
        text="", stop_reason="refusal", model=req.model, refusal_category=None
    )
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "refused"
    assert h.calls("receipt_to_records") == 1


def test_consistency_check_marks_uncertain(h):
    item = _item(h)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9), line("לחם", 7.5)], total=30.0)
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "uncertain"
    assert any(i.startswith("total:") for i in result.data["issues"])


def test_tab_arithmetic_check(h):
    item = _item(h)
    from conftest import tab

    h.outputs["c1"] = receipt(store="מכולת יוסי", kind="grocery", lines=[line("חלב", 20)], tab=tab(100, 20, 0, 150))
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "uncertain"
    assert any(i.startswith("tab.new_balance") for i in result.data["issues"])


def test_no_model_client_fails_cleanly(h):
    item = _item(h)
    h.service.llm = None
    result = _block().run([item], h.service.context(h.out, "x"))[0]
    assert result.data["status"] == "error"
