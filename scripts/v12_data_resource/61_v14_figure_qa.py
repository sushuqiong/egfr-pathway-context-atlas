#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 figure QA: page-size compliance, OCR text-layer clipping, and same-line text overlap detection."""
import csv, os, subprocess, shutil, sys, itertools
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def qa(fig_dir, tmp=r"C:\Users\fengq\ocr_v14qa"):
    shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp,exist_ok=True)
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    too_tall=[]; report=[]
    for f in sorted(x for x in os.listdir(fig_dir) if x.endswith(".png")):
        dst=os.path.join(tmp,f); shutil.copy(os.path.join(fig_dir,f),dst)
        im=Image.open(dst); W,H=im.size
        r=subprocess.run([TESS,dst,"stdout","--psm","11","tsv"],capture_output=True,env=env)
        ws=[]
        for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(),delimiter="\t"):
            t=(row.get("text") or "").strip()
            if not t: continue
            try: ws.append(dict(t=t,c=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
            except Exception: pass
        ws=[w for w in ws if w["c"]>30]
        clip=[w["t"] for w in ws if w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2 or w["x"]<=2 or w["y"]<=2]
        # same-line overlap: two words whose vertical centres are close and whose horizontal spans intersect
        ov=[]
        for a,b in itertools.combinations(ws,2):
            if abs((a["y"]+a["h"]/2)-(b["y"]+b["h"]/2)) < 0.5*min(a["h"],b["h"]):
                if not (a["x"]+a["w"] <= b["x"] or b["x"]+b["w"] <= a["x"]):
                    ov.append((a["t"],b["t"]))
        cm_w, cm_h = W/300*2.54, H/300*2.54
        if cm_h > 24.0: too_tall.append(f"{f} ({cm_h:.1f} cm)")
        report.append((f, cm_w, cm_h, len(ws), len(clip), len(ov), ov[:3], clip[:3]))
    return report, too_tall
if __name__ == "__main__":
    fig_dir=sys.argv[1] if len(sys.argv)>1 else "."
    rep, tall = qa(fig_dir)
    ok=True
    for f,cw,ch,nw,nc,no,ov,cl in rep:
        flag = "OK " if (cw<=17.2 and ch<=24.0 and nc==0 and no==0) else "CHECK"
        if flag=="CHECK": ok=False
        print(f"{flag} {f}: {cw:.1f} x {ch:.1f} cm | words={nw} clipped={nc} overlaps={no}")
        if ov: print("      overlap pairs:", ov)
        if cl: print("      clipped:", cl)
    print("\nALL FIGURES CLEAN" if ok else "\nFIGURES NEED ATTENTION")
