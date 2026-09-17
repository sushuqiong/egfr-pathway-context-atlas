#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: assemble the reusable data resource package (eight file classes) into EGFR的v12/01_数据包/."""
import csv, os, shutil, json, datetime
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"
R=os.path.join(V12,"results")
PK=os.path.join(V12,"01_数据包"); os.makedirs(PK, exist_ok=True)
dirs={"01_source_registry":"队列来源登记（accession、原论文、下载日期、纳排）",
      "02_sample_annotation":"样本与配对注释（患者/样本/检测记录、疾病、组织学、对照类型、配对、排除原因）",
      "03_expression_layer":"表达数据层（按队列组织的处理后矩阵、基因映射与转换记录）",
      "04_module_definition_and_scores":"模块定义与评分层（成员、逐平台覆盖、逐样本分数）",
      "05_composition_annotation":"细胞组成注释层（xCell 原始输出、四类 compartment 构造）",
      "06_single_cell_derived":"单细胞派生层（原始/整理标签、供者-样本-细胞类型、患者级汇总）",
      "07_estimates_and_qc":"完整估计与质控层（效应量、标准误、样本量、模型、校正范围、失败原因）",
      "08_reproduction":"复现材料（脚本、环境、运行顺序、示例、预期输出）"}
for d,desc in dirs.items(): os.makedirs(os.path.join(PK,d), exist_ok=True)
copies=[("v12_resource_inventory.csv","01_source_registry",None),
        ("v12_cohort_registry.csv","01_source_registry",None),
        ("v12_cohort_summary.csv","01_source_registry",None),
        ("v12_sample_level_registry.csv","02_sample_annotation",None),
        ("v12_escc_squamous_samples.csv","02_sample_annotation",None),
        ("v12_duplicate_sample_ids.csv","02_sample_annotation",None),
        ("v12_duplicate_patient_ids.csv","02_sample_annotation",None),
        ("v12_gene_coverage.csv","04_module_definition_and_scores",None),
        ("v12_common_gene_sensitivity_summary.csv","04_module_definition_and_scores",None),
        ("v12_common_gene_sensitivity_per_cohort.csv","04_module_definition_and_scores",None),
        ("v12_mutation_status_by_sample.csv","07_estimates_and_qc",None),
        ("v12_escc_mutation_denominators.csv","07_estimates_and_qc",None),
        ("v12_escc_cna_summary.csv","07_estimates_and_qc",None),
        ("v12_escc_squamous_survival_cox.csv","07_estimates_and_qc",None),
        ("v12_sc_comparisons.csv","06_single_cell_derived",None),
        ("v12_sc_dataset_audit.csv","06_single_cell_derived",None),
        ("v12_sc_localization.csv","06_single_cell_derived",None)]
for f,d,_ in copies:
    src=os.path.join(R,f)
    if os.path.exists(src): shutil.copy(src, os.path.join(PK,d,f))
    else: print("  (pending)", f)
# xCell raw layer + module definitions + per-sample scores from the atlas
for src,dst in [(r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results\xcell\xcell_composition_scores.csv","05_composition_annotation"),
                (r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\config\gene_sets_extended.csv","04_module_definition_and_scores")]:
    if os.path.exists(src): shutil.copy(src, os.path.join(PK,dst,os.path.basename(src)))
# module scores per patient (TCGA layers)
sc_path=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results\cbio_v3_patient_module_scores.csv"
if os.path.exists(sc_path): shutil.copy(sc_path, os.path.join(PK,"04_module_definition_and_scores","tcga_patient_module_scores.csv"))
# field dictionary
fields = """# 字段字典 (field dictionary) — v12 数据资源

## 02_sample_annotation/v12_sample_level_registry.csv
| 字段 | 含义 | 备注 |
|---|---|---|
| accession | GEO 系列号 | 唯一队列标识 |
| sample_id | 样本标识（GSM） | 27 队列间 0 重复 |
| patient_id | 患者标识 | 18/27 队列提供；其余队列以样本标识代替（patient_id_available=0） |
| patient_id_available | 患者标识是否可得 | 1=系列提供；0=未提供，样本按独立供者处理 |
| group | 病例/对照标签 | 由各队列原始注释映射，映射规则见 Methods |
| tissue_or_sample_type | 组织或样本类型 | 如 tumor / adjacent normal / healthy mucosa |
| platform | 检测平台 | 如 GPL570 |
| n_genes | 该样本可用基因数 | 用于覆盖度质控 |

## 01_source_registry/v12_cohort_summary.csv
n_assays / n_samples / n_patients / n_case / n_control / n_paired_patients / platform

## 04_module_definition_and_scores/v12_gene_coverage.csv
| accession, module, n_members, n_present, coverage, missing | 每队列每模块的成员基因覆盖情况 |

## 04_module_definition_and_scores/v12_common_gene_sensitivity_summary.csv
spearman / sign_agreement / flag：全成员 vs 跨队列共同基因子集的一致性与方向一致性

## 07_estimates_and_qc/v12_mutation_status_by_sample.csv
| assay_status | 含义 |
|---|---|
| mutation_assayed_no_variant_reported | 该样本在所选突变数据中已被检测，但未报告该基因突变（**不等于证明野生型**） |
| variant_reported | 报告了该基因突变 |
（未进入突变检测名单的样本不出现在本表中 —— 即"未检测/未知"，不得当作野生型）

## 06_single_cell_derived/v12_sc_comparisons.csv
context, module, cell_type, comparison_type（tumour-vs-adjacent / case-vs-healthy / tumour-vs-healthy / cell-identity）,
n_donors_a, n_donors_b, n_overlap_donors, n_pairs, test_used, p_paired, p_unpaired, p_used, fdr
"""
open(os.path.join(PK,"字段字典_field_dictionary.md"),"w",encoding="utf-8").write(fields)
# package README
readme = """# v12 数据资源包（Data Descriptor 配套）

本目录按可复用性组织为 8 类文件（对应手稿 Data Records 一节）。

1. **01_source_registry** 队列来源登记：accession、原论文、下载日期、纳排、检测平台、样本/患者计数
2. **02_sample_annotation** 样本与配对注释：患者/样本/检测记录编号、疾病、组织学、对照类型、配对关系、排除原因
3. **03_expression_layer** 表达数据层：按队列组织的处理后矩阵与基因映射/转换记录（体积大，随仓库/仓库附件提供）
4. **04_module_definition_and_scores** 模块定义与评分层：17 模块成员、逐平台覆盖、逐样本分数、共同基因集敏感性
5. **05_composition_annotation** 细胞组成注释层：xCell 原始输出 + 四类 compartment 构造说明
6. **06_single_cell_derived** 单细胞派生层：数据集审计、比较结果、细胞类型定位
7. **07_estimates_and_qc** 完整估计与质控层：效应量、样本量、模型、校正范围、突变检测状态、ESCC 鳞癌子集
8. **08_reproduction** 复现材料：脚本、环境、运行顺序、示例与预期输出

## 关键计数（自动生成）
见 `01_source_registry/v12_resource_inventory.csv` 与 `MAIN_COUNTS.md`。

## 复用示例
见 `08_reproduction/`：① 替换模块基因集重算评分；② 更换组成校正方案重算效应。
"""
open(os.path.join(PK,"README_数据包.md"),"w",encoding="utf-8").write(readme)
print("package skeleton:", PK)
for d in sorted(dirs): print(f"  {d}: {len(os.listdir(os.path.join(PK,d)))} files")
