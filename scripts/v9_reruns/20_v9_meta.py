#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v9 meta on unified g-scale (paired g_equiv) + joint-model composition summary."""
import os
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
V9=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\reruns\results"
df=pd.read_csv(os.path.join(V9,"v9_percohort_joint_unified.csv"))
df=df[(df["role"].isin(["discovery","validation"])) & (df["var_unified"]>0) & np.isfinite(df["var_unified"])].copy()
print("rows input:",len(df))
def reml(y,v):
    k=len(y); t=0.0
    for _ in range(300):
        w=1.0/(v+t); mu=np.sum(w*y)/np.sum(w)
        num=np.sum(w**2*(k/(k-1.0)*(y-mu)**2-v)); den=np.sum(w**2)
        nt=max(0.0,num/den)
        if abs(nt-t)<1e-9: break
        t=nt
    return t
def hk(y,v,t):
    k=len(y); w=1.0/(v+t); mu=np.sum(w*y)/np.sum(w)
    if k<=1: return mu,np.nan,np.nan,(np.nan,np.nan)
    q=np.sum(w*(y-mu)**2); se=np.sqrt(max(q/((k-1)*np.sum(w)),1e-12)); df=k-1
    p=2*stats.t.sf(abs(mu/se),df); tc=stats.t.ppf(0.975,df)
    return mu,se,p,(mu-tc*se,mu+tc*se)
def dl(y,v):
    k=len(y); w=1.0/v; mu=np.sum(w*y)/np.sum(w); Q=np.sum(w*(y-mu)**2)
    C=np.sum(w)-np.sum(w**2)/np.sum(w)
    t=max(0.0,(Q-(k-1))/C) if C>0 else 0.0
    return t, mu
out=[]
for (dis,feat),d in df.groupby(["disease","feature"]):
    d=d[np.isfinite(d["var_unified"]) & (d["var_unified"]>0)]
    if len(d)==0: continue
    y=d["smd_unified"].values.astype(float); v=d["var_unified"].values.astype(float); k=len(d)
    tdl,mdl=dl(y,v); w=1.0/(v+tdl); muv=np.sum(w*y)/np.sum(w)
    sedl=np.sqrt(1.0/np.sum(w)); pdl=2*stats.norm.sf(abs(muv)/sedl)
    trem=reml(y,v); muhk,seh,p_hk,(lo,hi)=hk(y,v,trem)
    Q=np.sum((1.0/v)*(y-np.sum((1.0/v)*y)/np.sum(1.0/v))**2); I2=max(0.0,(Q-(k-1))/Q)*100 if Q>0 else 0.0
    out.append(dict(disease=dis,feature=feat,k=k,accession=";".join(d["accession"]),
        n_case=int(d["n_case"].sum()), n_control=int(d["n_control"].sum()),
        smd_min=float(y.min()), smd_max=float(y.max()),
        smd_DL=muv, p_DL=pdl, smd_REML=muhk, se_HK=seh, p_REML_HK=p_hk, ci_lo=lo, ci_hi=hi,
        Q=Q, I2=I2, tau2_REML=trem))
res=pd.DataFrame(out)
for col in ["fdr_DL","fdr_REML_HK"]:
    res[col]=np.nan
for dis,g in res.groupby("disease"):
    for col,pcol in [("fdr_DL","p_DL"),("fdr_REML_HK","p_REML_HK")]:
        mask=(g["k"]>=2)&np.isfinite(g[pcol])
        if mask.sum():
            _,fdr,_,_=multipletests(g.loc[mask,pcol].values,method="fdr_bh")
            res.loc[g.index[mask],col]=fdr
res.to_csv(os.path.join(V9,"context_meta_v9_unified.csv"),index=False)
sigD=((res["k"]>=2)&(res["fdr_DL"]<0.05)).sum(); sigR=((res["k"]>=2)&(res["fdr_REML_HK"]<0.05)).sum()
print("DL sig (k>=2):",sigD," REML/HK sig:",sigR)
print("REML/HK sig list:")
print(res[(res["k"]>=2)&(res["fdr_REML_HK"]<0.05)][["disease","feature","k","smd_REML","ci_lo","ci_hi","p_REML_HK","fdr_REML_HK"]].to_string(index=False))
print("per disease DL:",res[(res["k"]>=2)&(res["fdr_DL"]<0.05)].groupby("disease").size().to_dict())
print("per disease REML/HK:",res[(res["k"]>=2)&(res["fdr_REML_HK"]<0.05)].groupby("disease").size().to_dict())
# ---- joint-model composition summary ----
df["fdr_joint"]=np.nan
for acc,g in df.groupby("accession"):
    m=np.isfinite(g["p_adj"])
    if m.sum():
        _,fdr,_,_=multipletests(g.loc[m,"p_adj"].values,method="fdr_bh")
        df.loc[g.index[m],"fdr_joint"]=fdr
sm=df.groupby(["disease","feature"]).agg(n=("accession","size"),
    n_sig_joint=("fdr_joint",lambda x:(x<0.05).sum()),
    pos_joint=("d_adj",lambda x:(x>0).sum()),
    neg_joint=("d_adj",lambda x:(x<0).sum()),
    median_d_adj=("d_adj","median")).reset_index()
sm["n_fdr_adj"]=sm["n_sig_joint"]
sm["majority_adj"]=np.maximum(sm["pos_joint"],sm["neg_joint"])
sm["joint_robust"]=(sm["n_fdr_adj"]>=2)&(sm["majority_adj"]/sm["n"]>=2/3)
sm.to_csv(os.path.join(V9,"v9_composition_joint_summary.csv"),index=False)
print("joint-robust total:",int(sm["joint_robust"].sum())," by disease:",sm[sm["joint_robust"]].groupby("disease").size().to_dict())
# contrast with xCell-residual 19 list (read xcell summary)
xc=pd.read_csv(r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results\xcell\context_atlas_summary_xcell_adjusted.csv")
xr=set(zip(xc.loc[xc["robust_xcell"]==True,"disease"], xc.loc[xc["robust_xcell"]==True,"feature"]))
jr=set(zip(sm.loc[sm["joint_robust"],"disease"],sm.loc[sm["joint_robust"],"feature"]))
print("overlap xCell-19 vs joint-robust:",len(xr&jr)," xCell-only:",len(xr-jr)," joint-only:",len(jr-xr))
print("saved files")
