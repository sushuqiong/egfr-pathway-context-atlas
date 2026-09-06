# v9 外部验证扩至 PAAD（+STAD 尝试状态）

> 脚本：`EGFR_external_validation/02_external_paad.R`；结果：`results/external_paad_gse21501_module_os.csv`
> 队列：GSE21501（PDAC 术后队列，GPL4133 Agilent 4x44K，n=102，66 OS 事件；os time/os event）。

## 结果
TCGA 中 PAAD 七个不良模块（HGF/MET 1.64、ERBB-R 1.56、ERBB-L 1.54、EPH 1.50、EGFR 1.38、TGFβ 1.39、WNT 1.36）**在 GSE21501 中全部未复现**：
HGF/MET HR 1.03 (p=0.82)；EPH 1.15 (p=0.27)；TGFβ 1.10；ERBB-R 0.92；ERBB-L 1.07；WNT 0.88；PI3K 1.01。
仅 JAK-STAT (HR 1.32, p=0.032) 与 SRC/FAK (HR 1.29, p=0.034) 达名义显著，二者 FDR 均>0.05（0.29）。

## 解读（必须写进论文）
1. **PAAD"模块表达 OS 不良"目前为 TCGA 单源信号，未获独立外部队列支持** → 与 CRC ERBB-ligand 命运一致。
   可能解释：TCGA-PAAD 的预后信号部分由分期/治疗史/分子亚型（basal/classical）混杂；不同平台与队列构成的模块代理噪声；亚组（KRAS-wt、classical）内才存在的真实信号被稀释。
2. 这**反过来支持"bulk 通路激活多为组成/临床背景信号"的论文核心论点**：细胞组成与临床背景驱动了大部分 bulk 关联，肿瘤内在信号只在少数亚组或少数模块成立。
3. 明确下一步：PAAD basal/classical 分层后重测（待做）；改用带治疗注释的 ICGC-PACA-CA 做二次外部。

## STAD 外部状态（如实）
GSE62254（ACRG，300 例）与 GSE15459（200 例）在 GEO 内**无 OS 字段**（ACRG 生存须合并论文补充临床表）；已下载表达供后续合并使用。STAD 外部 OS 验证推迟到获取补充生存表后。

## 对稿件 v0.6 的修改
- §3.5 外部验证段加入 PAAD 未复现句；§3.8(i)/§4.4 PAAD"跨层收敛"叙述改为"TCGA 单源、待外部验证"，并把 JAK-STAT/SRC 的名义提示如实呈现。
- 摘要/结论中 PAAD 表述从"seven adverse associations"降为中性（结果不变、解释收敛）。
- Limitations 更新："PAAD 与 CRC ERBB-ligand 的 OS 信号在各自独立外部队列均未复现，提示 TCGA 单源预后信号需队列级验证"。
