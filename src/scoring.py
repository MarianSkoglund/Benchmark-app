from collections.abc import Mapping
from typing import Any


SCORE_ORDER = ["Below market", "Emerging", "Competitive", "Leading"]


def score_value(user_value: float, p25: float, p50: float, p75: float) -> str:
    """Score a user value against benchmark percentile thresholds.

    The MVP assumes higher values are better for all included metrics.
    """
    user_value = float(user_value)
    p25 = float(p25)
    p50 = float(p50)
    p75 = float(p75)

    if not p25 <= p50 <= p75:
        raise ValueError("Benchmark percentiles must follow p25 <= p50 <= p75.")

    if user_value < p25:
        return "Below market"
    if user_value < p50:
        return "Emerging"
    if user_value < p75:
        return "Competitive"
    return "Leading"


def compare_to_benchmark(user_value: float, benchmark: Mapping[str, Any]) -> dict[str, float | str]:
    """Return the display-ready benchmark comparison fields for one metric."""
    status = score_value(
        user_value=user_value,
        p25=benchmark["p25"],
        p50=benchmark["p50"],
        p75=benchmark["p75"],
    )

    return {
        "user_value": float(user_value),
        "market_median": float(benchmark["p50"]),
        "top_quartile": float(benchmark["p75"]),
        "status": status,
    }
