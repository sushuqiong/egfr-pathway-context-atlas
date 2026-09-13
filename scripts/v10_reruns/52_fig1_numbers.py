#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\02_图片\fig1_flowchart_v10.dot"
s=open(p,encoding="utf-8").read()
s=s.replace("REML/Hartung-Knapp: 7 states (DL: 20)","REML/Hartung-Knapp: 18 states (DL: 76)")
open(p,"w",encoding="utf-8").write(s)
print("dot updated:", "18 states (DL: 76)" in s)
