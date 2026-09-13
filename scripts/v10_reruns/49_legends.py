#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s=open(p,encoding="utf-8").read()
s=s.replace("REML/Hartung-Knapp 7; DerSimonian-Laird 20","REML/Hartung-Knapp 18; DerSimonian-Laird 76")
open(p,"w",encoding="utf-8").write(s)
print("legend numbers fixed:", s.count("REML/Hartung-Knapp 18; DerSimonian-Laird 76"))
