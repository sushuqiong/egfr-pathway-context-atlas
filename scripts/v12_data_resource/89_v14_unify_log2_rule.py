#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: unify the log2 decision in the external reuse example with the internal pipeline rule.

Internal rule (as recorded in 03_expression/transformation_log.csv): a matrix is treated as already
log-scaled UNLESS it looks like raw intensities, i.e. log2 is applied only when the integer fraction
exceeds 0.90 AND the maximum exceeds 50. The example script had the condition inverted.
"""
import os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
old_block = """frac_int <- mean(abs(v-round(v))<1e-8, na.rm=TRUE); mx <- max(v, na.rm=TRUE)
logged <- frac_int>0.90 && mx>50
if (!logged) expr <- log2(expr+1)
cat(sprintf("integer fraction %.3f, input max %.2f -> log2 applied: %s\\n", frac_int, mx, !logged))"""
new_block = """frac_int <- mean(abs(v-round(v))<1e-8, na.rm=TRUE); mx <- max(v, na.rm=TRUE)
raw_intensities <- (frac_int > 0.90) && (mx > 50)     # same deterministic rule as the internal pipeline
if (raw_intensities) expr <- log2(expr+1)
cat(sprintf("integer fraction %.3f, input max %.2f -> raw intensities: %s -> log2 applied: %s\\n",
            frac_int, mx, raw_intensities, raw_intensities))"""
for rel in [os.path.join(V14,"scripts","76_v14_external_reuse_example.R"),
            os.path.join(V14,"dataset_package","09_reuse_examples","example3_external_cohort_rebuild.R")]:
    s=open(rel,encoding="utf-8").read()
    if old_block in s:
        s=s.replace(old_block,new_block); open(rel,"w",encoding="utf-8").write(s); print("rule unified in", os.path.basename(rel))
    else:
        # fall back: replace just the two decision lines
        s2=s.replace("logged <- frac_int>0.90 && mx>50","raw_intensities <- (frac_int > 0.90) && (mx > 50)")
        s2=s2.replace("if (!logged) expr <- log2(expr+1)","if (raw_intensities) expr <- log2(expr+1)")
        if s2!=s:
            open(rel,"w",encoding="utf-8").write(s2); print("rule unified (fallback) in", os.path.basename(rel))
        else:
            print("WARNING: rule not found in", os.path.basename(rel))
