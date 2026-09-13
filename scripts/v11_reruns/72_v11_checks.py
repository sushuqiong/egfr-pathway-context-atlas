#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, collections
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
s=open(P,encoding="utf-8").read()
# --- trim abstract to <=250 words ---
i=s.find("## Abstract"); j=s.find("## 1. Introduction")
abs_new = """## Abstract

**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, but how they compare across diseases, how much of a bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.

**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts across ten contexts. Effects were placed on one common standardized scale (unpaired: Hedges-corrected SMDH; matched: Hedges-corrected SMCRPH with the empirical within-pair correlation; both use the root-mean-variance denominator) and pooled with REML/Hartung-Knapp inference. Composition was addressed by comparing base models (module ~ disease [+ patient]) with adjusted models adding four compartment scores on identical samples. Single-cell comparisons used paired signed-rank tests where complete patient pairs existed. TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, a driver screen restricted to mutation-profiled samples, and external validation in independent cohorts with tissue-type and stage correction.

**Results.** Fifty-five of 170 states were per-cohort robust; meta-analysis retained 17 (74 under DerSimonian-Laird; 6 with non-shrinking Knapp-Hartung; 3 unpaired-only), and base-versus-adjusted comparison retained 21 (CRC 10, STAD 9, ESCC 1, IBD 1; none in PAAD) with a median adjusted-to-base coefficient ratio of 0.87. In TCGA, 17/108 associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. No module passed pre-specified external replication (CRC VEGF/PDGF HR 1.16, p=0.042; 1.09, p=0.22 after stage adjustment). Single-cell analysis yielded 16 same-cell-type comparisons (10 paired, median 15 pairs) and 12 separately labelled cell-identity contrasts.

**Conclusions.** Most bulk RTK-related differences track tissue composition and clinical background, attenuation was typically modest, and no surviving signal replicated externally. The atlas provides composition-aware, evidence-tiered hypotheses with explicit decision rules rather than evidence of pathway activation.

"""
s=s[:i]+abs_new+s[j:]
open(P,"w",encoding="utf-8").write(s)
print("abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1))))
print("\n== stale scan ==")
stale=["18 states","retained 7","573","190 OS events","12 hits","overlap (5","fully attenuated","carried entirely",
       "was prospective","only six states","Methods 2.10). The TCGA","178 with survival","6 states remained",
       "11 pooled","95% CI 1.05-1.40, p=0.0069","HR 1.21"]
for ph in stale:
    c=s.count(ph)
    if c: print("  STALE",c,":",ph)
print("  (done)")
print("\n== structure ==")
for pat in [r"^### 2\.\d+", r"^### 3\.\d+", r"^### 4\.\d+"]:
    f=re.findall(pat,s,re.M); dup=[k for k,v in collections.Counter(f).items() if v>1]
    print(" ",pat,"n=",len(f),"dups:",dup or "none")
print("markdown residue (**Results.** outside abstract):", len(re.findall(r"^\*\*(Results|Methods)\.\*\*", s, re.M)))
print("version note residue:", s.count("v9:")+s.count("v10:"))
body,_,ref=s.partition("## References")
def expand(t):
    out=[]
    for part in t.split(","):
        part=part.strip()
        if "-" in part:
            a,b=part.split("-"); out+=list(range(int(a),int(b)+1))
        else: out.append(int(part))
    return out
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
rn=[int(m.group(1)) for l in ref.splitlines() if (m:=re.match(r"\s*(\d+)\.",l))]
print("\n== citations ==")
print("refs:",len(rn),"sequential:",rn==list(range(1,len(rn)+1)),"cited:",len(order),
      "violations:",sum(1 for i in range(1,len(order)) if order[i]<order[i-1]),
      "uncited:",[n for n in rn if n not in set(order)])
