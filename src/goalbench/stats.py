"""Small, dependency-free statistics: Wilson interval, exact McNemar test, percentiles."""

from __future__ import annotations

import math


def wilson(hits: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (95% by default)."""
    if n == 0:
        return (0.0, 1.0)
    p = hits / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(only_first: int, only_second: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pairs (binomial, p = 0.5)."""
    n = only_first + only_second
    if n == 0:
        return 1.0
    k = min(only_first, only_second)
    tail = math.fsum(math.comb(n, i) for i in range(k + 1)) / float(1 << n)
    return min(1.0, 2 * tail)


def percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile: the ceil(q * n)-th smallest value (1-based)."""
    if not values:
        return float("nan")
    ordered = sorted(values)
    rank = max(1, math.ceil(q * len(ordered)))
    return ordered[rank - 1]
