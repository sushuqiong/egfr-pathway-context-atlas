#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR QA v2: copy figures to an ASCII temp dir, call tesseract TSV, and analyse layout."""
import csv, os, shutil, subprocess, collections, tempfile
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"; FIGDIR=os.path.join(V11,"02_图片")
TMP=r"C:\Users\fengq\ocr_tmp"; shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
FIGS=["fig1_parallel_layers_v11.png","fig2a_raw_v11.png","fig2b_adjusted_v11.png","fig3_base_vs_adjusted_v11.png",
      "fig4_survival_v11.png","fig5_molecular_v11.png","fig6_sc_v11.png","fig_paper_xcell_vs_marker.png","fig_paper_xcell_heatmap.png"]
EXPECT={"fig1_parallel_layers_v11.png":["55/170","17","74","0.87","16","12","556/187"],
 "fig2a_raw_v11.png":["Raw","LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"],
 "fig2b_adjusted_v11.png":["Adjusted","LUAD","Asthma"],
 "fig3_base_vs_adjusted_v11.png":["Base","adjusted","170"],
 "fig4_survival_v11.png":["LUAD","CRC","STAD","PAAD","HCC","ESCC","hazard"],
 "fig5_molecular_v11.png":["Amplification","Mutation","EGFR","ERBB2","TP53","KRAS"],
 "fig6_sc_v11.png":["Same-cell-type","cell-identity","pairs","CRC","IBD","STAD"],
 "fig_paper_xcell_vs_marker.png":["xCell","marker"],
 "fig_paper_xcell_heatmap.png":["LUAD","CRC","STAD","PAAD"]}
def ocr(path):
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    r=subprocess.run([TESS,path,"stdout","--psm","11","tsv"],capture_output=True,env=env)
    txt=r.stdout.decode("utf-8","replace"); err=r.stderr.decode("utf-8","replace")
    rows=[]
    for row in csv.DictReader(txt.splitlines(), delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try: rows.append(dict(text=t,conf=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    return rows, err.strip()
def iou(a,b):
    x1,y1=max(a["x"],b["x"]),max(a["y"],b["y"]); x2,y2=min(a["x"]+a["w"],b["x"]+b["w"]),min(a["y"]+a["h"],b["y"]+b["h"])
    if x2<=x1 or y2<=y1: return 0.0
    return (x2-x1)*(y2-y1)/float(min(a["w"]*a["h"],b["w"]*b["h"]))
out=[]
for f in FIGS:
    src=os.path.join(FIGDIR,f); dst=os.path.join(TMP,f)
    shutil.copy(src,dst)
    W,H=Image.open(dst).size
    words,err=ocr(dst); words=[w for w in words if w["conf"]>30]
    clip=[w for w in words if w["x"]<=2 or w["y"]<=2 or w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2]
    tiny=[w for w in words if w["h"]<22]
    ov=[(a["text"],b["text"]) for i,a in enumerate(words) for b in words[i+1:] if iou(a,b)>0.35]
    txt=" ".join(w["text"] for w in words).lower()
    miss=[t for t in EXPECT.get(f,[]) if t.lower() not in txt]
    med=sorted(w["h"] for w in words)[len(words)//2] if words else 0
    out.append(dict(file=f,size=f"{W}x{H}",words=len(words),median_text_h=med,
                    clipping=len(clip),tiny=len(tiny),overlaps=len(ov),missing=";".join(miss),
                    ocr_err=err[:60]))
    print(f"{f:34} {W}x{H} words={len(words):3} med_h={med:3} clip={len(clip)} tiny={len(tiny)} ov={len(ov)} miss={miss} {('ERR:'+err[:40]) if err else ''}")
with open(os.path.join(V11,"04_评审记录与报告","ocr_figure_qa.csv"),"w",encoding="utf-8-sig",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("\nsaved -> 04_评审记录与报告/ocr_figure_qa.csv")
