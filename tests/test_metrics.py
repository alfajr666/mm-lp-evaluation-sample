import math

import pandas as pd

from framework.metrics import compute_depth_profile, quote_presence_ratio, time_weighted_avg_spread


def test_quote_presence_ratio():
    df = pd.DataFrame(
        [
            {"best_bid": 100, "best_ask": 101},
            {"best_bid": 0, "best_ask": 101},
            {"best_bid": 100, "best_ask": 99},
            {"best_bid": 100, "best_ask": 102},
        ]
    )
    assert quote_presence_ratio(df) == 50.0


def test_twas_equal_intervals_simple_mean():
    df = pd.DataFrame(
        [
            {"timestamp_utc": "2026-03-01T00:00:00Z", "best_bid": 100, "best_ask": 101},
            {"timestamp_utc": "2026-03-01T00:01:00Z", "best_bid": 100, "best_ask": 102},
        ]
    )
    # spreads are ~0.9950% and ~1.9802%; with equal interval should average directly
    twas = time_weighted_avg_spread(df)
    assert round(twas, 4) == round((0.9950248756 + 1.9801980198) / 2, 4)


def test_depth_profile_respects_side_of_book():
    df = pd.DataFrame(
        [
            {
                "timestamp_utc": "2026-03-01T00:00:00Z",
                "exchange": "x",
                "pair": "BTCUSDT",
                "best_bid": 99.0,
                "best_ask": 101.0,
                "bid_1_price": 99.5,
                "bid_1_qty": 1.0,
                "ask_1_price": 100.5,
                "ask_1_qty": 1.0,
                # invalid crossed levels that should be ignored by side filter
                "bid_2_price": 100.2,
                "bid_2_qty": 10.0,
                "ask_2_price": 99.8,
                "ask_2_qty": 10.0,
            }
        ]
    )
    depth = compute_depth_profile(df, thresholds=(1.0,))
    bid = depth.loc[0, "bid_depth_1.0pct_notional"]
    ask = depth.loc[0, "ask_depth_1.0pct_notional"]
    assert math.isclose(bid, 99.5, rel_tol=1e-9)
    assert math.isclose(ask, 100.5, rel_tol=1e-9)
