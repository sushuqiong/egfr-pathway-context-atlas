#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: registry enhancement (design, patient-identity availability, provenance), checksums,
file inventory, and an offline input matrix for reuse example 1."""
import csv, os, hashlib, shutil, glob, collections
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p,fields=None):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0].keys())); w.writeheader(); w.writerows(rows)
reg=rd(os.path.join(R,"v12_cohort_registry.csv")); aud={r["accession"]:r for r in rd(os.path.join(R,"v12_dedup_patient_audit.csv"))}
CTX={"GSE32863":"LUAD","GSE19804":"LUAD","GSE10072":"LUAD","GSE44076":"CRC","GSE41258":"CRC","GSE23878":"CRC",
     "GSE75214":"IBD","GSE87473":"IBD","GSE179285":"IBD","GSE16879":"IBD","GSE4302":"Asthma","GSE43696":"Asthma",
     "GSE67472":"Asthma","GSE27342":"STAD","GSE63089":"STAD","GSE13911":"STAD","GSE15471":"PAAD","GSE28735":"PAAD",
     "GSE62452":"PAAD","GSE57957":"HCC","GSE62232":"HCC","GSE23400":"ESCC","GSE20347":"ESCC","GSE76925":"COPD",
     "GSE47460":"COPD","GSE33814":"NAFLD","GSE66676":"NAFLD"}
# origin PMIDs
pmids={}
for cand in ["TableS1b_cohort_pubmed_map.csv","TableS1_accessions.csv"]:
    p=os.path.join(PK,"01_cohort_registry",cand)
    if os.path.exists(p):
        for r in rd(p):
            keys=[k for k in r if k.lower() in ("accession","gse","series","cohort")]
            if keys: pmids[r[keys[0]]]=r.get("pmid") or r.get("PMID") or r.get("pubmed_id") or ""
rows=[]
for r in reg:
    a=r["accession"]; A=aud.get(a,{})
    has_pid = str(A.get("patient_id_present","")).upper()=="TRUE" and int(A.get("n_unique_patient_id",0) or 0) > 1
    both = int(A.get("patients_with_both_arms",0) or 0) if A.get("patients_with_both_arms") not in ("","NA",None) else 0
    design = "treatment-response (excluded from case-control analyses)" if a=="GSE16879" else "case-control"
    rows.append(dict(accession=a, context=CTX.get(a,""), platform=r["platform"],
        n_assay_records=r["n_assay_records"], n_unique_samples=r["n_unique_samples"],
        n_unique_patients=(A.get("n_unique_patient_id") if has_pid else "not provided"),
        patient_identity_available=("yes" if has_pid else "no"),
        n_case=r["n_case"], n_control=r["n_control"], patients_with_both_arms=both,
        paired_design_used=("yes" if (has_pid and both>=4) else "no"),
        design=design, included_in_estimates=("no" if a=="GSE16879" else "yes"),
        origin_pmid=pmids.get(a,""), provenance="processed matrices prepared from the public series (see 03_expression/transformation_log.csv)"))
wr(rows, os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
wr(rows, os.path.join(R,"v12_cohort_registry.csv"))
print("registry rows:",len(rows),"| case-control:",sum(1 for r in rows if r["design"]=="case-control"),
      "| paired used:",sum(1 for r in rows if r["paired_design_used"]=="yes"),
      "| patient ids missing:",sum(1 for r in rows if r["patient_identity_available"]=="no"))
# ---- file inventory + checksums ----
inv=[]; 
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK)
        h=hashlib.sha256()
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
print("inventory files:",len(inv),"| total MB:",round(sum(r['bytes'] for r in inv)/1e6,2))
# ---- offline demo input for reuse example 1 ----
demo_dir=os.path.join(PK,"09_reuse_examples","example_input"); os.makedirs(demo_dir,exist_ok=True)
src=None
for root in [r"C:\Users\fengq\Desktop\EGFR\EGFR_context_expansion\data_processed\bulk",
             r"C:\Users\fengq\Desktop\EGFR\EGFR_ERBB_context_project_v2\data_processed\bulk"]:
    c=glob.glob(os.path.join(root,"GSE13911_processed.rds"))
    if c: src=c[0]; break
if src:
    import subprocess
    rcode=f'''
suppressPackageStartupMessages({{library(dplyr)}})
o <- readRDS("{src.replace(chr(92),"/")}")
ex <- o$gene_expression; md <- o$sample_metadata
v <- apply(log2(ex+1), 1, var, na.rm=TRUE)
keep <- names(sort(v, decreasing=TRUE))[1:1500]
sub <- ex[keep, 1:min(20, ncol(ex))]
sub <- round(log2(sub+1), 4)
write.csv(sub, "09_reuse_examples/example_input/demo_expression_matrix.csv")
meta <- data.frame(sample_id=colnames(sub), group=as.character(md$group[1:ncol(sub)]))
write.csv(meta, "09_reuse_examples/example_input/demo_sample_metadata.csv", row.names=FALSE)
cat("demo matrix:", nrow(sub), "genes x", ncol(sub), "samples\\n")
'''
    open(os.path.join(V12,"scripts","_tmp_demo.R"),"w",encoding="utf-8").write(rcode)
    print("demo script written; run it from dataset_package root")
else:
    print("[WARN] GSE13911 not found for demo matrix")
