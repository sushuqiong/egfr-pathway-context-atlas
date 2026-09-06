# v11 PAAD 分子亚型（basal/classical）分层重测 + 状态

## 方法（无需全转录组/无新环境）
- **分类器基因表**：Moffitt 2015 (Nat Genet, ng.3398) 附件 MOESM62 TableS2 Gene Factorization——19,750 基因 × F6_BasalLike/F8_Classical 载荷；取各自 **top150 正载荷基因**（重叠 54，两臂基因现 132/131）。
- **表达**：cBioPortal paad_tcga_gdc（RNA-seq mrna profile，179 例）API 抓分类器+17 模块+TP53 ≈344 基因子集 → 样本内 z → 每样本 basal/classical 均分 → argmax 分型。
- 数据枢纽 S3 tar 与 GEO 均受阻 → 子集 API 方案规避，无需 conda/Docker。

## 结果（n=178，93 OS 事件）
- **分型**：Basal 81 (45%) / Classical 98；Basal vs Classical OS HR 0.81 (p=0.30，本队列无生存差异)。
- **关键模块 OS 按亚型**：无模块×亚型交互显著（HGF/MET、ERBB-R、EPH、WNT 因臂内事件/基因可用性未产出或未显著）；TGFβ 在 Classical 臂 HR 1.26 (p=0.042, 名义)；ERBB-LIGANDS 双臂方向 1.18-1.22 (未显著)。
- 解读：TCGA-PAAD 的"7 模块 OS 不良"在 basal/classical 分层内**未显示亚型特异性驱动**（也无整体交互），叠加 GSE21501 外部未复现 → 更支持"该信号以临床/队列背景为主、亚型为辅"的收敛解释；探索性提示 TGFβ/ERBB-LIGANDS 在特定亚型方向值得后续大样本验证。
- 局限：分型为载荷 top150 的变体（basal 比例偏高 45%），非官方 Moffitt 质控流程；事件数中等。

## 文件
- `EGFR_external_validation/results/paad_subtype_labels.csv`、`paad_subtype_module_os.csv`、`paad_subtype_expression.tsv`（344 基因×179 样本）
- 附件原件：`data_raw/41588_2015_BFng3398_MOESM6{0..3}`、`41591_2015_BFnm3850_MOESM34_ESM.*`

## 剩余队列（如实）
1. **纯度/ABSOLUTE 校正**：可基于新抓的 TCGA-PAAD 全表达（改为全基因抓取即可，API 已通）跑 ESTIMATE/EPIC 纯度代理；未在本轮执行（需~1-2h 全基因抓取+运行）。
2. **IBD 第二单细胞集**：需大体积下载（CELLxGENE/GEO，数百 MB），建议后台任务。
3. 如继续：可将本分型并入 v0.7 方法/结果 + DepMap/PRISM 分子亚型药敏注释。
