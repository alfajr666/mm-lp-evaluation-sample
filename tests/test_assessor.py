from framework.assessor import LiquidityReadinessAssessor


def test_assessor_mode_1_classification():
    assessor = LiquidityReadinessAssessor()
    result = assessor.assess(
        {
            "time_weighted_avg_spread_pct": 2.5,
            "depth_1pct_usd": 20_000,
            "quote_presence_ratio_pct": 85,
            "spread_resilience_min": 15,
            "daily_volume_to_circulating_supply_pct": 0.05,
        }
    )
    assert result.mode.startswith("Mode 1")
    assert result.score_mode_1 == 5


def test_assessor_mode_3_classification():
    assessor = LiquidityReadinessAssessor()
    result = assessor.assess(
        {
            "time_weighted_avg_spread_pct": 0.3,
            "depth_1pct_usd": 600_000,
            "quote_presence_ratio_pct": 99.2,
            "spread_resilience_min": 1.0,
            "daily_volume_to_circulating_supply_pct": 1.2,
        }
    )
    assert result.mode.startswith("Mode 3")
    assert result.score_mode_3 == 5
