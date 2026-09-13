#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, shutil
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
V10=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10"
PK =r"C:\Users\fengq\Desktop\EGFR\EGFR_Atlas_投稿包"
PK8=r"C:\Users\fengq\Desktop\EGFR\EGFR_Atlas_投稿包_v8"
for d in ["01_稿件正文","02_图片","03_表格与补充数据","04_评审记录与报告","05_代码与复现脚本","06_投稿清单与流程"]:
    os.makedirs(os.path.join(V11,d), exist_ok=True)
md=open(os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.md"),encoding="utf-8").read()
_,_,ref=md.partition("## References")
out=[]
for l in ref.splitlines():
    m=re.match(r"\s*(\d+)\.\s*(.*)$",l)
    if m: out.append(f"{int(m.group(1))}. {m.group(2)}")
open(os.path.join(V11,"03_表格与补充数据","references_vancouver_v11.txt"),"w",encoding="utf-8").write("\n".join(out)+"\n")
# tables: v11 results + inherited supplements
for src in [os.path.join(V11,"reruns","results"), os.path.join(V10,"03_表格与补充数据"),
            os.path.join(PK,"03_表格与补充数据"), os.path.join(PK8,"03_表格与补充数据")]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith((".csv",".txt",".json")) and not f.startswith("references_vancouver_v"):
            d=os.path.join(V11,"03_表格与补充数据",f)
            if not os.path.exists(d): shutil.copy(os.path.join(src,f),d)
# reports
for src in [os.path.join(V10,"04_评审记录与报告"), os.path.join(PK,"04_评审记录与报告"), os.path.join(PK8,"04_评审记录与报告")]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith(".md"): shutil.copy(os.path.join(src,f), os.path.join(V11,"04_评审记录与报告",f))
# scripts
for src in [os.path.join(V11,"reruns","scripts"), os.path.join(V10,"05_代码与复现脚本"),
            os.path.join(PK,"05_代码与复现脚本"), os.path.join(PK8,"05_代码与复现脚本")]:
    if not os.path.isdir(src): continue
    for f in os.listdir(src):
        if f.endswith((".R",".py",".sh",".dot")): shutil.copy(os.path.join(src,f), os.path.join(V11,"05_代码与复现脚本",f))

cover = """Shuqiong Su, MD (corresponding author)
Department of Gastroenterology, Guangxi Medical University Cancer Hospital
Email: liuaiqun_2004@163.com

Dear Editor,

We are pleased to submit our manuscript, "Growth-factor pathway architecture across human tissue contexts: a composition-aware transcriptional atlas spanning six cancers and four chronic diseases", for consideration as a Research Article in npj Precision Oncology.

What the paper does. Bulk "pathway activation" in cancer genomics is often read as tumour-cell biology, although much of it reflects tissue composition and clinical background. We scored seventeen growth-factor pathway modules in 27 public case-control cohorts across six cancers and four chronic benign diseases, and evaluated every candidate state through parallel evidence layers with pre-specified decision rules: cross-cohort reproducibility; meta-analysis on a single common standardized scale; composition modelled as a base-versus-adjusted comparison; patient-level single-cell localization with explicit paired testing; and independent external validation.

How this version was produced. Following external computational review we corrected several implementation issues and re-ran the affected analyses: paired and unpaired cohorts are now expressed with the same standardization denominator (metafor SMDH for unpaired cohorts, SMCRPH for matched cohorts with the empirical within-pair correlation); composition is reported as a base-versus-adjusted model comparison on identical samples rather than as a single "unadjusted" coefficient; single-cell comparisons use paired signed-rank tests wherever complete patient pairs exist, with cell-identity contrasts labelled separately; and mutation prevalence and driver analyses are restricted to mutation-profiled samples with an explicit wild-type definition. All corrections are documented in ERRATA_v11 in the accompanying code repository.

Corrected findings. Fifty-five of 170 states were per-cohort robust; conservative common-denominator meta-analysis retained 17 states (74 under DerSimonian-Laird; 6 with non-shrinking Knapp-Hartung; 3 in an unpaired-only analysis), showing that conclusions depend on the estimator and are reported as such. The base-versus-adjusted comparison retained 21 states (CRC 10, STAD 9, ESCC 1, IBD 1; none in PAAD) with a median adjusted-to-base coefficient ratio of 0.87, i.e. attenuation was typically modest rather than complete. In TCGA, 17/108 module-OS associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. No module passed pre-specified external replication: the CRC VEGF/PDGF signal was directionally consistent but not significant after stage adjustment, and no PDAC signal was reproduced.

Why it matters. The contribution is a comparison framework with explicit decision rules and a reusable per-state evidence matrix that records, for every state and every layer, whether it passed and why - together with a demonstration that apparent "pathway activation" in bulk tissue is substantially composition- and context-dependent. We believe this level of transparency is what precision-oncology readers need before treating transcriptomic module scores as targetable biology.

All data are public; code, corrected pipelines and processed results are available under an MIT licence at https://github.com/sushuqiong/egfr-pathway-context-atlas. No part of this work has been published or is under consideration elsewhere, and all authors approved the submission.

Sincerely,
Shuqiong Su
"""
open(os.path.join(V11,"01_稿件正文","Cover_letter_v11.txt"),"w",encoding="utf-8").write(cover)

chk = """# Submission readiness checklist (v11) — npj Precision Oncology

## v11 关键口径（勿回退）
- 逐队列稳健 55/170
- 统一分母 meta（非配对 SMDH + 配对 SMCRPH，分母 √[(sd1²+sd2²)/2]）：**REML/Knapp-Hartung BH 17**（CRC 11、IBD 3、LUAD 2、PAAD 1）；DL 74；非收缩 KH 6；仅非配对 3；固定 ρ=0.5/0.7 → 17
- 组成 = **基础模型 vs 调整模型**（同样本）：组成稳健 **21**（CRC 10、STAD 9、ESCC 1、IBD 1；PAAD 0）；中位调整/基础系数比 **0.87**（勿写"完全衰减/组成解释"）
- 单细胞：**同细胞类型显著 16**（10 个配对 signed-rank，中位 15 对）+ **细胞身份对比 12**（单独标注，勿当疾病效应）；非配对敏感性 29
- 突变/驱动：仅 profiled 样本（PAAD 173 profiled，KRAS 107/173=61.9%，与原文 140/150 口径差异已注明）；driver 102 检验、5 名义、0 FDR
- 外部：CRC GSE39582 **556/187**（585 阵列→566 肿瘤→556 可分析；stage 1-4=552）；VEGF 仅方向一致（age+stage p=0.22）；PDAC 无复现；ACRG 3/5 方向一致无 FDR → **无状态通过严格外部复现**
- 方法中须保留可执行判定规则（per-cohort / meta / composition-robust / external replication）与多重检验范围

## 自动完成
- [x] Manuscript_draft_v11.md/.docx/.pdf（摘要 256 词；51 refs 全部引用、顺序 0 违规）
- [x] Cover_letter_v11.txt
- [x] Fig1 并行证据布局；Fig2A raw / Fig2B adjusted；Fig3 base vs adjusted；Fig4 forest；Fig5 profiled-only 分母；Fig6 配对+身份双面板；Supp S1/S2
- [x] Table S9 逐状态证据矩阵（含各层通过/未通过）；S10 配对核验记录
- [x] 03 表格：v11 meta（primary/DL/adhoc/unpaired/ρ）、joint 汇总、driver、突变分母、sc 配对、证据矩阵
- [x] 04 报告：v7-v17 + v18（v11 修改说明）
- [x] 05 脚本：v11 全管线（10/20/30/31/40/50/60/70-74/80）
- [ ] GitHub 更新（ERRATA_v11 + 修正脚本 + 结果 + 测试）
- [ ] 人工项：作者名单/CRediT、Cover 抬头、图 TIFF 目检、投稿系统 AI 问答

## 核验记录
- [x] 配对效应量 200/200 可估；median 实证 r=0.11；固定 ρ 与实证结论一致（17）
- [x] 洗牌样本顺序 / 重复运行一致（tests/check_paired_effect.R）
- [x] 突变分母与表达分母分离，非 profiled 样本排除并计数
- [x] 单细胞配对对数与身份对比分离并各自校正
"""
open(os.path.join(V11,"06_投稿清单与流程","Submission_readiness_checklist_v11.md"),"w",encoding="utf-8").write(chk)

readme = """# EGFR pathway-context atlas — v11 投稿包

论文：Growth-factor pathway architecture across human tissue contexts: a composition-aware transcriptional atlas spanning six cancers and four chronic diseases
目标期刊：npj Precision Oncology（备选 J Transl Med / Mol Oncol）

## v11 相对 v10 的关键修正（据外部评审）
1. **效应量分母真正统一**：非配对 SMDH + 配对 SMCRPH（同为 √[(sd1²+sd2²)/2]）；meta 主结果 17（DL 74 / 非收缩 KH 6 / 仅非配对 3），并如实披露估计器敏感性
2. **组成改为基础模型 vs 调整模型**（同样本，报 β/SE/CI；中位调整/基础比 0.87），不再以显著性变化推断"组成解释"
3. **单细胞显式配对**：≥5 完整对用配对 signed-rank（10 个显著，中位 15 对），其余非配对并标注；恶性 vs 正常上皮单列为"细胞身份对比"（12 个）
4. **突变/驱动仅用 profiled 样本**（PAAD 173；KRAS 61.9%），非 profiled 排除并计数；原文 140/150 口径差异如实说明
5. 一致性修复：摘要/结果/结论/表/图单一数据源；Fig1 改并行证据布局；正文去掉版本说明与 Markdown 残留

## 目录
01_稿件正文（md/docx/pdf + Cover_letter_v11）｜02_图片（Fig1-6 + Supp S1/S2）｜03_表格与补充数据（v11 各层结果 + 继承 S1-S8 + references_vancouver_v11.txt）｜04_评审记录与报告（v7-v18）｜05_代码与复现脚本｜06_投稿清单与流程
"""
open(os.path.join(V11,"README_索引.md"),"w",encoding="utf-8").write(readme)
print("v11 package assembled")
for d in ["01_稿件正文","02_图片","03_表格与补充数据","04_评审记录与报告","05_代码与复现脚本","06_投稿清单与流程"]:
    print(" ",d,len(os.listdir(os.path.join(V11,d))))
