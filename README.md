# MM LP Evaluation Framework

Lightweight framework for collecting orderbook data and evaluating liquidity provider performance across Indonesian crypto exchanges.

## Exchanges & Pairs

| Exchange | BTCIDR | BTCUSDT | USDTIDR | Type |
|----------|--------|---------|---------|------|
| Tokocrypto | ✅ | ✅ | ✅ | Orderbook (20 levels) |
| Upbit ID | ✅ | ✅ | ✅ | Orderbook (20 levels) |
| Binance | — | ✅ | — | Orderbook (20 levels, benchmark) |
| Reku | ✅ | — | ✅ | Orderbook (API sunset, expected empty) |
| Indodax | ✅ | — | ✅ | Ticker only |

## Quick Start

No virtual environment required. Uses system Python3:

```bash
# Install core dependencies
pip3 install -r requirements.txt

# Run one collection cycle
python3 scripts/poll_orderbooks.py --once

# Run continuous polling (every 60s)
python3 scripts/poll_orderbooks.py --interval-seconds 60
```

## Optional: Isolated Environment with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup venv with all dependencies (core + dev + notebook)
make setup-uv

# Run via make
make collect-once
make collect-live
```

## Optional: Notebook Support

```bash
pip3 install pandas numpy matplotlib seaborn ipywidgets jupyter
jupyter notebook
```

## Project Structure

```
├── scripts/
│   ├── poll_orderbooks.py       # Main data collection poller
│   ├── filter_legacy_data.py    # Trim old rows from collected CSVs
│   └── generate_sharper_visuals.py  # Chart generation from raw data
├── framework/
│   ├── assessor.py              # Liquidity readiness classifier (Mode 1/2/3)
│   └── metrics.py               # Spread, depth, resilience, tracking error
├── deploy/
│   └── mm-lp-poller.service     # systemd service for VPS deployment
├── notebooks/                   # Jupyter analysis notebooks
├── data/raw/                    # Collected CSV output (gitignored)
├── assets/charts/               # Generated chart images
├── pyproject.toml
├── requirements.txt
└── Makefile
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make collect-once` | One collection cycle + kline backfill |
| `make collect-live` | Continuous polling every 60s |
| `make test` | Run unit tests |
| `make notebook` | Open Jupyter Notebook |
| `make clean` | Remove Python cache files |
| `make setup-uv` | Create uv venv and install all dependencies |
| `make clean-uv` | Remove uv venv |

## CLI Reference

```bash
python3 scripts/poll_orderbooks.py [OPTIONS]

Options:
  --output-dir PATH         CSV output directory (default: data/raw)
  --interval-seconds INT    Polling cadence in seconds (default: 60)
  --once                    Run one cycle and exit
  --backfill-klines         Also fetch historical 1m/5m klines for Binance & Tokocrypto
```

## VPS Deployment

A systemd service file is provided for running the poller as a background service.

**1. Deploy project to server:**

```bash
git clone https://github.com/alfajr666/mm-lp-evaluation-sample.git /opt/mm-lp-evaluation-sample
cd /opt/mm-lp-evaluation-sample
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**2. Install and enable the service:**

```bash
sudo cp deploy/mm-lp-poller.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mm-lp-poller
sudo systemctl start mm-lp-poller
```

**3. Check status and logs:**

```bash
sudo systemctl status mm-lp-poller
journalctl -u mm-lp-poller -f
```

The service runs as `www-data`, restarts automatically on failure, and writes data to `/opt/mm-lp-evaluation-sample/data/raw/`.

## Dependencies

**Core (required):**
- `requests` — HTTP client for exchange APIs
- `schedule` — Job scheduling for live polling

**Optional (notebooks & analysis):**
- `pandas`, `numpy` — Data processing
- `matplotlib`, `seaborn` — Visualization
- `ipywidgets`, `jupyter` — Notebook interface
- `pytest` — Testing

## License

MIT