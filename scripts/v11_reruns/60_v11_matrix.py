#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the v11 per-state evidence matrix from frozen tables (no number is hand-typed)."""
import csv, os, math
A=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results"
V=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
def rd(p):
    with open(p, encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
def fl(x):
    try: return float(x)
    except Exception: return None
raw={ (r["disease"],r["feature"]):r for r in rd(os.path.join(A,"context_atlas_summary.csv")) }
xc ={ (r["disease"],r["feature"]):r for r in rd(os.path.join(A,"xcell/context_atlas_summary_xcell_adjusted.csv")) }
meta={ (r["disease"],r["feature"]):r for r in rd(os.path.join(V,"v11_meta_primary_reml_knha.csv")) }
dl ={ (r["disease"],r["feature"]):r for r in rd(os.path.join(V,"v11_meta_DL.csv")) }
adh={ (r["disease"],r["feature"]):r for r in rd(os.path.join(V,"v11_meta_adhoc.csv")) }
jj ={ (r["disease"],r["feature"]):r for r in rd(os.path.join(V,"v11_joint_summary.csv")) }
scr={}
scp=os.path.join(V,"sc_v11_patient_paired.csv")
if os.path.exists(scp):
    import collections
    agg=collections.defaultdict(lambda: dict(hits=0, cells=[], pairs=[], fams=set()))
    for r in rd(scp):
        if fl(r.get("fdr")) is not None and fl(r["fdr"])<0.05:
            k=(r["context"], r["module"])
            a=agg[k]; a["hits"]+=1; a["cells"].append(r["cell_type"]); a["fams"].add(r["comparison_type"])
            if r["n_pairs"] and int(float(r["n_pairs"]))>0: a["pairs"].append(int(float(r["n_pairs"])))
    for k,v in agg.items(): scr[k]=v
surv={}
for r in rd(os.path.join(A,"cbio_v3_survival_cox.csv")):
    surv.setdefault((r["context"], r["feature"]), r)
crc={ ( "CRC", r["feature"]):r for r in rd(os.path.join(V,"v11_external_crc.csv")) } if os.path.exists(os.path.join(V,"v11_external_crc.csv")) else {}
crc_v10={ ( "CRC", r["feature"]):r for r in rd(os.path.join(V,"v10_external_crc_gse39582.csv")) } if os.path.exists(os.path.join(V,"v10_external_crc_gse39582.csv")) else {}
keys=sorted(set(list(raw.keys())+list(jj.keys())))
out=[]
for k in keys:
    dis,fea=k
    r=raw.get(k,{}); x=xc.get(k,{}); m=meta.get(k,{}); d=dl.get(k,{}); ad=adh.get(k,{}); j=jj.get(k,{}); s=scr.get(k); sv=surv.get(k)
    ext=crc.get(k) or crc_v10.get(k)
    out.append(dict(
      disease=dis, feature=fea,
      n_cohorts=r.get("n_cohorts",""), per_cohort_robust=r.get("robust_consistent",""), n_fdr_raw=r.get("n_fdr_raw",""),
      median_smd=r.get("median_smd",""),
      meta_k=m.get("k",""), meta_est=m.get("est",""), meta_ci_lo=m.get("ci_lo",""), meta_ci_hi=m.get("ci_hi",""),
      meta_p=m.get("p",""), meta_fdr=m.get("fdr",""), meta_I2=m.get("I2",""), meta_measures=m.get("measures",""),
      dl_fdr=d.get("fdr",""), adhoc_fdr=ad.get("fdr",""),
      joint_n=j.get("n_analysed",""), joint_n_fdr=j.get("n_fdr",""), joint_median_d_adj=j.get("median_d_adj",""),
      joint_robust=j.get("joint_robust",""), xcell_resid_robust=x.get("robust_xcell",""),
      sc_hits=(s["hits"] if s else 0), sc_cells=("; ".join(sorted(set(s["cells"]))[:4]) if s else ""),
      sc_families=(";".join(sorted(s["fams"])) if s else ""), sc_median_pairs=(int(sorted(s["pairs"])[len(s["pairs"])//2]) if (s and s["pairs"]) else ""),
      tcga_hr=(sv.get("hazard_ratio_per_1sd","") if sv else ""), tcga_fdr=(sv.get("fdr","") if sv else ""),
      crc_ext_hr=(ext.get("HR","") if ext else ""), crc_ext_p=(ext.get("p","") if ext else ""), crc_ext_model=(ext.get("model","") if ext else ""),
    ))
with open(os.path.join(V,"v11_evidence_matrix.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("matrix rows:",len(out))
print("joint robust:",sum(1 for r in out if r["joint_robust"]=="TRUE"),
      "| meta BH-sig:",sum(1 for r in out if r["meta_fdr"] not in ("",None) and fl(r["meta_fdr"]) is not None and fl(r["meta_fdr"])<0.05),
      "| sc states with hits:",sum(1 for r in out if r["sc_hits"]))
