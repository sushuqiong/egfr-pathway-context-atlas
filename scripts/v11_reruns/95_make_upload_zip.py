#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the submission upload ZIP with self-explaining internal names."""
import os, zipfile, shutil
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
DESK=r"C:\Users\fengq\Desktop\EGFR"
stage=os.path.join(V11,"_upload_stage")
if os.path.isdir(stage): shutil.rmtree(stage)
os.makedirs(os.path.join(stage,"01_Manuscript"), exist_ok=True)
os.makedirs(os.path.join(stage,"02_Figures_TIFF"), exist_ok=True)
os.makedirs(os.path.join(stage,"03_Supplementary_Tables"), exist_ok=True)

copies=[
 (os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.docx"), "01_Manuscript/01_Manuscript_v11.docx"),
 (os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.pdf"),  "01_Manuscript/02_Manuscript_v11.pdf"),
 (os.path.join(V11,"01_稿件正文","Cover_letter_v11.txt"),       "01_Manuscript/03_Cover_Letter_v11.txt"),
 (os.path.join(V11,"06_投稿清单与流程","人工项填写指南_v11.md"), "00_先看这个_人工项填写指南.md"),
 (os.path.join(V11,"06_投稿清单与流程","送审自查包_v11.md"),     "00_先看这个_送审自查包.md"),
 (os.path.join(V11,"06_投稿清单与流程","Submission_readiness_checklist_v11.md"), "00_先看这个_投稿清单.md"),
]
for src,dst in copies:
    if os.path.exists(src): shutil.copy(src, os.path.join(stage,dst))
    else: print("[MISS]",src)
tiff_src=os.path.join(V11,"02_图片_TIFF")
for f in sorted(os.listdir(tiff_src)):
    if f.lower().endswith((".tif",".tiff",".csv")): shutil.copy(os.path.join(tiff_src,f), os.path.join(stage,"02_Figures_TIFF",f))
tab_src=os.path.join(V11,"03_表格与补充数据")
keep=[f for f in os.listdir(tab_src) if f.startswith(("TableS","v11_","sc_v11","context_atlas_summary","xcell")) and "_v9" not in f and "_v10" not in f]
for f in sorted(keep)[:60]:
    name=f
    if f=="v11_evidence_matrix.csv": name="TableS9_evidence_matrix_v11.csv"
    shutil.copy(os.path.join(tab_src,f), os.path.join(stage,"03_Supplementary_Tables",name))
shutil.copy(os.path.join(V11,"04_评审记录与报告","v18_v11_corrections.md"), os.path.join(stage,"04_修改说明_v18.md"))
with open(os.path.join(stage,"00_上传顺序.txt"),"w",encoding="utf-8") as f:
    f.write("""上传顺序（Springer Nature 投稿系统）
1. 01_Manuscript/03_Cover_Letter_v11.txt      -> Cover letter
2. 01_Manuscript/01_Manuscript_v11.docx       -> Manuscript（正式稿）
3. 02_Figures_TIFF/Figure1..Figure6, FigureS1/S2 -> Figures（300 dpi, 宽≤17cm；规格见 figure_specs.csv）
4. 03_Supplementary_Tables/                   -> Supplementary tables（逐个标注 S1, S2 ...）
5. 00_先看这个_人工项填写指南.md              -> 你自己照做（作者/CRediT、Cover 抬头、AI 问答）
说明：所有图与表均由 EGFR的v11 冻结结果表自动生成；tests/check_v11_consistency.py 当前 PASS。
""")
out=os.path.join(DESK,"★投稿上传-就选这个_v11.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for dp,dn,fn in os.walk(stage):
        for f in fn:
            fp=os.path.join(dp,f); z.write(fp, os.path.relpath(fp, stage))
print("ZIP:", out, round(os.path.getsize(out)/1e6,2), "MB")
print("contents:")
with zipfile.ZipFile(out) as z:
    for n in sorted(z.namelist())[:24]: print("  ", n)
shutil.rmtree(stage)
