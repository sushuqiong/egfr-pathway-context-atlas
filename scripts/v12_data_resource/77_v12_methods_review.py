#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: (a) write the validation thresholds into Methods, (b) add module version / source-version fields,
(c) produce the third-party-style adversarial review report."""
import csv, os, shutil
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# ---------- (a) Methods additions ----------
p=os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"); s=open(p,encoding="utf-8").read()
anchor="*Quality control.* Checks cover sample identity and duplication"
methods_add=("*Validation rules and thresholds.* The checks reported in Figure 2 and Supplementary Table S5 use explicit rules. "
 "*Common-gene sensitivity:* each cohort is re-scored using only the module members present in every cohort, and the Spearman correlation with full-member scoring is reported per module; a module is flagged when the direction of the disease effect disagrees with full-member scoring in at least 20% of cohorts, and is marked not scorable when fewer than three members are shared across all platforms. "
 "*Composition collinearity:* for each cohort we fit a linear model of disease status on the four compartment scores and report its R-squared, because in cohorts where composition predicts case status strongly, covariate adjustment removes part of the disease contrast by construction (median R-squared 0.33, maximum 0.89). "
 "*Composition reproducibility:* the four compartment scores were independently recomputed from the processed matrices for three cohorts with xCell and compared with the shipped values (Pearson 0.71-0.95, Spearman 0.48-0.94 across compartments and cohorts; the lowest rank agreement was for the fibroblast score in one cohort, where the magnitude nevertheless agreed, Pearson 0.91). "
 "*Proportional hazards:* the survival layer is checked with the scaled Schoenfeld residuals test (cox.zph) on the age-adjusted model, and a feature is flagged when the test p-value is below 0.05; none of the 17 features was flagged. "
 "*Pooling paired and unpaired cohorts:* because paired cohorts estimate the effect with a smaller sampling variance, they receive more weight in the meta-analytic summaries; the sensitivity analyses with fixed within-pair correlations (0.5 and 0.7) are therefore shipped alongside the empirical-correlation analysis, and the number of surviving states differs between them, which is reported rather than hidden.\n")
s=s.replace(anchor, methods_add+anchor, 1)
# mention supplementary tables and the separate legend file
s=s.replace("A file inventory with row counts and SHA-256 checksums is included",
            "Tables 1 and Supplementary Tables S1-S5 are provided as separate files, and figure legends are provided in a separate document; a file inventory with row counts and SHA-256 checksums is included",1)
open(p,"w",encoding="utf-8").write(s)
print("methods updated:", "Validation rules and thresholds" in s)
# ---------- (b) registry extras: module version, source versions ----------
ver=os.path.join(PK,"04_modules","module_definitions.csv")
rows=rd(ver)
if "module_version" not in rows[0]:
    for r in rows: r["module_version"]="v12.0-frozen-2026-09"
    wr(rows, ver); print("module definitions versioned")
src=os.path.join(PK,"01_cohort_registry","source_versions.csv")
src_rows=[
 dict(source="GEO (NCBI)", accessions="27 series as listed in the cohort registry", version_or_release="accessed 2026-09; processed matrices prepared locally via GEOquery", licence="per-series terms (public domain / author terms as declared by each submitter)"),
 dict(source="TCGA / GDC via cBioPortal", accessions="luad_tcga_gdc, coadread_tcga_pan_can_atlas_2018, stad_tcga_gdc, paad_tcga_gdc, lihc_tcga_pan_can_atlas_2018, esca_tcga_gdc", version_or_release="cBioPortal data releases as retrieved 2026-09 (mutation-profiled sample lists recorded per context)", licence="TCGA data use terms (open-access tier; no controlled-access data used)"),
 dict(source="CELLxGENE (single-cell)", accessions="CRC cellxgene_829a3cd1; IBD cellxgene_9bfecd44; LUAD cellxgene_01ff5cf0; STAD cellxgene_0d3807bf; asthma GSE193816 (processed)", version_or_release="dataset handles as retrieved 2026-09; per-dataset CELLxGENE identifiers to be completed from the collection pages at submission", licence="CELLxGENE terms of use (CC-BY-4.0 for most datasets; per-dataset as declared)"),
]
wr(src_rows, src); print("source version table written")
# add limitation line about source versions
s=open(p,encoding="utf-8").read()
s=s.replace("*Quality control.*","*Source versions.* Source releases and accessions, together with licence notes, are listed in Supplementary Table S1 and in 01_cohort_registry/source_versions.csv; CELLxGENE dataset handles are given and their full collection identifiers should be confirmed against the collection pages when citing.\n\n*Quality control.*",1)
open(p,"w",encoding="utf-8").write(s)
# ---------- (c) adversarial review report ----------
report = """# 第三方视角对抗性审查（v12）— 意见、核实与处置

> 方法：以敌对审稿人立场逐项攻击数据可信度、可复现性、统计设计与表述；每条给出证据（文件/脚本）与处置状态。

## A. 数据身份与设计
| # | 攻击点 | 核实结果 | 处置 |
|---|---|---|---|
| A1 | 队列数当患者数卖点 | 成立过（v11）；现已拆分为 26 队列 / 2,711 检测记录 / 1,086 例有标识患者 | 已修：Table 1 + registry 分列 |
| A2 | 配对设计靠硬编码 | **成立**：v11 有 3 个队列含 ≥4 例双组织患者却被当非配对 | 已修：改由元数据判定（15 配对）；主结果 17→13 并披露 |
| A3 | 9 个队列无患者标识却未声明 | 成立 | 已修：registry 增列，手稿明写"按必需非配对" |
| A4 | 队列间样本重复 | 未发现：GSM 级跨队列重复 **0** | 已记录：sample_dedup_patient_audit.csv |
| A5 | 治疗应答队列混入病例-对照资源 | **成立**（GSE16879 Responder/NonResponder） | 已修：单列并排除，理由入排除日志 |
| A6 | 组织学混用（食管腺癌当鳞癌） | **成立**：185 例中 89 例腺癌 | 已修：仅保留 96 例鳞癌，突变/CNA/生存全部重算 |
| A7 | 单细胞跨组织同患者当独立样本 | **成立**：19 例跨组，80 个比较实为不可检验 | 已修：供者感知设计（配对/互斥/不可检验三分） |
| A8 | 单细胞"对照"侧出现恶性细胞 | **成立**：358 个细胞标注矛盾 | 已修：标记不改标签，写入排除日志 |
| A9 | 单细胞数据集无对照臂仍用于比较 | **成立**：LUAD 全为肿瘤 | 已修：整层排除（117,266 细胞）并记录理由 |

## B. 数值与可复现
| # | 攻击点 | 核实结果 | 处置 |
|---|---|---|---|
| B1 | 组成分数靠行序对齐、不可连接 | **成立** | 已修：重建带 sample_id 的键值表 + 连接审计（全部通过） |
| B2 | 组成分数是否可复现？ | **已独立复算 3 队列**：Pearson 0.71–0.95、Spearman 0.48–0.94；GSE13911 成纤维细胞秩相关 0.48（量级 Pearson 0.91） | 已披露：QC 文件 + 手稿 Technical Validation |
| B3 | 效应量分母不统一 | v11 已修（SMDH/SMCRPH 同分母），但固定 ρ 与实证 ρ 结论不同（13 vs 17） | 已披露：两套结果同时提供，并解释配对权重更高 |
| B4 | 生存层未检验 PH 假设 | 成立过 | 已修：cox.zph 17 特征 **0 违反**，写入 Methods 与 QC |
| B5 | 组成模型共线性未报 | 成立过 | 已修：逐队列 R²（中位 0.33、最大 0.89、中位 VIF 2.09） |
| B6 | 跨平台基因覆盖不同却直接比较 | 成立 | 已修：覆盖表 + 共同基因集敏感性（中位 Spearman 0.89；3 模块方向不一致、2 模块不可重算） |
| B7 | "无突变记录=野生型" | 成立（措辞过强） | 已修：改为"未在所选突变数据中报告突变"，并区分未检测/未测未知 |
| B8 | 数字与图表不一致（v11 有 3 处） | 成立过 | 已修：单一数据源生成 + 自动审计（31 项）+ 低级错误审计（82 项）均 0 问题 |

## C. 交付与合规（Scientific Data）
| # | 攻击点 | 核实结果 | 处置 |
|---|---|---|---|
| C1 | 未归档派生数据 | 成立（首轮可用匿名链接，第二轮起强制） | 待你操作：Zenodo 上传（指南已给），DOI 回填 |
| C2 | 缺校验值/文件清单 | 成立过 | 已修：51 文件 SHA-256 + 行数 + 字节 |
| C3 | 图内混入图例/总标题 | 成立（旧版图内上下有图例） | 已修：图内无图例、无总标题；图例单独 Word |
| C4 | 表格非三线表 | 成立（早期 Word 表有竖线） | 已修：Table 1 与 S1–S5 全部 booktabs 三线表 |
| C5 | 缺少模块版本与上游版本/许可 | 成立过 | 已修：module_version 字段 + source_versions.csv（含 CELLxGENE/TCGA/GEO 许可说明） |
| C6 | 细胞标签原始与整理未分离 | 已满足 | 记录：raw 标签保留、整理映射单列 |
| C7 | 无复用示例/无法运行 | 成立过 | 已修：2 个示例 + 离线 demo 矩阵，均实跑通过 |

## D. 仍需人工/后续
1. Zenodo 存档与 DOI 回填（你执行上传，我回填）。
2. CELLxGENE collection 完整标识（提交时从数据集页面核对）。
3. 共同作者与 CRediT（如有多作者）。
4. 图件目检（我无法看图；OCR 几何检查已通过，像素级复核无越界）。
"""
open(os.path.join(V12,"04_adversarial_review_v12.md"),"w",encoding="utf-8").write(report)
print("adversarial review written")
