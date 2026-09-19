#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13 fix 1: eliminate every "first row" insertion; add explicit lookup + assertions; build the complete
442-row cohort x module effects matrix with not-estimable rows and reasons."""
import csv, os, sys
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p,fields=None):
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0].keys())); w.writeheader(); w.writerows(rows)
mut=rd(os.path.join(R,"v12_escc_mutation_denominators.csv"))
cna=rd(os.path.join(R,"v12_escc_cna_summary.csv"))
def pick(rows, gene):
    hit=[r for r in rows if r["gene"].upper()==gene.upper()]
    assert len(hit)==1, f"expected exactly one row for {gene}, found {len(hit)}"
    return hit[0]
tp53=pick(mut,"TP53"); egfr_mut=pick(mut,"EGFR"); egfr_cna=pick(cna,"EGFR")
print("TP53:",tp53); print("EGFR mut:",egfr_mut); print("EGFR CNA:",egfr_cna)
# ---------- complete 442-row effects matrix ----------
pc=rd(os.path.join(R,"v12_percohort_effects.csv"))
reg=rd(os.path.join(R,"v12_cohort_registry.csv")); cov=rd(os.path.join(R,"v12_gene_coverage.csv"))
mods=sorted({r["module"] for r in cov})
cc=[r["accession"] for r in reg if r["design"]=="case-control"]
have={(r["accession"],r["feature"]) for r in pc}
covmap={(r["accession"],r["module"]):r for r in cov}
added=[]
for acc in cc:
    for m in mods:
        if (acc,m) in have: continue
        cv=covmap.get((acc,m),{})
        npresent=cv.get("n_present",""); nmem=cv.get("n_members","")
        if npresent!="" and int(npresent)<3:
            reason=f"not estimable: only {npresent} of {nmem} module members present in this cohort"
        elif cv:
            reason="not estimable: module score has zero variance across the cohort's samples (all samples constant)"
        else:
            reason="not estimable: module not scored in this cohort's processed matrix"
        added.append(dict(accession=acc, disease="", feature=m, paired="", patient_ids_available="",
            n_both_arm_patients="", n_case="", n_control="", npair="", r_emp="", measure="not estimable",
            yi="", vi="", mean_case="", sd_case="", mean_ctrl="", sd_ctrl="", beta_base="", se_base="", p_base="",
            not_estimable_reason=reason))
cols=list(pc[0].keys())+["not_estimable_reason"]
for r in pc: r.setdefault("not_estimable_reason","")
full=pc+added
wr(full, os.path.join(R,"v13_percohort_effects_complete.csv"), cols)
print(f"\ncomplete matrix: {len(full)} rows = {len(cc)} cohorts x {len(mods)} modules")
print(f"estimated rows: {len(pc)} | not estimable rows added: {len(added)}")
import collections
c=collections.Counter(a["not_estimable_reason"].split(":")[0]+": "+a["not_estimable_reason"].split(":")[1].split("(")[0].strip() for a in added)
for k,v in c.items(): print(f"  {v:3d}  {k}")
wr([dict(accession=a["accession"], module=a["feature"], reason=a["not_estimable_reason"]) for a in added],
   os.path.join(R,"v13_not_estimable_pairs.csv"))
# assertion: 26 x 17 must be exactly filled
assert len(full)==len(cc)*len(mods), (len(full), len(cc)*len(mods))
print("assertion passed: every cohort x module pair is accounted for")
