# v12 状态与待决问题（2026-09-13）

## 背景
GPT6 对 v11 的意见 = **战略转向**：放弃 Research Article，改投 **Scientific Data 的 Data Descriptor（数据资源论文）**。
参考文件已解析：`_refs/`（GPT6_v11、编辑政策、NCI_TCGA_ESCA、SciData指南、数据政策、数据仓库指南）。

## Scientific Data 硬性要求（已确认）
- 结构：Title / Abstract（**≤170 词**）/ Background & Summary / Methods / Data Records / Technical Validation / Usage Notes / Data Availability / Code Availability / Author Contributions / Competing Interests / Ethics
- 标题 **≤110 字符**，少用缩写
- **Data Descriptor 不呈现研究结论**；Technical Validation 只允许 **1–2 图表 + 一段文字**（编辑会要求删减多余分析）
- 必须存入公共仓库并给 **DOI**（首轮可用匿名下载链接，**第二轮起强制 depository**；要求 CC0/CC-BY，不接受 -NC/-SA）
- 数据引用用 DOI URL 形式；CELLxGENE 需补完整 collection/dataset ID 与版本

## GPT6 指出的 3 处稿内矛盾——已用冻结表复核，全部成立
1. §3.4：把 joint-only 写成 "CRC VEGF/PDGF" → 实为 **ESCC VEGF/PDGF**（joint-only 三项 = ESCC VEGF/PDGF、STAD VEGF/PDGF、IBD JAK-STAT；残差法独有 = ESCC SRC/FAK）
2. §3.5：写 "STAD 支持 EPH 和 JAK-STAT" → 实为 STAD = **EPH、HGF/MET、VEGF/PDGF**；IBD = HGF/MET、JAK-STAT(上皮)、JAK-STAT(髓系)
3. Fig4：17 行含 **2 个单基因 EGFR** → 应写"15 个模块特征 + 2 个 EGFR 单基因"

## 新查出的两个实质问题（GPT6 怀疑成立）
### A. ESCC 组织学范围错误（严重）
- cBioPortal `esca_tcga_gdc`：样本级 CANCER_TYPE_DETAILED 全部为 "Esophageal Adenocarcinoma"（该字段不可靠），ONCOTREE=ESCA
- **患者级 DISEASE_TYPE 可靠**：腺癌 89 例、**鳞癌 96 例**（共 185）
- 我们的 ESCC 层用了 185 例表达样本 → **混入约 89 例腺癌**；突变分母 185 同样混用
- 影响：ESCC 的 EGFR 高倍扩增 14.6%、EGFR HR 0.56、ESCC 1 个 joint-robust（VEGF/PDGF）等全部需在纯鳞癌子集重算

### B. CRC 单细胞标签与独立性（严重）
- 47,107 个 CRC 细胞中，**"对照"组也含 malignant cell（358 个，20 位患者）**，其中 **19 位患者同时出现在两组** → 现"19 pairs"来自跨组织同患者
- 多类细胞型（colonocyte、crypt stem、secretory、goblet、BEST4+、tuft）同样存在患者跨组重叠 → **不足 5 对时改用非配对检验的做法不成立**（违反独立性），GPT6 第 5 点（对抗性表格）命中
- 需回查 cellxgene 原始 obs（sample_type/tissue/donor）确认组织来源标签，重建分组与配对规则后重算 Fig6/§3.5

## 待用户确认（5 项决策）
1. 确认转向 Scientific Data Data Descriptor？
2. 数据仓库选哪个（Zenodo / figshare / Dryad / OSF）？
3. ESCC：只保留 96 例鳞癌并重算（推荐）/ 保留 ESCA 全部但改名为"oesophageal carcinoma (mixed histology)"？
4. 可选层（TCGA 生存、突变、CPTAC、DepMap、药物映射）：核验后保留 / 移除（推荐移除 CPTAC·DepMap·药物映射，生存降为 Usage Notes 示例）？
5. 授权重建 CRC 单细胞分组/配对并重算（会改 Fig6 与 §3.5 结论）？

## 与答案无关、可立即推进的工作
- 3 处矛盾修复（v12 稿）
- 基因覆盖报告（逐平台 × 模块 实际纳入/缺失基因）+ 共同基因集敏感性
- 样本登记表（患者/组织样本/检测记录/细胞数分别计数；GEO GSM 级去重核查）
- 数据包目录结构（按 GPT6 第 4 节八类）+ 至少 2 个可运行复用示例
- 措辞修正：'explicit wild type' → '未在所选突变数据中报告突变'；区分 未检测/未知/未检出
