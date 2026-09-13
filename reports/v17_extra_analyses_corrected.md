# v17 修正索引后的附加分析（v10）

> 背景：GPT6 指出配对索引错误后，v9 的附加分析（LOOGO、评分一致性、ρ 敏感性）同样受同一缺陷影响，须以修正索引重跑。本报告为结果。

## A. 同队列评分方法一致性（GSVA vs 成员均值 z）
- 6 个代表队列（覆盖两代平台）× 17 模块 = **102 个状态-队列对**
- **median Spearman ρ = 0.936**（与 v9 报告的 0.94 一致）
- 结论：TCGA 用均值 z、GEO 用 GSVA 的既有做法不足以驱动模块层结论

## B. 关键状态稳定性（组成标记重叠 + 留一基因）
设计：26 个关键状态（v10 联合稳健 21 个 + PAAD RAS-MAPK/HGF-MET、LUAD FGFR/JAK-STAT、COPD SRC/FAK）× 其所属队列（CRC3/STAD3/IBD3/PAAD3/LUAD3/COPD2），每个状态计算变异版本：**full**、**minus_overlap**（去掉与成分标记面板共享的基因）、**drop_top3**（去掉各队列影响最大的 3 个成员基因）；合并用 REML/Hartung-Knapp。共 **331 个队列级变异效应 / 106 个状态×变异合并估计**。
- **minus_overlap（26/26 状态均有重叠基因被剔除）**：合并方向**无任何改变**；显著数 23 → 23（与 full 完全一致）
- **drop_top3（54 个变异）**：仅 **1 个**合并方向翻转 —— IBD SRC/FAK 去掉 FYN（est −0.096, p=0.104，同时失去显著性）
- 参考：full 版本 26 个状态中 23 个合并 p<0.05

## C. 结论与正文落点
1. 模块层结论对评分方法与组成标记重叠**稳健**；唯一敏感状态 IBD SRC/FAK 已在正文标注
2. 正文 Methods 2.2（LOOGO/稳定性句）与 Table S8 说明已按上述数字更新
3. 输出表：`v10_gsva_vs_meanz.csv`、`v10_keystate_loogo_variants.csv`、`v10_keystate_pooled.csv`
4. 与 v9 的差异：v9 报告的 "median r=0.93、2/112 翻号" 建立在含索引缺陷的效应量上；v10 用正确索引重算，结论方向一致但数字更可靠

## D. v10 最终核心数字（定稿）
- 逐队列稳健 55/170
- 统一尺度 meta：REML/Hartung-Knapp **18**（固定 ρ 下 19）、DerSimonian-Laird **76**
- 联合模型组成稳健 **21**（CRC 10、STAD 9、ESCC 1、IBD 1；PAAD 0）
- TCGA 17/108 FDR<0.05；11/15 过 age+stage
- 外部：CRC 556/187；无一状态通过严格复现（VEGF 方向一致但 stage 校正后 p=0.22）
