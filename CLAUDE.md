# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Payroll utility workspace for a single PAA (Pakistan Airports Authority) employee. Source documents (XLSX pay scale, monthly payslip PDFs) live at the repo root; small single-purpose Python scripts in `scripts/` extract, transform, and project payroll data; CSV outputs (also at the root) are the canonical machine-readable artifacts and the input to downstream calculations.

## Commands

No build system or test suite. Run scripts directly with the system Python (relies on `pypdf`, `openpyxl`, `reportlab`).

```bash
# Convert source pay-scale workbook -> CSV
python scripts/convert_payscale23.py

# Extract one payslip PDF -> CSV (slip section/item/value rows)
python scripts/extract_payslip_csv.py PaySlip-OF2902-Jan-2026.pdf jan.csv

# Regenerate the EG-04 -> EG-05 promotion fixation lookup
python scripts/generate_promotion_fixation.py

# Project a hypothetical post-increment slip from mar.csv + jan.csv baselines
python scripts/generate_post_increment_payslip.py

# Project a hypothetical promotion slip (EG-04 -> EG-05 by default)
python scripts/generate_promotion_payslip.py

# Compute slabbed income tax (annual / monthly / from a payslip CSV)
python scripts/calculate_income_tax.py 9326194
python scripts/calculate_income_tax.py --monthly 777183
python scripts/calculate_income_tax.py --slip may_promotion.csv

# Render any payslip CSV back into a PAA-portal-style PDF
python scripts/render_payslip_pdf.py jul_post_increment.csv PaySlip-OF2902-Jul-2026.pdf
```

Validate any change by re-running the affected script and inspecting the first lines of its CSV/PDF output.

## Architecture

The whole pipeline is CSV-mediated. Every script either produces or consumes a CSV with the schema `section,item,value`, where `section ∈ {meta, earning, deduction, summary, note}`. This keeps scripts independent and composable:

- **PDF → CSV** (`extract_payslip_csv.py`): parses the PAA portal's flat-text PDF layout. Detection is line-based using the section banners `E . A . R . N . I . N . G . S`, `D . E . D . U . C . T . I . O . N . S`, `M . I . S . C . E . L . L . A . N . E . O . U . S`. Header metadata is identified by hard-coded literal matches (`ATC`, `HEADQUARTERS`, `ABDUL MUSAWWER`, etc.) before the first banner appears — adding a new employee or a new label requires updating these matchers.
- **XLSX → CSV** (`convert_payscale23.py`): straight openpyxl dump of `PAYSCALE23.xlsx`. The output (`PAYSCALE23.csv`) has columns `Grade,Min,Increment,Max,1..20` — stage values 1..20 in the trailing columns, which other scripts index into.
- **Projection** (`generate_post_increment_payslip.py`, `generate_promotion_payslip.py`): read `mar.csv` for the latest state and `jan.csv` for a clean (no-austerity) deductions baseline, look up the grade row in `PAYSCALE23.csv`, advance/fix the basic, and recompute earnings and deductions per **`pay_rules.md`** (authoritative source for all formulas: 80%/25%/20% basic-linked allowances, GP FUND = 8% × (min+max)/2 grade-based, M/CYCLE MAINT. = grade increment, promotion = lowest higher stage + one increment, etc.). Adhoc reliefs are frozen amounts. INCOME TAX is recomputed by importing `annual_tax()` from `calculate_income_tax.py` and feeding it `sum(new_earnings) × 12`. FUEL is price-dependent and carried over; both the tax base and the FUEL source are recorded as `note,*` rows in the output.
- **Tax** (`calculate_income_tax.py`, **`tax_rules.md`**): the slab-based annual-tax function is both a CLI (`<annual> | --monthly <m> | --slip <csv>`) and a library imported by the projection scripts. Slabs live in `tax_rules.md`; the SLABS table in the Python file must mirror it.
- **CSV → PDF** (`render_payslip_pdf.py`): reportlab landscape A4, three-column layout (earnings | deductions | misc) with dashed separators mirroring the original portal print. Reads the same `section,item,value` schema; the `summary` row whose `item` starts with `GROSS EARNINGS …` is parsed back out via regex to fill the totals strip.

When changing one stage of the pipeline, prefer keeping the CSV schema stable so the others keep working without modification.

## Conventions

- Per `AGENTS.md`: keep executables in `scripts/`; the repo root is reserved for source documents (XLSX, PDFs) and generated deliverables (CSVs, projected PDFs). Do not put new scripts at the root.
- Python 3, 4-space indent, `pathlib.Path`, standard library + the three packages above. Keep scripts short and single-purpose with descriptive snake_case names (e.g. `extract_payslip_csv.py`, `generate_promotion_fixation.py`).
- Keep generated CSV headers stable — the pipeline relies on them for cross-script comparison and projection.
