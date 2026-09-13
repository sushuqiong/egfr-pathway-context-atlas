#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, subprocess
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s=open(P,encoding="utf-8").read()
# DL entry currently unnumbered-tail (#51). Add citation at its mention in Methods 2.3.
a="and DerSimonian-Laird pooling is reported for comparison."
b="and DerSimonian-Laird pooling is reported for comparison [51]."
assert a in s
s=s.replace(a,b,1)
open(P,"w",encoding="utf-8").write(s)
print("citation added")
