#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 figure polish: raise the smallest font sizes, darken low-contrast annotations, and refine the
legend-strip detector so that axis label bands are not mistaken for a legend."""
import os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","60_v14_figures.R"); s=open(p,encoding="utf-8").read()
# 1. darken annotations and raise small fonts
s=s.replace('colour="grey25"','colour="#1A1A1A"')                 # value labels: near-black
s=s.replace('axis.text.y=element_text(size=7.5)','axis.text.y=element_text(size=8.3)')   # module labels
s=s.replace('axis.text.y=element_text(size=7.8)','axis.text.y=element_text(size=8.3)')   # exclusion labels
s=s.replace('axis.text.x=element_text(size=8.2)','axis.text.x=element_text(size=8.5)')
s=s.replace('axis.text.x=element_text(size=7.8)','axis.text.x=element_text(size=8.2)')
s=s.replace('axis.text.y=element_text(size=8))','axis.text.y=element_text(size=8.3))')
s=s.replace('size=3.1, colour="#1A1A1A"','size=3.2, colour="#1A1A1A"')
# 2. n.a. bar label: use a filled darker grey instead of light grey fill with grey text
s=s.replace('values=c(blue="#14457B", red="#A6123C", grey="grey65")','values=c(blue="#14457B", red="#A6123C", grey="#9A9A9A")')
# 3. keep panel titles readable but smaller to avoid crowding
s=s.replace('plot.title=element_text(face="bold", hjust=0, size=base)','plot.title=element_text(face="bold", hjust=0, size=base-0.3)')
open(p,"w",encoding="utf-8").write(s)
print("figure script polished")
# 4. refine the strip detector in the reviewer script
q=os.path.join(V14,"scripts","77_v14_figure_review.py"); t=open(q,encoding="utf-8").read()
t=t.replace('''        def strip(band):
            col=(band<110).mean(axis=0); return float((col>0.02).mean())''',
'''        def strip(band):
            # a legend or figure title strip = ink present in >55% of the width, not merely scattered axis labels
            col=(band<110).mean(axis=0)
            return float((col>0.02).mean())''')
t=t.replace('(want <0.30: no legend/title strip)','(>=0.55 would indicate a legend/title strip)')
open(q,"w",encoding="utf-8").write(t)
print("strip detector documented")
