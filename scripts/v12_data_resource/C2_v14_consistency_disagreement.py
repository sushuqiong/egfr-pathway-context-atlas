#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (C2): explain the 68% cross-cohort direction consistency.

For every context-module pair the per-cohort effects are inspected so that the manuscript can say where the
disagreement actually sits (how many cohorts, which contexts, which modules) instead of leaving 68% open to
misreading.
"""
import csv, collections, os, statistics
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
def rd(p):
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
cons=rd(os.path.join(R,"v13_qc_cross_cohort_consistency.csv"))
eff=rd(os.path.join(R,"v13_percohort_effects_complete.csv")) or rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
by={}
for r in eff:
    try: yi=float(r["yi"])
    except Exception: continue
    by.setdefault((r["disease"],r["feature"]),[]).append((r["accession"],yi))
rows=[]
for c in cons:
    k=int(c["k"])
    if k<2: continue
    yis=by.get((c["disease"],c["feature"]),[])
    pos=[a for a,y in yis if y>0]; neg=[a for a,y in yis if y<0]
    rows.append(dict(context=c["disease"], module=c["feature"], k=k,
                     cohorts_positive=len(pos), cohorts_negative=len(neg),
                     median_effect=round(float(c["median_yi"]),3), direction_consistent=c["direction_consistent"],
                     pattern=("all positive" if not neg else "all negative" if not pos else f"{len(pos)} positive / {len(neg)} negative"),
                     positive_cohorts=";".join(pos[:6]), negative_cohorts=";".join(neg[:6]),
                     range_of_effects=f"{min(y for _,y in yis):.2f} to {max(y for _,y in yis):.2f}" if yis else ""))
with open(os.path.join(PK,"08_qc","qc_cross_cohort_disagreement_detail.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
inc=[r for r in rows if str(r["direction_consistent"]).upper()!="TRUE"]
con_=[r for r in rows if str(r["direction_consistent"]).upper()=="TRUE"]
by_k=collections.Counter(r["k"] for r in inc)
by_ctx=collections.Counter(r["context"] for r in inc)
by_mod=collections.Counter(r["module"] for r in inc)
split_two=sum(1 for r in inc if r["k"]==2)
split_k3=sum(1 for r in inc if r["k"]==3)
small_split=sum(1 for r in inc if r["cohorts_positive"]<=1 or r["cohorts_negative"]<=1)
k_hi=[r for r in rows if r["k"]>=5]
k_hi_con=sum(1 for r in k_hi if str(r["direction_consistent"]).upper()=="TRUE")
summary=[dict(metric="pairs with at least two cohorts", value=len(rows)),
         dict(metric="pairs consistent in every cohort", value=len(con_)),
         dict(metric="pairs with at least one discordant cohort", value=len(inc)),
         dict(metric="inconsistent pairs with k = 2", value=split_two),
         dict(metric="inconsistent pairs with k = 3", value=split_k3),
         dict(metric="inconsistent pairs decided by a single opposing cohort", value=small_split),
         dict(metric="inconsistent pairs by context (top)", value="; ".join(f"{k} {v}" for k,v in by_ctx.most_common(4))),
         dict(metric="inconsistent pairs by module (top)", value="; ".join(f"{k} {v}" for k,v in by_mod.most_common(4))),
         dict(metric="consistency among pairs with k >= 5", value=f"{k_hi_con}/{len(k_hi)} ({100*k_hi_con/max(1,len(k_hi)):.0f}%)"),
         dict(metric="consistency among pairs with k = 2", value=f"{sum(1 for r in rows if r['k']==2 and str(r['direction_consistent']).upper()=='TRUE')}/{sum(1 for r in rows if r['k']==2)}")]
with open(os.path.join(PK,"08_qc","qc_cross_cohort_disagreement_summary.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["metric","value"],lineterminator="\n"); w.writeheader(); w.writerows(summary)
print("pairs:",len(rows),"| consistent:",len(con_),"| inconsistent:",len(inc))
for s in summary: print(f"  {s['metric']}: {s['value']}")
print("\nnamed examples (largest k among inconsistent pairs):")
for r in sorted(inc,key=lambda x:-x["k"])[:6]:
    print(f"  {r['context']}/{r['module']}: k={r['k']}, {r['pattern']} ({r['positive_cohorts']} | {r['negative_cohorts']}), median {r['median_effect']}")
