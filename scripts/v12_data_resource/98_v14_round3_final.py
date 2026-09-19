#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14.3 final: legends fix, tables + SI rebuild, submission ZIP without internal notes,
inventory/checksums, verification and push."""
import csv, hashlib, os, re, shutil, subprocess, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
TBL=os.path.join(V14,"03_tables"); FIG=os.path.join(V14,"02_figures")
# 1. legends: supplementary range
q=os.path.join(V14,"scripts","71_v14_tables_legends.py"); t=open(q,encoding="utf-8").read()
if "S1-S16" in t:
    t=t.replace("Tables S1-S16 accompany this manuscript","Tables S1-S17 accompany this manuscript")
    t=t.replace("Tables 1 and Supplementary Tables S1-S16","Table 1 and Supplementary Tables S1-S17")
    open(q,"w",encoding="utf-8").write(t); print("legends builder updated to S1-S17")
rr=subprocess.run([os.sys.executable, q],capture_output=True,text=True,cwd=V14)
print((rr.stdout or "").strip().splitlines()[-1][:90] if rr.stdout else rr.stderr[-200:])
# 2. SI pdf
soffice=r"C:\Program Files\LibreOffice\program\soffice.exe"
subprocess.run([soffice,"--headless","--convert-to","pdf","--outdir",TBL,os.path.join(TBL,"Tables_v14.docx")],capture_output=True)
src=os.path.join(TBL,"Tables_v14.pdf"); dst=os.path.join(TBL,"Supplementary_Information.pdf")
if os.path.exists(src): shutil.move(src,dst)
print("SI pdf:", os.path.exists(dst), round(os.path.getsize(dst)/1e6,2),"MB")
# 3. inventory + checksums (LF, hash lines only, trailing newline)
def digest(fp):
    h=hashlib.sha256()
    with open(fp,"rb") as fh:
        for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
    return h.hexdigest()
def rebuild_inventory():
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
    inv.append(dict(file="08_qc/file_inventory_and_checksums.csv", bytes="", rows=n, sha256="self-reference: its hash is recorded in checksums_sha256.txt"))
    inv.append(dict(file="08_qc/checksums_sha256.txt", bytes="", rows="", sha256="self-reference"))
    with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8",newline="\n") as f:
        w=csv.DictWriter(f,fieldnames=["file","bytes","rows","sha256"],lineterminator="\n"); w.writeheader(); w.writerows(inv)
    with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8",newline="\n") as f:
        f.write("\n".join(f"{r['sha256']}  {r['file']}" for r in inv if len(str(r["sha256"]))==64)+"\n")
    return len(inv), sum(1 for r in inv if len(str(r["sha256"]))==64)
n_all,n_ck=rebuild_inventory()
# two-pass: re-hash everything now that the checksum file exists
n_all2,n_ck2=rebuild_inventory()
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt",cwd=PK,shell=True,capture_output=True,text=True)
print(f"files {n_all2} | SHA entries {n_ck2} | verified {sum(1 for l in r.stdout.splitlines() if l.endswith(': OK'))} | problems {[l for l in r.stdout.splitlines() if not l.endswith(': OK')] or 'none'} | stderr {r.stderr.strip() or 'none'}")
# manuscript counts must match the manifest
mp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mp,encoding="utf-8").read()
md2=re.sub(r"\((\d+) files, with (\d+) SHA-256 entries[^)]*\)", f"({n_all2} files, with {n_ck2} SHA-256 entries because the two verification files are self-referential)", md)
if md2!=md:
    open(mp,"w",encoding="utf-8").write(md2); print("manuscript counts refreshed to", n_all2, n_ck2)
# 4. ZIPs: Zenodo = deposit; submission = manuscript artefacts ONLY (no internal notes)
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v14"); shutil.make_archive(z,"zip",PK)
stage=os.path.join(V14,"_stage6"); shutil.rmtree(stage,ignore_errors=True)
pairs=[("01_manuscript/DataDescriptor_v14.docx","01_Manuscript/DataDescriptor_v14.docx"),
       ("01_manuscript/DataDescriptor_v14.pdf","01_Manuscript/DataDescriptor_v14.pdf"),
       ("03_tables/Supplementary_Information.pdf","02_Supplementary/Supplementary_Information.pdf"),
       ("03_tables/Tables_v14.docx","02_Supplementary/Tables_v14.docx"),
       ("03_tables/Figure_legends_v14.docx","02_Supplementary/Figure_legends_v14.docx")]
names={1:"resource_overview",2:"technical_validation",3:"comparability_checks",4:"sensitivity_checks"}
for i in (1,2,3,4):
    for ext in ("png","pdf"): pairs.append((f"02_figures/Fig{i}_{names[i]}.{ext}", f"03_Figures/Fig{i}_{names[i]}.{ext}"))
for a,b in pairs:
    sp2=os.path.join(V14,a)
    if os.path.exists(sp2):
        os.makedirs(os.path.dirname(os.path.join(stage,b)),exist_ok=True); shutil.copy(sp2,os.path.join(stage,b))
open(os.path.join(stage,"00_READ_ME_FIRST.txt"),"w",encoding="utf-8").write(
"Submission package - cross-disease transcriptomic resource (v14)\n\n"
"01_Manuscript : DataDescriptor_v14.docx (editable) and .pdf\n"
"02_Supplementary : Supplementary_Information.pdf (Table 1 and Supplementary Tables S1-S17) and the same tables as .docx\n"
"03_Figures : Figures 1-4 as .png (300 dpi) and .pdf\n\n"
"The data deposit (93 files incl. analysis code) is provided separately as the Zenodo archive; the DOI is inserted in the\n"
"manuscript once the deposit is published. Internal working notes are intentionally not part of this package.\n")
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v14.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zips:", round(os.path.getsize(z+".zip")/1e6,2),"MB /",round(os.path.getsize(out)/1e6,2),"MB")
# 5. push
repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
shutil.copy(mp, os.path.join(repo,"manuscript","DataDescriptor_v14.md"))
for f in os.listdir(os.path.join(V14,"scripts")):
    shutil.copy(os.path.join(V14,"scripts",f), os.path.join(repo,"scripts","v12_data_resource",f))
for f in ["single_cell_sensitivity_min10cells_per_donor.csv","single_cell_multiplicity_strategy_comparison.csv"]:
    p=os.path.join(PK,"06_single_cell",f)
    if os.path.exists(p): shutil.copy(p, os.path.join(repo,"results",f))
for f in ["figure_qa_notes.md","checksums_sha256.txt"]:
    p=os.path.join(PK,"08_qc",f)
    if os.path.exists(p): shutil.copy(p, os.path.join(repo,"results",f))
for cmd in [["git","add","-A"],["git","-c","user.name=sushuqiong","-c","user.email=fengqi9666@qq.com","commit","-q","-m",
            "v14.3: second cold-read round closed - manuscript docx/pdf rebuilt from the current markdown with byte-identical embedded figures and superscript citations, single-cell sensitivity analyses folded in (Table S17), single-cohort rows labelled, counts regenerated from the manifest, duplicates removed, README/run_order/PROVENANCE corrected, submission package without internal notes"],
            ["git","push","-q","origin","main"]]:
    rr2=subprocess.run(cmd,cwd=repo,capture_output=True,text=True); print(cmd[1],"->",rr2.returncode)
print(subprocess.run(["git","log","--oneline","-1"],cwd=repo,capture_output=True,text=True).stdout.strip())
