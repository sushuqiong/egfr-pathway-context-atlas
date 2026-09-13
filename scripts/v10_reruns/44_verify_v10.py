#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, collections
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s=open(P,encoding="utf-8").read()
body,_,ref=s.partition("## References")
print("abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1))))
print("escapes:", len(re.findall(r"\\u[0-9a-fA-F]{4}", s)))
for pat in [r"^### 2\.\d+", r"^### 3\.\d+", r"^### 4\.\d+"]:
    f=re.findall(pat, s, re.M); dup=[k for k,v in collections.Counter(f).items() if v>1]
    print(pat,"n=",len(f),"dups:",dup or "none")
stale=["retained only 4","73 at k","19 states remained","six states remained","11 pooled states","HR 1.21",
       "was prospective","carried entirely","Methods 2.10). The TCGA","178 with survival","pooled states retained 11",
       "only six states","Multi-axis activation","negative control"]
for ph in stale:
    c=s.count(ph)
    if c: print("STALE",c,ph)
newph=["retained 7","21 of 170","556 tumour","187 deaths","no module state passed strict","4.8 Limitations",
       "SMCRH","metafor [","DerSimonian-Laird pooling is reported for comparison [","not estimable"]
for ph in newph:
    print(" present:",ph,"->",s.count(ph))
print("refs lines:", len([l for l in ref.splitlines() if re.match(r"\s*\d+\.",l)]))
print("fig legends has Fig6:", "**Figure 6." in s, "| Supp S2:", s.count("Supplementary Figure S2"))
