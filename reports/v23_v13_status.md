# v13 状态与可继续事项

## 本版做了什么（相对 v12）
| 编号 | 两份 AI 意见 | 处置 | 证据 |
|---|---|---|---|
| A1 | **"TP53 在食管鳞癌 0/96 是数据警报"（GPT6 与 Claude 均判为必改）** | **真因不是数据而是我的手稿模板**：模板取突变表首行（KRAS 0/96）却标注为 TP53。数据本身 TP53 = **86/96（89.58%）**，符合食管鳞癌预期。已改为**按基因显式取值 + 断言**（找不到即报错），全项目清查无其它"首行取值" | `00_manuscript/DataDescriptor_v13.md`；审计项"TP53 reported as 86/96 with an explicit gene lookup" |
| A2 | 突变层 join/标签是否错位 | 已复核：突变分母=**仅突变谱内样本**（96 例鳞癌）；EGFR 突变 2/96、KRAS 0/96、ERBB2 0/96；EGFR 高倍扩增 14/96（14.58%），增益或扩增 64（66.67%）；未检测/未知单列 | Data Records + S4/S5 |
| A3 | Zenodo DOI 缺失 | 仍待你上传（本版 ZIP = `★Zenodo上传-就选这个_v13.zip`）；正文与 README 占位符保留，可一键回填 | `03_Zenodo上传指南.md` |
| A5 | 仓库名与内容不符 | 正文已按实际内容改写；**建议把仓库重命名为 cross-disease-transcriptomic-resource**（改名会保留旧链接跳转，需你确认后我执行） | Data Availability |
| B1 | "复现成功"表述过强；精确 vs 有序混用 | 已全面区分：**精确**（bulk 分数/效应 49 项差 0；Cox 68 项 HR 差 0）vs **秩一致**（TCGA 分数重建 Spearman 0.95–0.98，并说明差异源于聚合顺序）；新增 S7 验证证据表 | S7 + Methods |
| B2 | 442 vs 434 行缺口 | 已补全：**442 行 = 434 估计 + 8 不可估计**，逐行给出原因（4 对仅 2/3 成员、4 对仅 2/6 成员） | `07_estimates/not_estimable_pairs.csv` |
| B3 | 跨队列可比是断言而非验证 | 新增：**方向一致性 112/165（68%）**；**覆盖阈值敏感性** BH 显著数 13→13→12→6（覆盖 0.60/0.80/0.90）；Fig3 面板 A/B | `qc_cross_cohort_consistency.csv`、`qc_coverage_threshold_sensitivity.csv` |
| B4 | 模块分数与 xCell 同源导致数学耦合 | 新增**签名重叠审计**：17/17 模块 >20% 成员落在 xCell 面板内（最高 100%）→ 调整定位为**敏感性分析**并写入 Methods | `qc_module_vs_xcell_signature_overlap.csv` |
| B5 | 高 R² 与低 VIF 看似矛盾 | 已分别定义并解释：**整体模型 R²**（疾病~四成分，中位 0.33、最高 0.89）vs **逐预测变量 VIF**（中位 2.09、最高 4.53）；Fig3 面板 D | `qc_vif_by_predictor.csv` |
| B6 | 配对阈值无依据；无患者 ID 不能证明独立 | 阈值写明（≥4 例双组织）并保留敏感性；无 ID 队列标注"按必需非配对、独立性不可推断" | S5 + 正文 |
| B7 | 单细胞 FDR family 未定义、供者汇总未说明 | 写明：细胞→供者均值、**每臂 ≥3 供者**、**≥5 完整配对**用配对检验、互斥才用非配对、否则不可检验；**BH 家族 = 情境 × 模块 × 比较类型**；240 比较构成（168/40/32） | Methods + S5 |
| B8 | 缺少筛选分母/流程图 | 新增 `curation_flow.csv`：27 序列→26 病例-对照→1 应答队列排除；单细胞 5 数据集（4 用）；6 癌种 | S9 + 08_qc |
| C1 | 三种分数未给选用指引 | 新增 S8 层级选用表（写进 README 与正文 Usage Notes） | S8 |
| C2 | 更新治理缺失 | 新增 `00_VERSION.txt` + `00_CHANGELOG.md` + 正文维护段（新版本发新 Zenodo version，旧 DOI 可引用） | 包根目录 |
| C3 | 再分发许可 | 新增 `source_versions.csv` 与许可合规段（派生数据 CC-BY-4.0；上游 GEO/TCGA/CELLxGENE 各自条款） | S1 + README |

## 图件与表格（按你的格式要求）
- 三张图**图内无图例、无总标题**，均为 17.0 cm、300 dpi；OCR 版面检查**三张全部 0 裁切**（Fig3 为新增：可比性与耦合验证）
- 表格全部**三线表**：`Tables_v13.docx`（Table 1 + S1–S9，含 S6 不可估计对、S7 验证证据、S8 层级选用、S9 可比性/耦合）；图例单独 `Figure_legends_v13.docx`

## 仍需你操作（唯一阻塞项）
上传桌面 `★Zenodo上传-就选这个_v13.zip` → 把 DOI 发我 → 我回填正文/README 的 `[DOI to be inserted after Zenodo deposit]` 并出终版。

## 可选后续（不需要你阻塞）
1. 仓库重命名（建议 `cross-disease-transcriptomic-resource`）并同步正文链接
2. CELLxGENE 数据集的完整 collection 标识核对
3. 共同作者与 CRediT
4. 再送一轮第三方审（本轮两审共 23 条意见，v13 已逐条闭环）
