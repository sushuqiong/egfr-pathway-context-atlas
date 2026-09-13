#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR QA v3: refined metrics (ignore sub-10px line-artifacts) and updated expectations."""
import csv, os, shutil, subprocess, collections
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"; FIGDIR=os.path.join(V11,"02_图片")
TMP=r"C:\Users\fengq\ocr_tmp"; shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
FIGS=["fig1_parallel_layers_v11.png","fig2a_raw_v11.png","fig2b_adjusted_v11.png","fig3_base_vs_adjusted_v11.png",
      "fig4_survival_v11.png","fig5_molecular_v11.png","fig6_sc_v11.png","fig_paper_xcell_vs_marker.png","fig_paper_xcell_heatmap.png"]
EXPECT={"fig1_parallel_layers_v11.png":["55 of 170","17","74","0.87","16","12","556 tumour","187 deaths"],
 "fig2a_raw_v11.png":["Raw","LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"],
 "fig2b_adjusted_v11.png":["Adjusted","LUAD","Asthma","not estimable"],
 "fig3_base_vs_adjusted_v11.png":["Base","adjusted","170"],
 "fig4_survival_v11.png":["LUAD","CRC","STAD","PAAD","HCC","ESCC","hazard"],
 "fig5_molecular_v11.png":["Amplification","Mutation","EGFR","ERBB2","TP53","KRAS","profiled"],
 "fig6_sc_v11.png":["Same-cell-type","identity","pairs","CRC","IBD","STAD"],
 "fig_paper_xcell_vs_marker.png":["marker","xCell"],
 "fig_paper_xcell_heatmap.png":["Sensitivity","xCell","residualization","LUAD","CRC","STAD","PAAD"]}
def ocr(path):
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    r=subprocess.run([TESS,path,"stdout","--psm","11","tsv"],capture_output=True,env=env)
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
rows=[]
for f in FIGS:
    src=os.path.join(FIGDIR,f); dst=os.path.join(TMP,f); shutil.copy(src,dst)
    W,H=Image.open(dst).size; ws=ocr(dst)
    real=[w for w in ws if w["h"]>=10 and w["w"]>=6]     # ignore line artifacts (<10px tall)
    clip=[w for w in real if w["x"]<=2 or w["y"]<=2 or w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2]
    tiny=[w for w in real if w["h"]<29]                  # < 7 pt at 300 dpi
    big=[w for w in real if w["h"]>=29]
    import re as _re
    def _clean(x): return len(_re.sub(r"[^0-9A-Za-z]","",x))>=3
    strong=[w for w in real if w["h"]>=29 and w["w"]>=25 and _clean(w["text"])]
    ov=[(a["text"],b["text"]) for i,a in enumerate(strong) for b in strong[i+1:] if iou(a,b)>0.3]
    txt=" ".join(w["text"] for w in real).lower()
    miss=[t for t in EXPECT.get(f,[]) if t.lower() not in txt]
    med=sorted(w["h"] for w in big)[len(big)//2] if big else 0
    rows.append(dict(file=f,size=f"{W}x{H}",words=len(real),median_text_h_px=med,below_7pt=len(tiny),
                     clipping=len(clip),overlaps=len(ov),missing=";".join(miss)))
    print(f"{f:34} {W}x{H} words={len(real):3} med_h={med:3} <7pt={len(tiny):3} clip={len(clip)} ov={len(ov)} miss={miss}")
with open(os.path.join(V11,"04_评审记录与报告","ocr_figure_qa.csv"),"w",encoding="utf-8-sig",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
bad=[r for r in rows if r["clipping"] or r["overlaps"] or r["missing"] or r["below_7pt"]>3]
print("\nFIGURES WITH REMAINING ISSUES:", len(bad))
for r in bad: print("  ", r)
