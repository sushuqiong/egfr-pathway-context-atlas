#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renumber citations by first-appearance order (user hard rule) and reorder the reference list."""
import re
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
body,sep,refsec=s.partition("## References")
# parse reference entries oldnum->line
lines=refsec.splitlines()
entries=[]; i=0
for line in lines:
    m=re.match(r"\s*(\d+)\.\s*(.*)$", line)
    if m:
        entries.append((int(m.group(1)), line))
entries.sort()
refmap={n:line for n,line in entries}
# scan body citation tokens incl ranges (9,10 / 21-50)
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
print("cited old nums:",len(order),"uncited:",uncited)
# rewrite tokens
def repl(m):
    nums=expand(m.group(1))
    return "["+",".join(str(old2new[n]) for n in nums)+"]"
body2=re.sub(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", repl, body)
# rebuild reference section in new order
new_entries=sorted(((old2new[n],refmap[n]) for n in sorted(refmap) if n in old2new), key=lambda x:x[0])
# uncited (none expected) appended after
for n in uncited: new_entries.append((n,refmap[n]))
def renum(line,new):
    m=re.match(r"^(\s*)\d+\.\s(.*)$", line)
    return f"{m.group(1)}{new}. {m.group(2)}" if m else line
refs_out="\n".join(renum(line,new) for new,(_,line) in enumerate(new_entries,1))
open(p,"w",encoding="utf-8").write(body2+sep+"\n"+refs_out+"\n")
print("renumbered; max:",len(new_entries))
# quick re-verify
s2=open(p,encoding="utf-8").read(); b2,_,r2=s2.partition("## References")
o2=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", b2):
    for v in expand(m.group(1)):
        if v not in o2: o2.append(v)
print("new order head:",o2[:26])
print("violations:",sum(1 for i in range(1,len(o2)) if o2[i]<o2[i-1]))
rn=[int(re.match(r"\s*(\d+)\.",l).group(1)) for l in r2.splitlines() if re.match(r"\s*\d+\.",l)]
print("refs list count:",len(rn),"sequential:",rn==list(range(1,len(rn)+1)))
