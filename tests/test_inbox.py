"""receipt_inbox: allowed senders, download, store once, read. Nothing else."""

from balash.blocks.inbox import ReceiptInbox
from balash.core.record import Record

from conftest import image_bytes, line, receipt

ALLOWED = "972500000001"


class FakeMedia:
    def __init__(self):
        self.files = {}
        self.downloads = []

    def download_media(self, media_id):
        self.downloads.append(media_id)
        return self.files[media_id], "image/jpeg"


def msg(sender=ALLOWED, kind="image", media_id="m1", caption="c1", mid="w1"):
    return Record("whatsapp_message", {"message_id": mid, "sender": sender, "type": kind, "text": "",
                                       "media_id": media_id, "mime_type": "image/jpeg", "caption": caption,
                                       "filename": "", "timestamp": "1"})


def _ctx(h, media):
    ctx = h.service.context(h.out, ALLOWED)
    ctx.media = media
    return ctx


def test_allowed_sender_becomes_receipt_record_with_sender(h):
    media = FakeMedia()
    media.files["m1"] = image_bytes(1)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    out = ReceiptInbox().run([msg()], _ctx(h, media))
    assert [r.kind for r in out] == ["receipt"]
    assert out[0].data["sender"] == ALLOWED
    assert out[0].data["status"] == "ok"
    assert out[0].data["output"]["total"] == 6.9


def test_unknown_sender_is_dropped_before_download_and_model(h):
    media = FakeMedia()
    out = ReceiptInbox().run([msg(sender="972599999999")], _ctx(h, media))
    assert out == []
    assert media.downloads == []
    assert h.llm.calls == []


def test_allowed_senders_param_overrides_instance_owners(h):
    media = FakeMedia()
    media.files["m1"] = image_bytes(2)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    block = ReceiptInbox({"allowed_senders": ["+972-59-9999999"]})
    assert block.run([msg()], _ctx(h, media)) == []
    out = block.run([msg(sender="972599999999")], _ctx(h, media))
    assert out[0].data["sender"] == "972599999999"


def test_text_messages_are_ignored(h):
    media = FakeMedia()
    assert ReceiptInbox().run([msg(kind="text")], _ctx(h, media)) == []
    assert media.downloads == []


def test_same_file_twice_is_read_once(h):
    media = FakeMedia()
    media.files["m1"] = image_bytes(3)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    ReceiptInbox().run([msg()], _ctx(h, media))
    out = ReceiptInbox().run([msg(mid="w2")], _ctx(h, media))
    assert [r.kind for r in out] == ["duplicate_item"]
    assert h.calls("receipt_to_records") == 1


def test_model_param_reaches_the_model_call(h):
    media = FakeMedia()
    media.files["m1"] = image_bytes(4)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    ReceiptInbox({"model": "claude-sonnet-5-5"}).run([msg()], _ctx(h, media))
    assert h.llm.calls[-1].model == "claude-sonnet-5-5"


def test_block_does_not_store_purchases_or_reply(h):
    media = FakeMedia()
    media.files["m1"] = image_bytes(5)
    h.outputs["c1"] = receipt(lines=[line("חלב", 6.9)])
    ReceiptInbox().run([msg()], _ctx(h, media))
    assert h.service.store.one("SELECT COUNT(*) n FROM receipts")["n"] == 0
    assert h.out.sent == []
