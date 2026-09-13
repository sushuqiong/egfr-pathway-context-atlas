#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, os, subprocess
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"; TMP=r"C:\Users\fengq\ocr_tmp"
def ocr(p):
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    r=subprocess.run([TESS,p,"stdout","--psm","11","tsv"],capture_output=True,env=env)
    out=[]
    for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(), delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try: out.append(dict(text=t,conf=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    return [w for w in out if w["conf"]>30]
def iou(a,b):
    x1,y1=max(a["x"],b["x"]),max(a["y"],b["y"]); x2,y2=min(a["x"]+a["w"],b["x"]+b["w"]),min(a["y"]+a["h"],b["y"]+b["h"])
    if x2<=x1 or y2<=y1: return 0.0
    return (x2-x1)*(y2-y1)/float(min(a["w"]*a["h"],b["w"]*b["h"]))
for f in ["fig2a_raw_v11.png","fig2b_adjusted_v11.png","fig4_survival_v11.png","fig6_sc_v11.png","fig_paper_xcell_heatmap.png"]:
    p=os.path.join(TMP,f); ws=ocr(p)
    from PIL import Image; W,H=Image.open(p).size
    print(f"\n===== {f} {W}x{H} =====")
    tiny=[(w['text'],w['h'],w['y']) for w in ws if w['h']<24]
    print("  tiny:", tiny[:12])
    ov=[(a['text'],a['x'],a['y'],a['w'],a['h'],b['text'],b['x'],b['y'],round(iou(a,b),2)) for i,a in enumerate(ws) for b in ws[i+1:] if iou(a,b)>0.35]
    for o in ov[:8]: print("  OV:", o)
    edges=[(w['text'],w['x'],w['y'],w['w'],w['h']) for w in ws if w['x']<=2 or w['y']<=2 or w['x']+w['w']>=W-2 or w['y']+w['h']>=H-2]
    if edges: print("  EDGE:", edges)
