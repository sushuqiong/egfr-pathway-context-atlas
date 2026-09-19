#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13: write the status/continuation note, the point-by-point response to both reviewers,
refresh the Zenodo guide, rebuild the ZIPs and push to GitHub."""
import os, subprocess, shutil, zipfile, csv
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
full=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
mut=rd(os.path.join(R,"v12_escc_mutation_denominators.csv")); cn=rd(os.path.join(R,"v12_escc_cna_summary.csv"))
tp53=[r for r in mut if r["gene"]=="TP53"][0]; eg=[r for r in cn if r["gene"]=="EGFR"][0]
state=f"""# v13 状态与可继续事项

## 本版做了什么（相对 v12）
| 编号 | 两份 AI 意见 | 处置 | 证据 |
|---|---|---|---|
| A1 | **"TP53 在食管鳞癌 0/96 是数据警报"（GPT6 与 Claude 均判为必改）** | **真因不是数据而是我的手稿模板**：模板取突变表首行（KRAS 0/96）却标注为 TP53。数据本身 TP53 = **{tp53['n_mutated_samples']}/{tp53['denominator_n']}（{tp53['pct']}%）**，符合食管鳞癌预期。已改为**按基因显式取值 + 断言**（找不到即报错），全项目清查无其它"首行取值" | `00_manuscript/DataDescriptor_v13.md`；审计项"TP53 reported as 86/96 with an explicit gene lookup" |
| A2 | 突变层 join/标签是否错位 | 已复核：突变分母=**仅突变谱内样本**（96 例鳞癌）；EGFR 突变 {eg['n_high_amp'] if False else [r for r in mut if r['gene']=='EGFR'][0]['n_mutated_samples']}/{tp53['denominator_n']}、KRAS 0/96、ERBB2 0/96；EGFR 高倍扩增 {eg['n_high_amp']}/{eg['n_cna_profiled']}（{eg['pct_high_amp']}%），增益或扩增 {eg['n_gain_or_amp']}（{eg['pct_gain']}%）；未检测/未知单列 | Data Records + S4/S5 |
| A3 | Zenodo DOI 缺失 | 仍待你上传（本版 ZIP = `★Zenodo上传-就选这个_v13.zip`）；正文与 README 占位符保留，可一键回填 | `03_Zenodo上传指南.md` |
| A5 | 仓库名与内容不符 | 正文已按实际内容改写；**建议把仓库重命名为 cross-disease-transcriptomic-resource**（改名会保留旧链接跳转，需你确认后我执行） | Data Availability |
| B1 | "复现成功"表述过强；精确 vs 有序混用 | 已全面区分：**精确**（bulk 分数/效应 49 项差 0；Cox 68 项 HR 差 0）vs **秩一致**（TCGA 分数重建 Spearman 0.95–0.98，并说明差异源于聚合顺序）；新增 S7 验证证据表 | S7 + Methods |
| B2 | 442 vs 434 行缺口 | 已补全：**442 行 = 434 估计 + 8 不可估计**，逐行给出原因（4 对仅 2/3 成员、4 对仅 2/6 成员） | `07_estimates/not_estimable_pairs.csv` |
| B3 | 跨队列可比是断言而非验证 | 新增：**方向一致性 112/165（68%）**；**覆盖阈值敏感性** BH 显著数 13→13→12→6（覆盖 0.60/0.80/0.90）；Fig3 面板 A/B | `qc_cross_cohort_consistency.csv`、`qc_coverage_threshold_sensitivity.csv` |
| B4 | 模块分数与 xCell 同源导致数学耦合 | 新增**签名重叠审计**：17/17 模块 >20% 成员落在 xCell 面板内（最高 100%）→ 调整定位为**敏感性分析**并写入 Methods | `qc_module_vs_xcell_signature_overlap.csv` |
| B5 | 高 R² 与低 VIF 看似矛盾 | 已分别定义并解释：**整体模型 R²**（疾病~四成分，中位 0.33、最高 0.89）vs **逐预测变量 VIF**（中位 2.09、最高 4.53）；Fig3 面板 D | `qc_vif_by_predictor.csv` |
| B6 | 配对阈值无依据；无患者 ID 不能证明独立 | 阈值写明（≥4 例双组织）并保留敏感性；无 ID 队列标注"按必需非配对、独立性不可推断" | S5 + 正文 |
| B7 | 单细胞 FDR family 未定义、供者汇总未说明 | 写明：细胞→供者均值、**每臂 ≥3 供者**、**≥5 完整配对**用配对检验、互斥才用非配对、否则不可检验；**BH 家族 = 情境 × 模块 × 比较类型**；240 比较构成（168/40/32） | Methods + S5 |
| B8 | 缺少筛选分母/流程图 | 新增 `curation_flow.csv`：27 序列→26 病例-对照→1 应答队列排除；单细胞 5 数据集（4 用）；6 癌种 | S9 + 08_qc |
| C1 | 三种分数未给选用指引 | 新增 S8 层级选用表（写进 README 与正文 Usage Notes） | S8 |
| C2 | 更新治理缺失 | 新增 `00_VERSION.txt` + `00_CHANGELOG.md` + 正文维护段（新版本发新 Zenodo version，旧 DOI 可引用） | 包根目录 |
| C3 | 再分发许可 | 新增 `source_versions.csv` 与许可合规段（派生数据 CC-BY-4.0；上游 GEO/TCGA/CELLxGENE 各自条款） | S1 + README |

## 图件与表格（按你的格式要求）
- 三张图**图内无图例、无总标题**，均为 17.0 cm、300 dpi；OCR 版面检查**三张全部 0 裁切**（Fig3 为新增：可比性与耦合验证）
- 表格全部**三线表**：`Tables_v13.docx`（Table 1 + S1–S9，含 S6 不可估计对、S7 验证证据、S8 层级选用、S9 可比性/耦合）；图例单独 `Figure_legends_v13.docx`

## 仍需你操作（唯一阻塞项）
上传桌面 `★Zenodo上传-就选这个_v13.zip` → 把 DOI 发我 → 我回填正文/README 的 `[DOI to be inserted after Zenodo deposit]` 并出终版。

## 可选后续（不需要你阻塞）
1. 仓库重命名（建议 `cross-disease-transcriptomic-resource`）并同步正文链接
2. CELLxGENE 数据集的完整 collection 标识核对
3. 共同作者与 CRediT
4. 再送一轮第三方审（本轮两审共 23 条意见，v13 已逐条闭环）
"""
open(os.path.join(V13,"00_状态与可继续事项_v13.md"),"w",encoding="utf-8").write(state)

resp=f"""# 对 GPT6 与 Claude 意见的逐条回应（v13）

## 一、最严重项

**1. "食管鳞癌 TP53 = 0/96"（两位均判必改）→ 已定位并修复，且两位的推测与真相不同。**
- 真相：**数据层没有错**。ESCC 分析层本就是纯鳞癌（94 例可生存分析、96 例有突变分母），TP53 = **{tp53['n_mutated_samples']}/{tp53['denominator_n']} = {tp53['pct']}%**。
- 错在**我的手稿模板**：用 `esc_mut[0]`（表首行，恰为 KRAS 0/96）却写成 "TP53"。已在生成器中改为**按基因名显式查找 + 断言**（找不到/多于一行即报错），并全项目清查其它"首行取值"模式（除本例外未发现）。
- 同时按你们的建议补强突变层表述：仅突变谱内样本纳入分母；"no mutation reported in the selected mutation data" 与 "not assayed/unknown" 严格分开。

**2. DOI 未插入 → 仍为阻塞项。**
本版 ZIP 已备好（`★Zenodo上传-就选这个_v13.zip`）；上传后我 1 分钟内回填 Data Records、Data Availability 与 README。

**3. 仓库名与内容不符 → 已在正文澄清。**
仓库 `egfr-pathway-context-atlas` 现托管跨疾病资源；建议重命名（GitHub 会保留旧链接跳转），需你确认后我执行。

## 二、方法学与验证

**4. "复现成功"表述过强（GPT6/Claude 一致）→ 已按证据分级重写。**
- 精确复现：bulk 模块分数（Spearman 1.00）与 49 个效应量/标准误（**最大绝对差 0**）；Cox 68 个比较（**HR 最大绝对差 0**）。
- 秩一致：TCGA 患者级分数重建 Spearman 0.95–0.98，差异来源=聚合顺序（已在 Methods 写出每层构造规则）。
- 新增 S7「验证证据表」明确标注每项属于哪一级，凡秩一致处绝不写"exact"。

**5. 442 vs 434 行缺口 → 已补全并逐行给因。**
26×17=442；434 估计 + 8 不可估计（4 对仅 2/3 成员、4 对仅 2/6 成员）。

**6. 跨队列可比是断言 → 已量化。**
方向一致性 112/165（68%）；覆盖阈值敏感性 BH 显著数 13/13/12/6；共同基因集敏感性（中位 Spearman 0.89，3 模块方向不一致、2 模块不可重算）；Fig3-A/B 呈现。

**7. 数学耦合（模块分数与 xCell 同源）→ 已量化并降级定位。**
17/17 模块 >20% 成员落在 xCell 489 基因面板内（最高 100%）；据此把"基础 vs 调整"明确定位为**敏感性分析**，并说明调整在高共线队列会按构造削弱疾病对比。

**8. R² 与 VIF 看似矛盾 → 已分别定义。**
整体模型 R²（疾病~四成分）中位 0.33/最高 0.89；逐预测变量 VIF 中位 2.09/最高 4.53；Fig3-D 展示两者关系。

**9. 配对阈值与无 ID 队列 → 已给依据。**
阈值 ≥4 例双组织患者（保留 0.5/0.7 固定相关敏感性）；9 个无 ID 队列标注"配对不可建立、独立性不可推断、按非配对分析"。

**10. 单细胞细节（供者汇总/最小细胞数/FDR family/身份对比）→ 已写明。**
细胞→供者均值后检验；每臂 ≥3 供者；≥5 完整配对才配对检验；互斥才非配对；否则不可检验（80 项）；BH 家族 = 情境×模块×比较类型；240 比较 = 168 肿瘤-癌旁 + 40 病例-健康 + 32 细胞身份。

**11. 筛选分母/流程图缺失 → 已补。**
`curation_flow.csv`：27 序列（本工作区已有处理矩阵）→ 26 病例-对照 + 1 应答队列排除；单细胞 5 数据集（4 用、LUAD 因无对照排除）；6 癌种。

## 三、呈现与治理

**12. 三种分数无选用指引 → 已加 S8（并写入 README）。**
**13. 更新治理缺失 → 已加 `00_VERSION.txt` + `00_CHANGELOG.md` + 维护段（新版本发新 DOI，旧 DOI 继续可引）。**
**14. 再分发许可 → 已加 `source_versions.csv` 与许可合规段。**
**15. 独立抽检 → 已执行三轮独立复算**（组成分数、模块分数/效应、TCGA 生存与分数重建），结果与偏差全部随包发布。

## 四、保留的亮点（两位均认可，本版未动）
非显著/不可估计/不可检验三态透明；三种评分层与组成分数性质严格区分；"未测/未知"与"无突变"分开；高共线性队列主动披露；图注把"不可检验"单列。
"""
open(os.path.join(V13,"04_对两审意见的逐条回应_v13.md"),"w",encoding="utf-8").write(resp)

# Zenodo guide refresh
g=os.path.join(V13,"03_Zenodo上传指南.md"); t=open(g,encoding="utf-8").read()
t=t.replace("★Zenodo上传-就选这个_v12","★Zenodo上传-就选这个_v13").replace("EGFR的v12","EGFR的v13").replace("DataDescriptor_v12","DataDescriptor_v13")
t=t.replace("# Zenodo 上传指南（v12 数据资源包）","# Zenodo 上传指南（v13 数据资源包）")
open(g,"w",encoding="utf-8").write(t)
# rebuild ZIPs including the new docs
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v13")
shutil.make_archive(z,"zip",PK)
stage=os.path.join(V13,"_stage2"); shutil.rmtree(stage,ignore_errors=True); os.makedirs(stage)
pairs=[("01_manuscript/DataDescriptor_v13.docx","01_Manuscript/DataDescriptor_v13.docx"),
       ("01_manuscript/DataDescriptor_v13.pdf","01_Manuscript/DataDescriptor_v13.pdf"),
       ("03_tables/Tables_v13.docx","02_Tables/Tables_v13.docx"),
       ("03_tables/Figure_legends_v13.docx","02_Tables/Figure_legends_v13.docx"),
       ("02_figures/Fig1_resource_overview.png","03_Figures/Fig1_resource_overview.png"),
       ("02_figures/Fig2_technical_validation.png","03_Figures/Fig2_technical_validation.png"),
       ("02_figures/Fig3_comparability_checks.png","03_Figures/Fig3_comparability_checks.png"),
       ("02_figures/Fig1_resource_overview.pdf","03_Figures/Fig1_resource_overview.pdf"),
       ("02_figures/Fig2_technical_validation.pdf","03_Figures/Fig2_technical_validation.pdf"),
       ("02_figures/Fig3_comparability_checks.pdf","03_Figures/Fig3_comparability_checks.pdf"),
       ("00_状态与可继续事项_v13.md","00_先看这个_状态与可继续事项.md"),
       ("04_对两审意见的逐条回应_v13.md","00_先看这个_对两审意见的逐条回应.md"),
       ("03_Zenodo上传指南.md","00_先看这个_Zenodo上传指南.md")]
for s,d in pairs:
    sp=os.path.join(V13,s)
    if os.path.exists(sp):
        os.makedirs(os.path.dirname(os.path.join(stage,d)),exist_ok=True); shutil.copy(sp,os.path.join(stage,d))
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v13.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zenodo zip MB:",round(os.path.getsize(z+".zip")/1e6,2),"| submission zip MB:",round(os.path.getsize(out)/1e6,2))
# push
repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
for f,rel in [("01_manuscript/DataDescriptor_v13.md","manuscript/DataDescriptor_v13.md"),
              ("04_对两审意见的逐条回应_v13.md","reports/v22_v13_response_to_reviewers.md"),
              ("00_状态与可继续事项_v13.md","reports/v23_v13_status.md")]:
    sp=os.path.join(V13,f)
    if os.path.exists(sp):
        dp=os.path.join(repo,rel); os.makedirs(os.path.dirname(dp),exist_ok=True); shutil.copy(sp,dp)
for f in os.listdir(os.path.join(V13,"scripts")):
    shutil.copy(os.path.join(V13,"scripts",f), os.path.join(repo,"scripts","v12_data_resource",f))
for f in ["Fig1_resource_overview.png","Fig2_technical_validation.png","Fig3_comparability_checks.png"]:
    shutil.copy(os.path.join(V13,"02_figures",f), os.path.join(repo,"figures",f))
for f in os.listdir(R):
    if f.startswith(("v13_","v12_qc_")): shutil.copy(os.path.join(R,f), os.path.join(repo,"results",f))
for s in [["git","add","-A"],["git","-c","user.name=sushuqiong","-c","user.email=fengqi9666@qq.com","commit","-q","-m",
           "v13: TP53 gene-label bug fixed (explicit lookup + assertion), complete 442-row estimates matrix, cross-cohort consistency, coverage-threshold sensitivity, signature-overlap audit, per-predictor VIF, curation flow, versioning and layer guidance"],
          ["git","push","-q","origin","main"]]:
    r=subprocess.run(s,cwd=repo,capture_output=True,text=True)
    print(s[1], "->", r.returncode, (r.stderr or r.stdout).strip().splitlines()[-1][:110] if (r.stderr or r.stdout).strip() else "")
print(subprocess.run(["git","log","--oneline","-1"],cwd=repo,capture_output=True,text=True).stdout.strip())
