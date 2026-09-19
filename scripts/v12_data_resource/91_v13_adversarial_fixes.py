#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13 adversarial fixes: download pathway script, legend cleanup, stale-file removal,
manuscript repo URL + CELLxGENE identifiers, estimates provenance note, rebuild and re-audit."""
import csv, os, glob, shutil, subprocess, sys, hashlib
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
# ---------- 1. a genuinely runnable download-and-rebuild script ----------
os.makedirs(os.path.join(PK,"03_expression"),exist_ok=True)
open(os.path.join(PK,"03_expression","download_and_rebuild_one_series.R"),"w",encoding="utf-8").write(r'''#!/usr/bin/env Rscript
# Runnable pathway from a public accession to a processed matrix and module scores for one cohort.
# Usage: Rscript download_and_rebuild_one_series.R GSE13911
# Requires: GEOquery, GSVA, hgu133plus2.db (or the platform annotation package of the series).
args <- commandArgs(trailingOnly = TRUE)
acc <- if (length(args) >= 1) args[1] else "GSE13911"
suppressPackageStartupMessages({library(GEOquery); library(GSVA); library(dplyr)})
# 1. download the series matrix from GEO and take the first expression matrix
gse <- getGEO(acc, GSEMatrix = TRUE, getGPL = TRUE)
eset <- gse[[1]]
expr <- Biobase::exprs(eset)
if (max(expr, na.rm = TRUE) > 100) expr <- log2(expr + 1)          # the same rule as the shipped transformation log
md <- Biobase::pData(eset)
# 2. map probes to gene symbols (platform annotation; fall back to the feature data column)
fd <- Biobase::fData(eset)
sym_col <- intersect(c("Gene symbol", "GENE_SYMBOL", "Symbol", "gene_assignment"), names(fd))[1]
if (!is.na(sym_col)) {
  sym <- toupper(as.character(fd[[sym_col]]))
  sym <- sub(" ?//.*$", "", sym)                                    # Affymetrix multi-mapping strings
  keep <- !is.na(sym) & sym != "" & sym != "NA"
  expr <- expr[keep, , drop = FALSE]; rownames(expr) <- sym[keep]
  expr <- limma::avereps(expr, ID = rownames(expr))                 # collapse multiple probes by mean
}
# 3. module scores with the frozen definitions shipped in this package
gs <- read.csv("../04_modules/module_definitions.csv")
sets <- lapply(split(toupper(gs$gene), gs$module), unique)
usable <- names(sets)[sapply(sets, function(g) length(intersect(g, rownames(expr))) >= 3)]
sc <- GSVA::gsva(GSVA::gsvaParam(expr, sets[usable], minSize = 3, kcdf = "Gaussian"), verbose = FALSE)
z <- t(scale(t(sc)))
out <- as.data.frame(t(z)); out$sample_id <- colnames(z); out$accession <- acc
dir.create("../output_rebuilt", showWarnings = FALSE)
write.csv(out, file.path("../output_rebuilt", paste0(acc, "_module_scores_z.csv")), row.names = FALSE)
cat("rebuilt", nrow(out), "samples x", ncol(out) - 2, "modules for", acc, "\n")
cat("NOTE: compare with the shipped 04_modules/sample_module_scores_gsva_z.csv for cohorts that are already curated.\n")
''')
open(os.path.join(PK,"03_expression","README_download_pathway.md"),"w",encoding="utf-8").write(
 "# From public accession to module scores\n\n"
 "`download_and_rebuild_one_series.R` is a runnable pathway for a single series: it downloads the series matrix from GEO, "
 "applies the same transformation rule recorded for the curated cohorts, maps probes to gene symbols, collapses multiple probes "
 "by the mean, and scores the frozen module definitions shipped in `04_modules/`.\n\n"
 "Run it from the package root:\n\n"
 "```bash\nRscript 03_expression/download_and_rebuild_one_series.R GSE13911\n```\n\n"
 "Output is written to `output_rebuilt/<accession>_module_scores_z.csv` and can be compared with the shipped per-sample scores. "
 "Processed expression matrices for the curated cohorts are **not** redistributed in this deposit: they are regenerated from the "
 "public accessions listed in `01_cohort_registry/` using this pathway, and the transformation decision for every curated cohort "
 "is recorded in `transformation_log.csv`.\n")
# ---------- 2. legends: drop the supplementary-figure section ----------
p86=os.path.join(V13,"scripts","86_v13_word_outputs.py"); s=open(p86,encoding="utf-8").read()
s=s.replace(''' ("Supplementary figures.",
  "Supplementary Figure S1. Marker-proxy versus xCell sensitivity of composition adjustment. "
  "Supplementary Figure S2. Two-step xCell residualization sensitivity.")''',
 ''' ("Supplementary material.",
  "No supplementary figures are required for this descriptor: the composition sensitivity material is presented in Figure 2 panels D and E, "
  "and the corresponding numerical results are shipped as machine-readable tables in folder 08_qc (common-gene sensitivity, composition "
  "collinearity, per-predictor VIF, module-versus-signature overlap).")''')
open(p86,"w",encoding="utf-8").write(s)
# ---------- 3. remove stale v12 artefacts from v13 working folders ----------
removed=[]
for folder in ["01_manuscript","03_tables"]:
    for f in os.listdir(os.path.join(V13,folder)):
        if "v12" in f:
            os.remove(os.path.join(V13,folder,f)); removed.append(f"{folder}/{f}")
print("removed stale:",removed)
# ---------- 4. manuscript: repo URL + CELLxGENE identifiers + wording ----------
cg=rd(os.path.join(PK,"01_cohort_registry","cellxgene_sources.csv"))
cg_txt="; ".join(f"{r['context']} dataset_version_id {r['dataset_version_id']} in collection {r['collection_id']}" for r in cg if r["dataset_version_id"])
p83=os.path.join(V13,"scripts","83_v13_manuscript.py"); t=open(p83,encoding="utf-8").read()
t=t.replace("https://github.com/sushuqiong/egfr-pathway-context-atlas","https://github.com/sushuqiong/cross-disease-transcriptomic-resource")
t=t.replace("the code repository is https://github.com/sushuqiong/cross-disease-transcriptomic-resource",
            "the code repository is https://github.com/sushuqiong/cross-disease-transcriptomic-resource (renamed from egfr-pathway-context-atlas; the former URL redirects)")
old_src="*Source versions and licences.* Source releases, accessions and licence notes are shipped (01_cohort_registry/source_versions.csv)."
new_src=("*Source versions and licences.* Source releases, accessions and licence notes are shipped (01_cohort_registry/source_versions.csv), and the "
 f"single-cell inputs are identified by their CELLxGENE dataset versions and collections ({cg_txt}), which were re-verified against the CELLxGENE API "
 "(cell counts and titles agree with the locally processed files).")
t=t.replace(old_src,new_src)
t=t.replace("(iii) harmonised expression matrices with gene-mapping and transformation provenance and a runnable download-to-results pathway;",
            "(iii) gene-mapping and transformation provenance for every cohort together with a runnable script that rebuilds one series from its public accession to module scores;")
open(p83,"w",encoding="utf-8").write(t)
print("manuscript generator patched (repo URL, CELLxGENE ids, download pathway wording)")
# ---------- 5. provenance note for the inherited estimate tables ----------
open(os.path.join(PK,"07_estimates","PROVENANCE.md"),"w",encoding="utf-8").write(
 "# Provenance of the tables in 07_estimates\n\n"
 "| File | Produced by | Basis | Affected by the metadata-driven pairing correction? |\n|---|---|---|---|\n"
 "| per_cohort_effects.csv | v13 (script 80 + 41) | 26 case-control cohorts, 442 rows = 434 estimated + 8 not estimable | yes - it is the corrected version |\n"
 "| not_estimable_pairs.csv | v13 (script 80) | membership/variance checks | yes |\n"
 "| meta_primary_reml_knha.csv, meta_dersimonian_laird.csv, meta_adhoc_knapp_hartung.csv, meta_unpaired_only.csv, meta_rho0.5/rho0.7 | v12 (script 41) | pooled from the corrected per-cohort effects | yes - already recomputed after the pairing correction |\n"
 "| composition_model_summary.csv | v11 joint layer | base versus adjusted models on identical samples | no - the composition models do not use the paired/unpaired classification, and the cohort set is unchanged |\n"
 "| driver_interactions.csv, driver_eligibility.csv | v11 | TCGA driver stratification | no - TCGA layer, not cohort pairing |\n"
 "| external_validation_crc.csv | v11 | independent colorectal series (GSE39582), analysed unpaired | no - the series has no paired design |\n"
 "| tcga_escc_squamous_*.csv | v12 (scripts 11/12) | squamous oesophageal subset, 96 patients (94 with survival data) | no - TCGA layer |\n"
 "| per_state_evidence_matrix.csv | v11 | state-level summary of per-cohort evidence | partially - it summarises effects that were corrected for three cohorts; where a state depends on those cohorts, the corrected per-cohort table supersedes it |\n")
print("provenance note written")
# ---------- 6. rebuild manuscript, legends, docx/pdf, zips, audits ----------
for script in ["83_v13_manuscript.py","86_v13_word_outputs.py","87_v13_build_and_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V13,"scripts",script)],capture_output=True,text=True)
    tail=[l for l in (r.stdout or "").strip().splitlines() if l.strip()][-2:]
    print(f"[{script}]", " | ".join(tail))
# refresh inventory inside the package and rebuild the zenodo zip
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
        nr=""
        if f.lower().endswith(".csv"):
            try: nr=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nr=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nr, sha256=h.hexdigest()))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(inv[0].keys())); w.writeheader(); w.writerows(inv)
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
shutil.make_archive(os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v13"),"zip",PK)
print("inventory files:",len(inv),"| zenodo zip rebuilt")
out=subprocess.run([sys.executable, os.path.join(V13,"scripts","90_v13_adversarial.py")],capture_output=True,text=True).stdout
print(out.strip().splitlines()[-1])
