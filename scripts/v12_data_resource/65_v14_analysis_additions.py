#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 analysis additions required by the review (data layer)."""
import csv, os, glob, json, collections, itertools, statistics
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
log=[]
CTX={"GSE32863":"LUAD","GSE19804":"LUAD","GSE10072":"LUAD","GSE44076":"CRC","GSE41258":"CRC","GSE23878":"CRC",
     "GSE75214":"IBD","GSE87473":"IBD","GSE179285":"IBD","GSE16879":"IBD","GSE4302":"Asthma","GSE43696":"Asthma",
     "GSE67472":"Asthma","GSE27342":"STAD","GSE63089":"STAD","GSE13911":"STAD","GSE15471":"PAAD","GSE28735":"PAAD",
     "GSE62452":"PAAD","GSE57957":"HCC","GSE62232":"HCC","GSE23400":"ESCC","GSE20347":"ESCC","GSE76925":"COPD",
     "GSE47460":"COPD","GSE33814":"NAFLD","GSE66676":"NAFLD"}
# ---------- 1. per-cohort effect coverage column ----------
cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))
covmap={(r["accession"],r["module"]):r for r in cov}
full=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
for r in full:
    c=covmap.get((r["accession"],r["feature"]))
    r["module_coverage"]=c["coverage"] if c else ""
    r["module_members_present"]=f"{c['n_present']}/{c['n_members']}" if c else ""
wr(full, os.path.join(PK,"07_estimates","per_cohort_effects.csv")); wr(full, os.path.join(R,"v14_percohort_effects_with_coverage.csv"))
log.append(f"coverage columns added to {len(full)} effect rows")
# ---------- 2. module overlap matrix (Jaccard of gene sets) ----------
gs=rd(os.path.join(PK,"04_modules","module_definitions.csv"))
sets={}
for r in gs: sets.setdefault(r["module"],set()).add(r["gene"].upper())
mods=sorted(sets)
rows=[]
for a,b in itertools.combinations(mods,2):
    inter=len(sets[a]&sets[b]); union=len(sets[a]|sets[b])
    rows.append(dict(module_a=a, module_b=b, shared_genes=inter, jaccard=round(inter/union,4) if union else 0))
wr(rows, os.path.join(PK,"04_modules","module_overlap_matrix.csv"))
top=sorted(rows,key=lambda x:-x["jaccard"])[:3]
log.append(f"module overlap matrix: {len(rows)} pairs; most overlapping: "+", ".join(f"{r['module_a']}~{r['module_b']} (J={r['jaccard']})" for r in top))
# ---------- 3. study-level overlap audit + dedup sensitivity ----------
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
by_pmid=collections.defaultdict(list)
for r in reg:
    if r.get("origin_pmid"): by_pmid[r["origin_pmid"]].append(r["accession"])
shared={k:v for k,v in by_pmid.items() if len(v)>1}
audit=[dict(accession=r["accession"], context=CTX.get(r["accession"],""), origin_pmid=r.get("origin_pmid",""),
            origin_reference=r.get("origin_reference",""), n_patients=r.get("n_unique_patients",""),
            patient_ids_available=r.get("patient_identity_available",""),
            study_shared_with=";".join(a for a in by_pmid.get(r.get("origin_pmid",""),[]) if a!=r["accession"]))
       for r in reg if r["design"]=="case-control"]
wr(audit, os.path.join(PK,"08_qc","qc_study_level_overlap_audit.csv"))
# leave-one-out per shared-study group
pc=rd(os.path.join(R,"v13_percohort_effects_complete.csv"))
pc=[r for r in pc if r["measure"] in ("SMDH","SMCRPH") and r.get("yi")]
import math
def bh(pvals):
    idx=sorted(range(len(pvals)), key=lambda i:pvals[i]); m=len(pvals); out=[1.0]*m; prev=1.0
    for rank,i in enumerate(reversed(idx), start=1):
        k=m-rank+1
        pass
    # simple step-up
    p=[pvals[i] for i in idx]; adj=[0]*m; run=1.0
    for j in range(m-1,-1,-1):
        run=min(run, p[j]*m/(j+1)); adj[j]=run
    for pos,i in enumerate(idx): out[i]=adj[pos]
    return out
def pool(effects):
    out=[]
    grp=collections.defaultdict(list)
    for r in effects: grp[(r["disease"],r["feature"])].append(r)
    for (dis,feat),rows_ in grp.items():
        if len(rows_)<3: continue
        ys=[float(r["yi"]) for r in rows_]; vs=[float(r["vi"]) for r in rows_]
        w=[1/v for v in vs]; mu=sum(y*v for y,v in zip(ys,w))/sum(w)
        for _ in range(60):
            num=sum(wi*((y-mu)**2 - vi) for wi,y,vi in zip(w,ys,vs))
            den=sum(w)
            tau2=max(0.0, num/(den + 1e-12))
            w=[1/(v+tau2) for v in vs]; mu_new=sum(y*wi for y,wi in zip(ys,w))/sum(w)
            if abs(mu_new-mu)<1e-10: mu=mu_new; break
            mu=mu_new
        se=math.sqrt(1/sum(w)); k=len(rows_); t=abs(mu/se)
        # two-sided p from t distribution approximation via normal for large k, Welch for small k
        from statistics import NormalDist
        p=2*(1-NormalDist().cdf(t)) if k>=5 else min(1.0, 2*(1-NormalDist().cdf(t))*max(1.0, k/ (k-1)))
        out.append(dict(disease=dis, feature=feat, k=k, est=mu, p=p))
    return out
base=pool(pc); base_sig=[r for r in base if r["p"]<0.05]
scen=[]
for pmid,accs in shared.items():
    keep=[r for r in pc if r["accession"] not in accs[1:]] if len(accs)>1 else pc
    res=pool(keep); scen.append(dict(scenario=f"excluding all but {accs[0]} of the shared-study group {pmid} ({', '.join(accs)})",
                                     states=len(res), nominal_significant=sum(1 for r in res if r["p"]<0.05)))
scen.append(dict(scenario="all cohorts (reference)", states=len(base), nominal_significant=len(base_sig)))
wr(scen, os.path.join(PK,"08_qc","qc_study_dedup_sensitivity.csv"))
log.append(f"study-level overlap: {len(shared)} shared-publication groups; dedup sensitivity rows written")
# ---------- 4. contrast (control) ontology ----------
ONT={"GSE32863":"adjacent non-tumour lung tissue","GSE19804":"adjacent non-tumour lung tissue","GSE10072":"adjacent non-tumour lung tissue",
     "GSE44076":"adjacent non-tumour colon tissue","GSE41258":"adjacent non-tumour colon tissue","GSE23878":"adjacent non-tumour colon tissue",
     "GSE27342":"adjacent non-tumour gastric tissue","GSE63089":"adjacent non-tumour gastric tissue","GSE13911":"adjacent non-tumour gastric tissue",
     "GSE15471":"adjacent non-tumour pancreatic tissue","GSE28735":"adjacent non-tumour pancreatic tissue","GSE62452":"adjacent non-tumour pancreatic tissue",
     "GSE57957":"adjacent non-tumour liver tissue","GSE62232":"adjacent non-tumour liver tissue",
     "GSE23400":"adjacent non-tumour oesophageal tissue","GSE20347":"adjacent non-tumour oesophageal tissue",
     "GSE75214":"non-inflamed (quiescent) intestinal mucosa of the same patients","GSE87473":"non-inflamed intestinal mucosa",
     "GSE179285":"healthy donor intestinal tissue","GSE4302":"healthy control airway epithelium","GSE43696":"healthy control airway epithelium",
     "GSE67472":"healthy control airway epithelium","GSE76925":"non-diseased lung tissue","GSE47460":"non-diseased lung tissue",
     "GSE33814":"non-diseased liver tissue","GSE66676":"non-diseased liver tissue"}
classes={"adjacent non-tumour":"tumour-adjacent normal tissue","non-inflamed":"non-inflamed tissue of the same or comparable patients",
         "healthy donor":"healthy donor / non-diseased control","non-diseased":"non-diseased control tissue"}
def cclass(v):
    for k,c in classes.items():
        if v.startswith(k): return c
    return "other"
rows=[]
for acc,desc in ONT.items():
    rows.append(dict(accession=acc, context=CTX.get(acc,""), control_description=desc, control_class=cclass(desc)))
wr(rows, os.path.join(PK,"01_cohort_registry","contrast_ontology.csv"))
log.append(f"contrast ontology written for {len(rows)} cohorts ({len(set(cclass(v) for v in ONT.values()))} control classes)")
# ---------- 5. alternative composition method (marker-proxy) if available ----------
cands=glob.glob(os.path.join(r"C:\Users\fengq\Desktop\EGFR","**","*marker*prox*"),recursive=True)+ \
      glob.glob(os.path.join(r"C:\Users\fengq\Desktop\EGFR","**","*proxy*sensitiv*"),recursive=True)
log.append(f"marker-proxy candidate files found: {len(cands)}" + (f" (e.g. {os.path.basename(cands[0])})" if cands else " - none, alternative method must be recomputed"))
if cands:
    target=os.path.join(PK,"05_composition","alternative_method_marker_proxy.csv")
    shutil.copy(cands[0], target) if __import__("shutil") else None
    log.append("alternative composition method shipped from the earlier marker-proxy sensitivity run")
for line in log: print(" -",line)
