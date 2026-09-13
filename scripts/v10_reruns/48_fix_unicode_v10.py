#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s=open(p,encoding="utf-8").read()
s=re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1),16)), s)
open(p,"w",encoding="utf-8").write(s)
print("abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1))))
for k in ["retained 18","76 under DerSimonian","median ri = 0.11","CRC 8, IBD 6, LUAD 2, PAAD 1, COPD 1","retained 19 versus 18","leftover \\u"]:
    print(repr(k),"->",s.count(k))
print("leftover escapes:", len(re.findall(r"\\u[0-9a-fA-F]{4}", s)))
