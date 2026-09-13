#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
s=open(P,encoding="utf-8").read()
a="scored by GSVA (Gaussian kernel, minSize \u2265 3)."
b="scored by GSVA (Gaussian kernel, minSize \u2265 3) [44]."
print("gsva anchor found:", a in s)
s=s.replace(a,b,1)
# abstract trim (4-8 words)
s=s.replace("**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, but how they compare across diseases, how much bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.",
            "**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, but how they compare across diseases, how much bulk signal reflects tissue composition, and whether signals replicate remain unclear.")
s=s.replace("In TCGA, 17/108 associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment.",
            "In TCGA, 17/108 associations were FDR<0.05 and 11/15 testable signals survived age+stage adjustment.")
s=s.replace("**Conclusions.** Most bulk RTK-related differences track tissue composition and clinical background, attenuation was typically modest, and no surviving signal replicated externally.",
            "**Conclusions.** Most bulk RTK-related differences track tissue composition and clinical background; attenuation was typically modest and no surviving signal replicated externally.")
open(P,"w",encoding="utf-8").write(s)
print("abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1))))
body,_,ref=s.partition("## References")
rn=[int(m.group(1)) for l in ref.splitlines() if (m:=re.match(r"\s*(\d+)\.",l))]
def expand(t):
    o=[]
    for p in t.split(","):
        p=p.strip()
        if "-" in p: x,y=p.split("-"); o+=list(range(int(x),int(y)+1))
        else: o.append(int(p))
    return o
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
print("cited:",len(order),"| uncited:",[n for n in rn if n not in set(order)],"| violations:",sum(1 for i in range(1,len(order)) if order[i]<order[i-1]))
