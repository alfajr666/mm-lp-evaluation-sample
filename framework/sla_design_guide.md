# SLA Design Guide for Exchange-MM Agreements

This guide translates liquidity diagnostics into enforceable contract terms.

## 1. Quote Presence Obligation
- **Baseline**: 97% minimum for anchor pairs (1-minute intervals).
- **Measurement**: Exclude pre-approved maintenance windows.
- **Project Insight**: As demonstrated by Reku's liquidity gaps, anything below 90% presence results in a non-functional market for HNWIs and institutional takers.

## 2. Spread Obligation
- **Max Spread**: Specified as a percentage of mid-price.
- **Regime 1 (Normal)**: Cap at 1.0% (calibrated against Tokocrypto's baseline).
- **Regime 2 (High Volatility)**: Cap at 3.5% with explicit trigger (e.g., >3% price move in 5 minutes).
- **Rationale**: Prevents "spread blowout" during predictable volatility spikes.

## 3. Depth Obligation
- **Minimum Notional**: Must guarantee at least $50k USD at 1% threshold for Mode 2 readiness.
- **Review**: Quarterly review to adjust for organic volume growth on the exchange.
- **Rationale**: Prevents gaming the SLA with "paper-thin" spreads that have zero executable depth (the "Tight but Thin" failure mode).

## 4. Reporting Requirements
- **Daily Report**: Automated metrics for quote presence, TWAS, and depth statistics.
- **Audit Rights**: Exchange retains monthly right to audit raw quote logs.
- **Rationale**: Auditability is the prerequisite for objective SLA enforcement.

## 5. Penalty Framework (Tiered)
- **Warning**: 96-97% uptime.
- **Fee Reduction**: 90-95% uptime (Recommend 20% reduction in monthly retainer).
- **Contract Review**: < 90% uptime or persistent depth failure.
- **Rationale**: Monetary penalties align MM incentives with exchange health better than reputational warnings.

## 6. Termination Clauses
- 30-day termination for sustained underperformance.
- 7-day termination for material breach with explicit definition.
- Rationale: protects exchange from prolonged liquidity risk.

## 7. Checklist Before Signing
- SLA metrics map directly to measured diagnostics.
- Data source and sampling interval are contractually defined.
- Dispute-resolution metric calculation is pre-agreed.
- Hedging/venue policy is disclosed for local-currency pairs.
