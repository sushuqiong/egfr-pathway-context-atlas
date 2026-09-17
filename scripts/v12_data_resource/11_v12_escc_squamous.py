#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: restrict the TCGA-ESCA layer to squamous-cell carcinoma patients (patient-level DISEASE_TYPE)
and rebuild the mutation / CNA / survival input tables on that subset."""
import csv, json, os, collections
RAW=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\data_raw\cbio_v3"
A  =r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results"
V  =r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
OUT=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12\results"; os.makedirs(OUT,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# --- 1. histology from patient-level clinical attributes ---
pat=json.load(open(os.path.join(RAW,"ESCC_clinical_patient_raw.json")))
hist={}
for r in pat:
    if r.get("clinicalAttributeId") in ("DISEASE_TYPE","PRIMARY_DIAGNOSIS"):
        hist.setdefault(r["patientId"], r["value"])
squamous={p for p,v in hist.items() if "Squamous" in v}
adeno={p for p,v in hist.items() if "Adenocarcinoma" in v}
print(f"patients: total={len(hist)} squamous={len(squamous)} adeno={len(adeno)} other={len(set(hist)-squamous-adeno)}")
smp=json.load(open(os.path.join(RAW,"ESCC_clinical_sample_raw.json")))
s2p={}
for r in smp:
    if r.get("clinicalAttributeId")=="ONCOTREE_CODE": s2p.setdefault(r["sampleId"], r["patientId"])
expr=rd(os.path.join(A,"cbio_v3_expression_gene_sample.csv"))
escc_expr=collections.defaultdict(set)
for r in expr:
    if r["context"]=="ESCC": escc_expr[r["sample_id"]].add(r["patient_id"])
# sample -> patient using expression table (authoritative for our layer)
sid2pid={s:list(ps)[0] for s,ps in escc_expr.items()}
sq_smp={s for s,p in sid2pid.items() if p in squamous}
print(f"expression samples: total={len(sid2pid)} squamous={len(sq_smp)} adeno={len({s for s,p in sid2pid.items() if p in adeno})}")
wr([dict(sample_id=s, patient_id=sid2pid[s], disease_type=hist.get(sid2pid[s],""), histology_group="squamous") for s in sorted(sq_smp)],
   os.path.join(OUT,"v12_escc_squamous_samples.csv"))
# --- 2. mutation layer on squamous subset ---
mut=rd(os.path.join(A,"cbio_v3_mutations.csv"))
prof=rd(os.path.join(V,"v11_mut_profiled_samples.csv"))
prof_sq={r["sample_id"] for r in prof if r["context"]=="ESCC"} & sq_smp
print(f"mutation-profiled samples: all={sum(1 for r in prof if r['context']=='ESCC')} squamous={len(prof_sq)}")
rows=[]
for gene in ["KRAS","TP53","EGFR","ERBB2"]:
    mutated={r["sample_id"] for r in mut if r["context"]=="ESCC" and r["gene"]==gene} & prof_sq
    rows.append(dict(context="ESCC_squamous", gene=gene, n_mutated_samples=len(mutated), denominator_n=len(prof_sq),
                     pct=round(100*len(mutated)/len(prof_sq),2) if prof_sq else ""))
wr(rows, os.path.join(OUT,"v12_escc_mutation_denominators.csv"))
print("mutation (squamous):", [(r['gene'],r['n_mutated_samples'],r['pct']) for r in rows])
# --- 3. CNA layer on squamous subset ---
cna=rd(os.path.join(A,"cbio_v3_cna_gene_sample.csv"))
cna_sq=[r for r in cna if r["context"]=="ESCC" and r.get("sample_id") in sq_smp]
denom=len({r["sample_id"] for r in cna_sq})
rows=[]
for gene in ["EGFR","ERBB2","MET"]:
    vals=[r for r in cna_sq if r["gene"]==gene]
    n2=len({r["sample_id"] for r in vals if r["value"] not in ("","NA") and float(r["value"])==2})
    n1=len({r["sample_id"] for r in vals if r["value"] not in ("","NA") and float(r["value"])>=1})
    rows.append(dict(context="ESCC_squamous", gene=gene, n_cna_profiled=denom, n_high_amp=n2, pct_high_amp=round(100*n2/denom,2) if denom else "",
                     n_gain_or_amp=n1, pct_gain=round(100*n1/denom,2) if denom else ""))
wr(rows, os.path.join(OUT,"v12_escc_cna_summary.csv"))
print("CNA (squamous):", [(r['gene'],r['n_high_amp'],r['pct_high_amp']) for r in rows])
# --- 4. survival input table on squamous subset ---
sc=rd(os.path.join(A,"cbio_v3_patient_module_scores.csv"))
clin=rd(os.path.join(A,"cbio_v3_clinical_patient.csv"))
time={ (r["patient_id"]):(r["value"]) for r in clin if r["context"]=="ESCC" and r["clinical_attribute_id"]=="OS_MONTHS" }
stat={ (r["patient_id"]):(r["value"]) for r in clin if r["context"]=="ESCC" and r["clinical_attribute_id"]=="OS_STATUS" }
age ={ (r["patient_id"]):(r["value"]) for r in clin if r["context"]=="ESCC" and r["clinical_attribute_id"]=="AGE" }
stage={ (r["patient_id"]):(r["value"]) for r in clin if r["context"]=="ESCC" and r["clinical_attribute_id"].startswith(("PATH_STAGE","CLINICAL_STAGE","AJCC")) }
rows=[]
for r in sc:
    if r["context"]!="ESCC": continue
    p=r["patient_id"]
    if p not in squamous: continue
    rows.append(dict(patient_id=p, module=r["module"], score=r["score"], OS_MONTHS=time.get(p,""), OS_STATUS=stat.get(p,""), AGE=age.get(p,"")))
wr(rows, os.path.join(OUT,"v12_escc_squamous_module_os_input.csv"))
print(f"survival input rows={len(rows)} patients={len({r['patient_id'] for r in rows})}")
print("done ->", OUT)
