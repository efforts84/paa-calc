"""Generate a hypothetical post-increment July payslip CSV.

Starts from the most recent extracted payslip (mar.csv), advances the
basic pay one stage on PAYSCALE23 (EG-04), recomputes basic-linked
allowances per pay_rules.md, and writes jul_post_increment.csv.

GP FUND and M/CYCLE MAINT. are grade-based (see pay_rules.md), so they
do NOT change on a within-grade increment. Other slab/flat deductions
are carried from the Jan-2026 baseline. INCOME TAX is recomputed from
tax_rules.md by annualising the projected monthly earnings. FUEL is
price-dependent and carried from the latest slip.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYSCALE = ROOT / "PAYSCALE23.csv"
SOURCE_SLIP = ROOT / "mar.csv"
OUTPUT = ROOT / "jul_post_increment.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calculate_income_tax import annual_tax  # noqa: E402


def load_grade_row(grade: str) -> dict:
    with PAYSCALE.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == grade:
                return {
                    "min": int(row[1]),
                    "increment": int(row[2]),
                    "max": int(row[3]),
                    "stages": [int(v) for v in row[4:]],
                }
    raise ValueError(f"Grade {grade} not found in {PAYSCALE}")


def next_stage(stages: list[int], current: int) -> int:
    idx = stages.index(current)
    return stages[idx + 1]


def load_slip(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    with path.open() as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            rows.append((row[0], row[1], row[2]))
    return rows


def main() -> None:
    base_rows = load_slip(SOURCE_SLIP)
    # Look up basic pay and grade
    meta = {item: value for sec, item, value in base_rows if sec == "meta"}
    earnings = {item: float(value) for sec, item, value in base_rows if sec == "earning"}

    grade_field = meta["grade"].split()[0]  # "EG-04"
    grade = load_grade_row(grade_field)
    current_basic = int(earnings["BASIC PAY"])
    new_basic = next_stage(grade["stages"], current_basic)

    # Recompute per pay_rules.md
    new_earnings = {
        "BASIC PAY": new_basic,
        "HOUSE RENT": round(new_basic * 0.80),
        "M/CYCLE MAINT.": round(grade["min"] * 0.10),
        "FUEL": int(earnings["FUEL"]),  # carried from Mar-2026
        "ENTERTAINMENT": int(earnings["ENTERTAINMENT"]),
        "UTILITY": round(new_basic * 0.25),
        "MEDICAL": round(new_basic * 0.25),
        "RATING": round(new_basic * 0.80),
        "ATCL ALLOWANCE": round(new_basic * 0.20),
        "CATEGORIZATION ALL.": int(earnings["CATEGORIZATION ALL."]),
        "ADHOC RELIEF-2023 20%": int(earnings["ADHOC RELIEF-2023 20%"]),
        "ADHOC RELIEF 2024 30%": int(earnings["ADHOC RELIEF 2024 30%"]),
    }

    # Deductions: Jan-2026 baseline (no Mar austerity adj). GP FUND is
    # grade-based per pay_rules.md so unchanged on a within-grade increment.
    jan_path = ROOT / "jan.csv"
    jan_rows = load_slip(jan_path)
    jan_deductions = {item: float(value) for sec, item, value in jan_rows if sec == "deduction"}

    annual_taxable = sum(new_earnings.values()) * 12
    monthly_tax = round(annual_tax(annual_taxable) / 12)

    new_deductions = {
        "GP FUND": round(0.08 * (grade["min"] + grade["max"]) / 2),
        "GRP INSURANCE": int(jan_deductions["GRP INSURANCE"]),
        "BENEVOLENT FUND": int(jan_deductions["BENEVOLENT FUND"]),
        "WELFARE FUND": int(jan_deductions["WELFARE FUND"]),
        "AL-SHIFA TRUST": int(jan_deductions["AL-SHIFA TRUST"]),
        "ATC GUILD CONTR. FUND": int(jan_deductions["ATC GUILD CONTR. FUND"]),
        "INCOME TAX": monthly_tax,
        "CAR ADVANCE": int(jan_deductions["CAR ADVANCE"]),
        "GPF ADVANCE": int(jan_deductions["GPF ADVANCE"]),
    }

    gross = sum(new_earnings.values())
    total_ded = sum(new_deductions.values())
    net = gross - total_ded

    # Write output
    with OUTPUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "item", "value"])
        # meta - copy with month change
        for sec, item, value in base_rows:
            if sec == "meta":
                if item == "month":
                    w.writerow([sec, item, "Jul-2026"])
                else:
                    w.writerow([sec, item, value])
        for item, val in new_earnings.items():
            w.writerow(["earning", item, f"{val:.2f}"])
        for item, val in new_deductions.items():
            w.writerow(["deduction", item, f"{val:.2f}"])
        w.writerow(["summary", "YTD EARN", ""])
        w.writerow(["summary", "YTD DED", ""])
        w.writerow(["summary", "YTD TAX", ""])
        w.writerow([
            "summary",
            f"GROSS EARNINGS {gross:,.2f} TOTAL DEDUCTIONS {total_ded:,.2f} NET PAY",
            f"{net:.2f}",
        ])
        w.writerow(["note", "basic_stage_change", f"{current_basic} -> {new_basic}"])
        w.writerow(["note", "fuel_source", "carried from Mar-2026 (price-dependent)"])
        w.writerow([
            "note",
            "income_tax_source",
            f"slab calc on annualised earnings {annual_taxable:,.0f}",
        ])

    print(f"Wrote {OUTPUT}")
    print(f"  Basic: {current_basic} -> {new_basic}")
    print(f"  Gross: {gross:,.2f}  Deductions: {total_ded:,.2f}  Net: {net:,.2f}")


if __name__ == "__main__":
    main()
