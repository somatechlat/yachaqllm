from datetime import date

import pytest

from rag.app.rule_engine import (
    ComputationResult,
    compute_import_taxes,
    compute_income_tax_liability,
    next_working_day,
)


def test_compute_import_taxes_matches_expected_breakdown():
    result = compute_import_taxes(1000.0, ad_valorem=0.1, fodinfa=0.005, ice=0.02, iva=0.12)
    assert isinstance(result, ComputationResult)
    assert result.base == 1000.0
    assert result.taxes["ad_valorem"] == pytest.approx(100.0)
    assert result.taxes["fodinfa"] == pytest.approx(5.0)
    assert result.taxes["ice"] == pytest.approx(20.0)
    taxable_plus = 1000.0 + 100.0 + 5.0 + 20.0
    assert result.taxes["iva"] == pytest.approx(round(taxable_plus * 0.12, 2))
    assert result.total == pytest.approx(1000.0 + sum(result.taxes.values()))


def test_compute_income_tax_liability_uses_last_matching_bracket():
    brackets = [
        (0.0, 0.0, 0.0),
        (11722.0, 0.15, 0.0),
        (14948.0, 0.20, 484.0),
    ]
    assert compute_income_tax_liability(15000.0, brackets) == pytest.approx(484.0 + (15000.0 - 14948.0) * 0.20)


def test_next_working_day_skips_weekend_and_holidays():
    holidays = [date(2025, 10, 16)]
    start = date(2025, 10, 10)  # Friday
    result = next_working_day(start, holidays=holidays, days=2)
    # Monday 13th counts as day 1, Tuesday 14th as day 2 unless holiday/h weekend
    assert result == date(2025, 10, 14)


def test_negative_input_raises():
    with pytest.raises(ValueError):
        compute_import_taxes(-1.0)
    with pytest.raises(ValueError):
        compute_income_tax_liability(-10.0, [])
    with pytest.raises(ValueError):
        next_working_day(date(2025, 1, 1), days=-1)
