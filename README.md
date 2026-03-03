# MM/LP Evaluation Framework for Emerging Crypto Exchanges

A data-driven decision framework for evaluating market maker and liquidity provider performance in emerging and fragmented crypto markets, with a practical focus on Indonesian exchanges.

## 1) The Problem
New exchanges need to decide when internal liquidity management is no longer enough. Once external MM/LPs are engaged, teams still lack a standardized way to evaluate performance and design enforceable SLAs.

## 2) The Approach
This repository collects high-frequency orderbook/ticker data across Binance, Tokocrypto, Reku, and Indodax, transforms raw snapshots into standardized liquidity diagnostics, and maps those diagnostics into an operational decision model. The framework then extends into an MM evaluation rubric and SLA design guide for practitioner use.

### Exchange/Pair Coverage

| Pair | Binance | Tokocrypto | Reku | Indodax |
|---|---|---|---|---|
| BTC/USDT | Full depth + history | Full depth + history | N/A | N/A |
| BTC/IDR | N/A | Full depth + history | Full depth | Ticker only |
| USDT/IDR | N/A | Full depth + history | Full depth | Ticker only |

## 3) Key Findings
Populate this section after data collection completes:
- TWAS spread by exchange/pair
- Depth at 1% (USD equivalent)
- Quote presence ratio
- Stress recovery behavior

## 4) Framework Output
The decision model (`LiquidityReadinessAssessor`) is implemented in `framework/assessor.py` and exposed in `notebooks/05_decision_threshold_model.ipynb` via ipywidgets.

## 5) Repository Navigation
1. `notebooks/01_data_collection.ipynb`: poll and store raw data.
2. `notebooks/02_liquidity_diagnostics.ipynb`: compute core liquidity metrics.
3. `notebooks/03_cross_exchange_comparison.ipynb`: compare distributions and fragmentation.
4. `notebooks/04_synthetic_mm_models.ipynb`: Good/Gaming/Stressed MM archetypes.
5. `notebooks/05_decision_threshold_model.ipynb`: mode assignment logic + interactive controls.
6. `framework/mm_evaluation_rubric.md` and `framework/sla_design_guide.md`: practitioner outputs.

## 6) About the Author
This framework is designed for operator-side decision making in exchange liquidity management and treasury workflows. It emphasizes measurable market quality and contract design that aligns MM behavior with exchange outcomes. The design is intentionally simple and reproducible: Python, CSV data, notebooks, and markdown outputs.

## Quick Start

```bash
cd mm-lp-evaluation-framework
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/poll_orderbooks.py --output-dir data/raw --once --backfill-klines
jupyter notebook
```

## Notes
- Raw data schema: `data/raw/data_dictionary.md`
- Collector logs and errors are written to `data/raw/collector.log` and `data/raw/collection_errors.csv`
- Thresholds in `framework/assessor.py` follow the brief and should be empirically recalibrated after a 2+ week collection window
