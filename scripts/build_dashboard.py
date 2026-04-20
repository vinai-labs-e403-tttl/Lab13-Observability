#!/usr/bin/env python3
"""Build the 6-panel observability dashboard from data/logs.jsonl.

Matches docs/dashboard-spec.md:
    1. Traffic (success vs failed request count)
    2. Latency P50/P95/P99 (ms) — SLO line at 3000ms
    3. Error rate breakdown by error_type (%) — SLO line at 2%
    4. Cumulative cost over time (USD) — daily budget line at $2.50
    5. Tokens in/out totals
    6. Quality score average (with latency-histogram fallback) — target 0.75

Thresholds are read from config/slo.yaml so that changes stay in one place.

Usage:
    # Baseline:
    python scripts/build_dashboard.py --out evidence/dashboard_baseline.png

    # After injecting an incident (label the snapshot for the report):
    python scripts/build_dashboard.py \\
        --out evidence/dashboard_rag_slow.png \\
        --title-suffix " — during rag_slow incident"
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# ---------- SLO thresholds (mirror config/slo.yaml) ----------
SLO_LATENCY_P95_MS = 3000
SLO_ERROR_RATE_PCT = 2.0
SLO_DAILY_COST_USD = 2.5
SLO_QUALITY_SCORE = 0.75


# ---------- Helpers ----------
def percentile(values: list[float], p: int) -> float:
    """Nearest-rank percentile (matches app/metrics.py so dashboard and /metrics agree)."""
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def _parse_ts(ts_str: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def parse_logs(log_path: Path) -> dict:
    """Aggregate logs.jsonl into series suitable for the 6 panels."""
    if not log_path.exists():
        raise FileNotFoundError(
            f"{log_path} not found. Run the app and send requests (e.g. "
            f"`python scripts/load_test.py --concurrency 3`) first."
        )

    latencies: list[int] = []
    costs: list[float] = []
    tokens_in: list[int] = []
    tokens_out: list[int] = []
    quality_scores: list[float] = []
    errors: Counter[str] = Counter()
    cumulative_cost: list[tuple[datetime, float]] = []

    total_requests = 0
    failed_requests = 0
    running_cost = 0.0

    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue

        event = rec.get("event")

        if event == "response_sent":
            total_requests += 1
            if (v := rec.get("latency_ms")) is not None:
                latencies.append(int(v))
            if (v := rec.get("tokens_in")) is not None:
                tokens_in.append(int(v))
            if (v := rec.get("tokens_out")) is not None:
                tokens_out.append(int(v))
            if (v := rec.get("quality_score")) is not None:
                quality_scores.append(float(v))
            if (v := rec.get("cost_usd")) is not None:
                cost = float(v)
                costs.append(cost)
                running_cost += cost
                ts = _parse_ts(rec.get("ts", ""))
                if ts is not None:
                    cumulative_cost.append((ts, running_cost))

        elif event == "request_failed":
            total_requests += 1
            failed_requests += 1
            errors[rec.get("error_type", "unknown")] += 1

    return {
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "latencies": latencies,
        "costs": costs,
        "tokens_in": sum(tokens_in),
        "tokens_out": sum(tokens_out),
        "quality_scores": quality_scores,
        "errors": errors,
        "cumulative_cost": cumulative_cost,
    }


# ---------- Panel renderers ----------
def _annotate(ax, x, y, text, **kwargs) -> None:
    ax.text(x, y, text, ha="center", va="bottom", fontsize=9, **kwargs)


def _panel_traffic(ax, data: dict) -> None:
    success = data["total_requests"] - data["failed_requests"]
    failed = data["failed_requests"]
    bars = ax.bar(["Success", "Failed"], [success, failed],
                  color=["#4caf50", "#f44336"])
    ax.set_title("1. Traffic — total requests", fontweight="bold")
    ax.set_ylabel("Count")
    for bar, v in zip(bars, [success, failed]):
        _annotate(ax, bar.get_x() + bar.get_width() / 2, v, str(v))
    ax.set_ylim(0, max(1, max(success, failed)) * 1.2)


def _panel_latency(ax, data: dict) -> None:
    lats = data["latencies"]
    p50, p95, p99 = percentile(lats, 50), percentile(lats, 95), percentile(lats, 99)
    bars = ax.bar(["P50", "P95", "P99"], [p50, p95, p99],
                  color=["#2196f3", "#ff9800", "#f44336"])
    ax.axhline(SLO_LATENCY_P95_MS, linestyle="--", color="red", linewidth=1.5,
               label=f"SLO P95 = {SLO_LATENCY_P95_MS}ms")
    ax.set_title("2. Latency — P50 / P95 / P99", fontweight="bold")
    ax.set_ylabel("milliseconds (ms)")
    ax.legend(loc="upper left", fontsize=9)
    for bar, v in zip(bars, [p50, p95, p99]):
        _annotate(ax, bar.get_x() + bar.get_width() / 2, v, f"{int(v)}")
    ax.set_ylim(0, max(SLO_LATENCY_P95_MS * 1.1, (p99 or 0) * 1.2, 100))


def _panel_errors(ax, data: dict) -> None:
    total = data["total_requests"]
    if data["errors"] and total:
        labels = list(data["errors"].keys())
        pcts = [100.0 * v / total for v in data["errors"].values()]
        bars = ax.bar(labels, pcts, color="#f44336")
        for bar, v in zip(bars, pcts):
            _annotate(ax, bar.get_x() + bar.get_width() / 2, v, f"{v:.1f}%")
        ax.set_ylim(0, max(pcts + [SLO_ERROR_RATE_PCT]) * 1.3)
    else:
        ax.text(0.5, 0.5, "No errors recorded ✓",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=12, color="#4caf50")
        ax.set_ylim(0, max(SLO_ERROR_RATE_PCT * 2, 5))
    ax.axhline(SLO_ERROR_RATE_PCT, linestyle="--", color="red", linewidth=1.5,
               label=f"SLO = {SLO_ERROR_RATE_PCT}%")
    ax.set_title("3. Error rate — by error_type", fontweight="bold")
    ax.set_ylabel("Error rate (%)")
    ax.legend(loc="upper right", fontsize=9)


def _panel_cost_over_time(ax, data: dict) -> None:
    series = data["cumulative_cost"]
    if series:
        ts, cum = zip(*series)
        ax.plot(ts, cum, marker="o", color="#9c27b0", linewidth=2, markersize=4)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        ax.tick_params(axis="x", rotation=30)
        top = max(cum[-1], SLO_DAILY_COST_USD) * 1.2
        ax.set_ylim(0, top)
    else:
        ax.text(0.5, 0.5, "No cost data",
                ha="center", va="center", transform=ax.transAxes, color="gray")
        ax.set_ylim(0, SLO_DAILY_COST_USD * 1.2)
    ax.axhline(SLO_DAILY_COST_USD, linestyle="--", color="red", linewidth=1.5,
               label=f"Daily budget = ${SLO_DAILY_COST_USD}")
    ax.set_title("4. Cumulative cost over time", fontweight="bold")
    ax.set_ylabel("USD")
    ax.set_xlabel("Time (UTC)")
    ax.legend(loc="upper left", fontsize=9)


def _panel_tokens(ax, data: dict) -> None:
    bars = ax.bar(["Input", "Output"],
                  [data["tokens_in"], data["tokens_out"]],
                  color=["#3f51b5", "#009688"])
    ax.set_title("5. Tokens — in vs out (totals)", fontweight="bold")
    ax.set_ylabel("Tokens (count)")
    for bar, v in zip(bars, [data["tokens_in"], data["tokens_out"]]):
        _annotate(ax, bar.get_x() + bar.get_width() / 2, v, str(v))
    top = max(data["tokens_in"], data["tokens_out"], 1) * 1.2
    ax.set_ylim(0, top)


def _panel_quality(ax, data: dict) -> None:
    scores = data["quality_scores"]
    if scores:
        avg = mean(scores)
        color = "#4caf50" if avg >= SLO_QUALITY_SCORE else "#ff9800"
        ax.bar(["Quality Avg"], [avg], color=color, width=0.5)
        _annotate(ax, 0, avg, f"{avg:.2f}")
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("Score (0-1)")
        ax.set_title("6. Quality score — average", fontweight="bold")
    else:
        # Fallback per dashboard-spec.md: "quality proxy" = latency distribution.
        # This also surfaces tail latency hot-spots.
        lats = data["latencies"]
        if lats:
            bins = min(10, max(3, len(lats) // 2))
            ax.hist(lats, bins=bins, color="#607d8b", edgecolor="black")
            ax.set_xlabel("Latency (ms)")
            ax.set_ylabel("Request count")
            ax.set_title("6. Latency distribution (quality proxy)", fontweight="bold")
        else:
            ax.text(0.5, 0.5, "No data",
                    ha="center", va="center", transform=ax.transAxes, color="gray")
            ax.set_title("6. Quality score — average", fontweight="bold")
    ax.axhline(SLO_QUALITY_SCORE, linestyle="--", color="red", linewidth=1.5,
               label=f"Target = {SLO_QUALITY_SCORE}")
    ax.legend(loc="upper right", fontsize=9)


# ---------- Main build ----------
def build_dashboard(data: dict, out_path: Path, title_suffix: str = "") -> None:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f"Day 13 Observability Dashboard{title_suffix}",
                 fontsize=16, fontweight="bold")

    _panel_traffic(axes[0, 0], data)
    _panel_latency(axes[0, 1], data)
    _panel_errors(axes[0, 2], data)
    _panel_cost_over_time(axes[1, 0], data)
    _panel_tokens(axes[1, 1], data)
    _panel_quality(axes[1, 2], data)

    # Footer with data summary, useful when the PNG is pasted into the report.
    lats = data["latencies"]
    footer = (
        f"Requests: {data['total_requests']} "
        f"(failed {data['failed_requests']})   |   "
        f"P50/P95/P99 = {int(percentile(lats, 50))} / "
        f"{int(percentile(lats, 95))} / {int(percentile(lats, 99))} ms   |   "
        f"Total cost: ${sum(data['costs']):.4f}   |   "
        f"Tokens in/out: {data['tokens_in']}/{data['tokens_out']}"
    )
    fig.text(0.5, 0.01, footer, ha="center", fontsize=10, color="#555")

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    print(f"[OK] Dashboard written to: {out_path}")
    print(f"     {footer}")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build the 6-panel Day 13 observability dashboard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--log-path", default="data/logs.jsonl",
                   help="Path to logs.jsonl (default: data/logs.jsonl)")
    p.add_argument("--out", default="evidence/dashboard.png",
                   help="Output PNG path (default: evidence/dashboard.png)")
    p.add_argument("--title-suffix", default="",
                   help="Text appended to the title, e.g. ' — during rag_slow'")
    args = p.parse_args()

    try:
        data = parse_logs(Path(args.log_path))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if data["total_requests"] == 0:
        print("WARNING: 0 response_sent / request_failed events in logs. "
              "Run the load test first.", file=sys.stderr)

    build_dashboard(data, Path(args.out), title_suffix=args.title_suffix)


if __name__ == "__main__":
    main()
