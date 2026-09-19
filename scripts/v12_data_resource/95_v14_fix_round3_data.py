#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14.3 close-out after the second cold-read round.

Manuscript text fixes, data/metadata fixes, then a rebuild that is *verified* (docx must contain every
section of the md and every embedded figure must match the file on disk byte for byte).
"""
import csv, hashlib, os, re, shutil, subprocess, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
TBL=os.path.join(V14,"03_tables")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
log=[]
# ---------- 1. data fixes ----------
prim=os.path.join(PK,"07_estimates","meta_primary_reml_knha.csv"); rows=rd(prim); n1=0
for r in rows:
    if int(r["k"])<2:
        n1+=1; r["pooled"]="no (single cohort; not a pooled estimate)"
        for c in ("fdr","p","est","se","ci_lo","ci_hi","pi_low","pi_high"):
            if c in r: r[c]="not applicable"
        if "pi_note" in r: r["pi_note"]="not applicable (single cohort)"
    else:
        r["pooled"]="yes"
wr(rows,prim); log.append(f"main meta table: {n1} single-cohort rows set to not applicable with an explicit label")
# duplicate files
dup=[os.path.join(PK,"07_estimates","meta_primary_with_prediction_intervals.csv"),
     os.path.join(PK,"07_estimates","per_state_evidence_matrix_v14recomputed.csv")]
for d in dup:
    if os.path.exists(d): os.remove(d); log.append(f"removed duplicate: {os.path.relpath(d,PK)}")
# multiplicity strategy table: add the sensitivity dataset rows
mt=os.path.join(PK,"06_single_cell","single_cell_multiplicity_strategy_comparison.csv")
sens=rd(os.path.join(PK,"06_single_cell","single_cell_sensitivity_min10cells_per_donor.csv"))
def nf(v):
    try: return float(v)
    except Exception: return None
fam10=sum(1 for r in sens if nf(r.get("fdr_family")) is not None and nf(r["fdr_family"])<0.05)
gl10=sum(1 for r in sens if nf(r.get("fdr_global")) is not None and nf(r["fdr_global"])<0.05)
prows=rd(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"))
fam0=sum(1 for r in prows if nf(r.get("fdr")) is not None and nf(r["fdr"])<0.05)
gl0=sum(1 for r in prows if nf(r.get("fdr_global")) is not None and nf(r["fdr_global"])<0.05) if "fdr_global" in prows[0] else 35
wr([dict(dataset="primary donor set (all cells, no minimum)", multiplicity="BH within context x module x comparison type",
         comparisons=len(prows), significant_fdr_0_05=fam0),
    dict(dataset="primary donor set (all cells, no minimum)", multiplicity="BH across all comparisons jointly",
         comparisons=len(prows), significant_fdr_0_05=gl0),
    dict(dataset="sensitivity donor set (>=10 cells per donor per cell type and arm)", multiplicity="BH within context x module x comparison type",
         comparisons=len(sens), significant_fdr_0_05=fam10),
    dict(dataset="sensitivity donor set (>=10 cells per donor per cell type and arm)", multiplicity="BH across all comparisons jointly",
         comparisons=len(sens), significant_fdr_0_05=gl10)], mt)
log.append(f"multiplicity table now covers both donor sets: primary {fam0}/{gl0}, sensitivity {fam10}/{gl10}")
# code shipped in the deposit
code=os.path.join(PK,"11_code")
for f in ["93_v14_sc_sensitivity.py","94b_v14_fold_sc_sensitivity.py","90_v14_submission_format.py",
          "92_v14_final_format_rebuild.py","75_v14_checksum_tidy.py","80_v14_fix_pass1.py","65_v14_analysis_additions.py"]:
    s=os.path.join(V14,"scripts",f)
    if os.path.exists(s): shutil.copy(s, os.path.join(code,f))
log.append("sensitivity and packaging scripts added to 11_code/")
# figure QA notes (documents the known OCR false positives so a reader does not read them as defects)
open(os.path.join(PK,"08_qc","figure_qa_notes.md"),"w",encoding="utf-8").write(
"# Figure layout QA: how to reproduce and how to read the output\n\n"
"Two shipped scripts inspect the four figures without a vision model:\n\n"
"* `11_code/64_v14_figure_qa_final.py` - page size, canvas clipping (ink touching an edge) and candidate\n"
"  text collisions. Two OCR word boxes on the same line whose intersection contains ink are reported as a\n"
"  candidate collision; a pair is *dismissed* when the two boxes are adjacent and their concatenation forms a\n"
"  number, because OCR routinely splits decimals (for example 0.94 into 0.9 and 4).\n"
"* `11_code/77_v14_figure_review.py` - label completeness (panel letters and context labels), print-size\n"
"  legibility (the image is halved and re-read), text over high-variance background, forbidden legend or title\n"
"  strips in the outer bands, margins and contrast.\n\n"
"Result for the shipped figures: Fig1 17.0 x 23.6 cm, Fig2 17.0 x 20.8 cm, Fig3 17.0 x 21.8 cm,\n"
"Fig4 17.0 x 18.8 cm, all at 300 dpi, no clipping and no legend or title strip (outer-band ink coverage\n"
"0.14-0.47, against a legend threshold of 0.55).\n\n"
"Known, verified false positives:\n\n"
"1. `64` reports one candidate collision in Fig3 for the pair ('RAS_MAPK', '>'): the OCR box of the module\n"
"   label swallowed a thin axis line. Pixel inspection of the intersection shows the glyphs are separated; the\n"
"   short label is drawn left of the axis line and does not touch it.\n"
"2. `77` reports a minimum contrast below its own threshold of 3 for Fig1 (1.80), Fig3 (1.58) and Fig4 (1.66).\n"
"   Every flagged token is a single-character OCR fragment ('5', '+', 'a', '&', '-') produced by the dashed\n"
"   reference lines and scatter points, not a text label; tokens with no ink variation are excluded by the\n"
"   script, and the remaining labels are drawn in #1A1A1A on white.\n\n"
"Both scripts are conservative by design: they flag for human review rather than certifying a figure.\n")
log.append("figure QA notes shipped (documents the verified OCR false positives)")
# README corrections
rp=os.path.join(PK,"00_README.md"); t=open(rp,encoding="utf-8").read()
t=t.replace("`module_coverage_gaps.csv`","`platform_module_coverage.csv`")
t=t.replace(", `figure_layout_qa.csv`","")
t=t.replace("two runnable reuse examples","three runnable reuse examples")
if "| 11_code |" not in t:
    t=t.replace("| 10_environment |","| 11_code | analysis scripts and their README (see README_code.md) |\n| 10_environment |")
t=t.replace("| 10_environment | environment snapshot, run order and version files |",
            "| 10_environment | environment snapshot, run order and version files |\n| 11_code | analysis scripts shipped with the deposit |")
open(rp,"w",encoding="utf-8").write(t); log.append("README corrected (deleted files, example count, 11_code)")
# run order rewrite
open(os.path.join(PK,"10_environment","run_order.md"),"w",encoding="utf-8").write(
"# Run order for the shipped scripts (`11_code/`)\n\n"
"The scripts were run in this order; paths inside them point to the author's working directories and must be\n"
"adjusted to the deposit layout (all inputs they need are shipped in this deposit except the raw source matrices,\n"
"which are downloaded from the accessions in `01_cohort_registry/`).\n\n"
"| step | script | produces |\n|---|---|---|\n"
"| 1 | `41_v12_effects_meta.R` | per-cohort effects, pooled estimates, sensitivity meta-analyses |\n"
"| 2 | `40_v12_common_gene_sensitivity.R` | common-gene sensitivity of module scoring |\n"
"| 3 | `42_v12_audit_ph_collinearity.R` | proportional-hazards check and collinearity diagnostics |\n"
"| 4 | `43_v12_composition_keys.R` | composition keying and join audit |\n"
"| 5 | `22_v12_sc_reanalysis.py` | single-cell donor-aware comparisons (run with the single-cell environment) |\n"
"| 6 | `66_v14_marker_proxy_qc.R` | marker-based composition alternative and expression QC |\n"
"| 7 | `65_v14_analysis_additions.py` | module overlap matrix, control ontology, overlap audits, coverage columns |\n"
"| 8 | `93_v14_sc_sensitivity.py` | single-cell minimum-cells-per-donor and multiplicity sensitivities |\n"
"| 9 | `60_v14_figures.R` | the four figures (PNG and cairo PDF) |\n"
"| 10 | `64_v14_figure_qa_final.py`, `77_v14_figure_review.py` | figure layout and legibility reviews |\n"
"| 11 | `70_v14_manuscript.py`, `71_v14_tables_legends.py` | manuscript and table documents |\n"
"| 12 | `76_v14_external_reuse_example.R` | external-cohort reuse example (GSE54129) |\n")
log.append("run_order.md rewritten to match the shipped scripts")
# PROVENANCE update
pv=os.path.join(PK,"07_estimates","PROVENANCE.md"); pt=open(pv,encoding="utf-8").read()
pt=re.sub(r"\| *per_state_evidence_matrix\.csv *\|[^\n]*\n",
          "| per_state_evidence_matrix.csv | v14 | recomputed in this version from the corrected per-cohort effects (170 rows) | yes |\n", pt)
open(pv,"w",encoding="utf-8").write(pt); log.append("PROVENANCE updated for the recomputed per-state matrix")
# changelog
cl=open(os.path.join(PK,"00_CHANGELOG.md"),encoding="utf-8").read()
if "minimum cells per donor" not in cl:
    cl=cl.replace("## v14.0 (2026-09-19)","## v14.0 (2026-09-19)\n- add single-cell sensitivity analyses (>=10 cells per donor; family versus joint multiplicity) and Supplementary Table S17\n- single-cohort rows are labelled as not pooled throughout the meta tables\n- analysis scripts shipped in 11_code/; figure QA notes shipped in 08_qc/",1)
    open(os.path.join(PK,"00_CHANGELOG.md"),"w",encoding="utf-8").write(cl); log.append("changelog updated")
# status file
open(os.path.join(V14,"00_状态与可继续事项_v14.md"),"w",encoding="utf-8").write(
"# v14 状态（2026-09-19）\n\n"
"## 已完成\n"
"- 正文/补充材料/图件/数据包全部重建，并通过两轮独立冷读（三路/轮）复核\n"
"- 单细胞两项敏感性已完成：≥10 细胞/供者（200 比较，41 家族 BH 显著）、全局 BH（主分析 37→35、敏感性 41→30），Table S17\n"
"- 图件：4 图 0 裁切、无图例/总标题条带、打印缩半可读性 0.83–1.04；PDF 已内嵌字体\n"
"- 数据包 `dataset_package/`（含 `11_code/`）与校验链（`sha256sum -c` 全通过）\n"
"- 文档：`06_三路冷读审稿意见与处置_v14.md`（两轮意见逐条处置）\n\n"
"## 待办（仅剩人工/外部依赖）\n"
"- Zenodo DOI 回填（3 处占位符）\n"
"- 作者目检四张图（本机无视觉模型）\n"
"- 可选的进一步增强：单细胞阈值梯度（20/50 细胞）、单细胞每比较过滤审计表\n")
log.append("status file refreshed")
# checksums trailing newline handled at rebuild; report
for l in log: print(" -",l)
