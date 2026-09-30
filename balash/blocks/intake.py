"""raw_store: the first block after any channel.

Channels (WhatsApp webhook, CLI, folder) turn whatever arrived into
``incoming`` records holding the bytes and metadata. This block saves the file
once, forever, under a content hash, and emits an ``item`` record. A file that
was already received becomes a ``duplicate_item`` record instead.
"""

from __future__ import annotations

import hashlib
import mimetypes

from ..core.block import Block, Context, register
from ..core.record import Record, new_id
from ..core.store import utcnow

ACCEPTED = {"image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"}


@register
class RawStore(Block):
    """Input: ``incoming`` {bytes, media_type, source, sender, caption, filename}.
    Output: ``item`` or ``duplicate_item`` or ``unsupported_item``.
    Guarantees: a file is stored at most once; stored files are never changed.
    A file whose earlier processing ended in a technical error is processed again."""

    name = "raw_store"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out: list[Record] = []
        media_dir = ctx.config.media_dir
        media_dir.mkdir(parents=True, exist_ok=True)
        for rec in inputs:
            if rec.kind != "incoming":
                continue
            data: bytes = rec.data["bytes"]
            media_type = (rec.data.get("media_type") or "").split(";")[0].strip().lower()
            if media_type not in ACCEPTED:
                out.append(rec.derive("unsupported_item", {"media_type": media_type}))
                continue
            sha = hashlib.sha256(data).hexdigest()
            existing = ctx.store.item_by_sha(sha)
            if existing is not None and existing["status"] == "error":
                # processing failed for a technical reason: sending it again retries
                item = dict(existing)
                out.append(Record("item", item, id=item["id"], cites=[rec.id]))
                continue
            if existing is not None:
                out.append(
                    rec.derive(
                        "duplicate_item",
                        {"item_id": existing["id"], "received_at": existing["received_at"]},
                    )
                )
                continue
            ext = mimetypes.guess_extension(media_type) or ".bin"
            item_id = new_id("item")
            path = media_dir / f"{sha[:16]}{ext}"
            path.write_bytes(data)
            item = {
                "id": item_id,
                "source": rec.data.get("source", "unknown"),
                "sender": rec.data.get("sender"),
                "received_at": utcnow(),
                "media_type": media_type,
                "path": str(path),
                "sha256": sha,
                "caption": rec.data.get("caption"),
            }
            ctx.store.insert_item(item)
            out.append(Record("item", item, id=item_id, cites=[rec.id]))
        return out
