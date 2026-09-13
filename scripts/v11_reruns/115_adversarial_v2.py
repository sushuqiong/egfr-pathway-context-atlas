#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adversarial review v2: refined wording checks (only unhedged causal claims), abstract variants accepted."""
import csv, os, re, sys, statistics
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"; V=os.path.join(V11,"reruns","results")
MD=os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.md"); s=open(MD,encoding="utf-8").read()
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
ok=[]; bad=[]
def chk(cond,good,badder):(ok if cond else bad).append(good if cond else badder)
meta=rd(os.path.join(V,"v11_meta_primary_reml_knha.csv")); n_meta=sum(1 for r in meta if r["k"] and int(r["k"])>=2 and r["fdr"] not in("","NA") and float(r["fdr"])<0.05)
js=rd(os.path.join(V,"v11_joint_summary.csv")); n_joint=sum(1 for r in js if r["joint_robust"]=="TRUE")
pc=rd(os.path.join(V,"v11_percohort_effects.csv"))
ratio=statistics.median([abs(float(r["beta_adj"]))/abs(float(r["beta_base"])) for r in pc if r["beta_base"] not in("","NA") and abs(float(r["beta_base"]))>1e-9 and r["beta_adj"] not in("","NA")])
sc=rd(os.path.join(V,"sc_v11_patient_paired.csv"))
same=sum(1 for r in sc if r["fdr"] not in("","NA") and float(r["fdr"])<0.05 and r["comparison_type"]=="same-cell-type")
ident=sum(1 for r in sc if r["fdr"] not in("","NA") and float(r["fdr"])<0.05 and r["comparison_type"]=="cell-identity")
# 1 numbers
chk(f"retained {n_meta}" in s, f"meta {n_meta} present", f"meta {n_meta} absent")
chk(f"{n_joint} of 170 states were composition-robust" in s, f"joint {n_joint} present", f"joint {n_joint} absent")
chk("0.87" in s and abs(ratio-0.87)<0.015, f"ratio {ratio:.3f} consistent with 0.87", f"ratio mismatch {ratio:.3f}")
chk(f"{same} same-cell-type" in s and f"{ident} labelled cell-identity" in s, f"single-cell counts {same}/{ident} present", "single-cell counts absent")
absx=s[s.find("## Abstract"):s.find("## 1. Introduction")]
chk(("11 of 15" in absx) or ("11/15" in absx), "abstract states survival-of-adjustment result", "abstract missing survival-of-adjustment result")
# 2 unhedged causal wording only
unhedged=[]
for pat in [r"(?<!not )(?<!rather than )\bdemonstrat\w+", r"\bproves?\b", r"\bconfirms? that\b",
            r"\bfully attenuated\b", r"\bexplained by composition\b", r"\bdriven by composition\b",
            r"(?<!rather than )(?<!not )(?<!evidence of )(?<!measures of )\bpathway activation\b",
            r"\bthere is no effect\b", r"\bno effect was (found|observed)\b"]:
    for m in re.finditer(pat, s, re.I):
        pre = s[max(0,m.start()-1):m.start()]
        if pre == '"':        # quoted term used critically (e.g. reported as "pathway activation")
            continue
        ctx=s[max(0,m.start()-70):m.end()+70].replace("\n"," ")
        unhedged.append(f"{m.group(0)} :: ...{ctx}...")
chk(len(unhedged)==0, "no unhedged causal wording", "; ".join(unhedged[:3]) if unhedged else "")
# 3 hedges present
for w in ["composition-associated","not replicated","cannot distinguish","underpowered","exploratory","limitation","modest"]:
    chk(w.lower() in s.lower(), f"hedge '{w}' present", f"hedge missing: {w}")
# 4 coverage of GPT6 items
for k in ["SMCRPH","SMDH","base model","adjusted model","paired signed-rank","cell-identity","mutation-profiled","wild type",
          "Knapp-Hartung","non-shrinking","decision rules","externally replicated","BH-FDR","profiled-only" ]:
    chk(k.lower() in s.lower(), f"coverage {k}", f"missing coverage: {k}")
# 5 figures/tables
fm=sorted(set(re.findall(r"\bFigure (\d)\b",s))); fl=sorted(set(re.findall(r"\*\*Figure (\d)\.",s)))
chk(fm==fl, f"figure refs {fm} == legends", f"figure mismatch {fm} vs {fl}")
tabs=sorted(set(re.findall(r"Table S(\d+)",s)), key=int)
chk(len(tabs)>=9, f"supplementary tables referenced ({len(tabs)})", f"too few table refs {tabs}")
# 6 figures OCR QA present and clean
qap=os.path.join(V11,"04_评审记录与报告","ocr_figure_qa.csv")
if os.path.exists(qap):
    q=rd(qap); clip=sum(int(r["clipping"]) for r in q); ov=sum(int(r["overlaps"]) for r in q)
    chk(clip==0, "OCR: no clipping in any figure", f"OCR clipping found: {clip}")
    chk(ov==0, "OCR: no text overlaps", f"OCR overlaps reported: {ov} (verify artifacts)")
else: bad.append("OCR QA table missing")
# 7 file presence + specs
for f in ["01_稿件正文/Manuscript_draft_v11.docx","01_稿件正文/Manuscript_draft_v11.pdf","02_图片_TIFF/Figure6.tif",
          "02_图片_TIFF/figure_specs.csv","06_投稿清单与流程/图表制作规范_v11.md","06_投稿清单与流程/人工项填写指南_v11.md"]:
    chk(os.path.exists(os.path.join(V11,f)), f"file {f}", f"missing {f}")
spec=os.path.join(V11,"02_图片_TIFF","figure_specs.csv")
if os.path.exists(spec):
    wide=[r["file"] for r in rd(spec) if float(r["cm_w"])>17.05]
    chk(not wide, "all TIFF widths <= 17 cm", f"TIFF too wide: {wide}")
print("=== ADVERSARIAL REVIEW v2 ==="); print("passed:",len(ok)); [print("  OK ",x) for x in ok]
print("issues:",len(bad)); [print("  ISSUE",x) for x in bad]
open(os.path.join(V11,"04_评审记录与报告","adversarial_review_v11.md"),"w",encoding="utf-8").write(
 "# v11 对抗性审查（第二轮，含图件 OCR 质检）\n\n**通过 %d 项**\n"%len(ok)+"\n".join(f"- {x}" for x in ok)+
 "\n\n**问题 %d 项**\n"%len(bad)+("\n".join(f"- {x}" for x in bad) if bad else "- 无"))
sys.exit(1 if bad else 0)
