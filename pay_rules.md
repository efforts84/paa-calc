# Pay Rules

Rules used by the projection scripts (`generate_post_increment_payslip.py`,
`generate_promotion_payslip.py`). All formulas are validated against the
Jan / Feb / Mar 2026 PAA payslips for EG-04, basic 179,770.

## Basic pay

- **Annual increment**: advance one stage on the same grade row of
  `PAYSCALE23.csv`.
- **Promotion**: fix at the *lowest stage of the next grade that is
  strictly higher than current basic*, then add **one increment** of the
  new grade.
  - Example: EG-04 179,770 → EG-05 lowest-higher = 184,840 →
    + one EG-05 increment (9,240) = **194,080**.
  - This matches the `next_step_after_promotion` column of
    `promotion_fixation.csv`.

## Earnings (functions of new basic)

| Item                  | Formula                       |
|-----------------------|-------------------------------|
| HOUSE RENT            | 80% × basic                   |
| RATING                | 80% × basic                   |
| UTILITY               | 25% × basic                   |
| MEDICAL               | 25% × basic                   |
| ATCL ALLOWANCE        | 20% × basic                   |
| M/CYCLE MAINT.        | 10% × min(grade) |

## Earnings (fixed / frozen)

- ENTERTAINMENT, CATEGORIZATION ALL.: carried over.
- ADHOC RELIEF-2023 20%, ADHOC RELIEF 2024 30%: frozen amounts; do **not**
  recompute against the new basic.
- FUEL: price-dependent; carried from latest available slip.

## Deductions

| Item                       | Formula / source                                  |
|----------------------------|---------------------------------------------------|
| GP FUND                    | 8% × (min + max) / 2 of the **grade**             |
| GRP INSURANCE              | flat slab — carry over                            |
| BENEVOLENT FUND            | flat slab — carry over                            |
| WELFARE FUND               | flat — 400                                        |
| AL-SHIFA TRUST             | flat — 200                                        |
| ATC GUILD CONTR. FUND      | flat — 1,500                                      |
| INCOME TAX                 | recompute against annual taxable income (out of scope here — carry Jan-2026 baseline) |
| CAR ADVANCE / GPF ADVANCE  | continuing instalments — carry over               |

GP Fund examples:
- EG-04: 8% × (81,730 + 245,130) / 2 = 8% × 163,430 = **13,074**
- EG-05: 8% × (92,440 + 277,240) / 2 = 8% × 184,840 = **14,787**

GP Fund and M/Cycle Maint. are **grade-based**, so they do **not** change
on a normal annual increment within the same grade — only on promotion.
