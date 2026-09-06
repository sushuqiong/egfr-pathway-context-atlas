# v7 外部验证结果（Task 1）

> 脚本：`EGFR_external_validation/03_analyze_external_crc.R`
> 数据：GSE39582（GPL570，573 CRC，190 OS 事件；os.delay months/os.event）——独立于 TCGA 的公共 CRC 生存队列。
> GSE14333 在 GEO 无生存字段，跳过（如实在报告注明）。

## 结果
| 模块 | TCGA (COADREAD) | 外部 GSE39582 单变量 | 外部 +age 校正 |
|---|---|---|---|
| ERBB_LIGANDS | HR 0.79（FDR 0.050，保护） | HR 1.01，p=0.88 | HR 1.03，p=0.72 |
| WNT/CTNNB1 | （无 OS 显著） | HR 0.96，p=0.55 | HR 0.98 |
| EPH 受体 | （无 OS 显著） | HR 0.93，p=0.31 | HR 0.93 |
| **VEGF/PDGF** | HR 1.30（FDR 0.038，不良） | **HR 1.21，p=0.0069** | **HR 1.20，p=0.0087** |

## 意义（必须写进论文，影响显著）
1. **CRC ERBB_LIGANDS"保护性 HR 0.79"未通过独立外部验证（外部 HR≈1.0）** → 降级处理：
   - 摘要/结论删除"保护性"作为核心 claim；改为"TCGA 内部两流水线一致（0.75/0.79）但在独立队列 GSE39582 未复现（HR 1.01）——提示该信号与 TCGA 队列构成（早期/术后、平台）或校正差异相关，需进一步确认"。
   - Discussion 4.5 的 (a/b/c) 假说保留但前缀改为"内部一致但外部未复现"。
   - 这也验证了审稿人"同队列两流水线=伪复现"的担忧——真实的外部复现才是标准。
2. **CRC VEGF/PDGF 模块：TCGA 不良（1.30）在外部独立队列显著复现（1.21, p=0.007，age 校正后仍在）** → 升级为 CRC 方向最有外部支撑的 OS 信号，与"受体丢失 + 血管生成/基质轴"画像一致（跨层证据：bulk 上调 + 组成稳健 + OS 外部复现）。
3. WNT/EPH 的"无 OS 显著"在外部同样为 null（方向虽偏保护但与 TCGA 一样不显著）→ 不强claim OS，保留为组成稳健的细胞内在信号。

## 文件
- `EGFR_external_validation/results/external_crc_gse39582_module_os.csv`
- 脚本 03；GSE14333 因无生存字段未纳入。
