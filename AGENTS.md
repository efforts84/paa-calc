# Repository Guidelines

## Project Structure & Module Organization
This repository is a small payroll utility workspace. Keep reusable code in `scripts/` and keep generated outputs at the repository root when needed.

- `PAYSCALE23.xlsx`: source pay-scale workbook
- `*.pdf`: monthly payslips
- `*.csv`: generated extracts and calculations
- `scripts/`: Python helpers for conversion and extraction

Use clear script names such as `extract_payslip_csv.py` and `generate_promotion_fixation.py`.

## Build, Test, and Development Commands
There is no formal build system. Use the Python scripts directly:

- `python scripts/convert_payscale23.py`: convert `PAYSCALE23.xlsx` to `PAYSCALE23.csv`
- `python scripts/extract_payslip_csv.py <input.pdf> <output.csv>`: extract one payslip into CSV
- `python scripts/generate_promotion_fixation.py`: write `promotion_fixation.csv`
- `python scripts/generate_calculator_html.py`: regenerate `pay_calculator.html` after calculator source changes

If you change the workbook or PDFs, rerun the relevant script and verify the CSV output.

## Coding Style & Naming Conventions
Use Python 3, 4-space indentation, `pathlib.Path`, and standard library modules where possible. Keep scripts short and single-purpose. Prefer descriptive snake_case names for files, functions, and variables.

Examples:

- `parse_slip()`
- `output_path`
- `promotion_fixation.csv`

Keep generated CSV headers stable so downstream comparisons remain simple.

## Testing Guidelines
There is no automated test suite yet. Validate changes by running the script against the source file and inspecting the first rows of the output:

```bash
python scripts/extract_payslip_csv.py PaySlip-OF2902-Jan-2026.pdf jan.csv
sed -n '1,10p' jan.csv
```

For spreadsheet changes, confirm the expected rows and numeric values in the exported CSV.

## Commit & Pull Request Guidelines
No commit history is available in this workspace, so no repository-specific convention is established. Use short, imperative commit messages such as `Add April payslip extractor`.

For pull requests, include:

- a brief summary of what changed
- the input files used
- the generated output files
- any assumptions made in calculations

## Agent Notes
Do not place new executable scripts at the repository root. Keep them in `scripts/` and leave root-level files for source documents and generated deliverables.

When changing the pay calculator, edit `scripts/generate_calculator_html.py` first, then regenerate `pay_calculator.html`. Do not edit only the generated HTML.

Payslip display labels should not show percentage details. Keep percentage formulas in code, but render clean item names such as `Adhoc Relief 2023`, `GP Fund`, `Group Insurance`, and `Benevolent Fund`.

Keep the current `Adhoc Relief 2023` calculator formula as formula-based stage rollback: `Math.round(stageBackBasic(grade, basic, 4) * 0.20)`. Do not replace it with a hard-coded EG-04 amount.

FTP deploy settings live in the local `.env` file. Do not put the FTP password in docs or scripts. The active Hostinger web root for this account is the FTP root (`/`), not the nested `/public_html` directory.

To deploy the calculator, load `.env` in the shell and upload `pay_calculator.html` to all active entry names:

```bash
set -a
. ./.env
set +a
curl --ftp-create-dirs -T pay_calculator.html --user "$FTP_USER:$FTP_PASS" "ftp://$FTP_HOST:$FTP_PORT/index.html"
curl --ftp-create-dirs -T pay_calculator.html --user "$FTP_USER:$FTP_PASS" "ftp://$FTP_HOST:$FTP_PORT/default.php"
curl --ftp-create-dirs -T pay_calculator.html --user "$FTP_USER:$FTP_PASS" "ftp://$FTP_HOST:$FTP_PORT/pay_calculator.html"
```
