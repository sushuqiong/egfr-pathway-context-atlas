# v10 STAD 外部验证 + CPTAC LUAD/CRC 蛋白锚点

## A. STAD 外部 OS（ACRG, GSE62254; n=300, 152 OS 事件）
- 生存数据来源：论文附件 MOESM34（Cristescu et al, Nat Med 2015）临床总表 FINAL sheet；Tumor ID 与 GEO patient 编号 300/300 完全匹配（授权抓取，非猜测）。
- 模块-OS（同一 17 模块 GSVA-z 管线，GPL570；BH 每队列）：
  - **TCGA 五项不良模块中三项显著外部复现**：TIE/Ang HR 1.36 (FDR 4e-4; TCGA 1.34)、PDGFR-KIT HR 1.26 (FDR 9e-3; TCGA 1.27)、VEGF/PDGF HR 1.26 (FDR 6e-3; TCGA 1.26)；TAM/AXL 方向一致 (HR 1.18, p=0.044, FDR 0.068)；RET/ALK/NTRK 未复现 (HR 1.09, ns)。
  - 新增外部显著：FGFR HR 1.53 (FDR <1e-7)、IGF/INSR 1.35、TGFβ 1.28（TCGA 多变量层新晋的 STAD FGFR 得到外部强支持）。
  - 保护性（外部）：EPH HR 0.78 (FDR 8e-3)、SRC/FAK 0.79、HGF/MET 0.81、ERBB-LIG 0.83（EPH 与 bulk 上调/组成稳健形成"高表达预后好"的上下文信号，须在正文注明）。
- 文件：`results/external_stad_acrg_module_os.csv`、`external_stad_acrg_os.csv`。
- **科学意义**：STAD 与 CRC/PAAD 形成对照——TCGA OS 信号并非一律假阳性；STAD 血管/基质轴（TIE/VEGF/PDGFR）双源稳定，RET 单源，FGFR 外部新强信号。这正是"外部验证区分真信号与背景"方法学的正例。

## B. CPTAC 蛋白层扩展（LUAD n=110, CRC n=96）
- LUAD：RNA-蛋白 Spearman MET 0.885、EGFR 0.859、STAT3 0.810、ERBB2 0.740、ERBB3 0.687、SRC 0.583、VEGFA 0.55 —— 受体丢失型癌的转录-蛋白高度一致。
- CRC：MET 0.696、SRC 0.49、ERBB2 0.434、STAT3 0.37；**EGFR ≈0（-0.02）、KRAS 0.08** —— CRC EGFR 转录与蛋白解耦（转录下调故事不适用于蛋白推断；也提示配体/蛋白层面的检查必要性）。
- PAAD（此前）：MET 0.845、VEGFA 0.67、ERBB2 0.58、EGFR 0.48。
- 文件：`results/cptac_luad_rna_protein.csv`、`cptac_crc_rna_protein.csv`、`cptac_paad_rna_protein.csv`。

## C. 稿件改动（v0.6 md 已同步）
- §3.5 外部段补 STAD 复现/未复现数字；§3.9 补 LUAD/CRC ρ 与 CRC EGFR 解耦警示；Limitations 更新"三癌外部验证：CRC/PAAD 未复现、STAD 血管轴复现"。
