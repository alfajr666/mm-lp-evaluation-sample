# MM Evaluation Rubric (Indonesia-Focused)

Use this rubric when selecting market makers for anchor pairs (for example BTC/IDR, USDT/IDR).
Score each dimension from 1 (weak) to 5 (strong).

## 1. Spread Quality
- **Score Focus**: Committed TWAS target vs. observed mode thresholds. (Score 5 if < 0.5%, Score 3 if 0.5-2%, Score 1 if > 2%).
- **Project Insight**: Tokocrypto's ultra-tight spread (~0.000015%) suggests a primary-MM setup; any candidate offering > 0.5% for anchor pairs like BTC/USDT is non-competitive.

## 2. Depth Commitment
- **Score Focus**: Guaranteed notional at 1% threshold. (Score 5 if > $500k, Score 3 if $50k-$500k, Score 1 if < $50k).
- **Project Insight**: Tokocrypto's depth (~$24k USD) currently sits in Mode 1 (Retail/Emerging). A professional external MM must offer at least Mode 2 ($50k+) depth to justify engagement fees.

## 3. Uptime / Quote Presence
- **Score Focus**: Explicit SLA % commitment. (Score 5 if > 99%, Score 3 if 90-98%, Score 1 if < 90%).
- **Project Insight**: High quote presence is the baseline. Reku's "sparse" snapshots show that a MM failing this metric (below 95%) effectively leaves the exchange without a functional market.

## 4. Stress Behavior Policy
- **Score Focus**: Documented behavior during high-volatility windows (Recovery Time < 2 min for Score 5).
- **Project Insight**: Resilience during 2-sigma volatility events separates operationally reliable MMs from "fair-weather" cosmetic quoting.

## 5. Inventory & Hedging Transparency
- **Score Focus**: Visibility into IDR hedging venues and inventory limits.
- **Rationale**: Given the IDR-denomination of pairs like BTC/IDR, poor hedging discipline can lead to toxic flow and destabilized spreads.

## 6. Reporting Cadence & Auditability
- **Score Focus**: Reporting frequency and willingness to provide raw quote logs.
- **Rationale**: Without verifiable evidence, SLA enforcement (penalties) becomes impossible. Professional MMs should provide daily automated reports.

## Scoring Template

| Candidate | Spread (1-5) | Depth (1-5) | Uptime (1-5) | Stress (1-5) | Inventory (1-5) | Reporting (1-5) | Total (30) | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| MM A |  |  |  |  |  |  |  |  |
| MM B |  |  |  |  |  |  |  |  |
| MM C |  |  |  |  |  |  |  |  |

## One-Page HTML Template

```html
<table border="1" cellspacing="0" cellpadding="8">
  <thead>
    <tr>
      <th>Candidate</th><th>Spread</th><th>Depth</th><th>Uptime</th>
      <th>Stress</th><th>Inventory</th><th>Reporting</th><th>Total</th><th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>MM A</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>MM B</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>MM C</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>
```
