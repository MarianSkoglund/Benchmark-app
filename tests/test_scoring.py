import pytest

from src.scoring import compare_to_benchmark, score_value


def test_score_value_below_market_when_value_is_below_p25():
    assert score_value(user_value=9, p25=10, p50=20, p75=30) == "Below market"


def test_score_value_emerging_from_p25_to_below_p50():
    assert score_value(user_value=10, p25=10, p50=20, p75=30) == "Emerging"
    assert score_value(user_value=19.99, p25=10, p50=20, p75=30) == "Emerging"


def test_score_value_competitive_from_p50_to_below_p75():
    assert score_value(user_value=20, p25=10, p50=20, p75=30) == "Competitive"
    assert score_value(user_value=29.99, p25=10, p50=20, p75=30) == "Competitive"


def test_score_value_leading_at_or_above_p75():
    assert score_value(user_value=30, p25=10, p50=20, p75=30) == "Leading"
    assert score_value(user_value=40, p25=10, p50=20, p75=30) == "Leading"


def test_score_value_rejects_invalid_percentile_order():
    with pytest.raises(ValueError, match="p25 <= p50 <= p75"):
        score_value(user_value=20, p25=30, p50=20, p75=10)


def test_compare_to_benchmark_returns_expected_fields():
    benchmark = {"p25": 10, "p50": 20, "p75": 30}

    result = compare_to_benchmark(user_value=25, benchmark=benchmark)

    assert result == {
        "user_value": 25.0,
        "market_median": 20.0,
        "top_quartile": 30.0,
        "status": "Competitive",
    }
