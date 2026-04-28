"""Compute income tax on annual taxable salary per tax_rules.md.

Usage:
    python scripts/calculate_income_tax.py <annual_taxable_income>
    python scripts/calculate_income_tax.py --monthly <monthly_taxable_income>
    python scripts/calculate_income_tax.py --slip <payslip.csv>

The --slip mode sums the earnings rows of a payslip CSV, multiplies by
12 to project annual taxable salary, and reports annual + monthly tax.
"""

import csv
import sys
from pathlib import Path


# (lower_bound, base_tax, rate_on_excess) ordered ascending.
SLABS = [
    (0,         0,        0.00),
    (600_000,   0,        0.01),
    (1_200_000, 6_000,    0.11),
    (2_200_000, 116_000,  0.23),
    (3_200_000, 346_000,  0.30),
    (4_100_000, 616_000,  0.35),
]


def annual_tax(annual_income: float) -> float:
    """Tax payable on a given annual taxable income."""
    if annual_income <= 0:
        return 0.0
    applicable = SLABS[0]
    for slab in SLABS:
        if annual_income > slab[0]:
            applicable = slab
        else:
            break
    lower, base, rate = applicable
    return base + (annual_income - lower) * rate


def slab_label(annual_income: float) -> str:
    bounds = [s[0] for s in SLABS] + [float("inf")]
    for i in range(len(SLABS)):
        if bounds[i] < annual_income <= bounds[i + 1]:
            upper = bounds[i + 1]
            upper_s = "above" if upper == float("inf") else f"{upper:,.0f}"
            return f"{bounds[i]:,.0f} – {upper_s}"
    return "0 – 600,000"


def annual_taxable_from_slip(csv_path: Path) -> float:
    total = 0.0
    with csv_path.open() as f:
        reader = csv.reader(f)
        next(reader)
        for sec, item, value in reader:
            if sec == "earning":
                total += float(value)
    return total * 12


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        sys.exit(2)

    if argv[1] == "--monthly":
        annual = float(argv[2]) * 12
    elif argv[1] == "--slip":
        annual = annual_taxable_from_slip(Path(argv[2]))
    else:
        annual = float(argv[1])

    tax = annual_tax(annual)
    print(f"Annual taxable income : {annual:>15,.2f}")
    print(f"Slab                  : {slab_label(annual)}")
    print(f"Annual tax            : {tax:>15,.2f}")
    print(f"Monthly tax (annual/12): {tax / 12:>15,.2f}")


if __name__ == "__main__":
    main(sys.argv)
