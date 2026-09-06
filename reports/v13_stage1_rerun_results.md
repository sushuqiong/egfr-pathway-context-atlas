# v9 阶段一：三大 rerun 结果（对照 v8）

> 运行记录：reruns/results/run1_log.txt、context_meta_v9_unified.csv、v9_percohort_joint_unified.csv、v9_composition_joint_summary.csv、external_crc_gse39582_refined.csv
> 核心结论：**GPT6 的担忧成立——统一效应量与联合模型显著改变核心数字。**

## 1) 统一效应量 meta（配对 g_equiv 与未配对 Hedges' g 同尺度；配对相关实证估计，r 兜底 0.5）
| 指标 | v8（旧尺度） | v9（统一 g 尺度） |
|---|---|---|
| DL pooled-sig (k≥2) | 73 | **31** |
| REML/HK pooled-sig (k≥2) | 4 | **11** |

REML/HK 显著 11：CRC WNT/β-cat +2.58、CRC EPH +1.87、CRC ERBB-lig −0.37、CRC PDGFR-KIT −1.07；IBD ERBB-R −1.28、HGF/MET +1.52、JAK-STAT +1.78、SRC/FAK +0.45、TIE +1.14、VEGF/PDGF +1.30；COPD SRC/FAK −0.28。
**PAAD 从两组显著集全部消失**；IBD 与 CRC 主导。注意：部分配对队列实证 r 极高 → CI 极窄，需按 r 敏感性复核（下一步做 r=0.5/0.7 固定比较与 CI 报告）。

## 2) 联合模型组成校正（module ~ group + epi/fib/end/imm [+ patient]，不再残差化）
- 逐队列显著 p<0.05：151（未 FDR 时）
- **联合稳健状态仅 6**（CRC 5、IBD 1）——对比 xCell 残差法 "19"（重叠仅 5；xCell-only 14；joint-only 1）
- 含义：**残差法确实高估了"校正后仍稳健"**；联合模型更保守；IBD JAK-STAT 在联合模型中保留（缓解与 sc 的旧矛盾）；PAAD 依旧全部衰减。

## 3) 外部队列身份/样本数审计
- **GSE39582**：GEO 585 阵列（元数据解析 0 癌旁纳入；原论文"566 原发+19 癌旁"的差异源于 GEO 收录 585 个 array 与我们仅用带 OS 注释的样本）；**可分析 573 / 190 事件**（12 条缺 OS 时间排除）；VEGF/PDGF uni HR 1.21 (95%CI 1.05–1.40, p=0.0069)，age 1.20 (1.05–1.38)；stage 因 tnm.stage 解析缺失未校正（注明局限）；ERBB-lig HR 1.01 (0.88–1.16)。
- **GSE21501**：132 阵列 → 102 可分析 / 66 事件（30 无 OS）。
- **ACRG/GSE62254**：300 肿瘤、300 唯一患者、152 OS 事件（论文补充表）；0 重复。

## 下一步（v9 阶段二）
1. 配对相关敏感性（r 固定 0.5/0.7 vs 实证）复核 meta CI
2. 逐状态证据矩阵（原始/逐队列/统一meta/联合模型/sc/外部预后分格）→ 决定正文新数字
3. 按新数字改 v9 正文（标题 composition-aware、删除 19/73 等旧数、内部矛盾清单修复）→ 图/表/docx
