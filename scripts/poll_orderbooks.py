#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

REQUEST_TIMEOUT = 15
LEVELS = 20

EXCHANGE_CONFIG = {
    "binance": {
        "orderbook": "https://api.binance.com/api/v3/depth",
        "klines": "https://api.binance.com/api/v3/klines",
        "pairs": ["BTCUSDT"],
    },
    "tokocrypto": {
        "orderbook": "https://www.tokocrypto.com/open/v1/market/depth",
        "klines": "https://www.tokocrypto.com/open/v1/market/klines",
        "pairs": ["BTC_USDT", "BTC_IDR", "USDT_IDR"],
    },
    "reku": {
        "orderbook": "https://api.reku.id/v2/orderbook",
        "pairs": ["btcidr", "usdtidr"],
    },
    "indodax": {
        "ticker": "https://indodax.com/api/ticker/{pair}",
        "pairs": ["btcidr", "usdtidr"],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(output_dir / "collector.log"),
            logging.StreamHandler(),
        ],
    )


def _ensure_csv_header(path: Path, header: List[str]) -> None:
    if not path.exists():
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def _append_row(path: Path, row: Dict[str, object], header: List[str]) -> None:
    _ensure_csv_header(path, header)
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(row)


def _request_json(url: str, params: Dict[str, object] | None = None, retries: int = 3) -> Dict:
    last_err = None
    for i in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            logging.warning("request failed (attempt %s/%s): %s", i, retries, exc)
            time.sleep(i)
    raise RuntimeError(f"request failed after {retries} retries: {last_err}")


def _extract_payload_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(payload.get("data"), dict):
        return payload["data"]
    if isinstance(payload.get("result"), dict):
        return payload["result"]
    return payload


def _normalize_side(raw_levels: Any) -> List[List[float]]:
    levels: List[List[float]] = []
    if not isinstance(raw_levels, list):
        return levels
    for level in raw_levels:
        if isinstance(level, (list, tuple)) and len(level) >= 2:
            try:
                levels.append([float(level[0]), float(level[1])])
            except (TypeError, ValueError):
                continue
        elif isinstance(level, dict):
            price = level.get("price") or level.get("rate")
            qty = level.get("qty") or level.get("amount") or level.get("volume")
            try:
                levels.append([float(price), float(qty)])
            except (TypeError, ValueError):
                continue
    return levels


def _normalize_orderbook(exchange: str, pair: str, bids: List[List[str]], asks: List[List[str]]) -> Tuple[List[str], Dict[str, object]]:
    header = ["timestamp_utc", "exchange", "pair", "best_bid", "best_ask", "mid_price"]
    row: Dict[str, object] = {
        "timestamp_utc": utc_now(),
        "exchange": exchange,
        "pair": pair,
    }

    best_bid = float(bids[0][0]) if bids else 0.0
    best_ask = float(asks[0][0]) if asks else 0.0
    row["best_bid"] = best_bid
    row["best_ask"] = best_ask
    row["mid_price"] = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else ""

    for i in range(1, LEVELS + 1):
        header += [f"bid_{i}_price", f"bid_{i}_qty", f"ask_{i}_price", f"ask_{i}_qty"]
        if i <= len(bids):
            row[f"bid_{i}_price"] = float(bids[i - 1][0])
            row[f"bid_{i}_qty"] = float(bids[i - 1][1])
        else:
            row[f"bid_{i}_price"] = ""
            row[f"bid_{i}_qty"] = ""

        if i <= len(asks):
            row[f"ask_{i}_price"] = float(asks[i - 1][0])
            row[f"ask_{i}_qty"] = float(asks[i - 1][1])
        else:
            row[f"ask_{i}_price"] = ""
            row[f"ask_{i}_qty"] = ""

    return header, row


def collect_binance_like(output_dir: Path, exchange: str, pair: str) -> None:
    cfg = EXCHANGE_CONFIG[exchange]
    payload = _request_json(cfg["orderbook"], params={"symbol": pair, "limit": LEVELS})
    depth = _extract_payload_data(payload)
    bids = _normalize_side(depth.get("bids", []))
    asks = _normalize_side(depth.get("asks", []))
    header, row = _normalize_orderbook(exchange, pair, bids, asks)
    _append_row(output_dir / f"orderbook_{exchange}_{pair}.csv", row, header)


def collect_reku(output_dir: Path) -> None:
    cfg = EXCHANGE_CONFIG["reku"]
    for pair in cfg["pairs"]:
        payload = _request_json(cfg["orderbook"], params={"symbol": pair})
        book = _extract_payload_data(payload)
        # Reku v2 uses 'b' for bids and 's' for asks (short for sell/buy?)
        # Let's check keys. Based on debug: {"s":[],"b":[]}
        bids = _normalize_side(book.get("b", []))
        asks = _normalize_side(book.get("s", []))
        header, row = _normalize_orderbook("reku", pair.upper(), bids, asks)
        _append_row(output_dir / f"orderbook_reku_{pair.upper()}.csv", row, header)


def collect_indodax_ticker(output_dir: Path, pair: str) -> None:
    url = EXCHANGE_CONFIG["indodax"]["ticker"].format(pair=pair)
    payload = _request_json(url)
    t = payload.get("ticker", {})
    row = {
        "timestamp_utc": utc_now(),
        "exchange": "indodax",
        "pair": pair.upper(),
        "best_bid": t.get("buy", ""),
        "best_ask": t.get("sell", ""),
        "last_price": t.get("last", ""),
    }
    header = list(row.keys())
    _append_row(output_dir / f"ticker_indodax_{pair.upper()}.csv", row, header)


def log_error(output_dir: Path, exchange: str, pair: str, error: Exception) -> None:
    row = {
        "timestamp_utc": utc_now(),
        "exchange": exchange,
        "pair": pair,
        "error": str(error),
    }
    header = list(row.keys())
    _append_row(output_dir / "collection_errors.csv", row, header)


def collect_once(output_dir: Path) -> None:
    for exchange in ("binance", "tokocrypto"):
        for pair in EXCHANGE_CONFIG[exchange]["pairs"]:
            try:
                collect_binance_like(output_dir, exchange, pair)
            except Exception as exc:  # noqa: BLE001
                logging.error("%s %s failed: %s", exchange, pair, exc)
                log_error(output_dir, exchange, pair, exc)

    try:
        collect_reku(output_dir)
    except Exception as exc:  # noqa: BLE001
        logging.error("reku failed: %s", exc)
        log_error(output_dir, "reku", "orderbookall", exc)

    for pair in EXCHANGE_CONFIG["indodax"]["pairs"]:
        try:
            collect_indodax_ticker(output_dir, pair)
        except Exception as exc:  # noqa: BLE001
            logging.error("indodax %s failed: %s", pair, exc)
            log_error(output_dir, "indodax", pair, exc)


def backfill_klines(output_dir: Path, exchange: str, pair: str, interval: str, limit: int = 1000) -> None:
    cfg = EXCHANGE_CONFIG[exchange]
    raw_payload = _request_json(cfg["klines"], params={"symbol": pair, "interval": interval, "limit": limit})
    payload = raw_payload if isinstance(raw_payload, list) else _extract_payload_data(raw_payload)
    if isinstance(payload, dict) and "list" in payload:
        payload = payload["list"]
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected kline payload type for {exchange} {pair} {interval}")
    header = [
        "open_time_utc",
        "close_time_utc",
        "exchange",
        "pair",
        "interval",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "trade_count",
    ]
    path = output_dir / f"klines_{exchange}_{pair}_{interval}.csv"
    _ensure_csv_header(path, header)
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        for k in payload:
            writer.writerow(
                {
                    "open_time_utc": datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).isoformat(),
                    "close_time_utc": datetime.fromtimestamp(k[6] / 1000, tz=timezone.utc).isoformat(),
                    "exchange": exchange,
                    "pair": pair,
                    "interval": interval,
                    "open": k[1],
                    "high": k[2],
                    "low": k[3],
                    "close": k[4],
                    "volume": k[5],
                    "quote_volume": k[7],
                    "trade_count": k[8],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll exchange orderbooks/tickers into CSV files.")
    parser.add_argument("--output-dir", default="data/raw", help="CSV output directory")
    parser.add_argument("--interval-seconds", type=int, default=60, help="Polling cadence")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--backfill-klines", action="store_true", help="Also fetch historical klines for Binance/Tokocrypto")
    args = parser.parse_args()

    out = Path(args.output_dir)
    setup_logging(out)

    if args.backfill_klines:
        for exchange in ("binance", "tokocrypto"):
            for pair in EXCHANGE_CONFIG[exchange]["pairs"]:
                for interval in ("1m", "5m"):
                    try:
                        backfill_klines(out, exchange, pair, interval)
                        logging.info("backfilled klines: %s %s %s", exchange, pair, interval)
                    except Exception as exc:  # noqa: BLE001
                        logging.error("kline backfill failed: %s %s %s: %s", exchange, pair, interval, exc)
                        log_error(out, exchange, f"{pair}:{interval}", exc)

    if args.once:
        collect_once(out)
        return

    import schedule

    schedule.every(args.interval_seconds).seconds.do(collect_once, output_dir=out)
    logging.info("collector started: interval=%ss output=%s", args.interval_seconds, out)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
