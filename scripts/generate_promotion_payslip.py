"""Generate a hypothetical promotion payslip CSV (May-2026 by default).

Applies the promotion rule from pay_rules.md: fix at the lowest stage
of the next grade strictly higher than current basic, then add one
increment of the new grade. Recomputes basic-linked earnings and
grade-based deductions per pay_rules.md.

Promotion-fixation reference values are also tabulated in
promotion_fixation.csv (next_step_after_promotion column).
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYSCALE = ROOT / "PAYSCALE23.csv"
PROMOTION = ROOT / "promotion_fixation.csv"
LATEST_SLIP = ROOT / "mar.csv"
JAN_SLIP = ROOT / "jan.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calculate_income_tax import annual_tax  # noqa: E402

MONTH = "May-2026"
NEW_DESIGNATION = "DIRECTOR"  # assumed for EG-05; update if different
OUTPUT = ROOT / f"{MONTH.split('-')[0].lower()}_promotion.csv"


def load_slip(path: Path) -> list[tuple[str, str, str]]:
    with path.open() as f:
        reader = csv.reader(f)
        next(reader)
        return [(row[0], row[1], row[2]) for row in reader]


def load_promotion() -> dict[str, str]:
    with PROMOTION.open() as f:
        reader = csv.DictReader(f)
        return next(reader)


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
    raise ValueError(grade)


def main() -> None:
    promo = load_promotion()
    new_grade = promo["promoted_grade"]
    new_grade_row = load_grade_row(new_grade)
    # Promotion rule: lowest higher stage + one increment of the new grade.
    new_basic = int(promo["lowest_higher_stage"]) + new_grade_row["increment"]
    # Sanity-check against the precomputed value.
    assert new_basic == int(promo["next_step_after_promotion"]), (
        f"promotion-rule basic {new_basic} != next_step_after_promotion "
        f"{promo['next_step_after_promotion']}"
    )

    base_rows = load_slip(LATEST_SLIP)
    meta = {item: value for sec, item, value in base_rows if sec == "meta"}
    earnings = {item: float(value) for sec, item, value in base_rows if sec == "earning"}

    new_earnings = {
        "BASIC PAY": new_basic,
        "HOUSE RENT": round(new_basic * 0.80),
        "M/CYCLE MAINT.": round(new_grade_row["min"] * 0.10),
        "FUEL": int(earnings["FUEL"]),  # price-dependent; carried
        "ENTERTAINMENT": int(earnings["ENTERTAINMENT"]),
        "UTILITY": round(new_basic * 0.25),
        "MEDICAL": round(new_basic * 0.25),
        "RATING": round(new_basic * 0.80),
        "ATCL ALLOWANCE": round(new_basic * 0.20),
        "CATEGORIZATION ALL.": int(earnings["CATEGORIZATION ALL."]),
        "ADHOC RELIEF-2023 20%": int(earnings["ADHOC RELIEF-2023 20%"]),
        "ADHOC RELIEF 2024 30%": int(earnings["ADHOC RELIEF 2024 30%"]),
    }

    jan_deductions = {item: float(value) for sec, item, value in load_slip(JAN_SLIP)
                      if sec == "deduction"}
    current_basic = int(earnings["BASIC PAY"])
    annual_taxable = sum(new_earnings.values()) * 12
    monthly_tax = round(annual_tax(annual_taxable) / 12)

    new_deductions = {
        "GP FUND": round(0.08 * (new_grade_row["min"] + new_grade_row["max"]) / 2),
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

    # Update grade/designation in meta
    grade_suffix = meta["grade"].split(maxsplit=1)[1] if " " in meta["grade"] else ""
    new_grade_field = f"{new_grade} {grade_suffix}".strip()

    with OUTPUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "item", "value"])
        for sec, item, value in base_rows:
            if sec != "meta":
                continue
            if item == "month":
                w.writerow([sec, item, MONTH])
            elif item == "grade":
                w.writerow([sec, item, new_grade_field])
            elif item == "designation":
                w.writerow([sec, item, NEW_DESIGNATION])
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
        w.writerow(["note", "promotion", f"{promo['current_grade']} -> {new_grade}"])
        w.writerow(["note", "basic_fixation",
                    f"{current_basic} -> {new_basic} "
                    f"(lowest higher stage {promo['lowest_higher_stage']} "
                    f"+ 1 increment {new_grade_row['increment']})"])
        w.writerow(["note", "designation_assumed", NEW_DESIGNATION])
        w.writerow(["note", "fuel_source", "carried from Mar-2026 (price-dependent)"])
        w.writerow([
            "note",
            "income_tax_source",
            f"slab calc on annualised earnings {annual_taxable:,.0f}",
        ])

    print(f"Wrote {OUTPUT}")
    print(f"  Grade: {promo['current_grade']} -> {new_grade}")
    print(f"  Basic: {current_basic} -> {new_basic}")
    print(f"  Gross: {gross:,.2f}  Deductions: {total_ded:,.2f}  Net: {net:,.2f}")


if __name__ == "__main__":
    main()
