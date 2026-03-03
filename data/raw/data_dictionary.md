# Data Dictionary

## Scope
This project stores raw market data in flat CSV files partitioned by `exchange` and `pair`.

## Files
- `orderbook_<exchange>_<pair>.csv`: one row per snapshot (60s cadence target)
- `ticker_<exchange>_<pair>.csv`: top-of-book ticker rows for ticker-only endpoints
- `klines_<exchange>_<pair>_<interval>.csv`: OHLCV history
- `collection_errors.csv`: polling errors with timestamp and endpoint context

## Orderbook Schema
- `timestamp_utc`: ISO-8601 UTC timestamp at collection time
- `exchange`: exchange id (`binance`, `tokocrypto`, `reku`, `indodax`)
- `pair`: symbol/pair key (`BTCUSDT`, `BTCIDR`, `USDTIDR`)
- `mid_price`: midpoint from best bid/ask
- `best_bid`, `best_ask`: top-of-book prices
- `bid_{n}_price`, `bid_{n}_qty`: nth bid level, up to 20
- `ask_{n}_price`, `ask_{n}_qty`: nth ask level, up to 20

## Ticker Schema
- `timestamp_utc`
- `exchange`
- `pair`
- `best_bid`
- `best_ask`
- `last_price`

## Klines Schema
- `open_time_utc`, `close_time_utc`
- `exchange`, `pair`, `interval`
- `open`, `high`, `low`, `close`, `volume`
- `quote_volume`, `trade_count`

## Known Limitations
- Indodax depth is not publicly accessible in this design; ticker is used as proxy.
- Reku is focused on IDR-denominated pairs; cross-exchange normalization is required.
- Endpoint stability may vary and can require adapter updates.
