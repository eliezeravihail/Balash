"""WhatsApp Business Cloud API: webhook parsing, signature check, media and sending.

Only this module knows Meta's formats. It turns webhook payloads into
``InboundMessage`` objects and exposes send_text / send_image.
"""

from __future__ import annotations

import hashlib
import hmac
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from ..config import WhatsAppConfig
from ..core.block import log
from ..core.store import Store

GRAPH = "https://graph.facebook.com"
# Sent outside the 24-hour customer service window: the message must wait
# until the person writes again (or be sent as an approved template).
OUTSIDE_WINDOW_CODES = {131047, 131026}


@dataclass
class InboundMessage:
    message_id: str
    sender: str
    type: str  # text | image | document | other
    text: str = ""
    media_id: str = ""
    mime_type: str = ""
    caption: str = ""
    filename: str = ""
    timestamp: str = ""


class WhatsAppError(RuntimeError):
    def __init__(self, code: int | None, message: str):
        super().__init__(f"WhatsApp error {code}: {message}")
        self.code = code


def verify_signature(app_secret: str, body: bytes, header: str | None) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.split("=", 1)[1])


def parse_webhook(payload: dict[str, Any]) -> list[InboundMessage]:
    out: list[InboundMessage] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for m in value.get("messages", []) or []:
                kind = m.get("type", "")
                msg = InboundMessage(
                    message_id=m.get("id", ""), sender=m.get("from", ""), type=kind, timestamp=m.get("timestamp", "")
                )
                if kind == "text":
                    msg.text = (m.get("text") or {}).get("body", "")
                elif kind in ("image", "document"):
                    media = m.get(kind) or {}
                    msg.media_id = media.get("id", "")
                    msg.mime_type = media.get("mime_type", "")
                    msg.caption = media.get("caption", "") or ""
                    msg.filename = media.get("filename", "") or ""
                else:
                    msg.type = "other"
                out.append(msg)
    return out


class WhatsAppClient:
    def __init__(self, config: WhatsAppConfig, http: httpx.Client | None = None):
        self.config = config
        self.http = http or httpx.Client(timeout=30)

    @property
    def _base(self) -> str:
        return f"{GRAPH}/{self.config.graph_version}"

    @property
    def _auth(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.access_token}"}

    def _check(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            try:
                err = response.json().get("error", {})
            except ValueError:
                err = {}
            raise WhatsAppError(err.get("code"), err.get("message") or response.text[:300])
        return response.json() if response.content else {}

    def download_media(self, media_id: str) -> tuple[bytes, str]:
        meta = self._check(self.http.get(f"{self._base}/{media_id}", headers=self._auth))
        response = self.http.get(meta["url"], headers=self._auth)
        if response.status_code >= 400:
            raise WhatsAppError(response.status_code, "media download failed")
        return response.content, meta.get("mime_type", "")

    def send_text(self, to: str, body: str) -> None:
        self._check(
            self.http.post(
                f"{self._base}/{self.config.phone_number_id}/messages",
                headers=self._auth,
                json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body[:4096]}},
            )
        )

    def send_image(self, to: str, path: str, caption: str | None = None) -> None:
        p = Path(path)
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        uploaded = self._check(
            self.http.post(
                f"{self._base}/{self.config.phone_number_id}/media",
                headers=self._auth,
                data={"messaging_product": "whatsapp", "type": mime},
                files={"file": (p.name, p.read_bytes(), mime)},
            )
        )
        image: dict[str, Any] = {"id": uploaded["id"]}
        if caption:
            image["caption"] = caption
        self._check(
            self.http.post(
                f"{self._base}/{self.config.phone_number_id}/messages",
                headers=self._auth,
                json={"messaging_product": "whatsapp", "to": to, "type": "image", "image": image},
            )
        )


class WhatsAppSender:
    """MessageSender over WhatsApp with an outbox. Every message is written to
    the outbox first; a message that cannot be delivered because the 24-hour
    window is closed stays pending and is sent when the person writes again."""

    def __init__(self, client: WhatsAppClient, store: Store):
        self.client = client
        self.store = store

    def send_text(self, to: str, body: str) -> None:
        self._deliver(self.store.queue_message(to, "text", body), to, "text", body, None)

    def send_image(self, to: str, path: str, caption: str | None = None) -> None:
        self._deliver(self.store.queue_message(to, "image", caption, path), to, "image", caption, path)

    def flush(self, to: str) -> int:
        sent = 0
        for row in self.store.pending_messages(to):
            if self._deliver(row["id"], to, row["kind"], row["body"], row["media_path"]):
                sent += 1
        return sent

    def _deliver(self, msg_id: int, to: str, kind: str, body: str | None, media: str | None) -> bool:
        try:
            if kind == "text":
                self.client.send_text(to, body or "")
            else:
                self.client.send_image(to, media or "", body)
        except WhatsAppError as exc:
            self.store.mark_sent(msg_id, error=str(exc))
            if exc.code in OUTSIDE_WINDOW_CODES:
                log.info("message %s to %s waits for the next inbound message", msg_id, to)
                return False
            raise
        self.store.mark_sent(msg_id)
        return True


class ConsoleSender:
    """MessageSender for the command line and tests: prints and remembers."""

    def __init__(self, echo: bool = True):
        self.echo = echo
        self.sent: list[tuple[str, str, str]] = []

    def send_text(self, to: str, body: str) -> None:
        self.sent.append((to, "text", body))
        if self.echo:
            print(f"\n{body}\n")

    def send_image(self, to: str, path: str, caption: str | None = None) -> None:
        self.sent.append((to, "image", path))
        if self.echo:
            print(f"[{caption or 'תמונה'}] {path}")
