#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 figure review beyond clipping: label completeness, print-size legibility, text-on-busy-background,
forbidden legend/title strips, margins, contrast and panel geometry. Uses only local tooling (OCR + pixels)."""
import csv, os, subprocess, shutil, sys
import numpy as np
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
ENV=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
def tokens(img_path):
    r=subprocess.run([TESS,img_path,"stdout","--psm","11","tsv"],capture_output=True,env=ENV)
    out=[]
    for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(),delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try:
            out.append(dict(t=t,c=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),
                            w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    return [w for w in out if w["c"]>30]
EXPECT={
 "Fig1_resource_overview.png": dict(letters=["A","B","C"], contexts=["LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"], modules=17),
 "Fig2_technical_validation.png": dict(letters=["A","B","C"], contexts=[], modules=0),
 "Fig3_comparability_checks.png": dict(letters=["A","B","C","D"], contexts=[], modules=0),
 "Fig4_sensitivity_checks.png": dict(letters=["A","B"], contexts=[], modules=0)}
def audit(fig_dir,tmp=r"C:\Users\fengq\fig_review"):
    shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    rows=[]
    for f,exp in EXPECT.items():
        src=os.path.join(fig_dir,f)
        if not os.path.exists(src): continue
        dst=os.path.join(tmp,f); shutil.copy(src,dst)
        im=Image.open(dst).convert("RGB"); W,H=im.size; arr=np.array(im.convert("L"))
        tk=tokens(dst); words=" ".join(t["t"] for t in tk)
        # 1 label completeness
        miss_letters=[l for l in exp["letters"] if l not in [t["t"] for t in tk]]
        miss_ctx=[c for c in exp["contexts"] if c.lower() not in words.lower()]
        # 2 print-size legibility: 50% downscale then OCR again
        small=os.path.join(tmp,"small_"+f)
        Image.open(dst).resize((W//2,H//2), Image.LANCZOS).save(small)
        tk_small=tokens(small)
        keep=len(tk_small)/max(1,len(tk))
        # 3 text on busy background: variance of local background inside each text box
        busy=0
        for t in tk:
            box=arr[max(0,t["y"]):t["y"]+t["h"], max(0,t["x"]):t["x"]+t["w"]]
            if box.size < 30: continue
            bg=box[box>np.percentile(box,60)]
            if bg.size and bg.std()>48: busy+=1
        # 4 forbidden legend/title strip: ink columns covering most of the width in the outer bands
        def strip(band):
            # a legend or figure title strip = ink present in >55% of the width, not merely scattered axis labels
            col=(band<110).mean(axis=0)
            return float((col>0.02).mean())
        top=strip(arr[:max(1,int(H*0.035)),:]); bottom=strip(arr[int(H*0.965):,:])
        # 5 margins
        ink=np.argwhere(arr<200)
        if ink.size:
            m_top,m_bot=ink[:,0].min(),H-1-ink[:,0].max(); m_left,m_right=ink[:,1].min(),W-1-ink[:,1].max()
        else: m_top=m_bot=m_left=m_right=0
        # 6 contrast per token (text vs local background luminance)
        ratios=[]; low_contrast=[]
        for t in tk:
            box=arr[max(0,t["y"]):t["y"]+t["h"], max(0,t["x"]):t["x"]+t["w"]].astype(float)
            if box.size<40 or box.std()<18: continue      # skip boxes with no readable contrast (graphical false positives)
            fg=float(np.percentile(box,5)); bgp=float(np.percentile(box,95))
            if bgp>fg:
                ratios.append((bgp+5)/(fg+5))
                low_contrast.append((t["t"], round((bgp+5)/(fg+5),2), t["x"], t["y"]))
        rows.append(dict(file=f, cm=f"{W/300*2.54:.1f}x{H/300*2.54:.1f}", tokens=len(tk),
                         missing_letters=";".join(miss_letters), missing_contexts=";".join(miss_ctx),
                         print_size_token_retention=f"{keep:.2f}", busy_background_tokens=busy,
                         top_strip_cover=f"{top:.2f}", bottom_strip_cover=f"{bottom:.2f}",
                         margins=f"top {m_top} bottom {m_bot} left {m_left} right {m_right}",
                         min_contrast=f"{min(ratios):.2f}" if ratios else "n/a",
                         worst=[x for x in low_contrast if x[1]<3][:5]))
    return rows
if __name__=="__main__":
    fig_dir=sys.argv[1] if len(sys.argv)>1 else "."
    rows=audit(fig_dir)
    for r in rows:
        print(f"\n{r['file']}  ({r['cm']} cm)  OCR tokens={r['tokens']}")
        print(f"  label completeness : missing panel letters={r['missing_letters'] or 'none'} | missing contexts={r['missing_contexts'] or 'none'}")
        print(f"  print-size check   : token retention at 50% scale = {r['print_size_token_retention']} (>0.6 acceptable)")
        print(f"  text on busy colour: {r['busy_background_tokens']} tokens sit on high-variance background")
        print(f"  outer strips       : top {r['top_strip_cover']} | bottom {r['bottom_strip_cover']} (>=0.55 would indicate a legend/title strip)")
        print(f"  margins (px)       : {r['margins']}")
        print(f"  minimum contrast   : {r['min_contrast']} (>3 acceptable)  worst: {r.get('worst')}")
