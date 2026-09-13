#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR-based layout QA for v11 figures (tesseract TSV word boxes).

Checks: clipping (ink/text touching canvas edges), text-box overlap, minimum text height
(300 dpi: 29 px ~ 7 pt), and presence of expected tokens per figure.
"""
import csv, os, subprocess, sys, collections
from PIL import Image
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
V11 = r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
FIGDIR = os.path.join(V11, "02_图片")
FIGS = ["fig1_parallel_layers_v11.png","fig2a_raw_v11.png","fig2b_adjusted_v11.png",
        "fig3_base_vs_adjusted_v11.png","fig4_survival_v11.png","fig5_molecular_v11.png",
        "fig6_sc_v11.png","fig_paper_xcell_vs_marker.png","fig_paper_xcell_heatmap.png"]
EXPECT = {
 "fig1_parallel_layers_v11.png": ["55/170","17","74","6","3","21","0.87","16","12","17","556/187","102/66","300/152","parallel"],
 "fig2a_raw_v11.png": ["A","Raw","LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"],
 "fig2b_adjusted_v11.png": ["B","Adjusted","n.e.","LUAD","Asthma"],
 "fig3_base_vs_adjusted_v11.png": ["base","adjusted","0.87"],
 "fig4_survival_v11.png": ["LUAD","CRC","STAD","PAAD","HCC","ESCC","hazard"],
 "fig5_molecular_v11.png": ["A","B","amplification","mutation","EGFR","ERBB2","TP53","KRAS"],
 "fig6_sc_v11.png": ["A","B","pairs","CRC","IBD","STAD","cell-identity","same-cell-type"],
 "fig_paper_xcell_vs_marker.png": ["xCell","marker"],
 "fig_paper_xcell_heatmap.png": ["LUAD","CRC","STAD","PAAD"],
}
def ocr_tsv(path):
    out = subprocess.run([TESS, path, "stdout", "--psm", "11", "tsv"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    rows=[]
    for r in csv.DictReader(out.stdout.splitlines(), delimiter="\t"):
        try:
            if not r.get("text","").strip(): continue
            rows.append(dict(text=r["text"], conf=float(r["conf"] or -1),
                             x=int(r["left"]), y=int(r["top"]), w=int(r["width"]), h=int(r["height"])))
        except Exception: pass
    return rows
def iou(a,b):
    x1=max(a["x"],b["x"]); y1=max(a["y"],b["y"])
    x2=min(a["x"]+a["w"], b["x"]+b["w"]); y2=min(a["y"]+a["h"], b["y"]+b["h"])
    if x2<=x1 or y2<=y1: return 0.0
    inter=(x2-x1)*(y2-y1)
    return inter/float(min(a["w"]*a["h"], b["w"]*b["h"]))
summary=[]
for f in FIGS:
    p=os.path.join(FIGDIR,f)
    if not os.path.exists(p): print("[MISS]",f); continue
    im=Image.open(p); W,H=im.size
    boxes=ocr_tsv(p)
    words=[b for b in boxes if b["conf"]>30]
    clip=[b for b in words if b["x"]<=2 or b["y"]<=2 or b["x"]+b["w"]>=W-2 or b["y"]+b["h"]>=H-2]
    small=[b for b in words if b["h"]<22]
    overlaps=[]
    for i in range(len(words)):
        for j in range(i+1,len(words)):
            if iou(words[i],words[j])>0.35: overlaps.append((words[i]["text"],words[j]["text"]))
    txt=" ".join(b["text"] for b in words)
    miss=[t for t in EXPECT.get(f,[]) if t.lower() not in txt.lower()]
    med=sorted(b["h"] for b in words)[len(words)//2] if words else 0
    summary.append(dict(file=f, px=f"{W}x{H}", n_words=len(words), median_h_px=med,
        clipping=len(clip), tiny=len(small), overlaps=len(overlaps), missing=";".join(miss)))
    print(f"\n== {f} ({W}x{H}) words={len(words)} median_h={med}px")
    if clip: print("   CLIPPING:", [b['text'] for b in clip][:8])
    if small: print("   TINY(<22px):", collections.Counter(b['text'] for b in small).most_common(8))
    if overlaps: print("   OVERLAP:", overlaps[:6])
    if miss: print("   MISSING TOKENS:", miss)
with open(os.path.join(V11,"04_评审记录与报告","ocr_figure_qa.csv"),"w",encoding="utf-8-sig",newline="") as fh:
    w=csv.DictWriter(fh, fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
print("\nQA table ->", os.path.join(V11,"04_评审记录与报告","ocr_figure_qa.csv"))
