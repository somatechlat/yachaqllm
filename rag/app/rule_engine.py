"""Deterministic financial and administrative rules for Ecuador."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple


@dataclass
class ComputationResult:
    base: float
    taxes: Dict[str, float]
    total: float


def round2(value: float) -> float:
    return round(value, 2)


def compute_import_taxes(
    cif: float,
    ad_valorem: float = 0.1,
    fodinfa: float = 0.005,
    ice: float = 0.0,
    iva: float = 0.12,
) -> ComputationResult:
    """Compute Ecuadorian import taxes with standard rates."""
    if cif < 0:
        raise ValueError("CIF must be non-negative")

    base = cif
    ad_valorem_tax = base * ad_valorem
    fodinfa_tax = base * fodinfa
    ice_tax = base * ice
    taxable_base = base + ad_valorem_tax + fodinfa_tax + ice_tax
    iva_tax = taxable_base * iva

    taxes = {
        "ad_valorem": round2(ad_valorem_tax),
        "fodinfa": round2(fodinfa_tax),
        "ice": round2(ice_tax),
        "iva": round2(iva_tax),
    }
    total = round2(base + sum(taxes.values()))
    return ComputationResult(base=round2(base), taxes=taxes, total=total)


def compute_income_tax_liability(amount: float, brackets: Iterable[Tuple[float, float, float]]) -> float:
    """Return income tax liability using Ecuadorian-style bracket tuples.

    Each bracket is a tuple (lower_limit, rate, fixed_fee).
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")

    liability = 0.0
    for lower, rate, fixed_fee in brackets:
        if amount >= lower:
            liability = fixed_fee + (amount - lower) * rate
        else:
            break
    return round2(max(liability, 0.0))


def next_working_day(start: date, holidays: List[date] | None = None, days: int = 5) -> date:
    """Return the next working day after adding `days` business days."""
    if days < 0:
        raise ValueError("days must be non-negative")

    holidays = set(holidays or [])
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() >= 5 or current in holidays:
            continue
        added += 1
    return current
