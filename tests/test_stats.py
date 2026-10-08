from __future__ import annotations

import pytest

from goalbench.stats import mcnemar_exact, percentile, wilson


def test_wilson_matches_reference_values() -> None:
    # Computed by hand: p = 127/150, z = 1.96 -> centre 0.83803, half-width 0.05759.
    low, high = wilson(127, 150)
    assert low == pytest.approx(0.78044, abs=1e-4)
    assert high == pytest.approx(0.89562, abs=1e-4)


def test_wilson_edges_stay_inside_unit_interval() -> None:
    assert wilson(0, 10)[0] == pytest.approx(0.0)
    assert wilson(10, 10)[1] == pytest.approx(1.0)
    assert wilson(0, 0) == (0.0, 1.0)


def test_mcnemar_exact() -> None:
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(0, 6) == pytest.approx(2 / 64)
    assert mcnemar_exact(5, 5) == 1.0
    assert mcnemar_exact(3, 10) == mcnemar_exact(10, 3)


def test_percentile_nearest_rank() -> None:
    values = [float(v) for v in range(1, 151)]
    assert percentile(values, 0.95) == 143.0
    assert percentile(values, 0.5) == 75.0
    assert percentile([7.0], 0.95) == 7.0
