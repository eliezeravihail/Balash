"""receipt_inbox: one block from a WhatsApp message to receipt records.

In one pipeline line it does four things, each of them a block of its own that
can be tested and replaced separately:

1. **Sender allowlist.** Only numbers on the list are handled. Anything else
   is dropped before downloading, so a stranger costs nothing.
2. **Media download** of the photo or PDF through the channel.
3. **raw_store**: the file is kept once, forever; a repeat is recognised.
4. **receipt_to_records**: the model reads the document into records.

It does nothing else. It does not save purchases, reply, check balances or
send alerts; those are other blocks further down the pipeline.
"""

from __future__ import annotations

import re
from typing import Any

from ..core.block import Block, Context, log, register
from ..core.record import Record
from .intake import RawStore
from .receipts import ReceiptToRecords

MEDIA_TYPES = ("image", "document")


def _digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))


@register
class ReceiptInbox(Block):
    """Input: ``whatsapp_message`` {message_id, sender, type, media_id, mime_type, caption, filename}
    as the webhook received it, or ``incoming`` {bytes, ...} for local files.
    Output: ``receipt`` {sender, item_id, status, issues, output} per document, and
    ``duplicate_item`` / ``unsupported_item`` for files that were not read.
    Params: ``allowed_senders`` (default: the instance owners), ``model`` (overrides
    the reading model). Local ``incoming`` files are trusted and skip the allowlist."""

    name = "receipt_inbox"

    def allowed(self, ctx: Context) -> set[str]:
        configured = self.params.get("allowed_senders")
        numbers = configured if configured is not None else ctx.config.owners
        return {_digits(n) for n in numbers if _digits(n)}

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        allowed = self.allowed(ctx)
        incoming: list[Record] = []
        for rec in inputs:
            if rec.kind == "incoming":
                incoming.append(rec)
                continue
            if rec.kind != "whatsapp_message":
                continue
            m = rec.data
            sender = _digits(m.get("sender"))
            if sender not in allowed:
                log.warning("receipt_inbox: dropped message from %s, not an allowed sender", sender or "unknown")
                continue
            if m.get("type") not in MEDIA_TYPES:
                continue
            if ctx.media is None:
                raise RuntimeError("receipt_inbox needs a media source to download WhatsApp attachments")
            data, mime = ctx.media.download_media(m["media_id"])
            incoming.append(
                rec.derive(
                    "incoming",
                    {
                        "bytes": data,
                        "media_type": m.get("mime_type") or mime,
                        "source": "whatsapp",
                        "sender": sender,
                        "caption": m.get("caption") or "",
                        "filename": m.get("filename") or "",
                    },
                )
            )

        stored = RawStore().run(incoming, ctx)
        reader = ReceiptToRecords({"model": self.params["model"]} if self.params.get("model") else {})
        receipts = reader.run(stored, ctx)

        sender_of = {r.data["id"]: r.data.get("sender") for r in stored if r.kind == "item"}
        for r in receipts:
            r.data["sender"] = sender_of.get(r.data["item_id"])
        not_read = [r for r in stored if r.kind in ("duplicate_item", "unsupported_item")]
        return receipts + not_read
