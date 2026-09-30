"""HTTP server: the WhatsApp webhook and the monthly scheduler."""

from __future__ import annotations

import json
import threading
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from .blocks.wording import HELP
from .channels.whatsapp import InboundMessage, WhatsAppClient, WhatsAppSender, parse_webhook, verify_signature
from .core.block import log
from .service import Service

ERROR_TEXT = "משהו השתבש בעיבוד ההודעה. היא נשמרה, ואפשר לנסות לשלוח שוב בעוד כמה דקות."


def create_app(service: Service, client: WhatsAppClient | None = None, scheduler: bool = True) -> FastAPI:
    config = service.config
    client = client or WhatsAppClient(config.whatsapp)
    sender = WhatsAppSender(client, service.store)
    service.media = client
    stop = threading.Event()

    def scheduler_loop() -> None:
        while not stop.wait(900):
            try:
                run_scheduled_report(service, sender)
            except Exception:
                log.exception("scheduled report failed")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        thread = None
        if scheduler:
            thread = threading.Thread(target=scheduler_loop, daemon=True)
            thread.start()
        yield
        stop.set()

    app = FastAPI(title="Balash", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "instance": config.instance}

    @app.get("/webhook")
    def verify(request: Request) -> PlainTextResponse:
        q = request.query_params
        if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == config.whatsapp.verify_token and config.whatsapp.verify_token:
            return PlainTextResponse(q.get("hub.challenge", ""))
        raise HTTPException(status_code=403, detail="verification failed")

    @app.post("/webhook")
    async def receive(request: Request, background: BackgroundTasks) -> dict:
        body = await request.body()
        if config.whatsapp.app_secret and not verify_signature(
            config.whatsapp.app_secret, body, request.headers.get("x-hub-signature-256")
        ):
            raise HTTPException(status_code=403, detail="bad signature")
        try:
            payload = json.loads(body or b"{}")
        except ValueError:
            raise HTTPException(status_code=400, detail="bad json")
        for msg in parse_webhook(payload):
            # Documents go to the pipeline, where receipt_inbox checks the sender
            # before downloading anything. Everything else needs an owner here.
            # No owners configured means nobody is allowed, never everybody.
            if msg.type not in ("image", "document") and msg.sender not in config.owners:
                log.warning("ignoring message from %s: not in owners", msg.sender)
                continue
            seen_key = f"wa_msg:{msg.message_id}"
            if msg.message_id and service.store.kv_get(seen_key):
                continue
            service.store.kv_set(seen_key, "1")
            background.add_task(process_message, service, client, sender, msg)
        return {"ok": True}

    return app


def process_message(service: Service, client: WhatsAppClient, sender: WhatsAppSender, msg: InboundMessage) -> None:
    try:
        if msg.type in ("image", "document"):
            if msg.sender in service.config.owners:
                sender.flush(msg.sender)  # the window is open again: deliver anything that waited
            service.ingest_whatsapp(asdict(msg), sender)
            return
        sender.flush(msg.sender)
        if msg.type == "text":
            service.handle_text(msg.text, sender, msg.sender)
        else:
            sender.send_text(msg.sender, HELP)
    except Exception:
        log.exception("processing message %s failed", msg.message_id)
        if msg.sender not in service.config.owners:
            return
        try:
            sender.send_text(msg.sender, ERROR_TEXT)
        except Exception:
            log.exception("could not report the failure")


def run_scheduled_report(service: Service, sender: WhatsAppSender, now: datetime | None = None) -> str | None:
    now = now or datetime.now(ZoneInfo(service.config.timezone))
    month = service.due_monthly_report(now)
    if not month or not service.config.owners:
        return None
    for owner in service.config.owners:
        service.monthly(month, sender, owner)
    service.store.kv_set("last_report_month", month)
    return month


def serve(service: Service, host: str, port: int) -> None:
    import uvicorn

    uvicorn.run(create_app(service), host=host, port=port)
