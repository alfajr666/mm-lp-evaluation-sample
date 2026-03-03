# SLA Design Guide for Exchange-MM Agreements

This guide translates liquidity diagnostics into enforceable contract terms.

## 1. Quote Presence Obligation
- Recommend baseline: 97% minimum for anchor pairs (1-minute intervals).
- Exclusions: pre-approved maintenance windows only.
- Rationale: two-sided continuity is the minimum requirement for market quality.

## 2. Spread Obligation
- Define max spread as % of mid-price.
- Use two regimes:
  - Normal conditions: stricter cap.
  - High-volatility conditions: wider cap with explicit trigger (example: >3% in 5 minutes).
- Rationale: prevents vague "best effort" behavior.

## 3. Depth Obligation
- Minimum cumulative depth at 0.5% and 1% from mid in USD-equivalent.
- Review quarterly as organic volume evolves.
- Rationale: spread-only SLAs can be gamed with shallow books.

## 4. Reporting Requirements
- Daily automated report: quote presence, realized spread, and depth statistics.
- Monthly raw quote log audit rights for exchange.
- Rationale: auditability is necessary for objective enforcement.

## 5. Penalty Framework
- Tiered financial consequences:
  - <97% uptime: warning
  - <95% uptime: fee reduction
  - <90% uptime: contract review
- Rationale: monetary penalties align incentives better than reputational warnings.

## 6. Termination Clauses
- 30-day termination for sustained underperformance.
- 7-day termination for material breach with explicit definition.
- Rationale: protects exchange from prolonged liquidity risk.

## 7. Checklist Before Signing
- SLA metrics map directly to measured diagnostics.
- Data source and sampling interval are contractually defined.
- Dispute-resolution metric calculation is pre-agreed.
- Hedging/venue policy is disclosed for local-currency pairs.
