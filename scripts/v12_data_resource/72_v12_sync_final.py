#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final v12 sync: refresh package estimates/QC tables, fix the patient-identifier flag,
regenerate inventory and checksums, and update the v12 check script expectations."""
import csv, os, shutil, hashlib, re
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# 1. per-cohort effects: fix the patient-identifier flag using the integrity audit
aud={r["accession"]:r for r in rd(os.path.join(R,"v12_dedup_patient_audit.csv"))}
pc=rd(os.path.join(R,"v12_percohort_effects.csv"))
nofix=0
for r in pc:
    a=r["accession"]; A=aud.get(a,{})
    npid=int(A.get("n_unique_patient_id",0) or 0)
    real = str(A.get("patient_id_present","")).upper()=="TRUE" and npid>1
    if str(r.get("patient_ids_available","")).upper()!=str(real).upper(): nofix+=1
    r["patient_ids_available"]=str(real).upper()
    if not real: r["n_both_arm_patients"]="0"
wr(pc, os.path.join(R,"v12_percohort_effects.csv")); wr(pc, os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
print("per-cohort rows:",len(pc),"| patient-identifier flags corrected:",nofix)
# 2. refresh meta + QC tables in the package
copy=[(os.path.join(R,"v12_meta_primary_reml_knha.csv"),"meta_primary_reml_knha.csv"),
      (os.path.join(R,"v12_meta_DL.csv"),"meta_dersimonian_laird.csv"),
      (os.path.join(R,"v12_meta_adhoc.csv"),"meta_adhoc_knapp_hartung.csv"),
      (os.path.join(R,"v12_meta_unpaired_only.csv"),"meta_unpaired_only.csv"),
      (os.path.join(R,"v12_meta_rho0.5.csv"),"meta_rho0.5_sensitivity.csv"),
      (os.path.join(R,"v12_meta_rho0.7.csv"),"meta_rho0.7_sensitivity.csv"),
      (os.path.join(R,"v12_qc_cox_ph_assumption.csv"),"qc_cox_proportional_hazards.csv"),
      (os.path.join(R,"v12_qc_composition_collinearity.csv"),"qc_composition_collinearity.csv"),
      (os.path.join(R,"v12_qc_composition_join_audit.csv"),"qc_composition_join_audit.csv"),
      (os.path.join(R,"v12_sample_ids_all.csv"),"sample_ids_all_cohorts.csv"),
      (os.path.join(R,"v12_dedup_patient_audit.csv"),"sample_dedup_patient_audit.csv")]
for src,name in copy:
    dst=os.path.join(PK,"08_qc",name) if name.startswith("qc_") or name.startswith("sample_") else os.path.join(PK,"07_estimates",name)
    if os.path.exists(src): shutil.copy(src,dst)
# composition model summary (from the v11 joint layer; cohort set unchanged)
if os.path.exists(os.path.join(V11,"v11_joint_summary.csv")):
    shutil.copy(os.path.join(V11,"v11_joint_summary.csv"), os.path.join(PK,"07_estimates","composition_model_summary.csv"))
# 3. exclusion log addition: treatment-response series + design corrections
ex=rd(os.path.join(PK,"08_qc","exclusion_and_flag_log.csv"))
ex.append(dict(item="Treatment-response series excluded from case-control resource (GSE16879, Responder vs NonResponder)", n=43,
               reason="design is treatment response, not case-control; listed in the registry with its design flag", layer="bulk"))
ex.append(dict(item="Cohorts analysed as unpaired because no patient identifiers are provided", n=9,
               reason="patient-level pairing cannot be established; flagged in the registry and in the per-cohort table", layer="bulk"))
ex.append(dict(item="Cohorts reclassified as paired after metadata-driven audit", n=3,
               reason="GSE41258, GSE13911 and GSE179285 contain >=4 patients with both arms; previously analysed as unpaired", layer="statistics"))
wr(ex, os.path.join(PK,"08_qc","exclusion_and_flag_log.csv"))
# 4. inventory + checksums
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for chunk in iter(lambda: fh.read(1<<20), b""): h.update(chunk)
        nrows=""
        if f.lower().endswith(".csv"):
            try: nrows=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nrows=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nrows, sha256=h.hexdigest()))
wr(inv, os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
print("inventory:",len(inv),"files |",round(sum(int(r['bytes']) for r in inv)/1e6,2),"MB")
# 5. update the check script expectations (26 case-control cohorts)
c=open(os.path.join(V12,"scripts","90_v12_checks.py"),encoding="utf-8").read()
c=c.replace('chk(f"{n_c} case-control expression cohorts" in md or True','chk(f"{n_c} case-control expression cohorts" in md')
open(os.path.join(V12,"scripts","90_v12_checks.py"),"w",encoding="utf-8").write(c)
print("checks script updated")
