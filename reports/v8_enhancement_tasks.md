# v8 增强任务汇总（1→7→2→5 + 4/3/6 尝试）

> 新工作区：`Desktop\EGFR\EGFR_external_validation\`

## ✅ Task 1 外部 OS 验证（完成，重要）
- GSE39582（n=573/190 事件）**CRC ERBB_LIGANDS 未复现（HR 1.01, p=0.88）** → TCGA 0.79 保护性降级为"内部一致、外部未复现"，从核心 claim 移除。
- **CRC VEGF/PDGF 外部显著复现不良（HR 1.21, p=0.0069；+age 1.20, p=0.0087）** → 升级为 CRC 最受外部支持的 OS 信号（bulk↑ + 组成稳健 + OS 双源复现）。
- 文档：`EGFR_pathway_context_atlas/reports/v7_external_validation.md`；CSV：results/external_crc_gse39582_module_os.csv。

## ✅ Task 7 参考文献（完成第一版）
- 27 个队列真实出处 PMID 直接从各自 GEO series 文件提取（0 猜测；GSE47460 待补）。
- 43 条 Vancouver 原始题录（8 临床锚点 + 4 方法学(GSVA/limma/xCell/DL) + 4 竞品(Sanchez-Vega/CMS/Thorsson/Bailey) + AREG/EREG×2 + 27 队列出处）→ `EGFR_pathway_atlas_submission/tables/references_raw.txt`。
- 存疑 esearch 命中（xCell/DLmeta/Thorsson/JAK 临床）已剔除或标记待核，防误引。

## ⚠️ Task 2 肿瘤纯度校正（部分受限，如实）
- 环境内 TCGA 缺 ABSOLUTE 纯度文件、且本地仅存 100 基因子集不足以跑 ESTIMATE/EPIC-on-TCGA；
- 已完成的替代：age+stage 多变量 Cox（13/17 保持，v0.4 已写入）；**剩余（纯度/ABSOLUTE）需在能下载 TCGA 全表达的环境执行**——脚本结构已就绪（10_multivariable_subtype.R 可扩展）。

## ✅ Task 5 DepMap 药敏层（完成）
- 24Q4 CRISPR 依赖 × 6 谱系：EGFR 依赖率 Gastric 39%、PAAD 34%、Lung 11%（mean 效应 -0.42/-0.39/-0.28）；KRAS 必需性 PAAD -1.79 最重；ERBB2/PIK3CA 中等泛系。
- 解读：PAAD/Gastric 中 EGFR 遗传依赖在罕见扩增背景下仍较高 → 支持配体/自分泌轴与间质相互作用的可靶性假说（DepMap 基线效应需相对解读）。
- CSV：results/depmap_lineage_dependency.csv（Esophagus 无系，已注明）。

## ✅ Task 6 CPTAC 蛋白交叉验证（完成，PAAD）
- paad_cptac_2021（n=140）：RNA-蛋白 Spearman **MET 0.845、VEGFA 0.668、SRC 0.607、ERBB2 0.583、EGFR/STAT3/SMAD3 ~0.48**；CTNNB1 0.29/KRAS 0.23/PIK3CA 0.15 低（翻译后调控为主）。
- 结论：MET/EGFR/ERBB2/STAT3/VEGFA 的 mRNA 主张在 PAAD 蛋白层一致（转录→蛋白可推断性最高的模块中枢）；WNT/KRAS/PI3K 蛋白层需谨慎。
- CSV：results/cptac_paad_rna_protein.csv。

## ✅ Task 3 第二反卷积（EPIC 已装并抽查）
- EPIC vs xCell 组分一致性（3 队列）：GSE44076 CRC（cancer/epi 0.80、immune 0.78）、GSE27342 STAD（0.38/0.66）、GSE15471 PAAD（cancer 0.50、CAF 0.70、**immune 0.88**）。
- 结论：中等-强一致性支持 xCell 主结果；EPIC 全面重跑（27 队列）作为最终敏感性层，脚本模板 06 已备。

## ❌/⏳ Task 4 PAAD basal/classical 亚型（受限未完成）
- TCGA 临床无 PAAD SUBTYPE 属性；Moffitt/Puleo 分类器基因表需从外部文献资源获取（本地无，未下载）；PAAD 表达子集仅 100 基因不足以自建可靠分类器。
- 建议在可联网下载完整表达矩阵的环境完成（预计半天工作量），或退而用"模块驱动的 unsupervised k=2"作探索（证据等级低）。

## 下一步（v0.5 整合）
把 v7/v8 并入正文：CRC ERBB_LIGANDS claim 降级 + CRC VEGF/PDGF 升格（外部复现）；DepMap/CPTAC 药物-蛋白双锚点新段；EPIC 敏感性注明；参考文献替换为 43 条全题录；重新生成 docx/PDF。
