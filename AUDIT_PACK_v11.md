# 送审自查包（v11）— 供第三方/审稿人快速核验

> 目的：把"改了哪些地方、每个数字来自哪张表、最可能被质疑什么、已如何应对"一次讲清，便于外部审查直接定位。
> 对应手稿：`EGFR的v11\01_稿件正文\Manuscript_draft_v11.md/.docx/.pdf`；代码：https://github.com/sushuqiong/egfr-pathway-context-atlas

## 1. v11 相对 v10 的四项实质性修正（均为外部评审提出的同向问题）
| # | 问题（v10） | 修正（v11） | 证据表 |
|---|---|---|---|
| 1 | 非配对 SMD（合并SD分母）与配对 SMCRH（sd1 分母）混用，却称"统一尺度" | 非配对 **SMDH** + 配对 **SMCRPH**（分母同为 √[(sd1²+sd2²)/2]）；配对用逐队列实证 r | `v11_percohort_effects.csv`（measure 列明 SMDH/SMCRPH） |
| 2 | 用调整模型的疾病系数当"未调整"；把不显著写成"完全衰减" | **基础模型 vs 调整模型**（同样本）分别报 β/SE/CI；量化中位调整/基础比 **0.87** | `v11_percohort_effects.csv`（beta_base/beta_adj/se/p），`v11_joint_summary.csv` |
| 3 | 单细胞代码为非配对 Mann-Whitney，方法却写配对 Wilcoxon；跨细胞身份比较混入 | ≥5 完整对→**配对 signed-rank** 并报对数；否则非配对并标注；恶性 vs 正常上皮单列**细胞身份对比** | `sc_v11_patient_paired.csv`（test_used / n_pairs / comparison_type / fdr / fdr_unpaired） |
| 4 | 突变率与 driver 用 **CNA 样本数**做分母，未限定野生型假设 | 分母取 cBioPortal **mutation-profiled 样本列表**；仅 profiled 判野生型，非 profiled 排除并计数 | `v11_mutation_audit.csv`、`v11_mutation_denominators.csv`、`v11_mutation_profiled_samples.csv`、`v11_driver_eligibility.csv` |

## 2. 每个核心数字的来源（可直接用脚本复算）
| 手稿数字 | 含义 | 表 | 脚本 |
|---|---|---|---|
| 55/170 | 逐队列稳健 | `context_atlas_summary.csv` | 历史 01；v11 未改判定规则 |
| **17** | meta 主（REML+Knapp-Hartung, BH） | `v11_meta_primary_reml_knha.csv` | `40_v11_meta.R` |
| 74 / 6 / 3 | DL / 非收缩 KH / 仅非配对 敏感性 | `v11_meta_DL.csv`、`v11_meta_adhoc.csv`、`v11_meta_unpaired_only.csv` | 同上 |
| 17（ρ=0.5/0.7） | 固定相关敏感性 | `v11_meta_rho0.5.csv`、`v11_meta_rho0.7.csv` | 同上 |
| **21**（CRC10/STAD9/ESCC1/IBD1） | 组成稳健 | `v11_joint_summary.csv` | `10_v11_effects_two_model.R` + `40_v11_meta.R` |
| **0.87** | 中位调整/基础系数比 | `v11_percohort_effects.csv` | `10_v11_effects_two_model.R` |
| **16（10 配对；中位 15 对）+ 12** | 单细胞同类型 / 身份对比 | `sc_v11_patient_paired.csv` | `20_v11_sc_paired.py` |
| 17/108；11/15 | TCGA 预后 | `cbio_v3_survival_cox.csv` + 多变量历史结果 | 历史 04/10 |
| CRC 556/187；VEGF 1.16→age+stage 1.09 | 外部验证 | `v11_external_crc.csv` | `12_v10_crc_external.R`（v11 沿用，机制未变） |
| PAAD KRAS 61.9%（107/173） | 突变分母 | `v11_mutation_denominators.csv` | `30_v11_mutation_audit.py` |
| 102 / 5 / 0 | driver 检验/名义/FDR | `v11_driver_interactions.csv`、`v11_driver_eligibility.csv` | `50_v11_driver_profiled.R` |

## 3. 最可能被追问的点与现成答案
1. **为什么 17 与 74 差这么多？** 属于推断方法敏感性：Knapp-Hartung 调整与 DL 在小 k 下方差估计差异大；v11 同时报告两者与非收缩 KH、仅非配对三种设置（手稿 Results 3.1 与 Limitations 4.8）。**未隐藏任何一个数字。**
2. **组成校正后不显著 ≠ 组成解释**：手稿 4.2/4.4 明确列出四种可能来源（系数变小、SE 变大、疾病-组成共线、调整掉机制本身），并给出 0.87 的量化衰减。
3. **PAAD 与原文 KRAS 频率不一致**：手稿 2.9/3.8 写明 profiled 分母 173、107 例（61.9%），并注明原文为 150 例中 140 例，差异归因于样本子集与突变调用流程不同；driver 分析仅用 profiled 样本并给出排除数。
4. **单细胞配对是否真的做了？** `tests/check_paired_effect.R` 提供手算 vs metafor、洗牌重排、重复运行三项核验；`sc_v11_patient_paired.csv` 中 `n_pairs` 与 `test_used` 逐行可查（显著配对检验的中位对数为 15）。
5. **手稿数字与图表是否同一来源？** `tests/check_v11_consistency.py` 自动比对文中数字与冻结表，并扫描旧版本残留；当前 **PASS**。
6. **可复现性**：`config/gene_sets_extended.csv` 已随仓库提供；脚本顶部 `ROOTS` 指向本机处理对象（GEO/cBioPortal 处理后 .rds），按 README 的 run order 可重跑；`ERRATA_v11.md` 逐项记录修正。

## 4. 已知限制（手稿已写，供审查者直接引用）
- k 小（多为 2–3），I² 不稳定；结论对估计器敏感
- xCell 是富集分数非比例；EPIC 与 xCell 仅中等一致；疾病与组成共线
- 外部验证无一通过预定义标准；GSE39582 分期字段部分缺失、治疗背景不可得
- 单细胞为转录层面；配对分析会排除单侧缺失该细胞型的患者
- 突变/驱动层限于 profiled 样本，与其他分期/检测范围不同的队列不可直接比较
- PDAC 亚型分类器为派生变体，未与原始分型比对；交互分析功效不足

## 5. 复现命令（本机）
```
# 效应量与双模型
Rscript scripts/v11_reruns/10_v11_effects_two_model.R
# meta 与联合汇总
Rscript scripts/v11_reruns/40_v11_meta.R
# 突变分母与 driver
python scripts/v11_reruns/30_v11_mutation_audit.py
python scripts/v11_reruns/31_v11_fetch_profiled_samples.py
Rscript scripts/v11_reruns/50_v11_driver_profiled.R
# 单细胞（需 h5py/scipy 环境：EGFR_ERBB_context_project_v2/.sc_venv）
python scripts/v11_reruns/20_v11_sc_paired.py
# 图 / 矩阵 / 一致性
Rscript scripts/v11_reruns/80_v11_figures.R
python scripts/v11_reruns/60_v11_matrix.py
python tests/check_v11_consistency.py
```
