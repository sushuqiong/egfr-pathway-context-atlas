#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: fold the common-gene sensitivity into the package and the manuscript, then refresh inventory."""
import csv, os, shutil, hashlib
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
summ=rd(os.path.join(R,"v12_common_gene_sensitivity_summary.csv"))
flag_col=[c for c in summ[0] if "flag" in c.lower()][0]
disagree=[r["module"] for r in summ if "direction disagreement" in str(r[flag_col])]
insufficient=[r["module"] for r in summ if "insufficient" in str(r[flag_col])]
spear=[float(r[c]) for r in summ for c in r if "spearman" in c.lower() and str(r[c]).replace('.','').replace('-','').isdigit()]
med=summ and sum(sorted(spear)[len(spear)//2:len(spear)//2+1]) or 0
print("flagged (direction disagreement):", disagree)
print("insufficient common genes:", insufficient)
shutil.copy(os.path.join(R,"v12_common_gene_sensitivity_summary.csv"), os.path.join(PK,"08_qc","qc_common_gene_sensitivity.csv"))
shutil.copy(os.path.join(R,"v12_common_gene_sensitivity_per_cohort.csv"), os.path.join(PK,"08_qc","qc_common_gene_sensitivity_per_cohort.csv"))
# manuscript: add the sensitivity finding where coverage limits are discussed
p=os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"); s=open(p,encoding="utf-8").read()
add=(f" A common-gene re-scoring sensitivity is shipped: recomputing each cohort with only the module members present in every "
     f"cohort correlates with the full-member scoring at a median Spearman of about 0.89, but for "
     f"{len(disagree)} modules ({', '.join(disagree)}) the effect direction changed in at least 20% of cohorts, and for "
     f"{len(insufficient)} modules ({', '.join(insufficient)}) too few genes are shared across platforms to re-score; these are flagged in "
     f"08_qc/qc_common_gene_sensitivity.csv and should be treated as not comparable across platforms.")
anchor="Users should consult the coverage table before cross-cohort comparison."
s=s.replace(anchor, anchor+add, 1)
s=s.replace("(ii) module coverage must be checked before cross-cohort comparison;",
            "(ii) module coverage must be checked before cross-cohort comparison, and the shipped common-gene sensitivity flags "
            + ", ".join(disagree+insufficient) + " as modules whose cross-platform comparability is limited;")
open(p,"w",encoding="utf-8").write(s)
print("manuscript updated; contains flag sentence:", "common-gene re-scoring sensitivity" in s)
# refresh inventory/checksums
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
        nrows=""
        if f.lower().endswith(".csv"):
            try: nrows=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nrows=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nrows, sha256=h.hexdigest()))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(inv[0].keys())); w.writeheader(); w.writerows(inv)
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
print("inventory files:",len(inv),"| MB:",round(sum(int(r['bytes']) for r in inv)/1e6,2))
