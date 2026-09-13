# v16 GPT6-v9 意见处理：bug 修复与核心数字重算（阶段一）

> 结论：GPT6 的三项核心指控**全部成立**，已按标准实现重算；核心数字发生实质变化，v9 的"11 / 6 / CRC VEGF 复现"三个支点作废。

## A. Bug 确认与修复（均已定位到代码）
| # | GPT6 指控 | 核实 | 修复 |
|---|---|---|---|
| 1 | 配对索引错误（病例/对照索引误用于整条向量） | **成立**：`y[match(cm, pv)]` 用整向量索引子集位置 → 配对相关恒为 1、var 缺失、200 条配对记录全被丢弃 | 重写为显式子集（`yc=y[match(cc,pidv[iscase])]` 等），改用 **metafor::escalc(measure="SMCRH", ri=实证)**；现 **200/200 配对记录全部可估**（median r_emp=0.99），ρ=0.5/0.7 敏感性结果一致 |
| 2 | meta 筛选误伤联合模型汇总（先删 var 缺失再汇总 joint） | **成立** → v9 "6 个稳健" 为程序筛选假象 | 联合汇总独立纳入（仅要求 p_adj 有限，逐队列 BH 后按规则），并输出四类状态：**robust 21 / estimated-ns 95 / estimated 54 / not analysed 0** |
| 3 | GSE39582 混入非肿瘤（17 例/3 事件）+ 分期解析错误 | **成立**：`dataset:ch1`=Non Tumoral 未排除；`tnm.stage` 为数字 0-4 而脚本只认罗马数字 | 肿瘤筛选 → **556/187**（原 573/190）；数字分期修复（1-4 期 552 例；0 期 4 例单独处理）；三位模型 + 95%CI + BH |

## B. 修正后核心数字（v10）
| 指标 | v9（有 bug） | **v10（修正）** |
|---|---|---|
| 逐队列稳健 | 55/170 | 55/170（不变）|
| Meta REML/Hartung–Knapp（BH）| 11 | **7**（IBD 6：ERBB-R↓/HGF-MET/JAK-STAT/SRC-FAK/TIE/VEGF + COPD SRC-FAK↓）|
| Meta DL（BH）| 31 | **20**（IBD 11、COPD 5、Asthma 4）|
| 联合模型组成稳健 | 6（假象）| **21**（CRC 10、STAD 9、ESCC 1、IBD 1；PAAD 0）|
| CRC 外部 VEGF/PDGF | HR 1.21 复现 | **HR 1.16 (p=0.042)；age 校正 1.15 (p=0.049)；age+stage 校正 1.09 (p=0.217) → 不能称"外部复现"** |
| CRC 外部其它 | — | FGFR 1.15 (p=0.048)、IGF/INSR 1.16 (p=0.045) 分期校正后名义；EPH 0.88 (p=0.09)；ERBB-lig/WNT/PDGFR 均 null |

**CRC 联合稳健 10**：EPH、ERBB-lig↓、FGFR↓、HGF-MET、IGF↓、JAK-STAT、RET↓、TAM/AXL、VEGF、WNT｜**STAD 9**：EPH、ERBB-R↓、HGF-MET、JAK-STAT、PI3K-AKT、RAS-MAPK、RET↓、VEGF、WNT｜**ESCC 1**：VEGF｜**IBD 1**：JAK-STAT。

## C. 需改写的论文支点（v10 文本）
1. 摘要/结果：11→7、6→21、"CRC VEGF 外部复现"→"方向一致但分期校正后不显著（未复现）"
2. 叙事重心：由"少数状态存活"改为"逐队列 55 → 严格 meta 7（IBD 主导）→ joint 21（CRC/STAD 主导）"，并显式区分四类状态
3. 局限：配对 r 高（0.99）与 SMCRH 假设；EPIC 输入尺度与细胞类别对应；模块混合含义；亚型/交互措辞降级
4. 图件全部从 v10 冻结结果表重生成（修 Fig1 旧数字、Fig2 重复面板/EPH 名称、Fig5 图注、Fig6 标注）

## D. 已做核验（针对 GPT6 第 8 节）
- 配对效应现可估并有实证 r + 固定 ρ 敏感性（7=7=7）
- meta 用标准 metafor（REML/Knha、DL）而非自写迭代
- 组成数据与表达矩阵按 **sample ID 显式连接**（行数相等等不再作为依据）
- 组别参照水平显式设为 Control（不再事后 ×(−1) 翻转；23_fix_sign 类脚本弃用）

## E. 待办（阶段二/三）
图件重生成 → 正文 v10 重写 → 主包 v10 → GitHub 更新（含 errata 说明与可复现入口、config 文件、相对路径、双跑一致性测试）
