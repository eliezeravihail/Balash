"""Command line: run the same pipelines without WhatsApp.

    balash init                      create config/instance.yaml and the data folder
    balash ingest receipt.jpg ...    read receipts, print what was read and any alert
    balash pay 250 "מכולת יוסי"      record a payment on a grocery tab
    balash report [--month 2026-09]  monthly statistics, charts saved under data/reports
    balash balances                  current balance of every grocery tab
    balash blocks                    list the available blocks
    balash serve                     run the WhatsApp webhook server
"""

from __future__ import annotations

import argparse
import logging
import mimetypes
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .channels.whatsapp import ConsoleSender
from .config import load_config
from .service import Service

EXAMPLE = Path(__file__).resolve().parent.parent / "config" / "instance.example.yaml"


def _service(args: argparse.Namespace, need_llm: bool) -> Service:
    config = load_config(args.config)
    llm = None
    if need_llm:
        from .harness.llm import AnthropicLLM

        llm = AnthropicLLM()
    return Service(config, llm)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="balash", description="Balash: purchase tracking from receipts.")
    parser.add_argument("--config", default=None, help="path to instance.yaml (default: config/instance.yaml)")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("ingest")
    p.add_argument("files", nargs="+")
    p.add_argument("--caption", default="")
    p = sub.add_parser("pay")
    p.add_argument("amount")
    p.add_argument("store", nargs="?", default="")
    p = sub.add_parser("report")
    p.add_argument("--month", default=None, help="YYYY-MM, default: this month")
    sub.add_parser("balances")
    sub.add_parser("blocks")
    p = sub.add_parser("serve")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    if args.cmd == "init":
        target = Path(args.config or "config/instance.yaml")
        if target.exists():
            print(f"{target} already exists")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(EXAMPLE, target)
            print(f"created {target}. Edit it, then set ANTHROPIC_API_KEY.")
        load_config(target).data_dir.mkdir(parents=True, exist_ok=True)
        return 0

    if args.cmd == "blocks":
        from .core.block import all_blocks

        for name, cls in sorted(all_blocks().items()):
            doc = (cls.__doc__ or "").strip().splitlines()[0] if cls.__doc__ else ""
            print(f"{name:22} {cls.kind:9} {doc}")
        return 0

    if args.cmd == "serve":
        from .app import serve
        from .harness.llm import AnthropicLLM

        config = load_config(args.config)
        if not config.whatsapp.enabled:
            print("WhatsApp is not configured in instance.yaml", file=sys.stderr)
            return 2
        if not config.owners:
            print("No owners in instance.yaml: set BALASH_OWNER_NUMBER. Nobody could use the bot.", file=sys.stderr)
            return 2
        serve(Service(config, AnthropicLLM()), args.host, args.port)
        return 0

    out = ConsoleSender()
    if args.cmd == "ingest":
        service = _service(args, need_llm=True)
        for f in args.files:
            path = Path(f)
            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            print(f"--- {path.name}")
            service.ingest(path.read_bytes(), mime, out, "cli", source="cli", caption=args.caption, filename=path.name)
        return 0

    service = _service(args, need_llm=False)
    now = datetime.now(ZoneInfo(service.config.timezone))
    if args.cmd == "pay":
        service.handle_text(f"שילמתי {args.amount} {args.store}".strip(), out, "cli", now)
    elif args.cmd == "report":
        service.monthly(args.month or now.strftime("%Y-%m"), out, "cli")
    elif args.cmd == "balances":
        service.handle_text("יתרה", out, "cli", now)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
