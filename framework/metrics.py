from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class DepthProfile:
    threshold_pct: float
    bid_notional: float
    ask_notional: float


def _safe_mid(best_bid: float, best_ask: float) -> float:
    if pd.isna(best_bid) or pd.isna(best_ask) or best_bid <= 0 or best_ask <= 0:
        return np.nan
    return (best_bid + best_ask) / 2


def compute_spread_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["mid_price"] = out.apply(lambda r: _safe_mid(r["best_bid"], r["best_ask"]), axis=1)
    out["spread_abs"] = out["best_ask"] - out["best_bid"]
    out["spread_pct"] = np.where(out["mid_price"] > 0, out["spread_abs"] / out["mid_price"] * 100, np.nan)
    return out


def time_weighted_avg_spread(df: pd.DataFrame, time_col: str = "timestamp_utc") -> float:
    d = compute_spread_metrics(df).dropna(subset=[time_col, "spread_pct"]).copy()
    if d.empty:
        return float("nan")
    d[time_col] = pd.to_datetime(d[time_col], utc=True)
    d = d.sort_values(time_col)
    deltas = d[time_col].diff().shift(-1).dt.total_seconds()
    deltas = deltas.fillna(deltas.median() if deltas.notna().any() else 60.0)
    return float(np.average(d["spread_pct"], weights=deltas.clip(lower=1)))


def quote_presence_ratio(df: pd.DataFrame) -> float:
    if df.empty:
        return float("nan")
    valid = (df["best_bid"] > 0) & (df["best_ask"] > 0) & (df["best_ask"] > df["best_bid"])
    return float(valid.mean() * 100)


def _extract_levels(row: pd.Series, side: str, max_levels: int = 20) -> List[Tuple[float, float]]:
    levels: List[Tuple[float, float]] = []
    for i in range(1, max_levels + 1):
        p = row.get(f"{side}_{i}_price")
        q = row.get(f"{side}_{i}_qty")
        if pd.isna(p) or pd.isna(q) or p <= 0 or q <= 0:
            continue
        levels.append((float(p), float(q)))
    return levels


def _depth_notional_within_threshold(levels: Iterable[Tuple[float, float]], mid: float, threshold_pct: float, side: str) -> float:
    if mid <= 0:
        return float("nan")
    threshold = threshold_pct / 100
    total = 0.0
    for price, qty in levels:
        if side == "bid" and price > mid:
            continue
        if side == "ask" and price < mid:
            continue
        dist = abs(price - mid) / mid
        if dist <= threshold:
            total += price * qty
    return total


def compute_depth_profile(df: pd.DataFrame, thresholds: Iterable[float] = (0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows: List[Dict[str, float]] = []
    working = compute_spread_metrics(df)
    for _, r in working.iterrows():
        mid = float(r.get("mid_price") or np.nan)
        bids = _extract_levels(r, "bid")
        asks = _extract_levels(r, "ask")
        out: Dict[str, float] = {
            "timestamp_utc": r.get("timestamp_utc"),
            "exchange": r.get("exchange"),
            "pair": r.get("pair"),
            "mid_price": mid,
        }
        for t in thresholds:
            out[f"bid_depth_{t:.1f}pct_notional"] = _depth_notional_within_threshold(bids, mid, t, "bid")
            out[f"ask_depth_{t:.1f}pct_notional"] = _depth_notional_within_threshold(asks, mid, t, "ask")
        rows.append(out)
    return pd.DataFrame(rows)


def detect_volatility_spikes(klines: pd.DataFrame, std_multiplier: float = 2.0) -> pd.DataFrame:
    d = klines.copy()
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d["ret_5m"] = d["close"].pct_change()
    sigma = d["ret_5m"].std(skipna=True)
    if pd.isna(sigma) or sigma == 0:
        d["is_spike"] = False
        return d
    d["is_spike"] = d["ret_5m"].abs() > (std_multiplier * sigma)
    return d


def spread_resilience_minutes(orderbook_df: pd.DataFrame, spike_times: pd.Series, baseline_quantile: float = 0.5) -> float:
    d = compute_spread_metrics(orderbook_df).copy()
    d["timestamp_utc"] = pd.to_datetime(d["timestamp_utc"], utc=True)
    baseline = d["spread_pct"].quantile(baseline_quantile)
    if pd.isna(baseline):
        return float("nan")

    recoveries: List[float] = []
    for ts in pd.to_datetime(spike_times, utc=True).dropna().unique():
        after = d[d["timestamp_utc"] >= ts].sort_values("timestamp_utc")
        rec = after[after["spread_pct"] <= baseline]
        if rec.empty:
            continue
        mins = (rec.iloc[0]["timestamp_utc"] - ts).total_seconds() / 60
        if mins >= 0:
            recoveries.append(mins)
    if not recoveries:
        return float("nan")
    return float(np.mean(recoveries))


def price_tracking_error_pct(local_df: pd.DataFrame, benchmark_df: pd.DataFrame, on: str = "timestamp_utc") -> pd.DataFrame:
    l = compute_spread_metrics(local_df)[[on, "mid_price"]].rename(columns={"mid_price": "local_mid"})
    b = compute_spread_metrics(benchmark_df)[[on, "mid_price"]].rename(columns={"mid_price": "bench_mid"})
    l[on] = pd.to_datetime(l[on], utc=True)
    b[on] = pd.to_datetime(b[on], utc=True)
    merged = pd.merge_asof(l.sort_values(on), b.sort_values(on), on=on, direction="nearest", tolerance=pd.Timedelta("60s"))
    merged["tracking_error_pct"] = np.where(
        merged["bench_mid"] > 0,
        (merged["local_mid"] - merged["bench_mid"]).abs() / merged["bench_mid"] * 100,
        np.nan,
    )
    return merged


def summarize_metrics(
    orderbook_df: pd.DataFrame,
    depth_df: Optional[pd.DataFrame] = None,
    resilience_minutes: Optional[float] = None,
    tracking_df: Optional[pd.DataFrame] = None,
) -> Dict[str, float]:
    depth_df = depth_df if depth_df is not None else compute_depth_profile(orderbook_df)
    summary: Dict[str, float] = {
        "time_weighted_avg_spread_pct": time_weighted_avg_spread(orderbook_df),
        "quote_presence_ratio_pct": quote_presence_ratio(orderbook_df),
        "spread_resilience_min": resilience_minutes if resilience_minutes is not None else float("nan"),
    }

    for t in (0.5, 1.0, 2.0):
        bid_col = f"bid_depth_{t:.1f}pct_notional"
        ask_col = f"ask_depth_{t:.1f}pct_notional"
        summary[f"avg_depth_{t:.1f}pct_notional"] = float(depth_df[[bid_col, ask_col]].mean(axis=1).mean()) if bid_col in depth_df and ask_col in depth_df else float("nan")

    if tracking_df is not None and "tracking_error_pct" in tracking_df:
        summary["avg_tracking_error_pct"] = float(pd.to_numeric(tracking_df["tracking_error_pct"], errors="coerce").mean())
    else:
        summary["avg_tracking_error_pct"] = float("nan")

    return summary
