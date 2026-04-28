# Income Tax Rules

Slab structure used by `scripts/calculate_income_tax.py`. Slabs apply
to **annual taxable salary income** (Pakistan, salaried-individual rates).

| Annual taxable income (Rs.)        | Tax payable                                           |
|------------------------------------|-------------------------------------------------------|
| Up to 600,000                      | 0%                                                    |
| 600,001 – 1,200,000                | 1% of the amount exceeding 600,000                    |
| 1,200,001 – 2,200,000              | 6,000 + 11% of the amount exceeding 1,200,000         |
| 2,200,001 – 3,200,000              | 116,000 + 23% of the amount exceeding 2,200,000       |
| 3,200,001 – 4,100,000              | 346,000 + 30% of the amount exceeding 3,200,000       |
| Above 4,100,000                    | 616,000 + 35% of the amount exceeding 4,100,000       |

## Worked example

Annual taxable salary = 9,326,194:
- Falls in the top slab.
- Tax = 616,000 + 35% × (9,326,194 − 4,100,000)
- Tax = 616,000 + 35% × 5,226,194
- Tax = 616,000 + 1,829,168 ≈ **2,445,168 / yr**  (≈ **203,764 / month**)
- Matches the INCOME TAX line on the Jan-2026 payslip.

## Notes

- This script computes **annual tax on a given annual taxable income**.
  Monthly tax in payroll is normally the annual tax / 12, with mid-year
  adjustments folded into the next month's deduction (out of scope).
- Adhoc reliefs and most allowances are treated as taxable salary unless
  otherwise specified.
