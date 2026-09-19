#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 fix pass 2b: robust segment-based edits of the manuscript generator."""
import os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
def seg_replace(prefix, suffix, new_middle, label):
    """replace text between prefix and the first occurrence of suffix after it"""
    global s
    i=s.find(prefix)
    assert i>=0, f"prefix not found: {label}"
    j=s.find(suffix, i)
    assert j>=0, f"suffix not found: {label}"
    s = s[:i] + prefix + new_middle + s[j:]
    print("patched:",label)
# GSVA citation
i=s.find("in the bulk cohorts")
assert i>=0, "bulk sentence not found"
seg_replace("in the bulk cohorts it is a", "z-scored within the cohort", " GSVA value7 ", "cite GSVA")
# xCell citation
seg_replace("Compartment scores were estimated with xCell ", " (expression-derived", "v1.1.08", "cite xCell")
# pooling citation + k=1 rule
seg_replace("Pooling uses REML", " heterojeneity", "", "noop-check") if False else None
seg_replace("Pooling uses REML", " variance correction", "", "noop-check2") if False else None
i2=s.find("Pooling uses REML")
assert i2>=0
j2=s.find("variance correction", i2)
s = s[:i2] + "Pooled estimates are reported only when at least two cohorts contribute: cohort-module pairs with a single contributing cohort remain in the same table but are labelled 'single cohort; not a pooled estimate' and carry no p-value, confidence interval or prediction interval. Pooling uses random-effects meta-analysis9 with REML (restricted maximum likelihood) heterogeneity and the Hartung-Knapp10,11 " + s[j2:]
print("patched: pooling citations and k=1 rule")
# single-cell dataset wording
seg_replace("Four datasets contributed contrasts:", "; one lung dataset was excluded",
            "", "single-cell count wording")
seg_replace("Four single-cell datasets were processed and three contributed",
            "; one lung dataset was excluded", "", "noop") if False else None
i3=s.find("datasets were processed and three contributed")
if i3<0:
    i3=s.find("Four datasets contributed contrasts")
    assert i3>=0
    # rebuild that sentence cleanly
    j3=s.find("; one lung dataset was excluded", i3)
    seg_new = ("Four single-cell datasets were processed and three contributed testable contrasts: colorectal cancer "
               "(tumour versus non-tumour tissue, 29 donors), inflammatory bowel disease (disease versus healthy donors, 18 donors), "
               "gastric cancer (tumour versus adjacent and versus non-pathological tissue, 59 donors) and asthma (8 donors), which was "
               "prepared with the same pipeline but contributed no comparison to the shipped table because no comparison satisfied the "
               "donor rules after aggregation")
    s = s[:i3] + seg_new + s[j3:]
    print("patched: single-cell wording")
# asthma sentence tail cleanup
s=s.replace("and asthma (8 donors), which was prepared with the same pipeline but contributed no comparison to the shipped table because no comparison satisfied the donor rules after aggregation; one lung dataset was excluded",
            "and asthma (8 donors), which was prepared with the same pipeline but contributed no comparison to the shipped table because no comparison satisfied the donor rules after aggregation. One lung dataset was excluded")
open(p,"w",encoding="utf-8").write(s); print("written")
