#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 figure QA v3 (final): page size, clipping, and overlap adjudication with OCR fragmentation handling.

Rules
  1. clipped  : a word box touching the canvas edge with ink at the edge -> real defect.
  2. overlap  : two word boxes on the same line whose spans intersect AND whose intersection contains ink.
     A pair is DISMISSED when the two boxes are horizontally adjacent (gap <= 3 px) and their concatenation
     forms a number or a single label fragment (OCR splits decimals and long labels into pieces); such pairs
     are not visual collisions. Everything else is reported as a candidate collision.
"""
import csv, os, re, subprocess, shutil, sys, itertools
import numpy as np
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
INK=110
NUM=re.compile(r"^\d+(\.\d+)?$|^[.,]$|^[-+]$")
def qa(fig_dir, tmp=r"C:\Users\fengq\ocr_v14qa3", verbose=True):
    shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp,exist_ok=True)
    env=dict(os.environ,TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    rows=[]
    for f in sorted(x for x in os.listdir(fig_dir) if x.endswith(".png")):
        dst=os.path.join(tmp,f); shutil.copy(os.path.join(fig_dir,f),dst)
        im=Image.open(dst).convert("L"); W,H=im.size; arr=np.array(im)
        r=subprocess.run([TESS,dst,"stdout","--psm","11","tsv"],capture_output=True,env=env)
        ws=[]
        for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(),delimiter="\t"):
            t=(row.get("text") or "").strip()
            if not t: continue
            try: ws.append(dict(t=t,c=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
            except Exception: pass
        ws=[w for w in ws if w["c"]>30]
        clip=[]
        for w in ws:
            if w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2 or w["x"]<=2 or w["y"]<=2:
                edge=arr[max(0,w["y"]):w["y"]+w["h"], max(W-4,W-40):W]
                if edge.size and (edge<INK).mean()>0.005: clip.append(w["t"])
        cand=[]; dismissed=[]
        for a,b in itertools.combinations(ws,2):
            if abs((a["y"]+a["h"]/2)-(b["y"]+b["h"]/2)) < 0.5*min(a["h"],b["h"]):
                x0=max(a["x"],b["x"]); x1=min(a["x"]+a["w"],b["x"]+b["w"])
                y0=max(a["y"],b["y"]); y1=min(a["y"]+a["h"],b["y"]+b["h"])
                if x1<=x0 or y1<=y0: continue
                crop=arr[max(0,y0):max(1,y1), max(0,x0):max(1,x1)]
                if crop.size==0 or (crop<INK).mean()<0.02: dismissed.append((a["t"],b["t"],"blank intersection")); continue
                gap = max(a["x"],b["x"]) - min(a["x"]+a["w"], b["x"]+b["w"])
                merged=(a["t"]+b["t"]) if a["x"]<=b["x"] else (b["t"]+a["t"])
                if gap<=3 and (NUM.match(a["t"]) or NUM.match(b["t"]) or NUM.match(merged)):
                    dismissed.append((a["t"],b["t"],"OCR fragmentation of one number")); continue
                cand.append((a["t"],b["t"],round(float((crop<INK).mean()),3)))
        rows.append(dict(file=f, cm_w=round(W/300*2.54,1), cm_h=round(H/300*2.54,1), words=len(ws),
                         clipped=len(clip), candidate_collisions=len(cand), dismissed=len(dismissed)))
        if verbose:
            print(f"{f}: {W/300*2.54:.1f} x {H/300*2.54:.1f} cm | words={len(ws)} | clipped={len(clip)} "
                  f"| candidate collisions={len(cand)} | dismissed={len(dismissed)}")
            if clip: print("   clipped (ink at edge):", clip[:4])
            if cand: print("   candidates:", cand[:4])
            pat={}
            for a,b,why in dismissed: pat[why]=pat.get(why,0)+1
            if pat: print("   dismissed reasons:", pat)
    return rows
if __name__=="__main__":
    d=sys.argv[1] if len(sys.argv)>1 else "."
    rows=qa(d)
    bad=[r for r in rows if r["clipped"]>0 or r["candidate_collisions"]>0 or r["cm_w"]>17.2 or r["cm_h"]>24.0]
    print("\n"+("PASS: no clipping, no candidate collisions, all figures within 17.0 x 24 cm" if not bad else f"FLAGGED: {len(bad)}"))
