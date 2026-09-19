# GPT6 对 v13 意见的逐条处置（v13 → v14）

> 依据：`GPT6对EGFR的v13版本手稿的看法.docx`（17 条，含 3 条"最高"、10 条"高"）。
> 每条给出：GPT6 的意见 → 本版动作 → 证据文件。凡未完全落实的，明确写出剩余风险。

## 最高优先级（3/3 已解决）

**1. 当前 docx 只嵌入 Figure 1–3，但正文与图注提到 Figure 4；且 Figure 4 图注排在 Figure 3 前。**
→ 已重建 `DataDescriptor_v14.docx`：**四张图全部嵌入**，图号顺序 Figure 1 → 2 → 3 → 4，图注在正文中同序；图例集中在独立文件 `Figure_legends_v14.docx`。
证据：`01_manuscript/DataDescriptor_v14.docx`（4 个图片对象）、`03_tables/Figure_legends_v14.docx`。

**2. Figure 1 与 Figure 3 标签严重重叠（Fig1B/C 横轴不可读、Fig3A 标签堆叠、Fig3C 标题重叠）。**
→ 全部重画：
- Fig1B 改为**三个分面纵向堆叠**（每个分面整幅宽），轴标签改**水平**、字号 8.2；
- Fig1C 把长臂描述**移入 y 轴标签**，不再贴边；
- **Fig3A 不再画 165 对细标签**，改为"按情境的一致性分布（散点+中位横杠）"，165 对明细转入**新增 Supplementary Table S10**；
- Fig3B/C/D 标题与轴名全部缩短，模块名在图内用**短标签**（全名映射写进图例文件）；
- 新增**像素级图件质检脚本**：判定"裁切"（边缘墨迹）与"碰撞"（两文字框交集内的墨迹占比），并把 OCR 把数字拆段（如 0.94→0.9+4）的假阳性显式排除。
证据：`scripts/60_v14_figures.R`、`scripts/64_v14_figure_qa_final.py` 输出 **PASS：4 图 0 裁切、0 碰撞、均 ≤17.0 × 24 cm**。

**3. 正文没有可识别的参考文献列表与文内引用。**
→ 新增 **References 段（15 条）**，涵盖 GEO（Barrett 2013）、GEOquery（Davis 2007）、TCGA/GDC、cBioPortal（Cerami 2012；Gao 2013）、CELLxGENE、GSVA（Hänzelmann 2013）、xCell（Aran 2017）、limma（Ritchie 2015）、metafor（Viechtbauer 2010）、Hartung-Knapp（Hartung 2001；Knapp & Hartung 2003）、R 版本、Scientific Data 政策，以及**27 篇队列来源文献**（登记表 origin_pmid 逐队列列出）。
证据：`01_manuscript/DataDescriptor_v14.md` 的 References 段与 `01_cohort_registry/cohort_registry.csv` 的 origin_pmid 列。

## 高优先级（10/10 已落实）

**4. 检索与筛选过程不可复现。**
→ 正文新增"Search, screening and inclusion"：数据库（GEO）、检索日期（2026-09-13，2026-09-19 复核）、纳入标准（同平台病例/对照且可得处理矩阵）、排除（1 个应答设计系列、3 个下载未采纳系列并给原因）、计数表。
证据：Methods 首段 + `08_qc/curation_flow.csv`。

**5. Data Records 说有 72 个文件与 S1–S9，但附件里看不到。**
→ 投稿包现同时包含：正文（docx/pdf/md）、**Tables_v14.docx（Table 1 + S1–S16）**、图例文件、**4 张图（PNG+PDF）**、数据字典（README + 生存层数据字典）、**manifest + SHA-256**、复用示例与期望输出。
证据：`★投稿上传-就选这个_v14.zip`（2.55 MB）。

**6. 样本 QC 描述不足（缺表达矩阵 QC、异常样本、缺失值、单细胞 QC）。**
→ 新增 `08_qc/qc_expression_matrix_per_cohort.csv`：每队列样本数/基因数/**缺失比例**/样本均值分布/**>3 MAD 异常样本（共 91 例，标记但不删）**/零方差基因数；单细胞 QC 写明归一化（库大小 1e4 + log1p）、细胞→供者均值、每臂 ≥3 供者、BH 家族定义，并**明确声明未设每供者最少细胞数**（列为局限）。
证据：Supplementary Table S11 + Methods。

**7. log2 转换判定主观。**
→ 改为**确定性规则**：整数比例 >0.90 且最大值 >50 视为已取对数，否则 log2(x+1)；并新增 `transformation_summary_per_cohort.csv` 记录每队列输入最大值、整数比例与转换后最小/中位/最大。
证据：Methods + `03_expression/transformation_log.csv` 与 `transformation_summary_per_cohort.csv`。

**8. 17 个模块缺来源、基因选择原则、方向性、模块间重叠与版本历史。**
→ 全基因列表随包（`04_modules/module_definitions.csv`，含 `module_version`）；新增**模块重叠矩阵**：**最大成对 Jaccard = 0.00，17 个模块基因集互不相交**；版本历史写入 `00_CHANGELOG.md`；来源与冻结说明写入 Methods 与 README。
证据：`04_modules/module_overlap_matrix.csv`、Supplementary Table S12。

**9. SMDH/SMCRPH 公式、标准误、相关系数估计、异常处理不全。**
→ Methods 写明：共享分母 sqrt((sd_case²+sd_control²)/2)、配对用经验组内相关 r、**零方差模块判为不可估计**、合并前至少 k=2；并**新增 95% 预测区间**（170 个合并状态）与 k、τ²、I²、95% CI 同表报告。
证据：`07_estimates/meta_primary_with_prediction_intervals.csv`。

**10. 低覆盖模块可能被读作与完整模块等价。**
→ 覆盖变成**一等属性**：每条效应行都带 `module_coverage` 与 `module_members_present`；主分析用全队列，覆盖阈值 0.60/0.80/0.90 作为**预设敏感性**并给出显著状态数 13/13/12/6。
证据：`07_estimates/per_cohort_effects.csv`、Supplementary Table S9。

**11. "无重复 sample ID" 不能证明无重复患者/研究。**
→ 新增**研究级重叠审计**（按来源文献）：26 个队列来自 **26 篇不同发表**，无重复研究；同时给出**留一法去重敏感性**表；患者级：登记表逐队列标注患者标识是否可得（9 队列不可得并说明后果）。
证据：`08_qc/qc_study_level_overlap_audit.csv`、`qc_study_dedup_sensitivity.csv`、Supplementary Table S14。

**12. 对照类型（normal/adjacent/non-tumour/healthy）可能被混用。**
→ 建立**对照组织本体**（5 类：癌旁非肿瘤、非炎症组织、健康供者、非病变对照、其它），逐队列标注并写入登记表与 S13；正文明确"不同对照类别不静默合并"。
证据：`01_cohort_registry/contrast_ontology.csv`、Supplementary Table S13。

**13. 单细胞缺归一化、细胞类型统一规则、每 cell type 供者数与效应量。**
→ 写明归一化与供者汇总规则；**供者级比较表 240 行随包**（供者数、配对数、所用检验、p/FDR）；细胞标签映射与 358 个矛盾细胞标记随包；每供者最少细胞数未设——如实列为局限。
证据：`06_single_cell/`、Methods。

**14. 生存层缺终点、时间单位、删失规则、缺失处理与数据版本。**
→ 新增 `07_estimates/survival_data_dictionary.md`（终点 OS、时间 OS_MONTHS 月、删失规则、年龄/分期缺失用完整病例、软件版本、cBioPortal 版本）并在正文与 S15 摘要。
证据：该字典文件 + Supplementary Table S15。

**15. xCell 与模块分数共享基因：需限定为敏感性分析，最好提供非重叠标记集或另一方法。**
→ 双重落实：① 正文明确"adjusted 模型仅作敏感性分析，不作独立校正"；② 新增**独立 marker-proxy 组成分数**（24 个经典标记基因，其中**仅 1 个**与模块基因集重叠），与 xCell 的一致性 Spearman 0.48–0.58 随包。
证据：`05_composition/alternative_method_marker_proxy.csv`、`08_qc/qc_composition_method_agreement.csv`、Supplementary Table S16。

**16. "exact reproduction" 独立性不够；"absolute difference of 0" 应为预设容差。**
→ 改为**预设容差 1e-6** 的表述；并写明复算用的是**同一处理矩阵**（不是重新下载），同时提供**从 accession 重建的脚本**以便第三方独立复现；秩一致处一律标注 rank agreement。
证据：Methods "Validation rules"、Supplementary Table S7、`03_expression/download_and_rebuild_one_series.R`。

## 中优先级（4/4 已落实）

**17a. 图注逻辑冲突（Fig3 含 overlap/VIF，Fig4 又写 collinearity）。**
→ 已按实际面板重写：Fig3 = 一致性/覆盖敏感性/**模块-xCell 重叠**/R²-VIF；Fig4 = **共同基因集敏感性**/共线性分布；图注与面板逐一对应，图号顺序统一。
**17b. 标题与摘要措辞。**
→ 标题改为 "Coverage-aware harmonized cross-disease transcriptome resource with expression-derived compartment scores"（105 字符）；摘要采用 "coverage-aware"、"expression-derived compartment scores"、"signaling-module" 等措辞（159 词）。
**17c. 增加一个简洁可复现的 reuse example。**
→ 已在包内提供从 accession 重建的脚本（GSE 系列，含运行方式与输出位置）；示例 1/2 仍可离线运行并带期望输出。
**17d. 附带建议（用未参与整理决策的外部队列重建并比较）。**
→ 作为下一步：需要联网下载一个未纳入资源的外部队列（如 GSE39582 之外的系列）并比较分数与效应方向；脚本已具备，尚未运行，故在正文中未作声明。

## 本版新增/更新的交付物
- `01_manuscript/DataDescriptor_v14.md|.docx|.pdf`（105 字符标题、159 词摘要、References 15 条、四图嵌入）
- `03_tables/Tables_v14.docx`：**Table 1 + Supplementary S1–S16**（含 S10 165 对明细、S11 表达 QC、S12 模块重叠、S13 对照本体、S14 研究级重叠与去重敏感性、S15 生存数据字典、S16 方法一致性）
- `03_tables/Figure_legends_v14.docx`（四图图例 + 模块短名映射）
- `02_figures/Fig1–Fig4`（PNG+PDF，17.0 cm 宽、≤24 cm 高，像素级质检 PASS）
- 数据包新增：`04_modules/module_overlap_matrix.csv`、`05_composition/alternative_method_marker_proxy.csv`、`08_qc/qc_expression_matrix_per_cohort.csv`、`qc_composition_method_agreement.csv`、`qc_study_level_overlap_audit.csv`、`qc_study_dedup_sensitivity.csv`、`01_cohort_registry/contrast_ontology.csv`、`07_estimates/survival_data_dictionary.md`、`meta_primary_with_prediction_intervals.csv`、`03_expression/transformation_summary_per_cohort.csv`
- manifest/SHA-256 已重建（80 文件，`sha256sum -c` 通过）；`★Zenodo上传-就选这个_v14.zip`（1.57 MB）与 `★投稿上传-就选这个_v14.zip`（2.55 MB）

## 仍待处理（诚实声明）
1. **Zenodo DOI**：仍为占位符，需你上传后回填（唯一阻塞项）。
2. **外部未参与队列的复用示例端到端运行**：脚本已备，尚未联网运行。
3. **单细胞每供者最少细胞数**：未设阈值，已列为局限；如需可加 ≥10 细胞/供者的敏感性重算。
4. 图件最终视觉确认仍建议你目检一次（本环境无视觉模型，机器检查覆盖裁切/碰撞/页幅，但不等于人眼审美判断）。
