from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class AssessmentResult:
    mode: str
    score_mode_1: int
    score_mode_2: int
    score_mode_3: int
    reasons: List[str]


class LiquidityReadinessAssessor:
    """Classifies liquidity readiness into Mode 1, 2, or 3 using threshold rules."""

    def __init__(self) -> None:
        self.mode_labels = {
            1: "Mode 1 - Internal ops sufficient",
            2: "Mode 2 - Hybrid",
            3: "Mode 3 - Full external MM dependency",
        }

    def _score(self, metrics: Dict[str, float]) -> Tuple[int, int, int, List[str]]:
        m1 = 0
        m2 = 0
        m3 = 0
        reasons: List[str] = []

        spread = metrics.get("time_weighted_avg_spread_pct")
        depth_1 = metrics.get("depth_1pct_usd", metrics.get("avg_depth_1.0pct_notional"))
        quote = metrics.get("quote_presence_ratio_pct")
        resilience = metrics.get("spread_resilience_min")
        turnover = metrics.get("daily_volume_to_circulating_supply_pct")

        if spread is not None:
            if spread > 2:
                m1 += 1
                reasons.append(f"Spread {spread:.2f}% is wide (>2%), indicating immature liquidity.")
            elif 0.5 <= spread <= 2:
                m2 += 1
                reasons.append(f"Spread {spread:.2f}% fits hybrid operating range (0.5%-2%).")
            else:
                m3 += 1
                reasons.append(f"Spread {spread:.2f}% can support tight external-MM SLA targets.")

        if depth_1 is not None:
            if depth_1 < 50_000:
                m1 += 1
                reasons.append(f"Depth at 1% is ${depth_1:,.0f}, below $50k threshold.")
            elif depth_1 <= 500_000:
                m2 += 1
                reasons.append(f"Depth at 1% is ${depth_1:,.0f}, in hybrid range.")
            else:
                m3 += 1
                reasons.append(f"Depth at 1% is ${depth_1:,.0f}, sufficient for advanced MM structure.")

        if quote is not None:
            if quote < 90:
                m1 += 1
                reasons.append(f"Quote presence {quote:.2f}% is below operational baseline.")
            elif quote <= 98:
                m2 += 1
                reasons.append(f"Quote presence {quote:.2f}% supports single-MM hybrid setup.")
            else:
                m3 += 1
                reasons.append(f"Quote presence {quote:.2f}% is near institutional target.")

        if resilience is not None:
            if resilience > 10:
                m1 += 1
                reasons.append(f"Spread recovery {resilience:.1f} min is slow (>10 min).")
            elif resilience >= 2:
                m2 += 1
                reasons.append(f"Spread recovery {resilience:.1f} min is moderate (2-10 min).")
            else:
                m3 += 1
                reasons.append(f"Spread recovery {resilience:.1f} min is fast (<2 min).")

        if turnover is not None:
            if turnover < 0.1:
                m1 += 1
                reasons.append(f"Daily volume/supply {turnover:.3f}% is below 0.1%.")
            elif turnover <= 1:
                m2 += 1
                reasons.append(f"Daily volume/supply {turnover:.3f}% is in transitional band.")
            else:
                m3 += 1
                reasons.append(f"Daily volume/supply {turnover:.3f}% supports full external MM model.")

        return m1, m2, m3, reasons

    def assess(self, metrics: Dict[str, float]) -> AssessmentResult:
        m1, m2, m3, reasons = self._score(metrics)
        best_mode = max([(1, m1), (2, m2), (3, m3)], key=lambda x: (x[1], x[0]))[0]
        return AssessmentResult(
            mode=self.mode_labels[best_mode],
            score_mode_1=m1,
            score_mode_2=m2,
            score_mode_3=m3,
            reasons=reasons,
        )
