# 人工项填写指南（v11）— 点哪里、填什么、示例文本

> 适用：npj Precision Oncology（Springer Nature 投稿系统）。全部照做约 20–30 分钟。
> 所有自动项已完成；本指南只覆盖必须由你本人填写/确认的内容。

---

## 第 0 步（1 分钟）：投稿前自检
在本机执行（git-bash 里粘贴）：
```bash
cd /c/Users/fengq/Desktop/EGFR/egfr-pathway-context-atlas
/d/ProgramData/python tests/check_v11_consistency.py
```
看到 `RESULT: PASS` 即可（当前状态已 PASS）。若 FAIL，把输出发我。

---

## 第 1 步（5 分钟）：作者名单 + CRediT
打开 `EGFR的v11\01_稿件正文\Manuscript_draft_v11.md`（或 docx），找到 **Author list** 与 **Author contributions** 两处占位，按下面格式替换：

**作者行示例（按你的真实情况改）**
```
Shuqiong Su¹*, [共同作者姓名]², [姓名]³
¹ Department of Gastroenterology, Guangxi Medical University Cancer Hospital, Nanning, China
² [单位], [城市], China
* Correspondence: liuaiqun_2004@163.com
```

**CRediT 示例（按实际贡献勾选/删减）**
```
Author contributions
Shuqiong Su: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Supervision, Project administration.
[共同作者]: Validation, Writing – review & editing.
```
⚠️ 只有真实参与者才写；不要在作者列表中放 AI/工具名。

---

## 第 2 步（5 分钟）：Cover letter 抬头
打开 `EGFR的v11\01_稿件正文\Cover_letter_v11.txt`，在文件最上方加 5 行：

```
2026-09-14                       ← 投稿当天日期
Dear Editor,                     ← 若知道编辑姓名可写 Dr. XXX
npj Precision Oncology
Manuscript type: Article
ORCID: 0000-0000-0000-0000       ← 有就填，没有可删这行
```
正文段落**不要动**（已按 v11 定稿）。若你此前没提交过 ORCID，可在投稿系统里创建后回填。

---

## 第 3 步（2 分钟）：图件上传
用 `EGFR的v11\02_图片_TIFF\` 里的 TIFF（已 300 dpi、宽度 ≤17 cm）：
| 投稿系统里的图名 | 文件 |
|---|---|
| Figure 1 | Figure1.tif |
| Figure 2 | Figure2A.tif、Figure2B.tif（同一图的两个面板，系统里选 "Figure 2" 分别上传或合传） |
| Figure 3–6 | Figure3.tif … Figure6.tif |
| Supplementary Figure S1/S2 | FigureS1.tif、FigureS2.tif |
规格表：`02_图片_TIFF\figure_specs.csv`（含像素、cm、dpi）。
> 若系统只收 PDF 图：同目录 `02_图片\` 有对应 PDF 版可直接用。
> 不要上传中文文件名；不要 PNG+PDF 混传同一图。

---

## 第 4 步（10 分钟）：投稿系统逐屏填写（Springer Nature）
1. 打开 https://www.nature.com/npjprecisiononcology/ → 右上 **Submit manuscript** → 登入
2. **Article type**：选 *Article*
3. **Title / Abstract**：从 docx 直接复制（摘要 256 词，系统可能限 250–300 词，超限按提示删最后一句结论并告知我）
4. **Authors**：按第 1 步名单逐个添加（系统会发确认邮件给共同作者，请提前告知他们查收）
5. **Upload files**：顺序建议
   ① Cover letter（第 2 步文件）
   ② Manuscript（`Manuscript_draft_v11.docx`）
   ③ Figures（第 3 步 TIFF）
   ④ Supplementary（`03_表格与补充数据` 里的 TableS9 等，逐个上传并在系统里标注 S1、S2…）
6. **AI 使用问答**（必答）：选 **Yes**，粘贴——
   > Large-language-model tools were used to assist with parts of the data-analysis scripting (R/Python), with drafting and editing of the manuscript text, and with editorial review of the analyses. All statistical analyses were verified against the public source data by the author, and the author takes full responsibility for the content of the manuscript.
7. **Declarations**：Competing interests → None；Data availability → 公共数据 + GitHub 链接 `https://github.com/sushuqiong/egfr-pathway-context-atlas`
8. **Reviewers**：若系统要求推荐，选非同一机构的领域专家；可跳过时跳过
9. 最后 **Approve & Submit**（提交前截图留档）

---

## 第 5 步（2 分钟）：提交后
- 到通讯邮箱确认收到 "Submission received" 邮件
- 若系统生成 Manuscript ID，回填到 `06_投稿清单与流程\Submission_readiness_checklist_v11.md` 顶部
- 把 ID 发我，我登记进 `04_评审记录与报告`（后续审稿意见来时可直接对照处理）

---

## 附：若有疑问
- 数字相关问题：跑第 0 步的自检脚本，把输出发我
- 图件版式问题：把系统提示信息或截图发我（我可用离线 OCR 读图）
- 不要自行改动正文数字；若要改，先告诉我是哪句，我同步改表、图与一致性测试
