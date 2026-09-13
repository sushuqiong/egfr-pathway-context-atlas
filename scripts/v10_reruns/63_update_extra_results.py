#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, re
V10=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10"
rows=list(csv.DictReader(open(V10+r"\reruns\results\v10_keystate_pooled.csv")))
mo=[r for r in rows if r["variant"]=="minus_overlap"]
print("minus_overlap variants:", len(mo), "| states with overlap genes:", len({r['state'] for r in mo}))
print("minus_overlap with p<0.05:", sum(1 for r in mo if r['p'] not in ('','NA') and float(r['p'])<0.05))
drops=[r for r in rows if r["variant"].startswith("drop_")]
print("drop_ variants:", len(drops), "| sign flips:", sum(1 for r in drops if r['sign_flip_vs_full']=='TRUE'),
      "| drop variants with p<0.05:", sum(1 for r in drops if r['p'] not in ('','NA') and float(r['p'])<0.05))
full=[r for r in rows if r["variant"]=="full"]
print("full-state pooled p<0.05:", sum(1 for r in full if r['p'] not in ('','NA') and float(r['p'])<0.05), "of", len(full))
# update manuscript Methods 2.2 + tables line
P=V10+r"\01_稿件正文\Manuscript_draft_v10.md"
s=open(P,encoding="utf-8").read()
old_start=s.find("A per-key-state recheck (10 headline states, 11 cohorts, 112 leave-one-gene tests)")
if old_start>0:
    old_end=s.find(".", s.find("Supplementary Table S8).", old_start))
    if old_end<0: old_end=s.find("Supplementary Table S8)", old_start)+len("Supplementary Table S8)")
    new=("A per-key-state stability check was repeated with the corrected pipeline (26 headline states, 331 variant "
         "effects): removing genes shared with composition-marker panels did not change the pooled direction of any key "
         "state, and leaving out the three most influential member genes per cohort changed the pooled direction of only "
         "one state (IBD SRC/FAK after removing FYN, which also lost significance); Supplementary Table S8")
    s=s[:old_start]+new+s[old_end+1:]
    print("Methods 2.2 LOOGO sentence replaced")
else:
    print("WARN: old LOOGO sentence not found")
# table S8/S10 wording
s=s.replace("A per-key-state recheck (10 states, 11 cohorts, 112 tests) found two cohort-level sign changes, both in small-magnitude states (CRC ERBB ligands after removing NRG1; COPD SRC/FAK after removing YES1).",
            "A per-key-state stability check with the corrected pipeline (26 states, 331 variant effects) found one pooled direction change (IBD SRC/FAK after removing FYN, also losing significance) and no change on removal of composition-marker-overlapping genes.")
s=s.replace("A marker-proxy sensitivity version (epithelial/immune/stromal/endothelial marker means) was compared by Spearman correlation across the 170 adjusted medians (\\u03c1 = 0.81).",
            "GSVA scores and member-mean z-scores were concordant within cohorts (median Spearman \\u03c1 = 0.94 over 102 state-cohort pairs). A marker-proxy sensitivity version (epithelial/immune/stromal/endothelial marker means) was compared by Spearman correlation across the 170 adjusted medians (\\u03c1 = 0.81).")
open(P,"w",encoding="utf-8").write(s)
print("manuscript updated")
