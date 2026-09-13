#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil, re
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
REPO=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
# 1) checklist: mark TIFF/zip done, add upload pointer
p=os.path.join(V11,"06_投稿清单与流程","Submission_readiness_checklist_v11.md")
s=open(p,encoding="utf-8").read()
s=s.replace("- [ ] 人工项：作者名单/CRediT、Cover 抬头、图 TIFF 目检、投稿系统 AI 问答",
 "- [x] 图件 TIFF 导出（02_图片_TIFF，300 dpi，宽 ≤17 cm，规格表 figure_specs.csv）\n"
 "- [x] 上传 ZIP：Desktop\\EGFR\\★投稿上传-就选这个_v11.zip（含稿件/封面信/图/补充表/指南）\n"
 "- [x] 人工项填写指南：06_投稿清单与流程\\人工项填写指南_v11.md\n"
 "- [ ] 人工项（按指南逐项做）：作者名单/CRediT、Cover 抬头、投稿系统 AI 问答、目检图版")
open(p,"w",encoding="utf-8").write(s)
# 2) README: mention tiff + zip + guide
rp=os.path.join(V11,"README_索引.md"); rs=open(rp,encoding="utf-8").read()
rs += ("\n## 上传与人工项\n"
       "- 投稿用图：`02_图片_TIFF\\`（300 dpi TIFF，宽 ≤17 cm；`figure_specs.csv` 列出规格）\n"
       "- 一次打包上传：`Desktop\\EGFR\\★投稿上传-就选这个_v11.zip`（自解释内部命名 + 上传顺序说明）\n"
       "- 人工项照做：`06_投稿清单与流程\\人工项填写指南_v11.md`（作者/CRediT、Cover 抬头、AI 问答、提交后登记）\n")
open(rp,"w",encoding="utf-8").write(rs)
# 3) repo: add guide
shutil.copy(os.path.join(V11,"06_投稿清单与流程","人工项填写指南_v11.md"), os.path.join(REPO,"SUBMISSION_GUIDE_v11.md"))
print("docs updated")
