#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 correction: state the marker-proxy agreement honestly (weak for epithelial/fibroblast, moderate for
endothelial/immune) in both the manuscript generator and the reviewer-response document."""
import os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
old=("the two agree with Spearman coefficients of {'; '.join(f\"{r['compartment']} {r['spearman_vs_xcell']}\" for r in agr)} "
     "(08_qc/qc_composition_method_agreement.csv).")
new=("the two agree with Spearman coefficients of {'; '.join(f\"{r['compartment']} {r['spearman_vs_xcell']}\" for r in agr)} "
     "(08_qc/qc_composition_method_agreement.csv). Agreement is moderate for the endothelial and immune compartments and weak "
     "for the epithelial and fibroblast compartments, so the marker panel is reported as a coarse independent cross-check of the "
     "composition axis and not as a replacement for xCell.")
assert old in s, "manuscript anchor not found"
s=s.replace(old,new); open(p,"w",encoding="utf-8").write(s); print("manuscript generator updated")
q=os.path.join(V14,"scripts","73_v14_closeout.py"); t=open(q,encoding="utf-8").read()
bad='与 xCell 的一致性 Spearman 0.48–0.58 随包。'
good=('与 xCell 的一致性为 Spearman 0.28（上皮）/0.29（成纤维）/0.58（内皮）/0.56（免疫）随包；'
      '内皮与免疫为中等一致，上皮与成纤维仅为弱一致，因此该 marker 面板按粗粒度独立核查定位，不作为 xCell 的替代。')
assert bad in t, "response anchor not found"
t=t.replace(bad,good); open(q,"w",encoding="utf-8").write(t); print("close-out script text corrected")
rp=os.path.join(V14,"05_审稿意见与处置_v14.md")
if os.path.exists(rp):
    r=open(rp,encoding="utf-8").read().replace(bad,good)
    open(rp,"w",encoding="utf-8").write(r); print("standalone response file corrected")
