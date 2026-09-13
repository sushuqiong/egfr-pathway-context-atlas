#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
P = r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s = open(P, encoding="utf-8").read()
body, sep, refsec = s.partition("## References")
entries=[]
for line in refsec.splitlines():
    m=re.match(r"\s*(\d+)\.\s*(.*)$", line)
    if m: entries.append((int(m.group(1)), line))
entries.sort(); refmap={n:l for n,l in entries}
def expand(tok):
    out=[]
    for part in tok.split(","):
        part=part.strip()
        if "-" in part:
            a,b=part.split("-"); out+=list(range(int(a),int(b)+1))
        else: out.append(int(part))
    return out
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
old2new={v:i+1 for i,v in enumerate(order)}
uncited=[n for n in sorted(refmap) if n not in old2new]
body2=re.sub(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", lambda m: "["+",".join(str(old2new[n]) for n in expand(m.group(1)))+"]", body)
new_entries=sorted(((old2new[n], refmap[n]) for n in sorted(refmap) if n in old2new), key=lambda x:x[0])
for n in uncited: new_entries.append((n, refmap[n]))
def renum(line,new):
    m=re.match(r"^(\s*)\d+\.\s(.*)$", line)
    return f"{m.group(1)}{new}. {m.group(2)}" if m else line
refs_out="\n".join(renum(l,new) for new,(_,l) in enumerate(new_entries,1))
open(P,"w",encoding="utf-8").write(body2+sep+"\n"+refs_out+"\n")
print("renumbered refs:",len(new_entries),"uncited:",uncited)
s2=open(P,encoding="utf-8").read(); b2,_,r2=s2.partition("## References")
o2=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", b2):
    for v in expand(m.group(1)):
        if v not in o2: o2.append(v)
print("violations:",sum(1 for i in range(1,len(o2)) if o2[i]<o2[i-1]),"| cited unique:",len(o2))
rn=[int(re.match(r"\s*(\d+)\.",l).group(1)) for l in r2.splitlines() if re.match(r"\s*\d+\.",l)]
print("refs sequential:", rn==list(range(1,len(rn)+1)), "| n=",len(rn))
