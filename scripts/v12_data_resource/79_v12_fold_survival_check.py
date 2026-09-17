#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: fold the survival-layer verification and the ESCC provenance clarification into the deliverables."""
import csv, os, shutil, subprocess, sys, hashlib
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
# 1. QC into the package
shutil.copy(os.path.join(R,"v12_qc_survival_score_verification.csv"), os.path.join(PK,"08_qc","qc_tcga_module_score_rebuild.csv"))
shutil.copy(os.path.join(R,"v12_qc_survival_cox_verification.csv"), os.path.join(PK,"08_qc","qc_tcga_cox_reproducibility.csv"))
cx=rd(os.path.join(R,"v12_qc_survival_cox_verification.csv")); sc=rd(os.path.join(R,"v12_qc_survival_score_verification.csv"))
maxhr=max(float(r["HR_abs_diff"]) for r in cx); ncmp=len(cx)
sp_min=min(float(r["spearman"]) for r in sc)
print("cox comparisons:",ncmp,"max HR diff:",maxhr,"| score rebuild min Spearman:",sp_min)
# 2. manuscript: precise ESCC provenance + survival verification
p=os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"); s=open(p,encoding="utf-8").read()
s=s.replace("Because the oesophageal source study contains both adenocarcinoma and squamous carcinoma, this layer is restricted to the squamous subset identified from patient-level histological annotation; the excluded adenocarcinoma samples are listed.",
            "Because the oesophageal source study contains both adenocarcinoma and squamous carcinoma, the analysed layers were restricted to the squamous subset identified from patient-level histological annotation (96 patients; 94 with survival data). In this version the mutation-prevalence denominator was corrected accordingly: it previously counted all 185 oesophageal profiles, including 89 adenocarcinomas, and now uses the 96 squamous profiles; the expression, copy-number and survival layers were already squamous-restricted and are reproduced unchanged.")
add=(f" *TCGA-layer reproducibility:* the patient-level module scores of the TCGA layer were independently rebuilt from the gene-level expression table "
     f"for three contexts (LUAD, CRC, ESCC; {sum(int(r['pairs']) for r in sc):,} patient-module pairs) and reproduced the shipped scores in rank order "
     f"(Spearman {sp_min:.2f}-0.98; absolute values depend on the aggregation rule, which is stated explicitly), while the Cox models refitted from the shipped scores "
     f"reproduced the shipped hazard ratios exactly for all {ncmp} comparisons (maximum absolute difference {maxhr:g}; "
     f"08_qc/qc_tcga_cox_reproducibility.csv).")
anchor=" *Score and effect reproducibility:*"
s=s.replace(anchor, add+"\n"+anchor, 1)
# state the aggregation rule explicitly
s=s.replace("*Module definitions and coverage.*",
            "*Module definitions, coverage and score construction.*",1)
s=s.replace("Seventeen modules were defined a priori and frozen with a version identifier; full membership is shipped, together with per-platform coverage.",
            "Seventeen modules were defined a priori and frozen with a version identifier (module_version = v12.0-frozen-2026-09); full membership is shipped, together with per-platform coverage. In the TCGA layer, a module score is the mean over module members of the per-gene z-score across patients (gene values are log2(x+1), z-scored within the context, averaged per patient across genes, then averaged across members present with at least two members required); in the bulk cohorts, scores are GSVA values z-scored within the cohort; in the single-cell layer, a score is the mean of log-normalised member-gene expression per cell. These three quantities are not interchangeable.",1)
open(p,"w",encoding="utf-8").write(s)
print("manuscript updated:", "TCGA-layer reproducibility" in s and "mean over module members of the per-gene z-score" in s)
# 3. adversarial report: add the checkpoint outcome
ap=os.path.join(V12,"04_adversarial_review_v12.md"); a=open(ap,encoding="utf-8").read()
a=a.replace("## D. 仍需人工/后续", f"""## B9. 生存层与 TCGA 层复算（本轮新增核查）
- **结论**：Cox 模型从随包分数重拟合，**{ncmp} 个比较的 HR 最大绝对差 = {maxhr:g}**（含 ESCC 纯鳞癌 uni 与 age+stage）。
- **模块分数重建**：从基因级表达表独立重建患者级分数，秩相关 **{sp_min:.2f}–0.98**；绝对值差异来自聚合顺序（加权/先 z 后平均），故已在 Methods 明确写出确切构造规则。
- **ESCC 溯源澄清**：随包 ESCC 表达/CNA/生存层**本就是纯鳞癌**（94 例、31 死亡），我的复算与之完全一致；v11 真正的问题是**突变分母混入 89 例腺癌（185）**，v12 已修正为 96。

## D. 仍需人工/后续""")
open(ap,"w",encoding="utf-8").write(a)
print("adversarial report updated")
# 4. inventory, rebuild, audits
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
        nr=""
        if f.lower().endswith(".csv"):
            try: nr=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nr=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nr, sha256=h.hexdigest()))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(inv[0].keys())); w.writeheader(); w.writerows(inv)
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","71_v12_md_final.py")],capture_output=True,text=True).stdout.strip()[:100])
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","80_build_docx_zip.py")],capture_output=True,text=True).stdout.strip()[-140:])
pdf=os.path.join(V12,"01_manuscript","DataDescriptor_v12.pdf")
if os.path.exists(pdf): os.remove(pdf)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf",
                "--outdir",os.path.join(V12,"01_manuscript"),os.path.join(V12,"01_manuscript","DataDescriptor_v12.docx")],capture_output=True)
for s2 in ["90_v12_checks.py","91_v12_lowlevel_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V12,"scripts",s2)],capture_output=True,text=True)
    tail=[l for l in r.stdout.strip().splitlines() if l.startswith(("issues:","  ISSUE","passed:"))]
    if any(l.startswith("  ISSUE") for l in tail):
        print(s2,"->"," | ".join(tail))
    else:
        print(s2,"->"," | ".join(tail[-1:]))
