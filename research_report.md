# Liquidity Analysis & Operational Readiness Report

## Executive Summary
This report evaluates the liquidity profile of **Tokocrypto** and **Reku** (BTC/IDR and BTC/USDT pairs) to determine if they meet the operational thresholds for high-frequency market making or institutional liquidity provision.

---

## 📌 Key Metrics Synthesis

| Metric | Tokocrypto (BTC/IDR) | Reku (BTC/IDR) | Benchmark (Good MM) |
| :--- | :--- | :--- | :--- |
| **TWAS %** | ~0.000015%* | N/A (Low Data) | < 0.25% |
| **Quote Presence** | 100% | < 5% (Sparse) | > 99% |
| **Avg Depth @ 1%**| 377,332,200 IDR | 0 IDR | > $750k USD |

*\*Extremely low spread on Tokocrypto suggests potentially aggressive internal market making or a very narrow tick size relative to price.*

---

## 📊 Liquidity Gap Visualization
![Liquidity Gap](/Users/gilangfajar/Documents/Personal Files/Project/delomite/lima/research_chart.png)
*Figure 1: Numerical depth comparison at the 1.0% price threshold.*

---

## 📝 Analyst Notes
1.  **Tokocrypto Advantage**: Shows superior depth and consistency compared to Reku. However, the depth of $24k USD (converted) is still significantly below the "Good MM" synthetic benchmark of $750k, indicating a "Stressed" or "Emerging" profile for institutional use.
2.  **Reku Observation**: Data collection revealed massive liquidity gaps. Zero depth at 1% suggests that any significant taker order will cause >1% slippage, making it unsuitable for professional volume.
3.  **Non-obvious Insight**: The decoupling between spread (very tight) and depth (modest) on Tokocrypto suggests a "Tight but Thin" market. This is classic for exchanges that prioritize UX (tight spreads) over institutional capacity (deep orderbooks).

---

## 🛠 Operational Recommendation
- **Tokocrypto**: Recommended Mode: **MONITORED TRADING**. Liquidity is sufficient for retail but requires slippage guards for orders > 100M IDR.
- **Reku**: Recommended Mode: **NOT READY**. Requires primary market maker intervention to establish a basic bid-ask spread.

---
## ⚠️ Verification Checklist
- [x] Dates verified against snapshots
- [x] Numbers cross-checked with raw CSVs
- [x] Conditions compared against MM Archetypes
- [x] Multi-exchange depth normalized to notional value
