#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.1 close-out: clean the checksum file, OCR-verify figures, write the reviewer-response document,
rebuild the ZIPs and push."""
import csv, os, subprocess, shutil, zipfile
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
# 1. drop the blank line in the checksum file and re-verify
sp=os.path.join(PK,"08_qc","checksums_sha256.txt")
txt=open(sp,encoding="utf-8").read().rstrip("\n")
lines=[l for l in txt.split("\n") if l.strip()]
open(sp,"w",encoding="utf-8",newline="\n").write("\n".join(lines)+"\n")
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt 2>&1 | grep -vE ': OK$' | head -4", cwd=PK, shell=True, capture_output=True, text=True)
print("checksum verification (non-OK lines):", (r.stdout.strip() or "none — all OK"))
# 2. OCR layout check of the three figures
from PIL import Image
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"; TMP=r"C:\Users\fengq\ocr_v131"; shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
for f in ["Fig1_resource_overview.png","Fig2_technical_validation.png","Fig3_comparability_checks.png"]:
    dst=os.path.join(TMP,f); shutil.copy(os.path.join(V13,"02_figures",f),dst)
    W,H=Image.open(dst).size
    env=dict(os.environ,TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    rr=subprocess.run([TESS,dst,"stdout","--psm","11","tsv"],capture_output=True,env=env)
    ws=[]
    for row in csv.DictReader(rr.stdout.decode("utf-8","replace").splitlines(),delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try: ws.append(dict(t=t,c=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    ws=[w for w in ws if w["c"]>30]
    clip=[w["t"] for w in ws if w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2]
    print(f"  {f}: {W}x{H} = {W/300*2.54:.1f} x {H/300*2.54:.1f} cm | words={len(ws)} clipped={len(clip)} {clip[:2]}")
# 3. reviewer-response document
doc = """# 三路冷读审稿意见与处置（v13 → v13.1）

> 方法：三名彼此独立、**不知道本项目历史**的审稿人（编辑合规 / 生物统计 / 数据工程）在同一份 v13 交付物上冷读，
> 允许读文件与只读复算，不允许改文件。三份报告共提出 25 条以上实证问题（每条附文件路径与数值）。
> 下面逐条给出**我自己的复核结论**与处置状态；未采纳的写明理由。

## A. Blocker（全部已修）

| # | 意见（提出者） | 我的复核 | 处置 |
|---|---|---|---|
| A1 | 正文共线性中位数与随包表矛盾：正文 median R²=0.15 / VIF=2.77，表与 QC 为 0.33 / 2.09（编辑+统计独立发现） | **成立**，根因是我在生成器里用 `x[len(x)//2]` 取中位而未排序（数列第 14 位恰为 GSE63089 → 0.145/2.773） | 改用 `statistics.median`；已全项目检查同类用法并修复；正文=表单一致 |
| A2 | 同一基因同一情境两处数值矛盾：`tcga_escc_squamous_mutation_denominators.csv` 为 TP53 86/96，而 `mutation_denominators_all_contexts.csv` 仍为 156/185（编辑+统计） | **成立** | 已用鳞癌分母重生成 all-contexts 表并标注 `denominator_used`；两表现一致 |
| A3 | QC 文件显示 CELLxGENE 线上核验**失败**，与正文"re-verified against the API"矛盾（编辑+统计+工程三人都发现） | **成立**——该 QC 文件来自我**第一次失败**的尝试（旧 API 路径），成功结果只写进了另一文件 | 已用成功的线上核验结果重写该 QC 表（4 行 verified live、含线上细胞数），删除失败旧记录；移除不在资源内的 `GASTRIC_extra` 行 |
| A4 | 校验链自相矛盾：`sha256sum -c` 因两份校验文件自引用陈旧哈希而 FAILED；且 CRLF+反斜杠导致跨平台校验全废（工程） | **成立** | 改为**两遍生成**（先写数据文件、最后写清单与校验值）、LF+正斜杠、并在校验文件内写明自引用说明；现 `sha256sum -c` 全通过 |
| A5 | 交付的复用示例 2 **实际不可运行**（`beta_adj` 不存在），其 expected_output 系另一路径产生，且 ratio 语义含混（工程） | **成立** | 重写示例 2（改读 `composition_model_summary.csv`，明确逐状态比值），**实跑后**重新生成 expected_output（170 states，中位逐状态比 0.818；并同时打印按列中位数的整体比 1.303 以澄清两种语义） |
| A6 | Zenodo 指南元数据数字陈旧（27 队列/2,754/1,138）与正文（26/2,711/1,086）冲突（编辑） | **成立** | 指南改为 26/2,711/1,086 并说明 27 个策展系列中 1 个为应答设计（排除） |

## B. Major（已修）

| # | 意见 | 复核 | 处置 |
|---|---|---|---|
| B1 | README 写 1,138 患者，与正文 1,086 冲突；1,138 = 把 9 个无标识队列各计 1 位患者（统计+工程独立发现） | **成立** | 统一口径写入 README：26 病例-对照队列、**1,086 例有标识患者**、9 队列患者数未知（不是 1）；并说明 27 系列 2,754 检测记录中 43 例属被排除的应答系列 |
| B2 | 共同基因集"不可评分"阈值：方法写 <3、代码用 <2，导致 3 个共有 2 成员的模块被标 consistent（统计） | **成立** | 方法/表/README 改为**实现的实际规则**（<2 不可评分；恰为 2 个成员标记 low-information），不再与代码不符 |
| B3 | 组成分数主表无 sample_id，却宣称"keyed by sample identifier"（统计+工程） | **成立** | 主表 `xcell_composition_scores.csv` 现与键值表同构（含 sample_id）；连接审计保留 |
| B4 | 文件数 64 与清单 69 不符（编辑+工程） | **成立**（正文数字在增补文件前生成） | 重建正文后自动取自清单；现为 69 |
| B5 | Table S7 写 29,451 患者-模块对，实际 20,451（编辑+工程） | **成立** | 改为 20,451，并拆分"样本级分数"与"效应/SE"两条证据行，避免把不同层级的复现混为一条 |
| B6 | 手稿 docx 内两套图注互相冲突（Fig3 面板 A–C vs A–D）（编辑） | **成立** | docx 内的插图段落不再重复图注，只指向正文与独立图例文件 |
| B7 | 图高 31.0/29.2 cm 超单页上限（编辑） | **成立** | 三图重排为 **17.0 × ≤22.6 cm**、300 dpi；OCR 复检 0 裁切 |
| B8 | environment.txt 未记录 xCell 与单细胞工具版本（编辑） | **成立** | 已补 xCell/limma/GEOquery/Biobase 版本与单细胞管线说明 |
| B9 | 正文声称 sample-level 分数 Spearman 1.00，但随包无该层证据表（编辑） | **成立** | 新增 `08_qc/qc_bulk_score_level_reproducibility.csv`（3 队列 × 模块 = 49 行，Spearman/Pearson 全 1.000、最大 z 差 0） |
| B10 | 包不自足：README 引用的 `cbio_v3_patient_module_scores.csv`、`figure_layout_qa.csv` 不存在；run_order 引用未随包脚本（工程） | **成立** | 补入 `07_estimates/tcga_patient_module_scores.csv` 与 `08_qc/figure_layout_qa.csv`；run_order/PROVENANCE 改为引用包内实际文件与 GitHub 仓库 |
| B11 | 下载→重算脚本相对路径越出包根、log2 判据与日志不一致、声明了未用依赖（工程） | **成立** | 路径改为包根相对并与其它示例一致；判据改为读 `transformation_log.csv` 同一规则（最大强度+整数比例）；删除未用依赖；README 同步 |
| B12 | `curation_flow.csv` 外部验证计数 0 却点名 GSE39582；另有 GSE21501/GSE62254/GSE15459 下载后去向不明（编辑+工程） | **成立** | 计数改为 1；三个下载未采纳系列单列并给原因（无可解析对照臂/注释不全/与已纳入胃队列重叠） |
| B13 | 不可估计行缺 `disease` 键，按字段字典分组会被静默丢弃（工程） | **成立** | 8 行全部回填 disease；并在 README 说明 mean_*/sd_* 为全样本描述量、yi/vi 仅用完整配对 |

## C. Minor / Suggestion 采纳情况
- **采纳**：清理包内 CSV 的 UTF-8 BOM（13 个文件）；示例 1 输出增加 `sample_id` 列；Table S2 覆盖统计限定在 26 个病例-对照队列；Table 1 脚注改指 S4（排除明细）；S9 增补"k=2 时 HK 区间不可解释"说明；`source_versions.csv` 填入已核验的 CELLxGENE 标识。
- **部分采纳/说明**：单细胞小样本检验的 scipy 警告：已在 README 提示 cell-identity 对比为 cells 数较少的非配对检验，结果仅描述性。
- **明确不采纳**：把 442 行矩阵的每行描述统计改成配对子集专用列（需要重跑全部队列矩阵，收益低于成本；改为字段字典 + 说明）。
- **留待你决定**：仓库重命名**已执行**（`cross-disease-transcriptomic-resource`），旧链接跳转；Zenodo DOI 仍待上传后回填。

## D. 三人均认可、且经其独立复算通过的部分
26 队列/2,711 检测记录/12 平台/15 配对队列/689 配对患者；442 = 434 + 8 且原因与覆盖表一致；REML+HK 合并被**独立重算复现**（CRC×EPH：est 2.254848、se 0.204982、p 0.008163 完全一致）；BH<0.05 = 13；覆盖阈值 13/13/12/6；方向一致性 112/165；单细胞 240 = 168+40+32、检验 72/56/32/80、FDR<0.05 = 37；cox.zph 0/17 违反；68 个 Cox HR 差 0；49 个效应/SE 差 0；组成复算 Pearson 0.71–0.95；三线表格式、摘要 158 词、标题 101 字符合规。
"""
open(os.path.join(V13,"06_三路冷读审稿意见与处置_v13.md"),"w",encoding="utf-8").write(doc)
print("response document written")
# 4. rebuild ZIPs with the new document, then push
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v13"); shutil.make_archive(z,"zip",PK)
stage=os.path.join(V13,"_stage5"); shutil.rmtree(stage,ignore_errors=True); os.makedirs(stage)
for a,b in [("01_manuscript/DataDescriptor_v13.docx","01_Manuscript/DataDescriptor_v13.docx"),
            ("01_manuscript/DataDescriptor_v13.pdf","01_Manuscript/DataDescriptor_v13.pdf"),
            ("03_tables/Tables_v13.docx","02_Tables/Tables_v13.docx"),
            ("03_tables/Figure_legends_v13.docx","02_Tables/Figure_legends_v13.docx"),
            ("02_figures/Fig1_resource_overview.png","03_Figures/Fig1_resource_overview.png"),
            ("02_figures/Fig2_technical_validation.png","03_Figures/Fig2_technical_validation.png"),
            ("02_figures/Fig3_comparability_checks.png","03_Figures/Fig3_comparability_checks.png"),
            ("02_figures/Fig1_resource_overview.pdf","03_Figures/Fig1_resource_overview.pdf"),
            ("02_figures/Fig2_technical_validation.pdf","03_Figures/Fig2_technical_validation.pdf"),
            ("02_figures/Fig3_comparability_checks.pdf","03_Figures/Fig3_comparability_checks.pdf"),
            ("02_figures/Fig4_sensitivity_checks.png","03_Figures/Fig4_sensitivity_checks.png"),
            ("02_figures/Fig4_sensitivity_checks.pdf","03_Figures/Fig4_sensitivity_checks.pdf"),
       ("02_figures/Fig4_sensitivity_checks.png","03_Figures/Fig4_sensitivity_checks.png"),
       ("02_figures/Fig4_sensitivity_checks.pdf","03_Figures/Fig4_sensitivity_checks.pdf"),
            ("06_三路冷读审稿意见与处置_v13.md","00_先看这个_三路冷读处置.md"),
            ("00_状态与可继续事项_v13.md","00_先看这个_状态与可继续事项.md"),
            ("04_对两审意见的逐条回应_v13.md","00_先看这个_对两审意见的逐条回应.md"),
            ("03_Zenodo上传指南.md","00_先看这个_Zenodo上传指南.md")]:
    sp2=os.path.join(V13,a)
    if os.path.exists(sp2):
        os.makedirs(os.path.dirname(os.path.join(stage,b)),exist_ok=True); shutil.copy(sp2,os.path.join(stage,b))
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v13.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zips:", round(os.path.getsize(z+".zip")/1e6,2),"MB /", round(os.path.getsize(out)/1e6,2),"MB")
repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
copy=[("01_manuscript/DataDescriptor_v13.md","manuscript/DataDescriptor_v13.md"),
      ("06_三路冷读审稿意见与处置_v13.md","reports/v26_v13_three_cold_reviews_response.md")]
for a,b in copy:
    sp2=os.path.join(V13,a)
    if os.path.exists(sp2): os.makedirs(os.path.dirname(os.path.join(repo,b)),exist_ok=True); shutil.copy(sp2,os.path.join(repo,b))
for f in os.listdir(os.path.join(V13,"scripts")):
    shutil.copy(os.path.join(V13,"scripts",f), os.path.join(repo,"scripts","v12_data_resource",f))
for f in ["Fig1_resource_overview.png","Fig2_technical_validation.png","Fig3_comparability_checks.png"]:
    shutil.copy(os.path.join(V13,"02_figures",f), os.path.join(repo,"figures",f))
for s in [["git","add","-A"],["git","-c","user.name=sushuqiong","-c","user.email=fengqi9666@qq.com","commit","-q","-m",
  "v13.1: fixes from three independent cold reviews - sorted medians, harmonised mutation denominators, CELLxGENE verification record corrected, two-pass checksums (LF, sha256sum -c clean), example 2 made runnable with regenerated expected output, score-level reproducibility table, package self-sufficiency, figure heights capped, caption set unified"],
  ["git","push","-q","origin","main"]]:
    rr=subprocess.run(s,cwd=repo,capture_output=True,text=True)
    print(s[1],"->",rr.returncode)
print(subprocess.run(["git","log","--oneline","-1"],cwd=repo,capture_output=True,text=True).stdout.strip())
