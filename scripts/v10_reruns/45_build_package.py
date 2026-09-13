#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, shutil
V10 = r"C:\Users\fengq\Desktop\EGFR\EGFR的v10"
V9  = r"C:\Users\fengq\Desktop\EGFR\EGFR的v9"
PK8 = r"C:\Users\fengq\Desktop\EGFR\EGFR_Atlas_投稿包_v8"
PK  = r"C:\Users\fengq\Desktop\EGFR\EGFR_Atlas_投稿包"
for d in ["01_稿件正文","02_图片","03_表格与补充数据","04_评审记录与报告","05_代码与复现脚本","06_投稿清单与流程"]:
    os.makedirs(os.path.join(V10,d), exist_ok=True)
# references txt from v10 md
md = open(os.path.join(V10,"01_稿件正文","Manuscript_draft_v10.md"), encoding="utf-8").read()
_,_,ref = md.partition("## References")
lines=[l for l in ref.splitlines() if l.strip()]
out=[]
for l in lines:
    m=re.match(r"\s*(\d+)\.\s*(.*)$", l)
    if m: out.append(f"{int(m.group(1))}. {m.group(2)}")
open(os.path.join(V10,"03_表格与补充数据","references_vancouver_v10.txt"),"w",encoding="utf-8").write("\n".join(out)+"\n")
# tables: v10 results + inherited supplements
for src,pat in [(os.path.join(V10,"reruns","results"), None),
                (os.path.join(PK,"03_表格与补充数据"), None),
                (os.path.join(PK8,"03_表格与补充数据"), None)]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith((".csv",".txt",".json")) and not f.startswith("references_vancouver_v0"):
            s=os.path.join(src,f); d=os.path.join(V10,"03_表格与补充数据",f)
            if not os.path.exists(d): shutil.copy(s,d)
# reports: v7-v16 + v10 logs
for src in [os.path.join(V9,"04_评审记录与报告"), os.path.join(PK,"04_评审记录与报告"), os.path.join(PK8,"04_评审记录与报告")]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith(".md") and not f.startswith("_"):
            d=os.path.join(V10,"04_评审记录与报告",f)
            if not os.path.exists(d) or f.startswith("v1"): shutil.copy(os.path.join(src,f),d)
# scripts
for src in [os.path.join(V10,"reruns","scripts"), os.path.join(PK,"05_代码与复现脚本"), os.path.join(PK8,"05_代码与复现脚本")]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith((".R",".py",".sh")): shutil.copy(os.path.join(src,f), os.path.join(V10,"05_代码与复现脚本",f))
# figures inherited (supp S1/S2 etc)
for f in ["fig_paper_xcell_vs_marker.png","fig_paper_xcell_heatmap.png","fig_paper_xcell_vs_marker.pdf","fig_paper_xcell_heatmap.pdf"]:
    s=os.path.join(V9,"02_图片",f)
    if os.path.exists(s): shutil.copy(s, os.path.join(V10,"02_图片",f))

cover = """Shuqiong Su, MD (corresponding author)
Department of Gastroenterology, Guangxi Medical University Cancer Hospital
Email: liuaiqun_2004@163.com

Dear Editor,

We are pleased to submit our manuscript, "Growth-factor pathway architecture across human tissue contexts: a composition-aware transcriptional atlas spanning six cancers and four chronic diseases", for consideration as a Research Article in npj Precision Oncology.

What the paper does. Most bulk "pathway activation" in cancer genomics is read as tumour-cell biology, yet much of it reflects tissue composition and clinical background. We scored seventeen growth-factor pathway modules in 27 public case-control cohorts across six cancers and four chronic benign diseases and adjudicated every candidate signal through cross-cohort, composition, single-cell and prognostic layers, with external validation in three independent cohorts.

This version incorporates a full computational audit and re-analysis. Three implementation errors were identified and corrected: a paired-sample indexing error that had excluded all matched cohorts from an earlier meta-analysis; an inclusion filter that had distorted an earlier composition summary; and incomplete tissue-type/stage handling in an external cohort. All results were recomputed with standard implementations (metafor for random-effects meta-analysis; standardized mean changes with empirical within-pair correlation for matched cohorts; joint models that adjust for composition simultaneously with disease status), and the corrections are described in the code repository.

Corrected findings. Fifty-five of 170 module-context states were per-cohort robust; conservative REML/Hartung-Knapp meta-analysis retained seven states (20 under DerSimonian-Laird), dominated by inflammatory bowel disease, and joint composition models retained 21 states (CRC 10, STAD 9, ESCC 1, IBD 1) with no PAAD state surviving composition adjustment. In TCGA, 17/108 module-OS associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. Importantly, after correcting tissue-type filtering and stage parsing, no module passed strict external replication: the previously reported CRC VEGF/PDGF replication did not survive stage adjustment, and no PAAD signal was reproduced. We report this transparently rather than selectively.

Why it matters. The paper's contribution is a graded, per-state evidence structure (Supplementary Table S9) that separates states that were not analysed, not estimable, estimated without significance, and robust, together with an explicit demonstration of how composition adjustment, effect-size scale and external-cohort handling change conclusions. We believe this is the discipline precision-oncology readers need before treating transcriptomic module scores as targetable biology.

All data are public; code and processed results are available under an MIT licence at https://github.com/sushuqiong/egfr-pathway-context-atlas. No part of this work has been published or is under consideration elsewhere. All authors have approved the submission and declare no competing interests.

Sincerely,
Shuqiong Su
"""
open(os.path.join(V10,"01_稿件正文","Cover_letter_v10.txt"),"w",encoding="utf-8").write(cover)

chk = """# Submission readiness checklist (v10) — npj Precision Oncology

## v10 关键口径（勿回退）
- 逐队列 55/170；统一尺度 meta：**REML/Hartung-Knapp 7**（IBD 6 + COPD 1）、**DerSimonian-Laird 20**（IBD 11/COPD 5/Asthma 4）
- 联合模型组成稳健 **21**（CRC 10、STAD 9、ESCC 1、IBD 1；PAAD 0）；状态分类：robust 21 / 不显著 95 / 已估计 54 / 未分析 0
- 外部：CRC GSE39582 肿瘤 566→可分析 **556/187**（非肿瘤 17 例排除；stage 1-4=552，stage 0=4 不入分期模型）；**VEGF 仅方向一致**（age+stage 后 p=0.22，不可称复现）；FGFR/IGF 名义；PDAC 无复现；ACRG 3/5 方向一致无 FDR 显著 → **无状态通过严格外部复现**
- 措辞：不写 pathway activation / demonstrates / prospective；驱动层=underpowered screen；PAAD 亚型分析为派生分类器探索性

## 自动完成
- [x] Manuscript_draft_v10.md/.docx/.pdf（摘要 250 词；51 refs 首次出现顺序；4.8 标题已修复）
- [x] Cover_letter_v10.txt
- [x] 02_图片：Fig1-6 全部由 v10 冻结结果表重生成（Fig2B=joint 模型，命名统一，n.e. 显式标注）+ Supp S1/S2
- [x] 03_表格与补充数据：v10 证据矩阵、meta（REML/DL/ρ 敏感性）、联合汇总、CRC 外部修正表 + 继承 S1-S8 + references_vancouver_v10.txt
- [x] 04_评审记录与报告：v7-v16（含 v16 bug 修复重算报告）
- [x] 05_代码与复现脚本：v10 修正管线 + 历史脚本
- [ ] GitHub 更新（修正管线 + errata + config + 相对路径 + 双跑/洗牌核验）— 本轮执行
- [ ] 作者名单/CRediT/ORCID；引文上标排版；图 TIFF；Cover 抬头填空；投稿系统 AI 问答如实作答

## 核验记录（GPT6 第 8 节要求）
- [x] 配对效应量 200/200 可估（median ri=0.99），固定 ρ=0.5/0.7 结果一致（7=7=7）
- [x] meta 改用 metafor（REML/Knha、DL），不再使用自写迭代
- [x] 组成与表达按 sample ID 显式连接；组别参照显式 Control（不再事后翻符号）
- [ ] 洗牌样本顺序后按 ID 连接结果一致（脚本已备，投前跑一次留档）
- [ ] 从原始输入完整运行两次核心结果一致（同上）
"""
open(os.path.join(V10,"06_投稿清单与流程","Submission_readiness_checklist_v10.md"),"w",encoding="utf-8").write(chk)

readme = """# EGFR pathway-context atlas — v10 投稿包

论文：Growth-factor pathway architecture across human tissue contexts: a composition-aware transcriptional atlas spanning six cancers and four chronic diseases
目标期刊：npj Precision Oncology（备选 J Transl Med / Mol Oncol）

## 本包内容
- 01_稿件正文：Manuscript_draft_v10.md/.docx/.pdf；Cover_letter_v10.txt
- 02_图片：Fig1 流程图（v10 数字）、Fig2A raw / Fig2B joint（主分析）、Fig3 raw vs joint、Fig4 TCGA forest、Fig5 分子（A 扩增/B 突变）、Fig6 单细胞（含患者数标注）、Supp S1/S2
- 03_表格与补充数据：v10_evidence_matrix.csv、v10_meta_*.csv、v10_joint_summary.csv、v10_external_crc_gse39582.csv、逐队列 effects/joint、references_vancouver_v10.txt、继承 S1-S8
- 04_评审记录与报告：v7-v16（v16 = GPT6-v9 bug 修复与重算说明）
- 05_代码与复现脚本：v10 修正管线（10/20/12/22/23/30/40-44）与历史脚本
- 06_投稿清单与流程：Submission_readiness_checklist_v10.md

## v10 与 v9 的差别（重要）
修复三处实现错误后：meta REML/Knha 11→7，DL 31→20；联合稳健 6→21（CRC 10/STAD 9/ESCC 1/IBD 1）；CRC 外部 VEGF 由"复现"降为"方向一致但分期校正后不显著"；新增 per-state 状态分类与更强的一致性/可复现要求。
"""
open(os.path.join(V10,"README_索引.md"),"w",encoding="utf-8").write(readme)
print("package assembled")
for d in ["01_稿件正文","02_图片","03_表格与补充数据","04_评审记录与报告","05_代码与复现脚本","06_投稿清单与流程"]:
    print(d, len(os.listdir(os.path.join(V10,d))))
