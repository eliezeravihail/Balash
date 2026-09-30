import hashlib
import hmac
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from balash.app import create_app, run_scheduled_report
from balash.channels.whatsapp import WhatsAppError, WhatsAppSender, parse_webhook, verify_signature
from balash.config import WhatsAppConfig
from balash.service import parse_report_request

from conftest import image_bytes, line, receipt

OWNER = "972500000001"


class FakeWhatsApp:
    def __init__(self):
        self.media = {}
        self.sent = []
        self.fail_with = None

    def download_media(self, media_id):
        return self.media[media_id], "image/jpeg"

    def send_text(self, to, body):
        if self.fail_with:
            raise WhatsAppError(self.fail_with, "window closed")
        self.sent.append((to, "text", body))

    def send_image(self, to, path, caption=None):
        if self.fail_with:
            raise WhatsAppError(self.fail_with, "window closed")
        self.sent.append((to, "image", path))


def payload(msg: dict) -> dict:
    return {"object": "whatsapp_business_account",
            "entry": [{"changes": [{"value": {"messaging_product": "whatsapp", "messages": [msg]}}]}]}


def image_msg(mid, media_id, sender=OWNER, caption=""):
    return {"from": sender, "id": mid, "timestamp": "1", "type": "image",
            "image": {"id": media_id, "mime_type": "image/jpeg", "caption": caption}}


def text_msg(mid, body, sender=OWNER):
    return {"from": sender, "id": mid, "timestamp": "1", "type": "text", "text": {"body": body}}


def sign(secret, body):
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_signature_and_parsing():
    body = b'{"a":1}'
    assert verify_signature("s", body, sign("s", body))
    assert not verify_signature("s", body, sign("other", body))
    assert not verify_signature("s", body, None)
    msgs = parse_webhook(payload(image_msg("m1", "med1", caption="מכולת")))
    assert msgs[0].type == "image" and msgs[0].media_id == "med1" and msgs[0].caption == "מכולת"
    assert parse_webhook({"entry": [{"changes": [{"value": {"statuses": [{}]}}]}]}) == []


def _app(h, fake, secret="topsecret"):
    h.config.whatsapp = WhatsAppConfig(phone_number_id="1", access_token="t", app_secret=secret, verify_token="vt")
    return TestClient(create_app(h.service, client=fake, scheduler=False))


def test_webhook_verification(h):
    client = _app(h, FakeWhatsApp())
    ok = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "vt", "hub.challenge": "42"})
    assert ok.status_code == 200 and ok.text == "42"
    bad = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "no", "hub.challenge": "42"})
    assert bad.status_code == 403


def test_image_message_runs_the_pipeline_and_replies(h):
    fake = FakeWhatsApp()
    fake.media["med1"] = image_bytes(5)
    h.outputs["r1"] = receipt(lines=[line("חלב", 6.9)])
    client = _app(h, fake)
    body = json.dumps(payload(image_msg("m1", "med1", caption="r1"))).encode()
    res = client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert res.status_code == 200
    assert fake.sent and fake.sent[0][0] == OWNER and "שופרסל" in fake.sent[0][2]
    # the same webhook delivered twice is processed once
    client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert len(fake.sent) == 1


def test_bad_signature_and_unknown_sender_are_rejected(h):
    fake = FakeWhatsApp()
    client = _app(h, fake)
    body = json.dumps(payload(text_msg("m2", "יתרה"))).encode()
    assert client.post("/webhook", content=body, headers={"x-hub-signature-256": "sha256=00"}).status_code == 403
    body = json.dumps(payload(text_msg("m3", "יתרה", sender="972599999999"))).encode()
    client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert fake.sent == []


def test_text_commands_over_webhook(h):
    fake = FakeWhatsApp()
    client = _app(h, fake)
    body = json.dumps(payload(text_msg("m4", "שלום"))).encode()
    client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert "בלש" in fake.sent[0][2]


def test_message_outside_the_window_waits_and_is_flushed(h):
    fake = FakeWhatsApp()
    sender = WhatsAppSender(fake, h.service.store)
    fake.fail_with = 131047
    sender.send_text(OWNER, "דוח")
    assert fake.sent == [] and len(h.service.store.pending_messages(OWNER)) == 1
    fake.fail_with = None
    assert sender.flush(OWNER) == 1
    assert fake.sent == [(OWNER, "text", "דוח")]
    assert h.service.store.pending_messages(OWNER) == []


def test_report_request_parsing():
    now = datetime(2026, 9, 29, tzinfo=ZoneInfo("Asia/Jerusalem"))
    assert parse_report_request("דוח", now) == "2026-09"
    assert parse_report_request("דוח 8", now) == "2026-08"
    assert parse_report_request("דוח 11", now) == "2025-11"
    assert parse_report_request('דו"ח 2026-3', now) == "2026-03"
    assert parse_report_request("דוח 13", now) is None
    assert parse_report_request("מה נשמע", now) is None


def test_scheduled_report_runs_once_per_month(h):
    fake = FakeWhatsApp()
    sender = WhatsAppSender(fake, h.service.store)
    h.send(receipt(date="2026-09-03", lines=[line("חלב", 6.9)]))
    tz = ZoneInfo("Asia/Jerusalem")
    assert run_scheduled_report(h.service, sender, datetime(2026, 9, 30, 20, tzinfo=tz)) is None
    assert run_scheduled_report(h.service, sender, datetime(2026, 10, 1, 8, tzinfo=tz)) is None  # before 9:00
    assert run_scheduled_report(h.service, sender, datetime(2026, 10, 1, 9, 5, tzinfo=tz)) == "2026-09"
    assert any("ספטמבר 2026" in b for _, k, b in fake.sent if k == "text")
    assert run_scheduled_report(h.service, sender, datetime(2026, 10, 2, 9, tzinfo=tz)) is None


def test_no_owners_means_nobody(h):
    fake = FakeWhatsApp()
    client = _app(h, fake)
    h.config.owners = []
    body = json.dumps(payload(text_msg("m9", "יתרה"))).encode()
    client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert fake.sent == []


def test_image_from_unknown_number_is_not_downloaded_or_answered(h):
    fake = FakeWhatsApp()
    client = _app(h, fake)
    body = json.dumps(payload(image_msg("m10", "med9", sender="972599999999"))).encode()
    res = client.post("/webhook", content=body, headers={"x-hub-signature-256": sign("topsecret", body)})
    assert res.status_code == 200
    assert fake.sent == []
    assert h.llm.calls == []
