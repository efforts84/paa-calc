"""Render a payslip CSV (as produced by extract_payslip_csv.py or
generate_post_increment_payslip.py) into a PDF that mirrors the
PAA payroll-portal layout (Jan-2026 reference).

Usage:
    python scripts/render_payslip_pdf.py <input.csv> <output.pdf>
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


PAGE = landscape(A4)  # 297 x 210 mm
PAGE_W, PAGE_H = PAGE


def display_item_name(name: str) -> str:
    name = re.sub(r"\s*\([^)]*%[^)]*\)", "", name)
    name = re.sub(r"\s+\d+(?:\.\d+)?%", "", name)
    return name.strip()


def load_csv(path: Path):
    meta: dict[str, str] = {}
    earnings: list[tuple[str, float]] = []
    deductions: list[tuple[str, float]] = []
    summary: dict[str, str] = {}
    summary_line: tuple[str, str] | None = None
    with path.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            sec, item, value = row[0], row[1], row[2]
            if sec == "meta":
                meta[item] = value
            elif sec == "earning":
                earnings.append((display_item_name(item), float(value)))
            elif sec == "deduction":
                deductions.append((display_item_name(item), float(value)))
            elif sec == "summary":
                if item.startswith("GROSS EARNINGS"):
                    summary_line = (item, value)
                else:
                    summary[item] = value
    return meta, earnings, deductions, summary, summary_line


def fmt_money(v: float) -> str:
    return f"{v:,.2f}"


def parse_summary_line(line: str, net: str) -> tuple[str, str, str]:
    """Parse 'GROSS EARNINGS 762,278.00 TOTAL DEDUCTIONS 286,457.00 NET PAY' + net."""
    import re
    m = re.match(r"GROSS EARNINGS ([\d,\.]+) TOTAL DEDUCTIONS ([\d,\.]+) NET PAY", line)
    if not m:
        return "0.00", "0.00", net
    return m.group(1), m.group(2), f"{float(net):,.2f}"


def dashed_line(c: canvas.Canvas, x1: float, x2: float, y: float) -> None:
    c.setDash(1, 1)
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)
    c.setDash()


def draw_payslip(c: canvas.Canvas, csv_path: Path) -> None:
    meta, earnings, deductions, summary, summary_line = load_csv(csv_path)

    # ---- top header band (small, like a browser print header) ----
    now = datetime.now()
    header_left = now.strftime("%d/%m/%Y, %H:%M")
    month = meta.get("month", "")
    title = f"PaySlip-OF2902-{month}"
    c.setFont("Helvetica", 7)
    c.drawString(10 * mm, PAGE_H - 8 * mm, header_left)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 8 * mm, title)

    # PAA logo placeholder
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10 * mm, PAGE_H - 18 * mm, "PAA")
    c.setFont("Helvetica", 6)
    c.drawString(10 * mm, PAGE_H - 21 * mm, "Pakistan Airports Authority")

    # ---- top dashed separator ----
    top_y = PAGE_H - 25 * mm
    dashed_line(c, 10 * mm, PAGE_W - 10 * mm, top_y)

    # ---- meta block: 4 columns ----
    col1_x = 10 * mm
    col2_x = 70 * mm
    col3_x = 140 * mm
    col4_x = 215 * mm
    right_x = PAGE_W - 10 * mm

    row_y = top_y - 5 * mm
    line_h = 4 * mm

    # Row 1
    c.setFont("Helvetica-Bold", 8)
    c.drawString(col1_x, row_y, str(meta.get("page_number", "1")))
    c.drawString(col2_x, row_y, meta.get("cnic", ""))
    c.drawCentredString((col3_x + col4_x) / 2, row_y, meta.get("organization", ""))
    c.drawString(col4_x, row_y, meta.get("bank", ""))
    c.drawRightString(right_x, row_y, month)

    # Row 2
    row_y -= line_h
    c.drawString(col1_x, row_y, meta.get("slip_number", ""))
    c.drawString(col2_x, row_y, meta.get("employee_name", ""))
    c.drawCentredString((col3_x + col4_x) / 2, row_y, meta.get("location", ""))
    c.drawString(col4_x, row_y, meta.get("branch", ""))
    c.drawRightString(right_x, row_y, f"A/C #:{meta.get('account_number', '')}")

    # Row 3
    row_y -= line_h
    c.drawString(col1_x, row_y, meta.get("department", ""))
    c.drawString(col2_x, row_y, meta.get("designation", ""))
    c.drawCentredString((col3_x + col4_x) / 2, row_y, meta.get("grade", ""))
    c.drawString(col4_x, row_y, meta.get("city", ""))

    # ---- separator below meta ----
    sep_y = row_y - 4 * mm
    dashed_line(c, 10 * mm, PAGE_W - 10 * mm, sep_y)

    # ---- column headers ----
    earn_x = 15 * mm
    earn_amt_x = 110 * mm
    ded_x = 120 * mm
    ded_amt_x = 200 * mm
    misc_x = 210 * mm
    misc_amt_x = PAGE_W - 12 * mm

    hdr_y = sep_y - 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString((earn_x + earn_amt_x) / 2, hdr_y, "E . A . R . N . I . N . G . S")
    c.drawCentredString((ded_x + ded_amt_x) / 2, hdr_y, "D . E . D . U . C . T . I . O . N . S")
    c.drawCentredString((misc_x + misc_amt_x) / 2, hdr_y, "M . I . S . C . E . L . L . A . N . E . O . U . S")

    # vertical separators (dashed)
    body_top = hdr_y - 3 * mm
    body_bottom = 35 * mm
    for vx in (115 * mm, 205 * mm):
        c.setDash(1, 1)
        c.setLineWidth(0.4)
        c.line(vx, body_top, vx, body_bottom)
        c.setDash()

    # ---- earnings column ----
    item_y = body_top - 4 * mm
    c.setFont("Helvetica-Bold", 8)
    for name, amt in earnings:
        c.drawString(earn_x, item_y, name)
        c.drawRightString(earn_amt_x, item_y, fmt_money(amt))
        item_y -= line_h

    # ---- deductions column ----
    item_y = body_top - 4 * mm
    for name, amt in deductions:
        c.drawString(ded_x, item_y, name)
        c.drawRightString(ded_amt_x, item_y, fmt_money(amt))
        item_y -= line_h

    # ---- misc column: N.T.NO + YTD ----
    misc_y = body_top - 4 * mm
    c.drawString(misc_x, misc_y, "N.T.NO:")

    # YTD block lower
    ytd_y = body_bottom + 14 * mm
    for key in ("YTD EARN", "YTD DED", "YTD TAX"):
        val = summary.get(key, "")
        c.drawString(misc_x, ytd_y, f"{key}:")
        if val:
            c.drawRightString(misc_amt_x, ytd_y, f"{float(val):,.2f}")
        ytd_y -= line_h

    # ---- bottom dashed line + totals ----
    dashed_line(c, 10 * mm, PAGE_W - 10 * mm, body_bottom)

    if summary_line is not None:
        gross, total_ded, net = parse_summary_line(summary_line[0], summary_line[1])
    else:
        gross, total_ded, net = "0.00", "0.00", "0.00"

    tot_y = body_bottom - 6 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(earn_x, tot_y, "GROSS EARNINGS")
    c.drawRightString(earn_amt_x, tot_y, gross)
    c.drawString(ded_x, tot_y, "TOTAL DEDUCTIONS")
    c.drawRightString(ded_amt_x, tot_y, total_ded)
    c.drawString(misc_x, tot_y, "NET PAY")
    c.drawRightString(misc_amt_x, tot_y, net)

    dashed_line(c, 10 * mm, PAGE_W - 10 * mm, tot_y - 3 * mm)

    # ---- footer disclaimer ----
    foot_y = tot_y - 9 * mm
    c.setFont("Helvetica-Bold", 7)
    c.drawString(10 * mm, foot_y,
                 "Excess or Less payment of Arrears is subject to Adjustment in the subsequent months.")
    c.drawRightString(PAGE_W - 10 * mm, foot_y,
                      f"USER ID: OF2902   {now.strftime('%d-%b-%Y %I:%M %p')}   Prepared by Payroll Section")

    # ---- bottom URL/page footer ----
    c.setFont("Helvetica", 7)
    c.drawString(10 * mm, 6 * mm, "10.10.10.84:1005/Portals/Payslipprint.aspx")
    c.drawRightString(PAGE_W - 10 * mm, 6 * mm, "1/1")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    csv_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2])
    c = canvas.Canvas(str(pdf_path), pagesize=PAGE)
    draw_payslip(c, csv_path)
    c.showPage()
    c.save()
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
