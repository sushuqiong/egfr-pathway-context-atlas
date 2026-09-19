#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13: curation flow counts (screening denominators) as required by both reviewers."""
import csv, os, glob, collections
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results")
roots=[r"C:\Users\fengq\Desktop\EGFR\EGFR_ERBB_context_project_v2\data_processed\bulk",
       r"C:\Users\fengq\Desktop\EGFR\EGFR_context_expansion\data_processed\bulk",
       r"C:\Users\fengq\Desktop\EGFR\EGFR胃癌\EGFR_ERBB_context_project_v1\data_processed\bulk"]
present=set()
for d in roots:
    for f in glob.glob(os.path.join(d,"*_processed.rds")):
        present.add(os.path.basename(f).replace("_processed.rds",""))
reg=list(csv.DictReader(open(os.path.join(V13,"dataset_package","01_cohort_registry","cohort_registry.csv"),encoding="utf-8-sig")))
used={r["accession"] for r in reg}
cc={r["accession"] for r in reg if r["design"]=="case-control"}
excl={r["accession"] for r in reg if r["design"]!="case-control"}
extra=sorted(present-used)
rows=[
 dict(step="1. Series identified across ten disease contexts", n="candidate series as listed below", detail="contexts: LUAD, CRC, STAD, PAAD, HCC, ESCC, IBD, COPD, NAFLD, asthma"),
 dict(step="2. Series with processed matrices available in this workspace", n=len(present), detail=", ".join(sorted(present))),
 dict(step="3. Series retained as case-control cohorts", n=len(cc), detail="case and control samples on the same platform (see registry)"),
 dict(step="4. Series excluded after review: treatment-response design", n=len(excl), detail=", ".join(sorted(excl))+" (Responder vs NonResponder; no case/control arm)"),
 dict(step="5. Series used only as external validation", n=len([a for a in extra if a=="GSE39582"]), detail="GSE39582 (CRC, independent platform)"),
 dict(step="6. Series evaluated but not carried forward", n=len([a for a in extra if a not in ("GSE39582",)]),
      detail=", ".join([a for a in extra if a not in ("GSE39582",)]) or "none"),
 dict(step="7. Cohorts analysed in the estimates layer", n=len(cc), detail="one cohort (GSE47460/COPD) has 15 rather than 17 estimable modules; 8 cohort-module pairs are reported as not estimable"),
 dict(step="8. Single-cell datasets reviewed", n=5, detail="CRC, IBD, STAD, asthma used; LUAD excluded (tumour-only, no control arm)"),
 dict(step="9. Tumour molecular contexts reviewed", n=6, detail="LUAD, CRC, STAD, PAAD, HCC, ESCC (oesophageal layer restricted to squamous histology)"),
]
with open(os.path.join(R,"v13_qc_curation_flow.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(f"  {r['step']}: {r['n']}")
print()
print("workspace matrices:",len(present),"| in registry:",len(used),"| unused/extra:",extra)
