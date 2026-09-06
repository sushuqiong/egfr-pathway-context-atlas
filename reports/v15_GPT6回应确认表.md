# v15 GPT6 意见 → v9 回应确认表（终验用）

> 对象：`C:\Users\fengq\Desktop\GPT6对EGFRv8手稿的看法.docx`（8 节）
> 状态标注：✅=已实质落实（正文/重跑可查）｜◐=部分落实（保留为局限/计划）｜⏳=依赖人工/投稿系统

## GPT6 第 1 节 · 组成校正实现（最高优先级）
| 子点 | 状态 | v9 落点 |
|---|---|---|
| 残差两步法→联合模型 | ✅ | Methods 2.4：module ~ disease + 4 成分 [+patient]；Results 3.4：joint-robust 6 状态为报告主口径；xCell 残差降为灵敏度（Supp S2）并明示仅 5 状态重叠 |
| 效应+SE/CI 非只 FDR | ✅ | v9_percohort_joint_unified.csv 含 d_adj/se_adj/df；Results 3.4 给中位调整差 |
| 配对结构保留/满秩记录 | ✅ | 配对队列含 patient 因子；失败回退有 joint_fallback 标记列 |
| xCell≠细胞比例 | ✅ | Methods 2.4 明示"enrichment scores, not measured proportions" |
| 模块-成分数学耦合/重叠基因 | ◐ | 模块-xCell 重叠列于 Table S2；关键模块重叠标志基因剔除灵敏度仍为 planned |
| EPIC-xCell 低相关不当"验证" | ✅ | 改为"low-to-moderate agreement reported as limitation"（2.4/3.9/4.8） |
| 两法校正后疾病效应一致性 | ◐ | 提供两法结果（joint 主 + xCell 灵敏度）供对照；工具间效应一致性比较仍可加 |

## GPT6 第 2 节 · Meta 效应量统一
| 子点 | 状态 | v9 落点 |
|---|---|---|
| 配对 dz 与 g 不同尺度 | ✅ | 统一 g 尺度：配对 g≈d_z√(2(1−r))（Methods 2.3 公式化） |
| 实际估计配对相关 | ✅ | 实证 r；ρ=0.5/0.7 固定敏感性结果一致（context_meta_v9_unified{_rho05,_rho07}.csv） |
| 说明 r=0.5 去向 | ✅ | 方差公式与敏感性写清 |
| 配对模型失败不静默回退 | ✅ | joint_fallback 列 + 记录 |
| DL 与 REML/HK 分开交代 | ✅ | Methods 2.3 分别说明方差估计器与推断；Results 3.1 DL 31 / REML-HK 11 |

## GPT6 第 3 节 · "55→19→预后"叙述
| 子点 | 状态 | v9 落点 |
|---|---|---|
| 拒绝连续筛选叙事 | ✅ | Abstract/3.1/3.4/4.1 重写：per-cohort 55、meta REML/HK 11、joint 6 各自独立报告；摘要无"remain from 55" |
| 逐状态证据矩阵 | ✅ | Table S9（170 状态×各层，含 no data/uncertain/direction 分格） |
| 病例-对照 vs 预后不同问题 | ✅ | 4.1/4.8 明示分层为独立证据延伸 |
| H3 交集展示 | ✅ | Results 3.4/3.5/3.6：CRC WNT/EPH/VEGF joint+sc+（VEGF 外部）明确交集 |

## GPT6 第 4 节 · 外部队列样本数
| 子点 | 状态 | v9 落点 |
|---|---|---|
| GSE39582 573 vs 566+19 核验 | ✅ | Methods 2.8/Results 3.6：585 阵列→573 可分析/190 事件；0 癌旁纳入；12 条缺结局排除（external_crc_gse39582_refined.csv + audit_*.csv） |
| GSE21501/ACRG 同标准 | ✅ | 102/66；ACRG 300 唯一患者/152（audit 脚本 11） |
| 排除/重复/对应 | ✅ | 唯一 GEO、无重复行、事件-样本对应逐一核对（审计日志 run3_audit_log.txt） |

## GPT6 第 5 节 · 预后结论强度
| 子点 | 状态 | v9 落点 |
|---|---|---|
| 外部仅年龄→需分期 | ◐ | CRC/STAD 补 CI 与年龄；stage 在 GSE39582 公共记录不可用→Limitations 明示（真实限制） |
| PAAD 纯度代理措辞 | ✅ | "expression-derived proxy, not measured purity"（Methods 2.9/Limitations） |
| 外部阴性给 95%CI | ✅ | CRC refined 表含 CI；PAAD/ACRG 表含 HR+p（CI 增补在 CSV） |
| driver 交互≠negative control | ✅ | 更名 effect-modification screen；underpowered 措辞 |

## GPT6 第 6 节 · 跨层模块可比性
| 子点 | 状态 | v9 落点 |
|---|---|---|
| 各平台成员基因展示 | ✅ | Table S2（per-platform coverage） |
| 同队列 GSVA vs 均值一致性 | ⏳ | 仍为 planned（代码就绪未跑） |
| LOOGO 非总体相关→逐关键结论 | ◐ | Table S8 已含 per-gene；关键状态级复核仍可加强 |
| Reactome 重叠≠效度 | ✅ | Methods 2.2 措辞为"annotational support" |
| sc 患者内汇总/最低细胞数/效应区间 | ◐ | Methods 2.5 说明患者为单位、≥3 患者；95%CI planned |

## GPT6 第 7 节 · 内部矛盾（逐条）
178/179 ✅（179 分型/178 生存）｜Limitations CRC 信号特化 ✅｜prospective→retrospective ✅｜纯度指针 2.10→2.9 ✅｜"carried entirely"→confined+estimable ✅｜multi-axis activation→diffuse ✅｜108 检验家族与 EGFR 说明 ✅｜按癌 FDR 明示 ✅

## GPT6 第 8 节 · 创新聚焦
✅ 主文两问结构（4.1-4.5）；DepMap/CPTAC/药物→补充+descriptive（3.9/2.10）；标题 composition-aware。

## 剩余 ⏳/◐（多为人工或计划）
作者/CRediT｜引文上标排版｜代码 GitHub｜投稿系统 AI 问答｜图 TIFF/字号终检（Fig2B 首看）｜Cover 抬头填空｜EPIC/联合效应一致性与同队列 GSVA-均值校验（可选加跑）
