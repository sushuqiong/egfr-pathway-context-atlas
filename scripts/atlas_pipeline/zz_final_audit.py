#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os
P=r"C:\Users\fengq\Desktop\EGFR\EGFR_Atlas_投稿包"
md=open(os.path.join(P,"01_稿件正文","Manuscript_draft_v09.md"),encoding="utf-8").read()
body,_,refsec=md.partition("## References")
print("== 1) 摘要词数 ==")
abs_=md[md.find("## Abstract"):md.find("## 1. Introduction")]
print("abstract words:", len(re.findall(r"\S+", abs_)))
print("abstract 含引用:", bool(re.search(r"\[\d+", abs_)))
print("\n== 2) 旧口径残留扫描（应全为0）==")
stale=["only 4 pooled","73 at k","After xCell adjustment only 19","19 states remained composition",
 "eight composition-robust","carried entirely by non-amplified","was prospective","Multi-axis activation",
 "Methods 2.10). The TCGA","not explained by molecular subtype or by tumour purity","178 with survival",
 "REML/Hartung-Knapp pooling retained only 4","DerSimonian-Laird estimator identified 75","ERBB ligands +0.39",
 "Driver stratification as a negative control"]
for ph in stale:
    c=md.count(ph)
    if c: print("  STALE",c,ph)
print("  (done)")
print("\n== 3) 新口径存在性 ==")
new=["joint","composition-aware","retained 11","six states remained","VEGF/PDGF","GSE39582 (n=573","190 events",
 "Supplementary Table S9","Supplementary Figure S2","100 events" ]
for ph in ["composition-aware","Pooled states retained 11","six states remained","n=573, 190 events" if "n=573" in md else "n=573","190 events","Supplementary Table S9","Supplementary Figure S2","supplementary Table S2","Moffitt","Cristescu"]:
    print("  ",ph,"->",md.count(ph))
print("\n== 4) 引文核验 ==")
refnums=[int(m.group(1)) for l in refsec.splitlines() if (m:=re.match(r"\s*(\d+)\.\s",l))]
order=[]
def expand(t):
    out=[]
    for part in t.split(","):
        part=part.strip()
        if "-" in part:
            a,b=part.split("-"); out+=list(range(int(a),int(b)+1))
        else: out.append(int(part))
    return out
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
print("refs:",len(refnums),"sequential:",refnums==list(range(1,51)),"cited unique:",len(order),
      "violations:",sum(1 for i in range(1,len(order)) if order[i]<order[i-1]),
      "uncited:",[n for n in refnums if n not in set(order)])
print("\n== 5) 文件齐全性（主投稿包）==")
dirs={"01_稿件正文":["Manuscript_draft_v09.md","Manuscript_draft_v09.docx","Manuscript_draft_v09.pdf","Cover_letter_v09.txt","Cover_letter_v09_合成版占位.docx"],
 "06_投稿清单与流程":["Submission_readiness_checklist_v09.md","Cover_letter_header_template.docx"],
 "03_表格与补充数据":["TableS9_evidence_matrix_v9.csv","references_vancouver_v07.txt","context_meta_v9_unified.csv","external_crc_gse39582_refined.csv"]}
for d,need in dirs.items():
    have=set(os.listdir(os.path.join(P,d)))
    miss=[f for f in need if f not in have]
    print(f"  {d}: 缺 {miss if miss else '无'}")
figs=os.listdir(os.path.join(P,"02_图片"))
needf=["fig_paper_atlas_heatmap_v2.png","fig_paper_joint_heatmap.png","fig_paper_composition_adjustment_v2.png",
       "fig_paper_survival_forest_v2.png","fig_paper_molecular_context_mut.png","fig_paper_sc_source_v2.png",
       "fig_paper_xcell_vs_marker.png","fig_paper_xcell_heatmap.png","fig_analysis_flowchart.png"]
print("  02_图片 缺:", [f for f in needf if f not in figs] or "无","(共",len(figs),"张)")
print("\n== 6) 引用文件（S2 模块基因/覆盖表等）==")
t=os.listdir(os.path.join(P,"03_表格与补充数据"))
for probe in ["module_signature_consistency.csv","TableS1b_cohort_pubmed_map.csv","loogo_module_summary.csv"]:
    print("  ",probe,"->",probe in t)
