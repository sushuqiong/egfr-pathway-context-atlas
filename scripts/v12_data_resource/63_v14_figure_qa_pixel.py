#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 figure QA v2: page-size compliance, OCR clipping, and PIXEL-LEVEL overlap adjudication.

A candidate overlap pair (two OCR word boxes on the same line whose spans intersect) is re-checked by
counting dark pixels inside their intersection rectangle: if the intersection is essentially blank the
flag is an OCR bounding-box artefact, not a visual collision.
"""
import csv, os, subprocess, shutil, sys, itertools
import numpy as np
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
INK=110          # grey level below which a pixel counts as ink
ARTIFACT_FRAC=0.02   # <2% ink inside the intersection rectangle => artefact
def qa(fig_dir, tmp=r"C:\Users\fengq\ocr_v14qa2", verbose=True):
    shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp,exist_ok=True)
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    summary=[]
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
        clip=[w["t"] for w in ws if w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2 or w["x"]<=2 or w["y"]<=2]
        real=[]; arte=[]
        for a,b in itertools.combinations(ws,2):
            if abs((a["y"]+a["h"]/2)-(b["y"]+b["h"]/2)) < 0.5*min(a["h"],b["h"]):
                x0=max(a["x"],b["x"]); x1=min(a["x"]+a["w"],b["x"]+b["w"])
                y0=max(a["y"],b["y"]); y1=min(a["y"]+a["h"],b["y"]+b["h"])
                if x1<=x0 or y1<=y0: continue          # no true box intersection
                crop=arr[max(0,y0):max(1,y1), max(0,x0):max(1,x1)]
                frac=float((crop<INK).mean()) if crop.size else 0.0
                (real if frac>=ARTIFACT_FRAC else arte).append((a["t"],b["t"],round(frac,3)))
        summary.append(dict(file=f, cm_w=W/300*2.54, cm_h=H/300*2.54, words=len(ws), clipped=len(clip),
                            real_overlaps=len(real), artifact_flags=len(arte)))
        if verbose:
            print(f"{f}: {W/300*2.54:.1f} x {H/300*2.54:.1f} cm | words={len(ws)} | clipped={len(clip)} "
                  f"| real overlaps={len(real)} | bbox artefacts dismissed={len(arte)}")
            if clip: print("   clipped:", clip[:4])
            if real: print("   real overlaps (ink in intersection):", real[:4])
    return summary
if __name__ == "__main__":
    fig_dir=sys.argv[1] if len(sys.argv)>1 else "."
    rows=qa(fig_dir)
    bad=[r for r in rows if r["clipped"]>0 or r["real_overlaps"]>0 or r["cm_w"]>17.2 or r["cm_h"]>24.0]
    print("\n"+("ALL FIGURES CLEAN (0 clipping, 0 pixel-level overlaps, within page limits)" if not bad else f"ATTENTION: {len(bad)} figure(s) flagged"))
