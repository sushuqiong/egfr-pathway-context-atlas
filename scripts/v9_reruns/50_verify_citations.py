#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
body,_,refsec=s.partition("## References")
# reference list numbers
refnums=[]
for line in refsec.splitlines():
    m=re.match(r"\s*(\d+)\.\s",line)
    if m: refnums.append(int(m.group(1)))
# inline citations like [2,3] or [9,10]
order=[]
used_flat=[]
for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", body):
    vals=[int(x.strip()) for x in m.group(1).split(",")]
    used_flat+=vals
    for v in vals:
        if v not in order: order.append(v)
dangling=sorted(set(v for v in used_flat if v<1 or v>max(refnums)))
uncited=[n for n in refnums if n not in set(used_flat)]
multi=len(used_flat)-len(set(used_flat))
# first-appearance ascending violations
vio=0; prev=0; first_bad=[]
for n in order:
    if n<prev:
        vio+=1
        if len(first_bad)<12: first_bad.append((prev,n))
    prev=n
print("refs listed:",len(refnums),"min:",min(refnums),"max:",max(refnums),"duplicate nums:",len(refnums)-len(set(refnums)))
print("inline citation tokens found:",len(list(re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]",body))))
print("unique cited:",len(order),"dangling (>max):",dangling)
print("uncited refs:",uncited)
print("first-appearance ordering violations:",vio)
print("example descents:",first_bad)
print("first-appearance seq head:",order[:30])
