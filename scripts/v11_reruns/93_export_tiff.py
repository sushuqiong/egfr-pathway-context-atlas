#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export v11 figures to 300-dpi TIFF for journal submission, and report pixel sizes."""
import os, csv
from PIL import Image
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
SRC=os.path.join(V11,"02_图片"); DST=os.path.join(V11,"02_图片_TIFF")
os.makedirs(DST, exist_ok=True)
pairs=[("fig1_parallel_layers_v11.png","Figure1.png"),
       ("fig2a_raw_v11.png","Figure2A.png"),
       ("fig2b_adjusted_v11.png","Figure2B.png"),
       ("fig3_base_vs_adjusted_v11.png","Figure3.png"),
       ("fig4_survival_v11.png","Figure4.png"),
       ("fig5_molecular_v11.png","Figure5.png"),
       ("fig6_sc_v11.png","Figure6.png"),
       ("fig_paper_xcell_vs_marker.png","FigureS1.png"),
       ("fig_paper_xcell_heatmap.png","FigureS2.png")]
rows=[]
for src,dst in pairs:
    sp=os.path.join(SRC,src)
    if not os.path.exists(sp): print("[MISS]",src); continue
    im=Image.open(sp).convert("RGB")
    w,h=im.size
    # ensure >=300 dpi at final size: save with explicit dpi tag
    dp=os.path.join(DST,dst.replace(".png",".tif"))
    im.save(dp, format="TIFF", compression="tiff_lzw", dpi=(300,300))
    rows.append((dst, w, h, round(w/300*2.54,1), round(h/300*2.54,1), round(os.path.getsize(dp)/1e6,2)))
print(f"{'file':16}{'px_w':>7}{'px_h':>7}{'cm_w':>7}{'cm_h':>7}{'MB':>7}")
for r in rows: print(f"{r[0]:16}{r[1]:>7}{r[2]:>7}{r[3]:>7}{r[4]:>7}{r[5]:>7}")
with open(os.path.join(DST,"figure_specs.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["file","px_w","px_h","cm_w_at_300dpi","cm_h_at_300dpi","size_MB"]); w.writerows(rows)
print("TIFF files:", len(rows), "->", DST)
