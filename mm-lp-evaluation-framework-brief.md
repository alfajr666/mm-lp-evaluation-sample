# MM/LP Evaluation Framework for Emerging Crypto Exchanges
## Project Brief

> **Repo name:** `mm-lp-evaluation-framework`
>
> **Tagline:** *A data-driven decision framework for evaluating market maker and liquidity provider performance in emerging and fragmented crypto markets — with application to Indonesian exchanges.*
>
> **Audience:** Exchange BD/listings teams, exchange risk/treasury, fintech operators expanding into Southeast Asia, and any hiring manager evaluating candidates for exchange operations, market structure, or liquidity roles.

---

## Thesis Statement

Newly founded crypto exchanges face a critical but poorly defined decision: when does organic or internal liquidity management become insufficient, and how should they evaluate external MM/LP partners once engaged? This project builds an empirical framework answering both questions, grounded in real orderbook data from Indonesian crypto exchanges and contextualized against global benchmarks.

---

## Exchange & Pair Matrix

| Pair | Binance | Tokocrypto | Reku | Indodax |
|---|---|---|---|---|
| BTC/USDT | ✅ Full depth + history | ✅ Full depth + history | ❌ | ❌ |
| BTC/IDR | ❌ | ✅ Full depth + history | ✅ Full depth | ⚠️ Ticker only |
| USDT/IDR | ❌ | ✅ Full depth + history | ✅ Full depth | ⚠️ Ticker only |

---

## Project Structure — Five Components

---

### Component 1: Data Collection & Storage

**Objective:** Build a reliable, reproducible data pipeline collecting orderbook snapshots and historical data across all exchanges and pairs.

**What to collect:**

- Orderbook snapshots — top 20 levels bid and ask — polled every 60 seconds over a minimum 2-week collection window
- Historical klines from Tokocrypto (1m and 5m intervals, 90 days back)
- Reku `orderbookall` snapshots at same polling frequency
- Binance BTC/USDT orderbook and klines as benchmark
- Indodax ticker-only (best bid, best ask, last price) at same polling frequency

**Storage:** Flat CSV files per exchange per pair, timestamped. Simple and transparent for a portfolio project — no database overhead, fully auditable.

**Output:** Raw data folder with a data dictionary markdown file explaining schema, collection methodology, and known limitations (Indodax depth blocked, Reku IDR-only denomination).

**Agent brief:** Build a Python polling script using `requests` and `schedule`. Runs continuously, writes to CSV, handles connection errors gracefully with retry logic and error logging. No authentication required for any endpoint.

---

### Component 2: Liquidity Diagnostic & Scoring

**Objective:** Convert raw orderbook data into standardized liquidity metrics across all exchanges and pairs. This is the empirical backbone.

**Metrics to construct:**

**Bid-Ask Spread** — both absolute and as percentage of mid-price. Time-weighted average spread (TWAS) as the primary summary statistic.

**Order Book Depth** — cumulative volume available at 0.5%, 1%, and 2% from mid-price on both sides. This is the slippage proxy — how large a trade can execute before moving the market by each threshold.

**Quote Presence Ratio** — percentage of observed snapshots where a valid two-sided market exists. Proxy for NBBO participation/uptime. A MM scoring below 95% here is a red flag.

**Spread Resilience** — identify volatility spike windows from kline data (define as periods where 5m price move exceeds 2 standard deviations). Measure spread behavior during and after these windows. How quickly does spread recover to baseline?

**Price Tracking Error** — for BTC/USDT on Tokocrypto, measure deviation of mid-price from Binance mid-price in real time. Persistent deviation signals poor MM or arbitrage gap. For BTC/IDR and USDT/IDR, construct an implied cross-rate from Binance BTC/USDT + a USD/IDR reference rate and compare.

**Output:** A metrics dataframe per exchange per pair. Summary statistics table. Time-series plots of each metric. This notebook is the most important data asset.

**Agent brief:** Python notebook, pandas for data processing, matplotlib/seaborn for visualization. All metrics defined as functions so they're reusable in later components.

---

### Component 3: Cross-Exchange Comparison & The Liquidity Gap

**Objective:** Visually and statistically demonstrate the liquidity quality gap between exchanges. This is where the thesis gets proven empirically.

**Key analyses:**

**Spread comparison across exchanges** — for BTC/IDR: Tokocrypto vs Reku vs Indodax (ticker-level). Show the distribution, not just the mean. A box plot showing Reku's spread distribution vs Tokocrypto tells a clearer story than a single number.

**Depth comparison** — for each depth threshold (0.5%, 1%, 2%), show how much volume each exchange can absorb. Frame this in USD equivalent so it's intuitive to a non-technical reader. "Reku can absorb $X of BTC/IDR sell pressure before price moves 1%" is a concrete, meaningful statement.

**Stress event behavior** — pick 2–3 identifiable volatility events in the collection window. Show spread and depth behavior on each exchange during those events.

**The fragmentation narrative** — show that the same asset (BTC) priced in IDR trades at measurably different effective costs across exchanges simultaneously. This is the core market structure problem the framework is designed to solve.

**Output:** A standalone comparison report notebook with publication-quality charts. This is the section most likely to get shared or screenshot by someone reading the portfolio.

**Agent brief:** Build on Component 2 metrics functions. Focus on visualization quality — use consistent color coding per exchange throughout. Add a brief interpretive markdown cell after each major chart explaining what it means in plain English.

---

### Component 4: The Decision Threshold Model

**Objective:** Build the readiness matrix. A structured decision tool that takes liquidity diagnostic scores as input and outputs a recommendation across three operating modes.

**The three operating modes:**

- **Mode 1 — Internal ops sufficient:** Liquidity is thin but manageable through internal treasury activity, spread management, and basic inventory controls. No dedicated external MM needed yet.
- **Mode 2 — Hybrid:** Exchange should appoint one dedicated MM for anchor pairs while internal ops handles secondary pairs. MM agreement is simple, focused on spread and uptime.
- **Mode 3 — Full external MM dependency:** Exchange complexity exceeds internal capability. Multiple dedicated MMs, competitive quoting, formal SLA with penalty structure.

**The threshold matrix:**

| Metric | Mode 1 | Mode 2 | Mode 3 |
|---|---|---|---|
| Time-weighted avg spread | >2% | 0.5–2% | <0.5% target needed |
| Depth at 1% (USD equiv) | <$50K | $50K–$500K | >$500K |
| Quote presence ratio | <90% | 90–98% | >99% required |
| Spread resilience (recovery time) | >10 min | 2–10 min | <2 min required |
| Daily volume / circulating supply | <0.1% | 0.1–1% | >1% |

*Note: These thresholds are empirically calibrated against collected data and the Binance benchmark. They are not arbitrary — show the derivation in the notebook.*

**Output:** A decision function that takes a liquidity scorecard as input and returns a mode recommendation with reasoning. Applied to real exchange data so Reku and Tokocrypto each get a mode assignment.

**Agent brief:** Build as a Python class `LiquidityReadinessAssessor`. Takes a dictionary of metrics, applies threshold logic, returns mode + narrative explanation. Wrap in a simple interactive widget (ipywidgets) so a reader can adjust inputs and see the recommendation change in real time.

---

### Component 5: MM Evaluation Rubric & SLA Design Guide

**Objective:** Given that an exchange has decided to engage external MM (Mode 2 or 3), how do they evaluate candidates and structure the agreement?

#### Part A — The Evaluation Rubric

Score MM candidates across six dimensions on a 1–5 scale:

**Spread quality** — what spread commitment are they offering, and how does it compare to the Mode threshold? Are they committing to a specific TWAS or just best-effort?

**Depth commitment** — what minimum depth at each price tier are they guaranteeing? Get this in writing with specific USD thresholds.

**Uptime/quote presence** — what SLA percentage are they committing to? How is downtime defined — scheduled maintenance vs. unscheduled? What happens during exchange-side outages?

**Stress behavior policy** — do they have an explicit policy for behavior during extreme volatility? Any professional MM should be able to articulate this. Vague answers here are a red flag.

**Inventory and hedging transparency** — are they willing to share inventory reports? How do they hedge their IDR exposure? This matters especially for IDR-denominated pairs where hedging is non-trivial.

**Reporting cadence** — what data do they provide back to the exchange, at what frequency, and in what format? A MM who resists reporting requirements is not aligned with the exchange's interests.

#### Part B — SLA Design Guide

Key contractual elements every MM agreement for an Indonesian exchange should include:

**Minimum quote presence ratio** — recommend 97% for anchor pairs, measured in 1-minute intervals, excluding pre-agreed maintenance windows.

**Maximum spread obligation** — specify as a percentage of mid-price, separately for normal market hours and high-volatility periods (define volatility trigger explicitly, e.g., >3% price move in 5 minutes).

**Minimum depth obligation** — specify cumulative volume in USD equivalent at 0.5% and 1% from mid. Review quarterly as exchange volume grows.

**Reporting requirements** — daily automated report of quote uptime, realized spread, and depth metrics. Exchange retains right to audit raw quote logs monthly.

**Penalty structure** — tiered penalties for SLA breach: warning below 97% uptime, fee reduction below 95%, contract review below 90%. Make penalties financial, not just reputational.

**Termination clause** — 30-day notice for performance reasons, 7-day for material breach. Define material breach explicitly.

**Output:** A markdown document formatted as a professional guide readable by a non-technical BD head or CFO. Include a one-page scoring template (simple HTML table) that an exchange team could use directly in an MM RFP process.

**Agent brief:** Write as a polished markdown document with clear section headers. Tone is practitioner-facing, not academic. Every recommendation should have a one-sentence rationale grounded in the project's empirical findings.

---

### Component 6: Executive Summary & Portfolio Landing Page

**Objective:** A single-page README that tells the whole story in 5 minutes for a non-technical hiring manager.

**Structure:**

1. The problem (2 sentences)
2. The approach (3 sentences + the exchange/pair matrix table)
3. Key findings (3–4 bullet points with actual numbers from the data)
4. The framework output (one screenshot of the decision matrix widget)
5. How to navigate the repo (numbered list of components)
6. About the author (3 sentences connecting this to treasury ops background)

**Agent brief:** Write last, after all other components are complete. Pull actual numbers from the analysis. This is the first thing anyone sees — it needs to be sharp, specific, and confident.

---

## Synthetic MM Behavior Models

These sit inside Components 2/3 and are worth calling out separately.

Since MM internals cannot be observed from outside, build three synthetic MM archetypes and show what their observable orderbook fingerprint looks like:

**The Good MM** — tight consistent spread, deep book, fast resilience, quote presence >99%, smooth inventory tilting visible as gradual mid-price adjustments.

**The Gaming MM** — hits SLA metrics on paper but thins the book just beyond the measurement thresholds. Quote presence is high but depth at 1% is near zero. Spread is technically within SLA but at the maximum allowed level constantly.

**The Stressed MM** — performs well in normal conditions but spread blows out during volatility events and recovery is slow. Inventory management is reactive rather than proactive.

Show each archetype's metric signature side by side. This demonstrates understanding of failure modes, not just success metrics — which is what an exchange operator actually needs to know.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data collection | Python, `requests`, `schedule` |
| Data processing | `pandas`, `numpy` |
| Visualization | `matplotlib`, `seaborn` |
| Interactivity | `ipywidgets` |
| Notebooks | Jupyter |
| Documentation | Markdown |
| Version control | GitHub |

No database, no dashboard framework, no cloud infrastructure. Keep it simple and reproducible.

---

## Repo Structure

```
mm-lp-evaluation-framework/
├── README.md                                   ← Component 6
├── requirements.txt
├── data/
│   ├── raw/                                    ← Component 1 output
│   └── processed/                              ← Component 2 output
├── notebooks/
│   ├── 01_data_collection.ipynb                ← Component 1
│   ├── 02_liquidity_diagnostics.ipynb          ← Component 2
│   ├── 03_cross_exchange_comparison.ipynb      ← Component 3
│   ├── 04_synthetic_mm_models.ipynb            ← Synthetic archetypes
│   └── 05_decision_threshold_model.ipynb       ← Component 4
├── framework/
│   ├── mm_evaluation_rubric.md                 ← Component 5A
│   └── sla_design_guide.md                     ← Component 5B
└── assets/
    └── charts/                                 ← Exported charts for README
```

---

## Execution Order for Agents

| Step | Task | Dependency |
|---|---|---|
| 1 | Build data collection script, start polling | None |
| 2 | Build liquidity diagnostic functions | Partial data sufficient |
| 3 | Build synthetic MM behavior models | No real data needed |
| 4 | Run cross-exchange comparison analysis | Minimum 2 weeks of data |
| 5 | Calibrate and build decision threshold model | Component 3 complete |
| 6 | Write MM rubric and SLA design guide | Component 5 complete |
| 7 | Write README | All components complete |

---

## What This Project Proves to a Hiring Manager

**Exchange ops or BD role:** You understand market microstructure from the operator side, can quantify liquidity quality, and know how to structure MM agreements that protect the exchange.

**Risk or treasury role:** You can build data pipelines, define metrics rigorously, and translate quantitative findings into operational decisions.

**Fintech or startup role in SEA:** You have direct knowledge of Indonesian market structure and the specific constraints of operating in a fragmented, IDR-denominated environment.

No other candidate is walking in with this combination.

---

*Brief version: 1.0 — March 2026*
