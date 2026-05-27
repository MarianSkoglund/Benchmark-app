from src.recommendations import get_recommendation


def test_get_recommendation_uses_consulting_specific_recommendation():
    recommendation = get_recommendation(
        metric="utilization",
        status="Below market",
        industry="Consulting",
    )

    assert "resource planning" in recommendation


def test_get_recommendation_falls_back_to_generic_metric_recommendation():
    recommendation = get_recommendation(
        metric="growth",
        status="Leading",
        industry="Retail",
    )

    assert "predictive growth models" in recommendation
