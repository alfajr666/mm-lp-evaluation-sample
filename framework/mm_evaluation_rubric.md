# MM Evaluation Rubric (Indonesia-Focused)

Use this rubric when selecting market makers for anchor pairs (for example BTC/IDR, USDT/IDR).
Score each dimension from 1 (weak) to 5 (strong).

## 1. Spread Quality
- Score focus: committed spread target vs observed TWAS requirement for target mode.
- Rationale: tighter and stable spread directly reduces user execution cost.

## 2. Depth Commitment
- Score focus: guaranteed cumulative notional at 0.5% and 1% from mid (USD equivalent).
- Rationale: depth determines slippage and real executable liquidity.

## 3. Uptime / Quote Presence
- Score focus: explicit SLA %, exclusions, and measurement interval.
- Rationale: high quote presence is required for continuous two-sided markets.

## 4. Stress Behavior Policy
- Score focus: documented behavior during high-volatility windows and recovery commitments.
- Rationale: resilience during stress separates operationally reliable MMs from cosmetic quoting.

## 5. Inventory & Hedging Transparency
- Score focus: visibility into inventory limits, hedging venues, and IDR risk handling.
- Rationale: poor hedging discipline can destabilize local pair quality.

## 6. Reporting Cadence & Auditability
- Score focus: reporting frequency, metric coverage, and willingness to provide raw logs.
- Rationale: exchanges need verifiable evidence for SLA enforcement.

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
