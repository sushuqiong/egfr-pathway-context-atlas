#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: shorten and auto-wrap every panel title so nothing can be clipped at the canvas edge."""
import re, os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","60_v14_figures.R"); s=open(p,encoding="utf-8").read()
# 1. add a wrapping helper right after the theme function
helper = '''
wrap_title <- function(x, width = 46) vapply(as.character(x), function(s) paste(strwrap(s, width = width), collapse = "\\n"), character(1))
tlab <- function(x, width = 46) labs(title = wrap_title(x, width))
'''
if "wrap_title <- function" not in s:
    s=s.replace('ctxmap <- c(', helper + 'ctxmap <- c(',1)
# 2. shorten titles
reps = [
 ('title="A  Module gene coverage per disease context (dark red = lowest, pale = complete)"','title=wrap_title("A  Module gene coverage per disease context (dark red = low, pale = complete)")'),
 ('title="B  Cohort composition by context (one facet per measure)"','title=wrap_title("B  Cohort composition by context")'),
 ('title="C  Single-cell datasets and the comparison arms available"','title=wrap_title("C  Single-cell datasets and comparison arms")'),
 ('title="A  Exclusions, flags and non-testable comparisons"','title=wrap_title("A  Exclusions, flags and non-testable comparisons")'),
 ('title="B  Single-cell comparison design used"','title=wrap_title("B  Single-cell comparison design used")'),
 ('title="C  Estimates layer (all effects, including non-significant)"','title=wrap_title("C  Estimates layer (all effects, including non-significant)")'),
 ('title="A  Cross-cohort direction consistency (points: pairs; bar: median)"','title=wrap_title("A  Cross-cohort direction consistency (points: pairs, bar: median)")'),
 ('title="B  Coverage-threshold sensitivity (light: pairs pooled; red: BH-significant)"','title=wrap_title("B  Coverage-threshold sensitivity (light: pairs, red: significant)")'),
 ('title="C  Module versus xCell panel overlap (dashed: 20%)"','title=wrap_title("C  Module versus xCell panel overlap (dashed: 20%)")'),
 ('title="D  Model R2 versus per-predictor VIF"','title=wrap_title("D  Model R2 versus per-predictor VIF")'),
 ('title="A  Common-gene sensitivity (red: disagreement >=20% of cohorts; grey: not scorable)"','title=wrap_title("A  Common-gene sensitivity (red: disagreement in >=20% of cohorts; grey: not scorable)")'),
 ('title="B  Collinearity between disease status and composition"','title=wrap_title("B  Disease status versus composition")'),
]
for a,b in reps:
    if a in s: s=s.replace(a,b)
    else: print("NOT FOUND:",a[:60])
# 3. tighten margins and axis label sizes for the crowded panels
s=s.replace('plot.margin=margin(5,12,5,5)','plot.margin=margin(5,14,5,5)')
s=s.replace('theme(axis.text.x=element_text(size=8.5, angle=30, hjust=1), axis.text.y=element_text(size=7.5))',
            'theme(axis.text.x=element_text(size=8, angle=45, hjust=1), axis.text.y=element_text(size=7.5))')
s=s.replace('theme(axis.text.x=element_text(size=8.5, angle=30, hjust=1))','theme(axis.text.x=element_text(size=8, angle=45, hjust=1))')
s=s.replace('theme(axis.text.x=element_text(size=8.5, angle=30, hjust=1))','theme(axis.text.x=element_text(size=8, angle=45, hjust=1))')
open(p,"w",encoding="utf-8").write(s)
print("titles wrapped/shortened; margins and rotated label sizes adjusted")
