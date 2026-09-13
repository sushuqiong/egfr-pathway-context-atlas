#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adversarial review of the v11 manuscript and package."""
import csv, os, re, sys
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
V  =os.path.join(V11,"reruns","results")
MD =os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.md")
s=open(MD,encoding="utf-8").read()
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
problems=[]; notes=[]
def check(cond, ok, bad):
    (notes if cond else problems).append(ok if cond else bad)

# 1) numbers vs frozen tables
meta=rd(os.path.join(V,"v11_meta_primary_reml_knha.csv")); n_meta=sum(1 for r in meta if r["k"] and int(r["k"])>=2 and r["fdr"] not in ("","NA") and float(r["fdr"])<0.05)
js=rd(os.path.join(V,"v11_joint_summary.csv")); n_joint=sum(1 for r in js if r["joint_robust"]=="TRUE")
pc=rd(os.path.join(V,"v11_percohort_effects.csv"))
ratios=[abs(float(r["beta_adj"]))/abs(float(r["beta_base"])) for r in pc if r["beta_base"] and abs(float(r["beta_base"]))>1e-9 and r["beta_adj"] not in ("","NA")]
import statistics; med_ratio=statistics.median(ratios)
check(f"retained {n_meta}" in s, f"meta count {n_meta} present", f"meta count {n_meta} missing")
check(f"{n_joint} of 170 states were composition-robust" in s, f"joint {n_joint} present", f"joint {n_joint} missing")
check("0.87" in s and abs(med_ratio-0.87)<0.01, f"median ratio {med_ratio:.3f} matches 0.87", f"median ratio mismatch: table={med_ratio:.3f}")
# abstract vs results consistency of the same quantities
abs_txt=s[s.find("## Abstract"):s.find("## 1. Introduction")]
for num in [f"retained {n_meta}", f"{n_joint} (", "0.87", "17/108", "11 of 15"]:
    check(num in abs_txt or num.replace("retained ","") in abs_txt, f"abstract contains '{num}'", f"abstract missing '{num}'")

# 2) overclaim / forbidden wording
bad_words=["demonstrates","proves","proven","confirms that","establish that","fully attenuated","fully explained",
           "explained by composition","driven by composition","caused by composition","pathway activation drives",
           "no effect","absence of effect","carried entirely","prospective validation","is the exception",
           "only five states","overlap of 5","significant benefit"]
for w in bad_words:
    hits=[l.strip()[:140] for l in s.splitlines() if w.lower() in l.lower()]
    if hits: problems.append(f"wording '{w}' x{len(hits)}: {hits[0]}")
# required hedges
for w in ["composition-associated","not replicated","cannot distinguish","underpowered","exploratory","limitation"]:
    check(w.lower() in s.lower(), f"hedge '{w}' present", f"required hedge missing: {w}")

# 3) required rules / method coverage (GPT6 items 1,2,3,4,5,6)
need={"SMCRPH":"common-denominator paired measure","SMDH":"common-denominator unpaired measure",
      "base model":"base-vs-adjusted composition","adjusted model":"base-vs-adjusted composition",
      "paired signed-rank":"single-cell pairing","cell-identity":"cell-identity contrast labelling",
      "mutation-profiled":"mutation denominator rule","wild type":"explicit wild-type definition",
      "Knapp-Hartung":"H-K inference","non-shrinking":"ad hoc KH sensitivity",
      "decision rules":"pre-specified decision rules","per-cohort robust":"per-cohort rule",
      "externally replicated":"external replication criterion","BH-FDR":"multiplicity"}
for k,desc in need.items():
    check(k.lower() in s.lower(), f"methods coverage: {desc}", f"methods missing: {desc} ({k})")

# 4) figure/table cross-references
figs_mentioned=sorted(set(re.findall(r"\bFigure (\d)\b", s)))
figs_legend=sorted(set(re.findall(r"\*\*Figure (\d)\.", s)))
tabs_mentioned=sorted(set(re.findall(r"Table S(\d+)", s)))
check(figs_mentioned==figs_legend, f"figures consistent {figs_mentioned}", f"figure mentions {figs_mentioned} != legends {figs_legend}")
check(len(tabs_mentioned)>=8, f"supplementary tables referenced: {len(tabs_mentioned)}", f"too few supplementary table references: {tabs_mentioned}")

# 5) package completeness
need_files=["01_稿件正文/Manuscript_draft_v11.docx","01_稿件正文/Manuscript_draft_v11.pdf","01_稿件正文/Cover_letter_v11.txt",
            "02_图片_TIFF/Figure1.tif","02_图片_TIFF/Figure6.tif","02_图片_TIFF/figure_specs.csv",
            "06_投稿清单与流程/人工项填写指南_v11.md","06_投稿清单与流程/送审自查包_v11.md","04_评审记录与报告/v18_v11_corrections.md"]
for f in need_files:
    check(os.path.exists(os.path.join(V11,f)), f"file present: {f}", f"FILE MISSING: {f}")

# 6) citation integrity (repeat here)
body,_,ref=s.partition("## References")
rn=[int(m.group(1)) for l in ref.splitlines() if (m:=re.match(r"\s*(\d+)\.",l))]
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for p in re.split(r"[,\-]", m.group(1)):
        v=int(p.strip())
        if v not in order: order.append(v)
check(rn==list(range(1,len(rn)+1)), "refs sequential", "refs not sequential")
check(not [n for n in rn if n not in set(order)], "all refs cited", f"uncited: {[n for n in rn if n not in set(order)]}")
check(not any(order[i]<order[i-1] for i in range(1,len(order))), "first-appearance order ok", "citation order violated")
w=len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
notes.append(f"abstract words: {w}")
if w>260: problems.append(f"abstract long ({w} words)")

print("=== ADVERSARIAL REVIEW ===")
print(f"checks passed: {len(notes)}")
for n in notes: print("  OK  ", n)
print(f"problems: {len(problems)}")
for p in problems: print("  ISSUE", p)
open(os.path.join(V11,"04_评审记录与报告","adversarial_review_v11.md"),"w",encoding="utf-8").write(
 "# v11 对抗性审查\n\n**通过项**\n"+"\n".join(f"- {n}" for n in notes)+
 "\n\n**发现问题**\n"+("\n".join(f"- {p}" for p in problems) if problems else "- 无")+"\n")
print("\nreport -> 04_评审记录与报告/adversarial_review_v11.md")
sys.exit(1 if problems else 0)
