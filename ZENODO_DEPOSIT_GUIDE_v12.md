# Zenodo 上传指南（v12 数据资源包）— 点哪里、填什么

> 目标：把 `EGFR的v12\dataset_package\`（10 个目录 + README，约几 MB）上传到 Zenodo，拿到 DOI，再回填到正文。
> 你已用 GitHub 登录过 Zenodo，所以第 1 步直接在网页登录即可。

---

## 第 0 步：先把包打成 ZIP（1 分钟）
在 git-bash 里粘贴：
```bash
cd /c/Users/fengq/Desktop/EGFR/EGFR的v12 && python -c "
import shutil,os
shutil.make_archive(os.path.join(r'C:\Users\fengq\Desktop','★Zenodo上传-就选这个_v12'),'zip',r'C:\Users\fengq\Desktop\EGFR\EGFR的v12\dataset_package')
print('OK')
"
```
得到桌面文件：`★Zenodo上传-就选这个_v12.zip`。

---

## 第 1 步：登录 Zenodo
1. 打开 https://zenodo.org → 右上角 **Sign in**（或 **Sign up**）
2. 选 **Sign in with GitHub** → 授权（你之前用过，直接点即可）

## 第 2 步：新建上传
1. 右上角你的头像 → **New upload**（或直接打开 https://zenodo.org/uploads/new）
2. 点 **Choose files** → 选桌面的 `★Zenodo上传-就选这个_v12.zip`
3. 等待上传完成（几 MB，很快）

## 第 3 步：填写元数据（照抄下面的文本）
**Upload type**：`Dataset`

**Title**（≤ 也合规）：
```
A curated cross-disease transcriptomic resource with growth-factor and tissue-composition annotations
```
**Creators**：`Su, Shuqiong`（Orcid 若有就填；机构 `Department of Gastroenterology, Guangxi Medical University Cancer Hospital`）

**Description**（粘贴）：
```
Curated resource that reorganises public human tissue transcriptomes into a comparable, annotation-rich form for cross-disease reuse. Contents: (1) cohort registry with source accessions, platforms and origin publications; (2) sample-level annotation including tissue type, case-control role, paired relations and documented exclusion reasons; (3) gene-mapping and transformation provenance; (4) seventeen growth-factor signalling module definitions with per-platform gene coverage and sample-level scores; (5) expression-derived tissue-composition scores with four aggregated compartments; (6) patient-level summaries and donor-aware comparisons from four single-cell datasets, with raw and curated cell labels kept separate; (7) a complete estimates layer including non-significant and non-estimable results; (8) quality-control records; (9) two runnable reuse examples with expected outputs; (10) software environment and run order.

Scope: 27 case-control expression cohorts (2,754 assay records, 1,138 unique patients, 12 platforms) across ten contexts (six cancers, four chronic benign diseases) plus a squamous oesophageal TCGA subset (96 patients). Derived data are released under CC-BY-4.0; source data remain under the terms of GEO, TCGA/GDC (via cBioPortal) and CELLxGENE.

Limitations: module gene coverage is incomplete for part of the cohorts; composition scores are enrichment scores rather than cell proportions; cohort count is not patient count; the resource is not a patient-level multi-omics resource; module scores are not validated prognostic tools.
```
**Keywords**（逐个添加）：`transcriptomics`, `data resource`, `growth factor signalling`, `tumour microenvironment`, `tissue composition`, `cross-disease`, `reproducibility`, `TCGA`, `GEO`, `single-cell`

**License**：`Creative Commons Attribution 4.0 International (CC BY 4.0)`
**Language**：English
**Related identifiers**：Relation `is supplemented by` → `https://github.com/sushuqiong/egfr-pathway-context-atlas`

## 第 4 步：保存并发布
1. 点 **Save draft**（先存草稿，检查一遍）
2. 检查 3 处：Title、License = CC-BY-4.0、文件是那个 ZIP
3. 点 **Publish** → 得到 **DOI**（形如 `10.5281/zenodo.12345678`）

## 第 5 步：把 DOI 发我，并区分两种状态
- **首轮投稿可以先用匿名下载链接**：在 Zenodo 记录页点 **Share → Copy link**（或先保持 draft 用私有分享链接）
- **第二轮评审起必须正式 depository**（即上面的 Publish）
- 把 DOI 或链接发我，我回填到：正文 *Data Availability*、*Code Availability*、README、以及 Table 1 说明里（正文里有 `[to be inserted after deposit]` 占位）

## 第 6 步（可选但推荐）：给代码也拿一个 DOI
1. 打开你的 GitHub 仓库 → **Releases → Draft a new release**
2. Tag：`v12.0`，Title：`v12 resource release`，点 **Publish release**
3. 回到 Zenodo → 右上角头像 → **Settings → GitHub** → 找到 `egfr-pathway-context-atlas` → 打开开关
4. 以后再发 release，Zenodo 会自动给代码存档并给一个 DOI（可写进 Code Availability）

---

## 常见问题
- **上传超过 50 GB？** 本包只有几 MB，不会遇到。
- **想改内容？** 记录页 → **New version**，不要覆盖旧版本（旧 DOI 必须保持可用）。
- **审稿人要求匿名访问？** 用 draft 状态的私有链接，或记录页的 Share 链接（不暴露你的身份）。
- **许可能否用 CC-BY-NC？** 不能，Scientific Data 明确不接受 -NC/-SA（上游二次数据保留原条款的情况除外，本包不涉及）。
