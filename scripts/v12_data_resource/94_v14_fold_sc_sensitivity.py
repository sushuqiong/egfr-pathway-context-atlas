#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: fold the two single-cell sensitivity analyses into the package, the manuscript and the tables."""
import csv, os, re, shutil
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
SC=os.path.join(PK,"06_single_cell"); os.makedirs(SC,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
sens=os.path.join(R,"v14_sc_sensitivity_mindonorcells10.csv")
fdr=os.path.join(R,"v14_sc_fdr_strategy_comparison.csv")
assert os.path.exists(sens) and os.path.exists(fdr), "sensitivity outputs missing"
srows=rd(sens); frows=rd(fdr)
n_keys=["scenario","comparisons","testable","not_testable","significant_family_bh","significant_global_bh"]
def g(r,k): return r.get(k,"")
shutil.copy(sens, os.path.join(SC,"single_cell_sensitivity_min10cells_per_donor.csv"))
shutil.copy(fdr, os.path.join(SC,"single_cell_multiplicity_strategy_comparison.csv"))
prim=rd(os.path.join(SC,"single_cell_comparisons.csv"))
prim_fam=sum(1 for r in prim if r.get("fdr","") not in ("","nan") and float(r["fdr"])<0.05)
prim_nt=sum(1 for r in prim if r["test_used"]=="not testable")
s2=[r for r in frows if "all comparisons jointly" not in r["multiplicity"]]
grow=[r for r in frows if "all comparisons jointly" in r["multiplicity"]]
fam_sig=int(s2[0]["significant_fdr_0_05"]) if s2 else ""
glob_sig=int(grow[0]["significant_fdr_0_05"]) if grow else ""
sens_nt=sum(1 for r in srows if r["test_used"]=="not testable")
sens_tab=sum(1 for r in srows if r["test_used"]!="not testable")
print(f"primary: {len(prim)} comparisons, {prim_nt} not testable, {prim_fam} significant (family BH)")
print(f"min-10-cells sensitivity: {len(srows)} comparisons, {sens_nt} not testable, family BH significant={[r['significant_family_bh'] for r in srows][0] if srows else '?'}")
print(f"global BH: primary significant={glob_sig} | sensitivity significant={[r['significant_global_bh'] for r in srows][0] if srows else '?'}")
# ---- manuscript additions ----
mp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mp,encoding="utf-8").read()
add=(" Single-cell sensitivity analyses are shipped. (i) Minimum cells per donor: donor means were rebuilt keeping only donors that contribute at least "
      "ten cells to the cell type and arm, which leaves {t} testable comparisons and {nt} not testable, with {sf} significant at FDR below 0.05 under the "
      "primary family definition. (ii) Multiplicity strategy: under the primary strategy (Benjamini-Hochberg within context x module x comparison type) "
      "{pf} of the {pc} comparisons reach FDR below 0.05, whereas a single joint Benjamini-Hochberg correction across all comparisons leaves {gs}, "
      "which quantifies how much of the single-cell layer is descriptive rather than confirmatory.").format(
      t=sens_tab, nt=sens_nt, sf=[r['significant_family_bh'] for r in srows][0] if srows else "not applicable",
      pf=prim_fam, pc=len(prim), gs=glob_sig)
anchor="Survival layer: proportional hazards was not violated"
if anchor in md:
    md=md.replace(anchor, add.strip()+" "+anchor, 1)
else:
    md=md.rstrip()+"\n"+add+"\n"
open(mp,"w",encoding="utf-8").write(md); print("manuscript updated with both sensitivity results")
# ---- tables: S17 ----
q=os.path.join(V14,"scripts","71_v14_tables_legends.py"); t=open(q,encoding="utf-8").read()
if "Supplementary Table S17" not in t:
    t=t.replace('tp=os.path.join(OUT,"Tables_v14.docx")',
'''head(doc,"Supplementary Table S17. Single-cell sensitivity analyses")
three_line(doc,["Analysis","Comparisons","Not testable","Significant (FDR < 0.05)"],[
 ["Primary: donor means from all cells; BH within context x module x comparison type", len(rd(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"))), prim_nt, prim_fam],
 ["Sensitivity 1: only donors contributing at least ten cells per cell type and arm", len(rd(os.path.join(PK,"06_single_cell","single_cell_sensitivity_min10cells_per_donor.csv"))), sens_nt2, sens_fam2],
 ["Sensitivity 2: same donors, BH across all comparisons jointly", len(rd(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"))), prim_nt, glob_sig2)],8)
tp=os.path.join(OUT,"Tables_v14.docx")''')
    t=t.replace('doc=Document(); st=doc.styles[\'Normal\']',
'''scp=rd(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"))
prim_nt=sum(1 for r in scp if r["test_used"]=="not testable")
prim_fam=sum(1 for r in scp if r["fdr"] not in ("","nan") and float(r["fdr"])<0.05)
scs=rd(os.path.join(PK,"06_single_cell","single_cell_sensitivity_min10cells_per_donor.csv"))
sens_nt2=sum(1 for r in scs if r["test_used"]=="not testable")
sens_fam2=sum(1 for r in scs if r["fdr_family"] not in ("","nan") and float(r["fdr_family"])<0.05)
scf=rd(os.path.join(PK,"06_single_cell","single_cell_multiplicity_strategy_comparison.csv"))
glob_sig2=next((r["significant_fdr_0_05"] for r in scf if "jointly" in r["multiplicity"]), "not available")
glob_sig2=int(glob_sig2) if str(glob_sig2).isdigit() else "not available"
doc=Document(); st=doc.styles['Normal']''')
    open(q,"w",encoding="utf-8").write(t); print("tables builder extended with S17")
else:
    print("S17 already present")
# ---- response document ----
rp=os.path.join(V14,"06_三路冷读审稿意见与处置_v14.md"); rt=open(rp,encoding="utf-8").read()
rt=rt.replace("5. **单细胞每供者最少细胞数**、**全局 FDR 敏感性**：仍未做（已在正文列为局限）。",
 f"5. ~~单细胞每供者最少细胞数~~、~~全局 FDR 敏感性~~ **均已完成**：≥10 细胞/供者的敏感性重建出 {len(srows)} 个比较（{sens_nt} 个不可检验），家族 BH 显著 {[r['significant_family_bh'] for r in srows][0] if srows else 'n/a'} 个；全局 BH 下主分析仅 {glob_sig} 个显著（家族 BH 为 {prim_fam}），二者随包（`06_single_cell/single_cell_sensitivity_min10cells_per_donor.csv`、`single_cell_multiplicity_strategy_comparison.csv`，Table S17）。")
open(rp,"w",encoding="utf-8").write(rt); print("response document updated")
