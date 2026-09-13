#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect OCR word boxes for the problem figures: print text, height and overlapping pairs."""
import csv, os, subprocess
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"; TMP=r"C:\Users\fengq\ocr_tmp"
def ocr(path):
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    r=subprocess.run([TESS,path,"stdout","--psm","11","tsv"],capture_output=True,env=env)
    rows=[]
    for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(), delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try: rows.append(dict(text=t,conf=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    return [w for w in rows if w["conf"]>30]
def iou(a,b):
    x1,y1=max(a["x"],b["x"]),max(a["y"],b["y"]); x2,y2=min(a["x"]+a["w"],b["x"]+b["w"]),min(a["y"]+a["h"],b["y"]+b["h"])
    if x2<=x1 or y2<=y1: return 0.0
    return (x2-x1)*(y2-y1)/float(min(a["w"]*a["h"],b["w"]*b["h"]))
for f in ["fig1_parallel_layers_v11.png","fig2a_raw_v11.png","fig4_survival_v11.png","fig5_molecular_v11.png","fig6_sc_v11.png","fig_paper_xcell_heatmap.png"]:
    p=os.path.join(TMP,f)
    if not os.path.exists(p): print("[miss]",f); continue
    ws=ocr(p)
    print(f"\n===== {f}  ({len(ws)} words) =====")
    print("  heights: min",min(w['h'] for w in ws),"median",sorted(w['h'] for w in ws)[len(ws)//2],"max",max(w['h'] for w in ws))
    tiny=[w['text'] for w in ws if w['h']<24]
    print("  tiny(<24px):", tiny[:14])
    ov=[(a['text'],b['text'],round(iou(a,b),2)) for i,a in enumerate(ws) for b in ws[i+1:] if iou(a,b)>0.35]
    print("  overlaps:", ov[:8])
    print("  sample text:", " | ".join(w['text'] for w in ws[:22]))
