#!/usr/bin/env python3
"""Generate pay_calculator.html from PAYSCALE23.csv."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_payscale() -> dict:
    result = {}
    with (ROOT / "PAYSCALE23.csv").open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row or not row[0].strip():
                continue
            result[row[0]] = {
                "min": int(row[1]),
                "increment": int(row[2]),
                "max": int(row[3]),
                "stages": [int(v) for v in row[4:] if v.strip()],
            }
    return result


def main() -> None:
    html = (
        _HTML_TEMPLATE
        .replace("__PAYSCALE__", json.dumps(load_payscale()))
    )
    out = ROOT / "pay_calculator.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PAA Pay Calculator</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --ink: #172033;
  --muted: #667085;
  --line: #d9e1ec;
  --paper: #ffffff;
  --wash: #f3f6fa;
  --brand: #0d3f67;
  --brand-2: #176b75;
  --accent: #9b6a1b;
}
body {
  background: var(--wash);
  color: var(--ink);
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}
header {
  background: #0d3f67;
  color: #fff;
  padding: 1rem 1.2rem;
  border-bottom: 4px solid #176b75;
}
header h1 { font-size: 1.25rem; line-height: 1.25; }
header .sub { font-size: 0.78rem; line-height: 1.35; opacity: 0.78; margin-top: 0.22rem; overflow-wrap: anywhere; }
header .note { color: #dcebf4; font-size: 0.72rem; line-height: 1.35; margin-top: 0.35rem; max-width: 920px; opacity: 0.9; overflow-wrap: anywhere; }
.container { max-width: 1180px; margin: 1.1rem auto 2rem; overflow-x: hidden; padding: 0 0.9rem; }
.band {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin-bottom: 1rem;
  max-width: 100%;
  overflow-x: hidden;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(23, 32, 51, 0.06);
}
.band-title {
  align-items: center;
  border-bottom: 1px solid var(--line);
  color: var(--brand);
  display: flex;
  font-size: 0.78rem;
  font-weight: 800;
  justify-content: space-between;
  letter-spacing: 0.07em;
  margin-bottom: 0.85rem;
  padding-bottom: 0.48rem;
  text-transform: uppercase;
}
.grid { display: grid; gap: 0.8rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.field { display: flex; flex-direction: column; gap: 0.28rem; min-width: 0; }
.field label {
  color: #475467;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
input, select {
  background: #fbfcfe;
  border: 1.5px solid #cbd5e1;
  border-radius: 5px;
  color: var(--ink);
  font-size: 1rem;
  min-height: 2.5rem;
  min-width: 0;
  outline: none;
  padding: 0.42rem 0.58rem;
  width: 100%;
  max-width: 100%;
}
input:focus, select:focus { border-color: var(--brand-2); background: #fff; }
.hint { color: var(--muted); display: block; font-size: 0.7rem; line-height: 1.35; max-width: 100%; overflow-wrap: anywhere; }
.toolbar { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 0.85rem; }
.btn {
  background: var(--brand);
  border: 0;
  border-radius: 5px;
  color: #fff;
  cursor: pointer;
  font-size: 0.86rem;
  font-weight: 800;
  min-height: 2.55rem;
  padding: 0.45rem 0.85rem;
}
.btn.secondary { background: #eef4f8; border: 1px solid #c7d6e2; color: var(--brand); }
.btn.warn { background: #7f1d1d; }
.mode-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  border: 2px solid var(--brand);
  border-radius: 8px;
  margin-bottom: 0.8rem;
  overflow: hidden;
  width: min(620px, 100%);
}
.mode-btn {
  background: #fff;
  border: 0;
  color: var(--brand);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: 0.01em;
  min-height: 3.25rem;
  padding: 0.65rem 0.9rem;
}
.mode-btn + .mode-btn { border-left: 2px solid var(--brand); }
.mode-btn.active { background: var(--brand); box-shadow: inset 0 -4px 0 rgba(255,255,255,0.22); color: #fff; }
.mode-btn:not(.active):hover { background: #eef4f8; }
.allowance-editor { display: grid; gap: 0.65rem; }
.allowance-row {
  align-items: end;
  display: grid;
  gap: 0.65rem;
  grid-template-columns: minmax(180px, 1.4fr) minmax(120px, 0.7fr) auto;
  min-width: 0;
}
.allowance-row.percent { grid-template-columns: minmax(180px, 1.4fr) minmax(120px, 0.7fr) minmax(120px, 0.7fr) auto; }
.allowance-row.deduction-percent { grid-template-columns: minmax(180px, 1.4fr) minmax(120px, 0.7fr) minmax(150px, 0.8fr) auto; }
.allowance-row > * { min-width: 0; }
.mini-btn {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  color: #344054;
  cursor: pointer;
  font-weight: 800;
  min-height: 2.5rem;
  padding: 0.35rem 0.62rem;
}
.summary-grid { display: grid; gap: 1rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.pay-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  max-width: 100%;
  background: #fff;
}
.pay-head {
  background: #f0f4f8;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  padding: 0.65rem 0.75rem;
}
.pay-head strong { color: var(--brand); font-size: 0.9rem; }
.pay-head span { color: var(--muted); font-size: 0.76rem; }
.rows { padding: 0.25rem 0; }
.srow {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.28rem 0.75rem;
  font-size: 0.82rem;
  line-height: 1.25;
}
.srow:nth-child(even) { background: #fafcff; }
.srow.section {
  background: #eef4f8;
  color: var(--brand);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}
.srow .name { color: #344054; min-width: 0; overflow-wrap: anywhere; }
.srow .value { font-family: "Courier New", monospace; font-weight: 800; text-align: right; white-space: nowrap; }
.total-strip {
  background: var(--brand);
  color: #fff;
  display: grid;
  gap: 0.7rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding: 0.72rem 0.75rem;
}
.total-item { display: flex; flex-direction: column; gap: 0.14rem; }
.total-strip span { font-size: 0.68rem; opacity: 0.78; text-transform: uppercase; }
.total-strip strong { font-family: "Courier New", monospace; font-size: 0.98rem; }
.delta { border-top: 1px solid var(--line); color: var(--accent); font-weight: 800; padding: 0.55rem 0.75rem; }
.err-msg { color: #b42318; font-weight: 800; padding: 0.8rem; text-align: center; }
.print-actions { display: none; }
.hidden { display: none; }
@media (max-width: 850px) {
  .grid, .grid.two, .summary-grid { grid-template-columns: 1fr; }
  .allowance-row, .allowance-row.percent, .allowance-row.deduction-percent { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  html, body { max-width: 100%; overflow-x: hidden; }
  header { padding: 0.85rem 0.85rem; }
  header h1 { font-size: 1.05rem; }
  header .sub { font-size: 0.72rem; }
  header .note { font-size: 0.68rem; }
  .container { margin: 0.75rem 0 1.5rem; max-width: 100vw; padding: 0 0.55rem; width: 100vw; }
  .band { border-radius: 6px; margin-bottom: 0.75rem; padding: 0.78rem; width: 100%; }
  .band-title { align-items: stretch; flex-direction: column; gap: 0.55rem; font-size: 0.72rem; }
  .band-title .mini-btn { width: 100%; }
  .allowance-editor { gap: 0.8rem; }
  .allowance-row {
    background: #fbfcfe;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.65rem;
  }
  .allowance-row .mini-btn { width: 100%; }
  .toolbar, .mode-group { width: 100%; }
  .toolbar .btn { width: 100%; }
  .mode-btn { font-size: 0.92rem; min-height: 3rem; padding: 0.5rem 0.35rem; }
  .srow { align-items: flex-start; padding: 0.4rem 0.58rem; }
  .srow .name { flex: 1 1 auto; }
  .srow .value { flex: 0 0 auto; max-width: 46%; overflow-wrap: anywhere; white-space: normal; }
  .pay-head { align-items: flex-start; flex-direction: column; gap: 0.25rem; padding: 0.58rem; }
  .pay-head span { overflow-wrap: anywhere; }
  .pay-card, .rows, .field, input, select { max-width: 100%; width: 100%; }
  .total-strip { grid-template-columns: 1fr; gap: 0.5rem; }
  .total-item { align-items: center; flex-direction: row; justify-content: space-between; }
  .total-strip strong { font-size: 1rem; }
  .delta { font-size: 0.86rem; overflow-wrap: anywhere; }
}
@media print {
  body { background: #fff; }
  header, .input-band, .no-print { display: none !important; }
  .container { margin: 0; max-width: none; padding: 0; }
  .band { border: 0; box-shadow: none; padding: 0; }
  .print-actions { display: block; margin-bottom: 0.7rem; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>
<header>
  <h1>Pakistan Airports Authority - Pay Calculator</h1>
  <div class="sub">Generic allowance calculator for current pay, annual increment, and promotion</div>
  <div class="note">Note: This calculator was prepared by an Air Traffic Controller for estimation only. Please verify figures against official PAA/HR/Finance records; errors and omissions are possible.</div>
</header>

<div class="container">
  <div class="band input-band">
    <div class="band-title">Employee Pay Inputs</div>
    <div class="grid">
      <div class="field">
        <label for="grade-sel">Group / Grade</label>
        <select id="grade-sel" onchange="onGradeChange()"></select>
      </div>
      <div class="field">
        <label for="basic-sel">Basic Pay</label>
        <select id="basic-sel" onchange="calculateCurrent()"></select>
      </div>
    </div>
  </div>

  <div class="band input-band">
    <div class="band-title">
      <span>Percent Allowances</span>
      <button class="mini-btn" type="button" onclick="addPercentAllowance()">Add Percent</button>
    </div>
    <div id="percent-list" class="allowance-editor"></div>
    <div class="hint">Percent allowances are recalculated on the current and projected basic pay. Use this for ATC rating, ATCL, trade-specific allowance, house-specific rates not already automatic, etc.</div>
  </div>

  <div class="band input-band">
    <div class="band-title">
      <span>Fixed Amount Allowances</span>
      <button class="mini-btn" type="button" onclick="addFixedAllowance()">Add Fixed</button>
    </div>
    <div id="fixed-list" class="allowance-editor"></div>
    <div class="hint">Fixed allowances carry unchanged into increment/promotion unless edited here.</div>
  </div>

  <div class="band input-band">
    <div class="band-title">
      <span>Percent Deductions</span>
      <button class="mini-btn" type="button" onclick="addPercentDeduction()">Add Percent</button>
    </div>
    <div id="deduction-percent-list" class="allowance-editor"></div>
    <div class="hint">GP Fund is automatic at 8% of average basis: (minimum + maximum basic) / 2. Use this section for Group Insurance, Benevolent Fund, or other percentage deductions.</div>
  </div>

  <div class="band input-band">
    <div class="band-title">
      <span>Fixed Amount Deductions</span>
      <button class="mini-btn" type="button" onclick="addFixedDeduction()">Add Fixed</button>
    </div>
    <div id="deduction-fixed-list" class="allowance-editor"></div>
    <div class="hint">Use this for welfare fund, Al-Shifa, guild fund, advances, loan instalments, tax, or other fixed deductions.</div>
  </div>

  <div class="band input-band">
    <div class="band-title">Current Pay</div>
    <div id="current-content"></div>
  </div>

  <div class="band input-band">
    <div class="band-title">What To Calculate</div>
    <div class="mode-group">
      <button class="mode-btn active" id="btn-inc" onclick="setMode('increment')">Annual Increment</button>
      <button class="mode-btn" id="btn-promo" onclick="setMode('promotion')">Promotion</button>
    </div>
    <div class="toolbar">
      <button class="btn" type="button" onclick="calculateProjection()">Calculate</button>
      <button class="btn secondary" type="button" onclick="downloadPdf()">Download PDF</button>
    </div>
  </div>

  <div id="result-card" class="band hidden">
    <div class="print-actions">
      <h2>PAA Pay Calculation</h2>
      <p id="print-meta"></p>
    </div>
    <div class="band-title">Current vs Recalculated Pay</div>
    <div id="result-content"></div>
  </div>
</div>

<script>
const PAYSCALE = __PAYSCALE__;
const GRADE_ORDER = Object.keys(PAYSCALE);
const EG_ORDER = GRADE_ORDER.filter(function(g) { return g.startsWith('EG-'); });
const SG_ORDER = GRADE_ORDER.filter(function(g) { return g.startsWith('SG-'); });
const CURRENT_PETROL_RATE = 310.51;
const PROJECTED_PETROL_RATE = 350;
const TAX_SLABS = [
  [0, 0, 0.00],
  [600000, 0, 0.01],
  [1200000, 6000, 0.11],
  [2200000, 116000, 0.23],
  [3200000, 346000, 0.30],
  [4100000, 616000, 0.35],
];
let currentMode = 'increment';

function fmt(n) {
  return Math.round(Number(n) || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function money(n) {
  return 'Rs. ' + fmt(n);
}

function num(id) {
  return parseFloat(document.getElementById(id).value) || 0;
}

function gradeNo(grade) {
  return parseInt(grade.split('-')[1], 10);
}

function isEg(grade) {
  return grade.startsWith('EG-');
}

function isSg(grade) {
  return grade.startsWith('SG-');
}

function setMode(mode) {
  currentMode = mode;
  document.getElementById('btn-inc').classList.toggle('active', mode === 'increment');
  document.getElementById('btn-promo').classList.toggle('active', mode === 'promotion');
}

function initGrades() {
  const sel = document.getElementById('grade-sel');
  for (const grade of GRADE_ORDER) {
    const opt = document.createElement('option');
    opt.value = grade;
    opt.textContent = grade;
    sel.appendChild(opt);
  }
  if (PAYSCALE['EG-04']) sel.value = 'EG-04';
  onGradeChange();
  addPercentAllowance('Special Allowance', 20);
  addFixedAllowance('Fixed Allowance', 0);
  addPercentDeduction('Percent Deduction', 0);
  addFixedDeduction('Welfare Fund', 400);
  addFixedDeduction('Al-Shifa Trust', 200);
  addFixedDeduction('Fixed Amount Deduction', 0);
}

function onGradeChange() {
  const grade = document.getElementById('grade-sel').value;
  const row = PAYSCALE[grade];
  const basicSel = document.getElementById('basic-sel');
  basicSel.innerHTML = '';
  row.stages.forEach(function(v, idx) {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = 'Stage ' + (idx + 1) + ': ' + fmt(v);
    basicSel.appendChild(opt);
  });
  calculateCurrent();
}

function fieldHtml(label, value, cls) {
  return '<div class="field"><label>' + label + '</label><input class="' + cls + '" value="' + value + '" oninput="calculateCurrent()"></div>';
}

function addPercentAllowance(label, percent, basis) {
  const list = document.getElementById('percent-list');
  const row = document.createElement('div');
  row.className = 'allowance-row percent';
  row.innerHTML =
    fieldHtml('Name', label || '', 'allowance-name') +
    fieldHtml('Percent', percent === undefined ? '' : percent, 'allowance-percent') +
    '<div class="field"><label>Basis</label><select class="allowance-basis" onchange="calculateCurrent()">' +
      '<option value="running">Running Basic</option>' +
      '<option value="initial">Initial Basic</option>' +
    '</select></div>' +
    '<button class="mini-btn" type="button" onclick="removeAllowanceRow(this)">Remove</button>';
  list.appendChild(row);
  row.querySelector('.allowance-basis').value = basis || 'running';
  calculateCurrent();
}

function addFixedAllowance(label, amount) {
  const list = document.getElementById('fixed-list');
  const row = document.createElement('div');
  row.className = 'allowance-row';
  row.innerHTML =
    fieldHtml('Name', label || '', 'allowance-name') +
    fieldHtml('Amount', amount === undefined ? '' : amount, 'allowance-amount') +
    '<button class="mini-btn" type="button" onclick="removeAllowanceRow(this)">Remove</button>';
  list.appendChild(row);
  calculateCurrent();
}

function addPercentDeduction(label, percent, basis) {
  const list = document.getElementById('deduction-percent-list');
  const row = document.createElement('div');
  row.className = 'allowance-row deduction-percent';
  row.innerHTML =
    fieldHtml('Name', label || '', 'deduction-name') +
    fieldHtml('Percent', percent === undefined ? '' : percent, 'deduction-percent') +
    '<div class="field"><label>Basis</label><select class="deduction-basis" onchange="calculateCurrent()">' +
      '<option value="average">Average Basis</option>' +
      '<option value="basic">Basic Pay</option>' +
    '</select></div>' +
    '<button class="mini-btn" type="button" onclick="removeAllowanceRow(this)">Remove</button>';
  list.appendChild(row);
  row.querySelector('.deduction-basis').value = basis || 'average';
  calculateCurrent();
}

function addFixedDeduction(label, amount) {
  const list = document.getElementById('deduction-fixed-list');
  const row = document.createElement('div');
  row.className = 'allowance-row';
  row.innerHTML =
    fieldHtml('Name', label || '', 'deduction-name') +
    fieldHtml('Amount', amount === undefined ? '' : amount, 'deduction-amount') +
    '<button class="mini-btn" type="button" onclick="removeAllowanceRow(this)">Remove</button>';
  list.appendChild(row);
  calculateCurrent();
}

function removeAllowanceRow(button) {
  button.closest('.allowance-row').remove();
  calculateCurrent();
}

function entertainmentAmount(grade) {
  if (!isEg(grade)) return 0;
  const n = gradeNo(grade);
  if (n <= 2) return 1500;
  if (n <= 4) return 2500;
  if (n <= 6) return 3500;
  if (n <= 8) return 4500;
  if (n <= 10) return 5500;
  if (n === 11) return 10500;
  return 0;
}

function fuelLiters(grade) {
  const n = gradeNo(grade);
  if (isEg(grade)) {
    if (n <= 2) return 150;
    if (n <= 4) return 175;
    if (n <= 6) return 225;
    return 0;
  }
  if (isSg(grade)) {
    if (n <= 2) return 50;
    if (n <= 4) return 65;
    if (n <= 6) return 75;
    if (n <= 8) return 85;
    if (n === 9) return 95;
    if (n === 10) return 105;
    if (n === 11) return 120;
  }
  return 0;
}

function motorMaintenance(grade) {
  const row = PAYSCALE[grade];
  if (!row) return 0;
  if (isEg(grade) && gradeNo(grade) >= 7 && gradeNo(grade) <= 10) return 0;
  if (isSg(grade)) return Math.max(Math.round(row.min * 0.10), 1200);
  return Math.round(row.min * 0.10);
}

function stageBackBasic(grade, basic, count) {
  const stages = PAYSCALE[grade].stages;
  const idx = stages.indexOf(basic);
  if (idx < 0) return basic;
  return stages[Math.max(0, idx - count)];
}

function autoAllowances(grade, basic, petrolRate) {
  const liters = fuelLiters(grade);
  const fuel = Math.round(liters * petrolRate);
  const rows = [
    ['Basic Pay', basic],
    ['House Rent', Math.round(basic * 0.80)],
    ['Medical Allowance', Math.round(basic * 0.25)],
    ['Utility Allowance', Math.round(basic * 0.25)],
    ['Fuel / Conveyance (' + liters + ' liters)', fuel],
    ['Entertainment', entertainmentAmount(grade)],
    ['M/Cycle Maint.', motorMaintenance(grade)],
    ['Adhoc Relief 2023', Math.round(stageBackBasic(grade, basic, 4) * 0.20)],
    ['Adhoc Relief 2024', Math.round(stageBackBasic(grade, basic, 2) * 0.30)],
  ];
  return rows.filter(function(r) { return r[1] !== 0 || r[0] === 'Basic Pay'; });
}

function averageBasis(grade) {
  const row = PAYSCALE[grade];
  return (row.min + row.max) / 2;
}

function autoDeductions(grade) {
  const avg = averageBasis(grade);
  return [
    ['GP Fund', Math.round(avg * 0.08)],
    ['Group Insurance', Math.round(avg * 0.00667)],
    ['Benevolent Fund', Math.round(avg * 0.00587)],
  ];
}

function annualTax(annualIncome) {
  if (annualIncome <= 0) return 0;
  let applicable = TAX_SLABS[0];
  for (const slab of TAX_SLABS) {
    if (annualIncome > slab[0]) applicable = slab;
    else break;
  }
  return applicable[1] + (annualIncome - applicable[0]) * applicable[2];
}

function monthlyIncomeTaxFromGross(gross, floorTax) {
  const calculated = Math.round(annualTax(gross * 12) / 12);
  return Math.max(calculated, floorTax || 0);
}

function customPercentAllowances(grade, basic) {
  const initial = PAYSCALE[grade].min;
  return Array.from(document.querySelectorAll('#percent-list .allowance-row')).map(function(row) {
    const name = row.querySelector('.allowance-name').value.trim() || 'Percent Allowance';
    const pct = parseFloat(row.querySelector('.allowance-percent').value) || 0;
    const basis = row.querySelector('.allowance-basis').value;
    const basisAmount = basis === 'initial' ? initial : basic;
    return [name, Math.round(basisAmount * pct / 100)];
  }).filter(function(r) { return r[1] !== 0; });
}

function customFixedAllowances() {
  return Array.from(document.querySelectorAll('#fixed-list .allowance-row')).map(function(row) {
    const name = row.querySelector('.allowance-name').value.trim() || 'Fixed Allowance';
    const amount = parseFloat(row.querySelector('.allowance-amount').value) || 0;
    return [name, Math.round(amount)];
  }).filter(function(r) { return r[1] !== 0; });
}

function customPercentDeductions(grade, basic) {
  const avg = averageBasis(grade);
  return Array.from(document.querySelectorAll('#deduction-percent-list .allowance-row')).map(function(row) {
    const name = row.querySelector('.deduction-name').value.trim() || 'Percent Deduction';
    const pct = parseFloat(row.querySelector('.deduction-percent').value) || 0;
    const basis = row.querySelector('.deduction-basis').value;
    const basisAmount = basis === 'basic' ? basic : avg;
    return [name, Math.round(basisAmount * pct / 100)];
  }).filter(function(r) { return r[1] !== 0; });
}

function customFixedDeductions() {
  return Array.from(document.querySelectorAll('#deduction-fixed-list .allowance-row')).map(function(row) {
    const name = row.querySelector('.deduction-name').value.trim() || 'Fixed Deduction';
    const amount = parseFloat(row.querySelector('.deduction-amount').value) || 0;
    return [name, Math.round(amount)];
  }).filter(function(r) { return r[1] !== 0; });
}

function payRows(grade, basic, petrolRate) {
  return autoAllowances(grade, basic, petrolRate)
    .concat(customPercentAllowances(grade, basic))
    .concat(customFixedAllowances());
}

function deductionRows(grade, basic, gross, taxFloor) {
  return autoDeductions(grade)
    .concat([['Income Tax', monthlyIncomeTaxFromGross(gross, taxFloor)]])
    .concat(customPercentDeductions(grade, basic))
    .concat(customFixedDeductions());
}

function total(rows) {
  return rows.reduce(function(sum, row) { return sum + row[1]; }, 0);
}

function renderRows(rows) {
  return rows.map(function(row) {
    return '<div class="srow"><span class="name">' + row[0] + '</span><span class="value">' + fmt(row[1]) + '</span></div>';
  }).join('');
}

function renderSection(title) {
  return '<div class="srow section"><span>' + title + '</span><span></span></div>';
}

function renderPayCard(title, subtitle, earnings, deductions, delta) {
  const gross = total(earnings);
  const totalDeduction = total(deductions);
  const net = gross - totalDeduction;
  return '<div class="pay-card">' +
    '<div class="pay-head"><strong>' + title + '</strong><span>' + subtitle + '</span></div>' +
    '<div class="rows">' + renderSection('Earnings') + renderRows(earnings) + renderSection('Deductions') + renderRows(deductions) + '</div>' +
    '<div class="total-strip">' +
      '<div class="total-item"><span>Gross Pay</span><strong>' + fmt(gross) + '</strong></div>' +
      '<div class="total-item"><span>Deductions</span><strong>' + fmt(totalDeduction) + '</strong></div>' +
      '<div class="total-item"><span>Net Pay</span><strong>' + fmt(net) + '</strong></div>' +
    '</div>' +
    (delta === undefined ? '' : '<div class="delta">Difference: ' + money(delta) + '</div>') +
    '</div>';
}

function calculateCurrent() {
  const grade = document.getElementById('grade-sel').value;
  const basic = parseInt(document.getElementById('basic-sel').value, 10) || 0;
  const rows = payRows(grade, basic, CURRENT_PETROL_RATE);
  const deductions = deductionRows(grade, basic, total(rows), 0);
  document.getElementById('current-content').innerHTML =
    renderPayCard('Current Pay', grade + ' / Basic ' + fmt(basic), rows, deductions);
}

function promotedGrade(grade) {
  const order = isEg(grade) ? EG_ORDER : isSg(grade) ? SG_ORDER : GRADE_ORDER;
  const idx = order.indexOf(grade);
  if (idx < 0 || idx === order.length - 1) return null;
  return order[idx + 1];
}

function projection() {
  const grade = document.getElementById('grade-sel').value;
  const basic = parseInt(document.getElementById('basic-sel').value, 10) || 0;
  const stages = PAYSCALE[grade].stages;
  const idx = stages.indexOf(basic);
  if (idx < 0) throw new Error('Selected basic pay is not in the selected grade.');

  if (currentMode === 'increment') {
    if (idx === stages.length - 1) throw new Error('No further annual increment is available at maximum stage.');
    return { grade: grade, basic: stages[idx + 1], label: 'Annual Increment', note: 'Stage ' + (idx + 1) + ' to ' + (idx + 2) };
  }

  const nextGrade = promotedGrade(grade);
  if (!nextGrade) throw new Error('No next grade is available for promotion.');
  const nextRow = PAYSCALE[nextGrade];
  const lowestHigher = nextRow.stages.find(function(v) { return v > basic; });
  if (lowestHigher === undefined) throw new Error('No higher stage exists in ' + nextGrade + ' for this basic pay.');
  return {
    grade: nextGrade,
    basic: lowestHigher + nextRow.increment,
    label: 'Promotion',
    note: grade + ' to ' + nextGrade + ', lowest higher ' + fmt(lowestHigher) + ' + one increment ' + fmt(nextRow.increment),
  };
}

function showError(message) {
  document.getElementById('result-card').classList.remove('hidden');
  document.getElementById('result-content').innerHTML = '<p class="err-msg">' + message + '</p>';
}

function calculateProjection() {
  try {
    const grade = document.getElementById('grade-sel').value;
    const basic = parseInt(document.getElementById('basic-sel').value, 10) || 0;
    const currentRows = payRows(grade, basic, CURRENT_PETROL_RATE);
    const currentGross = total(currentRows);
    const currentTax = monthlyIncomeTaxFromGross(currentGross, 0);
    const currentDeductions = deductionRows(grade, basic, currentGross, currentTax);
    const projected = projection();
    const projectedRows = payRows(projected.grade, projected.basic, PROJECTED_PETROL_RATE);
    const projectedGross = total(projectedRows);
    const projectedDeductions = deductionRows(projected.grade, projected.basic, projectedGross, currentTax);
    const currentNet = total(currentRows) - total(currentDeductions);
    const projectedNet = total(projectedRows) - total(projectedDeductions);
    const diff = projectedNet - currentNet;

    document.getElementById('print-meta').textContent =
      grade + ' basic ' + fmt(basic) + ' / ' + projected.label + ' / ' + projected.note;
    document.getElementById('result-content').innerHTML =
      '<div class="summary-grid">' +
        renderPayCard('Current Pay', grade + ' / Basic ' + fmt(basic), currentRows, currentDeductions) +
        renderPayCard(projected.label, projected.grade + ' / Basic ' + fmt(projected.basic) + ' / Petrol ' + PROJECTED_PETROL_RATE + '/L / ' + projected.note, projectedRows, projectedDeductions, diff) +
      '</div>';
    document.getElementById('result-card').classList.remove('hidden');
    document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    showError(err.message);
  }
}

function downloadPdf() {
  calculateProjection();
  window.print();
}

initGrades();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
