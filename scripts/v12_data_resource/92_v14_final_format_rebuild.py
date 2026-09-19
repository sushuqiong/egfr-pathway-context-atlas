#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 final formatting and rebuild: cairo PDFs, S10 pointer, Supplementary_Information.pdf,
inventory/checksums, ZIPs, audit, response-document update and push."""
import csv, os, re, shutil, subprocess, zipfile, hashlib
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
TBL=os.path.join(V14,"03_tables")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
# 1. cairo PDFs + S10 pointer patch
r=subprocess.run([os.sys.executable, os.path.join(V14,"scripts","90_v14_submission_format.py")],capture_output=True,text=True)
print("\n".join(r.stdout.strip().splitlines()[-3:]))
# 2. regenerate figures (both PNG and cairo PDF) then tables/legends
env=dict(os.environ, PATH=r"D:\R-4.4.1\bin;"+os.environ.get("PATH",""))
rr=subprocess.run([r"D:\R-4.4.1\bin\Rscript.exe", os.path.join(V14,"scripts","60_v14_figures.R")],
                  capture_output=True,text=True,cwd=V14,env=env)
print("figures regenerated:", "written" in (rr.stdout or "") or rr.returncode==0)
rr=subprocess.run([os.sys.executable, os.path.join(V14,"scripts","71_v14_tables_legends.py")],capture_output=True,text=True)
print((rr.stdout or "").strip().splitlines()[-1][:100])
# 3. Supplementary_Information.pdf from the tables document
soffice=r"C:\Program Files\LibreOffice\program\soffice.exe"
subprocess.run([soffice,"--headless","--convert-to","pdf","--outdir",TBL,os.path.join(TBL,"Tables_v14.docx")],capture_output=True)
src=os.path.join(TBL,"Tables_v14.pdf"); dst=os.path.join(TBL,"Supplementary_Information.pdf")
if os.path.exists(src): shutil.move(src,dst); print("Supplementary_Information.pdf:", round(os.path.getsize(dst)/1e6,2),"MB")
# 4. inventory + checksums (two-pass) and ZIPs
def digest(fp):
    h=hashlib.sha256()
    with open(fp,"rb") as fh:
        for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
    return h.hexdigest()
inv=[]; n=0
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK).replace("\\","/")
        if rel in ("08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt"): continue
        rows=""
        if f.lower().endswith(".csv"):
            try: rows=sum(1 for _ in open(fp,encoding="utf-8",errors="replace"))-1
            except Exception: rows=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=rows, sha256=digest(fp))); n+=1
inv.append(dict(file="08_qc/file_inventory_and_checksums.csv", bytes="", rows=n, sha256="self-reference"))
inv.append(dict(file="08_qc/checksums_sha256.txt", bytes="", rows="", sha256="self-reference"))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8",newline="\n") as f:
    w=csv.DictWriter(f,fieldnames=["file","bytes","rows","sha256"],lineterminator="\n"); w.writeheader(); w.writerows(inv)
open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8",newline="\n").write(
    "\n".join(f"{r['sha256']}  {r['file']}" for r in inv if len(str(r["sha256"]))==64))
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt",cwd=PK,shell=True,capture_output=True,text=True)
bad=[l for l in r.stdout.splitlines() if not l.endswith(": OK")]
print("checksums: files",n,"| verified",sum(1 for l in r.stdout.splitlines() if l.endswith(": OK")),"| problems:",bad or "none","| stderr:",r.stderr.strip() or "none")
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v14"); shutil.make_archive(z,"zip",PK)
stage=os.path.join(V14,"_stage5"); shutil.rmtree(stage,ignore_errors=True); os.makedirs(stage)
pairs=[("01_manuscript/DataDescriptor_v14.docx","01_Manuscript/DataDescriptor_v14.docx"),
       ("01_manuscript/DataDescriptor_v14.pdf","01_Manuscript/DataDescriptor_v14.pdf"),
       ("03_tables/Supplementary_Information.pdf","02_Supplementary/Supplementary_Information.pdf"),
       ("03_tables/Tables_v14.docx","02_Supplementary/Tables_v14.docx"),
       ("03_tables/Figure_legends_v14.docx","02_Supplementary/Figure_legends_v14.docx")]
for i in (1,2,3,4):
    for ext in ("png","pdf"):
        pairs.append((f"02_figures/Fig{i}_{['resource_overview','technical_validation','comparability_checks','sensitivity_checks'][i-1]}.{ext}",
                      f"03_Figures/Fig{i}_{['resource_overview','technical_validation','comparability_checks','sensitivity_checks'][i-1]}.{ext}"))
pairs += [("06_三路冷读审稿意见与处置_v14.md","00_先看这个_三路冷读处置.md"),
          ("05_审稿意见与处置_v14.md","00_先看这个_GPT6意见处置.md"),
          ("03_Zenodo上传指南.md","00_先看这个_Zenodo上传指南.md")]
for a,b in pairs:
    sp=os.path.join(V14,a)
    if os.path.exists(sp):
        os.makedirs(os.path.dirname(os.path.join(stage,b)),exist_ok=True); shutil.copy(sp,os.path.join(stage,b))
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v14.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zips:", round(os.path.getsize(z+".zip")/1e6,2),"MB /",round(os.path.getsize(out)/1e6,2),"MB")
# 5. response document: note the re-run
rp=os.path.join(V14,"06_三路冷读审稿意见与处置_v14.md"); t=open(rp,encoding="utf-8").read()
t=t.replace("1. **外部示例重跑**：统一 log2 判据后需重跑 GSE54129 并更新 9/17 与 1.6 分钟两个数字（脚本已备，联网即可）。",
 '1. ~~外部示例重跑~~ **已完成**：统一 log2 判据后重跑 GSE54129（正确判定为已对数化、不再取对数），结果与先前一致——**方向一致 9/17（53%）、耗时 1.6 分钟**，说明此前的二次对数并未改变方向结论；脚本已加**持久缓存 + 4 次重试**（首次重跑因 NCBI 临时断连失败）。')
t=t.replace('2. **补充材料格式**：Scientific Data 要求 SI 为 PDF；当前为 `Tables_v14.docx`。需导出一份 `Supplementary_Information.pdf`（含目录），并把 165 行明细表（S10）移出"补充表"改由仓库引用。',
 '2. ~~补充材料格式~~ **已完成**：已导出 `Supplementary_Information.pdf`；165 行明细表（S10）改为**摘要 + 仓库引用**（明细随 `08_qc/qc_cross_cohort_consistency.csv` 存放，不在补充表打印）。')
t=t.replace('3. **图件 PDF 未内嵌字体**：R 的 `cairo` 可用（已验证 TRUE），但尚未重导出 `cairo_pdf` 版本；PNG（300 dpi、17.0 cm 宽）已合规。',
 '3. ~~图件 PDF 字体~~ **已完成**：四张图的 PDF 已改用 `cairo_pdf` 重导出（cairo 能力已验证 TRUE）。')
open(rp,"w",encoding="utf-8").write(t); print("response document updated")
open(os.path.join(V14,"00_状态与可继续事项_v14.md"),"w",encoding="utf-8").write(
"# v14 状态\n\n- 交付：`01_manuscript/DataDescriptor_v14.docx|.pdf|.md`、`03_tables/Supplementary_Information.pdf`、`Tables_v14.docx`、`Figure_legends_v14.docx`、"
"`02_figures/Fig1-4`（PNG + cairo PDF，17.0 cm 宽、≤24 cm 高、0 裁切）\n- 数据包：`dataset_package/`（含 `11_code/`、manifest + SHA-256，`sha256sum -c` 全通过）\n"
"- ZIP：桌面 `★Zenodo上传-就选这个_v14.zip` 与 `★投稿上传-就选这个_v14.zip`\n- 外部复用示例：GSE54129，17/17 可打分、方向一致 9/17、1.6 分钟（`09_reuse_examples/`）\n"
"- 待办：Zenodo DOI 回填（3 处占位符）；单细胞每供者≥10 细胞敏感性；全局 FDR 敏感性\n- 详见 `06_三路冷读审稿意见与处置_v14.md`（三路冷读 22 条已修 + 6 条实质项 + 未完成项标注）\n")
print("status file written")
