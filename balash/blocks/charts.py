"""stats_charts: static PNG charts for the monthly report (sent over WhatsApp).

Single-series bar charts: one hue, thin bars, direct value labels, a recessive
baseline, and no legend, since the title names the one series. Hebrew is
passed through ``chart_text``, which reorders it only when the installed
matplotlib does not lay out right-to-left text itself.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ..core.block import Block, Context, register  # noqa: E402
from ..core.record import Record  # noqa: E402
from ..core.text import month_label, rtl  # noqa: E402


SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
SERIES = "#2a78d6"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
    }
)


def _native_bidi() -> bool:
    """matplotlib 3.11 shapes right-to-left text on its own (verified on 3.11.2)."""
    major, minor = (int(x) for x in matplotlib.__version__.split(".")[:2])
    return (major, minor) >= (3, 11)


def chart_text(text: str) -> str:
    return text if _native_bidi() else rtl(text)


def _style(ax: Any) -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)


def hbar(values: dict[str, float], title: str, path: Path, limit: int = 10) -> Path:
    items = list(values.items())[:limit]
    labels = [chart_text(k) for k, _ in items][::-1]
    nums = [v for _, v in items][::-1]
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(items) + 1.4), dpi=150)
    bars = ax.barh(labels, nums, height=0.55, color=SERIES, edgecolor=SURFACE, linewidth=2)
    top = max(nums) if nums else 1
    for bar, v in zip(bars, nums):
        ax.text(bar.get_width() + top * 0.01, bar.get_y() + bar.get_height() / 2, f"{v:,.0f} ₪",
                va="center", ha="left", color=TEXT_2, fontsize=10)
    ax.set_xlim(0, top * 1.18)
    ax.set_xticks([])
    _style(ax)
    ax.set_title(chart_text(title), loc="right", color=TEXT, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def vbar(values: dict[str, float], title: str, path: Path) -> Path:
    labels = [date.fromisoformat(k).strftime("%d.%m") for k in values]
    nums = list(values.values())
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    bars = ax.bar(labels, nums, width=0.55, color=SERIES, edgecolor=SURFACE, linewidth=2)
    top = max(nums) if nums else 1
    for bar, v in zip(bars, nums):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + top * 0.02, f"{v:,.0f} ₪",
                ha="center", va="bottom", color=TEXT_2, fontsize=10)
    ax.set_ylim(0, top * 1.18)
    ax.set_yticks([])
    ax.set_xlabel(chart_text("תחילת שבוע"), color=TEXT_2)
    _style(ax)
    ax.set_title(chart_text(title), loc="right", color=TEXT, fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


@register
class StatsCharts(Block):
    """Input: ``monthly_stats``. Output: ``image`` records {path, caption}:
    spend by category, by week, and by store when there is more than one."""

    name = "stats_charts"

    def run(self, inputs: list[Record], ctx: Context) -> list[Record]:
        out: list[Record] = []
        for rec in inputs:
            if rec.kind != "monthly_stats":
                continue
            s = rec.data
            if not s["receipts"]:
                continue
            folder = ctx.config.reports_dir / s["month"]
            folder.mkdir(parents=True, exist_ok=True)
            label = month_label(s["month"])
            charts = []
            if s["by_category"]:
                charts.append((hbar(s["by_category"], f"הוצאות לפי קטגוריה, {label}", folder / "by_category.png"), "לפי קטגוריה"))
            if s["by_week"]:
                charts.append((vbar(s["by_week"], f"הוצאות לפי שבוע, {label}", folder / "by_week.png"), "לפי שבוע"))
            if len(s["by_store"]) > 1:
                charts.append((hbar(s["by_store"], f"הוצאות לפי חנות, {label}", folder / "by_store.png"), "לפי חנות"))
            out.extend(rec.derive("image", {"path": str(p), "caption": c}) for p, c in charts)
        return out
