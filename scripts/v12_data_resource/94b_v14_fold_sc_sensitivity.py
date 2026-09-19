#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: fold the two single-cell sensitivity analyses into package, manuscript, tables and response document."""
import csv, os, shutil
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
SC=os.path.join(PK,"06_single_cell"); os.makedirs(SC,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
sens=os.path.join(R,"v14_sc_sensitivity_mindonorcells10.csv"); fdr=os.path.join(R,"v14_sc_fdr_strategy_comparison.csv")
srows=rd(sens); frows=rd(fdr)
shutil.copy(sens, os.path.join(SC,"single_cell_sensitivity_min10cells_per_donor.csv"))
shutil.copy(fdr, os.path.join(SC,"single_cell_multiplicity_strategy_comparison.csv"))
prim=rd(os.path.join(SC,"single_cell_comparisons.csv"))
def num(v):
    try: return float(v)
    except Exception: return None
prim_fam=sum(1 for r in prim if num(r.get("fdr")) is not None and num(r["fdr"])<0.05)
prim_nt=sum(1 for r in prim if r["test_used"]=="not testable")
sens_fam=sum(1 for r in srows if num(r.get("fdr_family")) is not None and num(r["fdr_family"])<0.05)
sens_glob=sum(1 for r in srows if num(r.get("fdr_global")) is not None and num(r["fdr_global"])<0.05)
sens_nt=sum(1 for r in srows if r["test_used"]=="not testable")
glob_sig=next((int(r["significant_fdr_0_05"]) for r in frows if "jointly" in r["multiplicity"] and str(r["significant_fdr_0_05"]).isdigit()), "not available")
print(f"primary: {len(prim)} comparisons | {prim_nt} not testable | {prim_fam} significant (family BH) | global BH {glob_sig}")
print(f"sensitivity >=10 cells/donor: {len(srows)} comparisons | {sens_nt} not testable | {sens_fam} significant (family BH) | global BH {sens_glob}")
# manuscript
mp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mp,encoding="utf-8").read()
sent=("Single-cell sensitivity analyses are shipped. (i) Minimum cells per donor: rebuilding donor means with only donors that contribute at least ten cells "
      f"to the cell type and arm leaves {len(srows)} comparisons, of which {len(srows)-sens_nt} are testable and {sens_fam} reach FDR below 0.05 under the primary "
      f"family definition (the primary analysis has {len(prim)} comparisons, {len(prim)-prim_nt} testable and {prim_fam} significant; dropping low-cell donors makes "
      "some arms donor-disjoint and therefore testable by the unpaired rule, which is why the testable count does not simply fall). (ii) Multiplicity strategy: "
      f"the primary strategy (Benjamini-Hochberg within context x module x comparison type) yields {prim_fam} significant comparisons out of {len(prim)}, whereas a "
      f"single joint correction across all comparisons yields {glob_sig}, so {prim_fam-glob_sig} comparisons depend on the family definition and the single-cell layer "
      "is reported as descriptive.")
if "Minimum cells per donor: rebuilding donor means" not in md:
    a="Survival layer: proportional hazards was not violated"
    md = md.replace(a, sent+" "+a,1) if a in md else md.rstrip()+"\n"+sent+"\n"
    open(mp,"w",encoding="utf-8").write(md); print("manuscript updated")
# tables S17
q=os.path.join(V14,"scripts","71_v14_tables_legends.py"); t=open(q,encoding="utf-8").read()
if "Supplementary Table S17" not in t:
    t=t.replace("doc=Document(); st=doc.styles['Normal']",
'''scp=rd(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"))
def _n(v):
    try: return float(v)
    except Exception: return None
_prim_nt=sum(1 for r in scp if r["test_used"]=="not testable")
_prim_fam=sum(1 for r in scp if _n(r.get("fdr")) is not None and _n(r["fdr"])<0.05)
_scs=rd(os.path.join(PK,"06_single_cell","single_cell_sensitivity_min10cells_per_donor.csv"))
_nt2=sum(1 for r in _scs if r["test_used"]=="not testable")
_fam2=sum(1 for r in _scs if _n(r.get("fdr_family")) is not None and _n(r["fdr_family"])<0.05)
_gl2=sum(1 for r in _scs if _n(r.get("fdr_global")) is not None and _n(r["fdr_global"])<0.05)
_scf=rd(os.path.join(PK,"06_single_cell","single_cell_multiplicity_strategy_comparison.csv"))
_glp=next((r["significant_fdr_0_05"] for r in _scf if "jointly" in r["multiplicity"]), "not available")
doc=Document(); st=doc.styles['Normal']''',1)
    t=t.replace('tp=os.path.join(OUT,"Tables_v14.docx")',
'''head(doc,"Supplementary Table S17. Single-cell sensitivity analyses")
three_line(doc,["Analysis","Comparisons","Not testable","Significant, FDR < 0.05"],[
 ["Primary: donor means from all cells; BH within context x module x comparison type", len(scp), _prim_nt, _prim_fam],
 ["Sensitivity 1: only donors contributing at least ten cells per cell type and arm", len(_scs), _nt2, _fam2],
 ["Sensitivity 2: same donors, single BH correction across all comparisons", len(_scs), _nt2, _gl2],
 ["Primary under a single BH correction across all comparisons (for reference)", len(scp), _prim_nt, _glp]],8)
tp=os.path.join(OUT,"Tables_v14.docx")''',1)
    open(q,"w",encoding="utf-8").write(t); print("tables builder extended with S17")
# response document
rp=os.path.join(V14,"06_三路冷读审稿意见与处置_v14.md"); rt=open(rp,encoding="utf-8").read()
old5="5. **单细胞每供者最少细胞数**、**全局 FDR 敏感性**：仍未做（已在正文列为局限）。"
new5=(f"5. ~~单细胞每供者最少细胞数~~、~~全局 FDR 敏感性~~ **均已完成**：≥10 细胞/供者重建后 {len(srows)} 个比较（{len(srows)-sens_nt} 可检验、"
      f"{sens_fam} 个家族 BH 显著）；全局 BH 下主分析 {prim_fam}→{glob_sig}、敏感性分析 {sens_fam}→{sens_glob} 个显著。随包："
      "`06_single_cell/single_cell_sensitivity_min10cells_per_donor.csv`、`single_cell_multiplicity_strategy_comparison.csv`（Table S17）。")
rt=rt.replace(old5,new5); open(rp,"w",encoding="utf-8").write(rt); print("response document updated")
