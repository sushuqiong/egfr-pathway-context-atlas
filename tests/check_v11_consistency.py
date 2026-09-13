#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated consistency check for the v11 manuscript against the frozen result tables.

Usage:  python tests/check_v11_consistency.py
Exits non-zero if any headline number disagrees with the frozen tables or if stale
numbers from earlier versions reappear in the manuscript.
"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V11  = r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
MD   = r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
def rd(p):
    with open(p, encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
def fl(x):
    try: return float(x)
    except Exception: return None
fails=[]
# --- 1) headline numbers must match the frozen tables ---
meta = rd(os.path.join(V11,"v11_meta_primary_reml_knha.csv"))
n_meta = sum(1 for r in meta if r["k"] and int(r["k"])>=2 and fl(r["fdr"]) is not None and fl(r["fdr"])<0.05)
dl   = rd(os.path.join(V11,"v11_meta_DL.csv"))
n_dl = sum(1 for r in dl if r["k"] and int(r["k"])>=2 and fl(r["fdr"]) is not None and fl(r["fdr"])<0.05)
js   = rd(os.path.join(V11,"v11_joint_summary.csv"))
n_joint = sum(1 for r in js if r["joint_robust"]=="TRUE")
sc   = rd(os.path.join(V11,"sc_v11_patient_paired.csv"))
sc_same = sum(1 for r in sc if fl(r["fdr"]) is not None and fl(r["fdr"])<0.05 and r["comparison_type"]=="same-cell-type")
sc_id   = sum(1 for r in sc if fl(r["fdr"]) is not None and fl(r["fdr"])<0.05 and r["comparison_type"]=="cell-identity")
sc_paired = sum(1 for r in sc if fl(r["fdr"]) is not None and fl(r["fdr"])<0.05 and r["test_used"].startswith("wilcoxon"))
crc = rd(os.path.join(V11,"v11_external_crc.csv"))
crc_uni = next((r for r in crc if r["feature"]=="VEGF_PDGF_AXIS" and r["model"]=="uni"), None)
crc_as  = next((r for r in crc if r["feature"]=="VEGF_PDGF_AXIS" and r["model"]=="age+stage"), None)
mut = rd(os.path.join(V11,"v11_mutation_denominators.csv"))
paad_kras = next((r for r in mut if r["context"]=="PAAD" and r["gene"]=="KRAS"), None)
print("frozen tables: meta",n_meta,"| DL",n_dl,"| joint",n_joint,"| sc same/identity/paired",sc_same,sc_id,sc_paired)
# --- 2) manuscript must contain them and must not contain stale numbers ---
s = open(MD, encoding="utf-8").read()
must = [f"retained {n_meta} ", f"{n_dl} under DerSimonian-Laird", f"{n_joint} of 170 states were composition-robust",
        f"{sc_same} same-cell-type comparisons", f"{sc_id} labelled cell-identity contrasts",
        f"{sc_paired} paired", "556 tumour samples", "187 deaths", "61.9%", "0.87"]
for m in must:
    if m in s: print("  OK  manuscript contains:", m)
    else: fails.append(f"manuscript missing: {m}")
stale = ["retained 7","retained 11","retained 18","76 under DerSimonian","573 tumour","190 OS events",
         "12 hits","only six states","fully attenuated","carried entirely","was prospective","overlap (5",
         "median empirical within-pair correlation is **0.99**"]
for st in stale:
    if st in s: fails.append(f"stale text present: {st}")
# --- 3) citations ---
body,_,ref = s.partition("## References")
def expand(t):
    out=[]
    for p in t.split(","):
        p=p.strip()
        if "-" in p: x,y=p.split("-"); out+=list(range(int(x),int(y)+1))
        else: out.append(int(p))
    return out
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
rn=[int(m.group(1)) for l in ref.splitlines() if (m:=re.match(r"\s*(\d+)\.",l))]
if rn != list(range(1,len(rn)+1)): fails.append("reference numbering not sequential")
if [n for n in rn if n not in set(order)]: fails.append(f"uncited references: {[n for n in rn if n not in set(order)]}")
if any(order[i]<order[i-1] for i in range(1,len(order))): fails.append("first-appearance ordering violated")
print("\nrefs:",len(rn),"cited:",len(order))
# --- 4) abstract length ---
w=len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
print("abstract words:", w)
if w>300: fails.append(f"abstract too long: {w} words")
print("\nRESULT:", "PASS" if not fails else "FAIL")
for f in fails: print("  -", f)
sys.exit(1 if fails else 0)
