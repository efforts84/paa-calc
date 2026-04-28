#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

from pypdf import PdfReader


AMOUNT_RE = re.compile(r"^(.*?)(\d{1,3}(?:,\d{3})*\.\d{2})$")


def split_label_amount(line: str):
    match = AMOUNT_RE.match(line)
    if not match:
        return line.strip(), ""
    return match.group(1).strip(), match.group(2).replace(",", "")


def parse_slip(pdf_path: Path):
    text = ""
    for page in PdfReader(str(pdf_path)).pages:
        text += (page.extract_text() or "") + "\n"

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    meta_rows = []
    line_items = []
    summary_rows = []

    month = pdf_path.stem.replace("PaySlip-OF2902-", "")

    i = 0
    while i < len(lines):
        line = lines[i]

        if line == "E . A . R . N . I . N . G . S":
            section = "earning"
            i += 1
            continue
        if line == "D . E . D . U . C . T . I . O . N . S":
            section = "deduction"
            i += 1
            continue
        if line == "M . I . S . C . E . L . L . A . N . E . O . U . S":
            section = "misc"
            i += 1
            continue

        if line.startswith("GROSS EARNINGS "):
            label, amount = split_label_amount(line)
            summary_rows.append(("summary", label, amount))
            i += 1
            continue
        if line.startswith("TOTAL DEDUCTIONS "):
            label, amount = split_label_amount(line)
            summary_rows.append(("summary", label, amount))
            i += 1
            continue
        if line.startswith("NET PAY "):
            label, amount = split_label_amount(line)
            summary_rows.append(("summary", label, amount))
            i += 1
            continue
        if line.startswith("YTD EARN:"):
            summary_rows.append(("summary", "YTD EARN", line.split(":", 1)[1].strip().replace(",", "")))
            i += 1
            continue
        if line.startswith("YTD DED:"):
            summary_rows.append(("summary", "YTD DED", line.split(":", 1)[1].strip().replace(",", "")))
            i += 1
            continue
        if line.startswith("YTD TAX:"):
            summary_rows.append(("summary", "YTD TAX", line.split(":", 1)[1].strip().replace(",", "")))
            i += 1
            continue

        if i == 0 and line.isdigit():
            meta_rows.append(("meta", "page_number", line))
            i += 1
            continue

        # Header metadata comes before the earnings section.
        if "section" not in locals():
            if line == "ATC":
                meta_rows.append(("meta", "department", line))
            elif re.fullmatch(r"\d{5}-\d{7}-\d", line):
                meta_rows.append(("meta", "cnic", line))
            elif line == "SENIOR DEPUTY DIRECTOR":
                meta_rows.append(("meta", "designation", line))
            elif line == "PAKISTAN AIRPORTS AUTHORITY":
                meta_rows.append(("meta", "organization", line))
            elif line == "HEADQUARTERS":
                meta_rows.append(("meta", "location", line))
            elif line == "HABIB BANK LIMITED":
                meta_rows.append(("meta", "bank", line))
            elif line == "J.T.C. BRANCH KARACHI":
                meta_rows.append(("meta", "branch", line))
            elif line == "KARACHI":
                meta_rows.append(("meta", "city", line))
            elif line.startswith("OF2902-"):
                meta_rows.append(("meta", "slip_number", line))
            elif line.startswith("EG-"):
                meta_rows.append(("meta", "grade", line))
            elif line.startswith("A/C #:"):
                meta_rows.append(("meta", "account_number", line.split(":", 1)[1].strip()))
            elif line == "ABDUL MUSAWWER":
                meta_rows.append(("meta", "employee_name", line))
            elif re.fullmatch(r"[A-Z][a-z]{2}-\d{4}", line):
                meta_rows.append(("meta", "month", line))
            elif line == month:
                meta_rows.append(("meta", "month_file", line))
            i += 1
            continue

        if section in {"earning", "deduction"}:
            label, amount = split_label_amount(line)
            if amount:
                line_items.append((section, label, amount))
            i += 1
            continue

        i += 1

    return meta_rows, line_items, summary_rows


def write_csv(rows, output_path: Path):
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "item", "value"])
        writer.writerows(rows)


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: extract_payslip_csv.py INPUT_PDF OUTPUT_CSV")

    pdf_path = Path(argv[1]).resolve()
    csv_path = Path(argv[2]).resolve()
    meta_rows, line_items, summary_rows = parse_slip(pdf_path)
    write_csv(meta_rows + line_items + summary_rows, csv_path)
    print(csv_path)


if __name__ == "__main__":
    main(sys.argv)
