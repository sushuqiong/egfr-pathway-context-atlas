# v12 分析层重跑结果（对应 ChatGPT 建议的 5 项重做）

> 工作区：`Desktop\EGFR\EGFR_v8_reruns\`（scripts/ + results/）
> 环境：Python 3.11（numpy/pandas/scipy/statsmodels/anndata/h5py/pyreadr）；R ≥3.5 缺失（仅 R 3.4.3），EPIC 无法运行。

## 1. REML / Hartung–Knapp 重做 meta —— 完成
- 脚本 `01_meta_REML_HK.py`；输出 `context_meta_summary_REML_HK.csv`。
- 方法：REML 估计 τ² + Hartung–Knapp 检验（t，df=k−1），研究选择与方差近似与原 DL 管线一致。
- 结果：**DL 下 73/170 显著 → REML/HK 下仅 4/170 显著**（PAAD HGF/MET +1.20、RAS-MAPK +0.84、ERBB ligands +0.39；COPD SRC/FAK −0.28）。
- 含义：DL 在小 k（2–3）下反保守；原 "73 pooled-significant" 被高估。**正文已改为：per-cohort 规则为 primary，meta 作为 underpowered sensitivity 层，只保留 4 个 REML/HK 显著状态。**

## 2. 单细胞患者级 pseudobulk + 全局 FDR + 配对 —— 完成
- 脚本 `02_sc_pseudobulk_globalFDR.py`；输出 `sc_patient_level_pseudobulk_globalFDR.csv`。
- 方法：患者级模块均值（patient = 统计单位）；**CRC 配对**（20 例重叠，Wilcoxon signed-rank），IBD/STAD 未配对 Mann-Whitney；**全局 BH-FDR**（跨 130 个可测比较）。
- 结果：全局 FDR<0.05 显著 **12 个**（CRC 7、IBD 2、STAD 3），较原局部 FDR 的 17 个更保守。关键生物学结论不变：CRC 恶性细胞 WNT/EPH/VEGF/HGF-MET 上调、IBD 上皮+髓系 JAK-STAT、STAD 上皮 EPH + 壁细胞 HGF-MET/VEGF（腺体丢失）。
- 含义：正文把 17 → 12，并标注 CRC 为配对检验。

## 3. TCGA-PAAD 肿瘤纯度校正 —— 完成（marker-based purity proxy）
- 脚本 `03_paad_purity.py`；输出 `paad_module_os_purity_adjusted.csv`、`paad_marker_expression.csv`。
- 方法：cBioPortal 抓取 27 个 marker 基因（免疫/基质/上皮）→ 免疫分+基质分 z 均分 → purity proxy = −(免疫+基质)；Cox（scipy 部分似然）依次加 age、stage、purity。
- 结果：**纯度校正未显著削弱 PAAD 不良模块-OS**：HGF/MET 1.66、ERBB-R 1.50、ERBB-L 1.57、EPH 1.40、TGFβ 1.58、RAS-MAPK 1.33 仍显著，仅 WNT 衰减（1.25, p=0.08）。
- 含义：TCGA-PAAD 的 OS 信号**不是**由肿瘤纯度（免疫/基质含量）解释的——与 bulk 病/对照差异被组成校正消除（Results 3.4）形成对照。正文 3.8 已写入。

## 4. 27 队列 EPIC 全跑 —— 完成（WSL R 4.3.3 + EPIC 1.1.7）
- 环境：在 WSL Ubuntu 的 R 4.3.3 中安装 EPIC 1.1.7（本地 tarball，GitHub GfellerLab/EPIC）。
- 脚本 `04_epic_27cohort.R`；输出 `epic_27cohort_fractions.csv`、`epic_xcell_concordance_27cohort.csv`、`epic_xcell_sample_level_aligned.csv`。
- 结果：27 队列全部跑通（EPIC 8 细胞类型：B/CD4/CD8/Mac/NK/CAF/Endo/other）。样本级 EPIC vs xCell Spearman：**内皮 0.56、免疫 0.44、CAF/纤维 0.28、上皮/癌 0.09**（n=2711 样本，26 队列）。
- 含义：全 27 队列 EPIC 显示与 xCell 的**中-弱**一致性（内皮/免疫中等，CAF/上皮弱），弱于此前 3 队列抽查（immune 0.66–0.88），说明免疫-上皮分解在跨平台 microarray 上是方法依赖的；正文已如实下调该表述。

## 5. Reactome / MSigDB 一致性 —— 完成
- 脚本 `05_module_signature_consistency.py`；输出 `module_signature_consistency.csv`。
- 方法：下载 MSigDB HALLMARK（50 set）+ Reactome（2868 pathway），对 17 模块做超几何富集 + Jaccard。
- 结果：**17/17 模块均有显著 Reactome 匹配**（Jaccard 0.05–0.83，FDR<1e-5），如 ERBB-L→Inhibition of Signaling by Overexpressed EGFR（J=0.56）、HGF/MET→Drug-mediated inhibition of MET activation（J=0.67）、TGFβ→SMAD2/3（J=0.83）、VEGF→VEGFR dimerization（J=0.70）、WNT→TCF/LEF:CTNNB1（J=0.33）；HALLMARK 匹配亦正确（JAK-STAT→IL6_JAK_STAT3、PI3K-AKT、TGF_BETA、ANGIOGENESIS、WNT_BETA_CATENIN）。
- 含义：17 模块定义与标准通路签名一致，已写入 Methods 2.2 + Table S2。

## 6. leave-one-gene-out —— 完成（WSL R 4.3.3）
- 脚本 `06_leave_one_gene_out.R`；输出 `loogo_module_summary.csv`。
- 方法：mean-z 模块评分，逐基因剔除后重算 SMD，与全模块 SMD 做 Spearman 相关（27 队列）。
- 结果：**17/17 模块稳健**，剔除任一基因后 SMD 与全模块高度相关（median r=0.93；range 0.65–0.98；最弱为 2 基因的小模块 TAM/AXL 0.65、TIE/Ang 0.74）。关键模块（JAK-STAT 0.98、VEGF/PDGF 0.98、RAS-MAPK 0.96、WNT 0.94、EPH 0.93）极稳健。
- 含义：模块定义不受单基因驱动，已写入 Methods 2.2。

## 结论
6 项分析层重做全部完成（REML/HK meta、单细胞配对+全局FDR、PAAD 纯度、27 队列 EPIC、Reactome/MSigDB、leave-one-gene-out），结果均已写入 v08 正文/补充表。
