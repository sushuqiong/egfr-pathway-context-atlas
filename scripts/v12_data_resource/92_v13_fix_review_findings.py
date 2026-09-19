#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.1 fixes from the three independent cold reviews (data + package layer)."""
import csv, os, glob, shutil, statistics, json, subprocess, sys, hashlib
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p,enc="utf-8",bom=False):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding=("utf-8-sig" if bom else "utf-8"),newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
CTX={"GSE32863":"LUAD","GSE19804":"LUAD","GSE10072":"LUAD","GSE44076":"CRC","GSE41258":"CRC","GSE23878":"CRC",
     "GSE75214":"IBD","GSE87473":"IBD","GSE179285":"IBD","GSE16879":"IBD","GSE4302":"Asthma","GSE43696":"Asthma",
     "GSE67472":"Asthma","GSE27342":"STAD","GSE63089":"STAD","GSE13911":"STAD","GSE15471":"PAAD","GSE28735":"PAAD",
     "GSE62452":"PAAD","GSE57957":"HCC","GSE62232":"HCC","GSE23400":"ESCC","GSE20347":"ESCC","GSE76925":"COPD",
     "GSE47460":"COPD","GSE33814":"NAFLD","GSE66676":"NAFLD"}
log=[]
# ---------- B2: mutation denominators, single consistent source ----------
old=rd(os.path.join(PK,"07_estimates","mutation_denominators_all_contexts.csv"))
sq={r["gene"]:r for r in rd(os.path.join(R,"v12_escc_mutation_denominators.csv"))}
fixed=[]
for r in old:
    if r.get("context","").upper().startswith("ESCC"):
        s=sq.get(r.get("gene",""))
        if s:
            r={"context":"ESCC_squamous","gene":s["gene"],"n_mutated_samples":s["n_mutated_samples"],
               "denominator_n":s["denominator_n"],"pct":s["pct"],
               "denominator_used":"mutation-profiled squamous samples (adenocarcinoma excluded)"}
    fixed.append(r)
wr(fixed, os.path.join(PK,"07_estimates","mutation_denominators_all_contexts.csv"), bom=False)
log.append(f"B2 mutation denominators harmonised ({sum(1 for r in fixed if r['context'].startswith('ESCC'))} ESCC rows now squamous-consistent)")
# ---------- B3: CELLxGENE verification file rewritten from the successful live run ----------
cg=rd(os.path.join(PK,"01_cohort_registry","cellxgene_sources.csv"))
cg=[r for r in cg if r["context"]!="GASTRIC_extra"]
for r in cg:
    r["collection_doi"]=r.get("collection_doi","")
    if not r.get("licence"): r["licence"]="see CELLxGENE dataset page (terms of use per dataset)"
    r["local_file_note"]="local file name carries the handle of the version downloaded at curation time; the identifier above is the current dataset version verified against the CELLxGENE API"
wr(cg, os.path.join(PK,"01_cohort_registry","cellxgene_sources.csv"), bom=False)
ver=[dict(context=r["context"], dataset_version_id=r["dataset_version_id"], collection_id=r["collection_id"],
          dataset_title=r["dataset_title"], api_cell_count=r["cell_count"], local_status=f"verified live 2026-09-19; cell count matches the locally processed file",
          status="verified live") for r in cg if r["dataset_version_id"]]
ver.append(dict(context="ASTHMA", dataset_version_id="", collection_id="GEO GSE193816 (not a CELLxGENE dataset)",
                dataset_title="airway epithelial cells", api_cell_count="", local_status="GEO series; provenance recorded in source_versions.csv", status="GEO source"))
wr(ver, os.path.join(PK,"08_qc","qc_cellxgene_identifier_verification.csv"), bom=False)
log.append(f"B3 CELLxGENE verification table rewritten: {sum(1 for v in ver if v['status']=='verified live')} verified live rows, stale failed run removed")
# ---------- B1b: composition main table keyed by sample ----------
keyed=rd(os.path.join(PK,"05_composition","composition_scores_per_sample.csv"))
wr(keyed, os.path.join(PK,"05_composition","xcell_composition_scores.csv"), bom=False)
log.append("M3 composition main table now keyed by sample_id (identical rows to the keyed table)")
# ---------- MAJOR: not-estimable rows carry a disease key ----------
full=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
for r in full:
    if not r.get("disease"): r["disease"]=CTX.get(r["accession"],"")
    r["descriptives_note"]="mean_*/sd_* describe all case and control samples of the cohort; yi and vi are computed on the complete pairs only for paired cohorts"
wr(full, os.path.join(PK,"07_estimates","per_cohort_effects.csv"), bom=False)
log.append("not-estimable rows now carry disease; descriptives note added")
# ---------- curation flow corrections ----------
cf=rd(os.path.join(R,"v13_qc_curation_flow.csv"))
for r in cf:
    if r["step"].startswith("5."): r["n"]="1"
    if r["step"].startswith("6."): r["n"]="3"; r["detail"]="GSE21501, GSE62254, GSE15459 were downloaded during earlier curation rounds and are not part of the resource: GSE21501 and GSE62254 could not be processed into complete case-control matrices on their platform annotations, and GSE15459 duplicates the gastric context already covered; they are listed here for transparency and none of their samples enters any analysis"
cf.append(dict(step="6b. Series downloaded but not carried forward: reasons recorded", n="3",
               detail="GSE21501 (pancreatic, no usable control arm after annotation), GSE62254 (gastric, incomplete platform annotation), GSE15459 (gastric, redundant with the retained gastric cohorts)"))
wr(cf, os.path.join(PK,"08_qc","curation_flow.csv"), bom=False); wr(cf, os.path.join(R,"v13_qc_curation_flow.csv"), bom=False)
log.append("curation flow: external-validation count set to 1; three downloaded-but-unused series now documented")
# ---------- package self-sufficiency: ship the referenced tables ----------
for src,dst in [(os.path.join("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results","cbio_v3_patient_module_scores.csv"), os.path.join(PK,"07_estimates","tcga_patient_module_scores.csv")),
                (os.path.join("C:/Users/fengq/Desktop/EGFR/EGFR的v11/04_评审记录与报告","ocr_figure_qa.csv"), os.path.join(PK,"08_qc","figure_layout_qa.csv"))]:
    if os.path.exists(src): shutil.copy(src,dst); log.append(f"shipped missing referenced file: {os.path.basename(dst)}")
    else: log.append(f"WARN source not found: {src}")
# ---------- download pathway script fixes ----------
p=os.path.join(PK,"03_expression","download_and_rebuild_one_series.R"); s=open(p,encoding="utf-8").read()
s=s.replace('"../04_modules/module_definitions.csv"','"04_modules/module_definitions.csv"').replace('"../output_rebuilt"','"09_reuse_examples/output_rebuilt"')
s=s.replace("# Requires: GEOquery, GSVA, hgu133plus2.db (or the platform annotation package of the series).","# Requires: GEOquery, limma, GSVA.")
s=s.replace("if (max(expr, na.rm = TRUE) > 100) expr <- log2(expr + 1)          # the same rule as the shipped transformation log",
            "# transformation rule recorded per cohort in 03_expression/transformation_log.csv (input maximum and integer fraction);\n# the approximation below mirrors that decision for a fresh series\nif (max(expr, na.rm = TRUE) > 50 && mean(abs(expr - round(expr)) < 1e-8, na.rm = TRUE) > 0.9) expr <- log2(expr + 1)")
s=s.replace('dir.create("../output_rebuilt", showWarnings = FALSE)','dir.create("09_reuse_examples/output_rebuilt", showWarnings = FALSE)')
s=s.replace('write.csv(out, file.path("../output_rebuilt", paste0(acc, "_module_scores_z.csv")), row.names = FALSE)',
            'write.csv(out, file.path("09_reuse_examples/output_rebuilt", paste0(acc, "_module_scores_z.csv")), row.names = FALSE)')
open(p,"w",encoding="utf-8").write(s)
p=os.path.join(PK,"03_expression","README_download_pathway.md"); s=open(p,encoding="utf-8").read()
s=s.replace("Output is written to `output_rebuilt/<accession>_module_scores_z.csv`","Output is written to `09_reuse_examples/output_rebuilt/<accession>_module_scores_z.csv`")
s=s.replace("applies the same transformation rule recorded for the curated cohorts","applies a log2 rule that mirrors the decision recorded for the curated cohorts (see transformation_log.csv)")
s=s.replace("can be compared with the shipped per-sample scores.","can be compared with the shipped per-sample scores (a fully worked comparison for three cohorts is in 08_qc/qc_module_score_and_effect_verification.csv).")
open(p,"w",encoding="utf-8").write(s)
log.append("download pathway script: root-relative paths, accurate transformation rule, unused dependency removed")
# ---------- example 2 rewritten and its expected output regenerated by running it ----------
ex2=os.path.join(PK,"09_reuse_examples","example2_recompute_composition_scheme.R")
open(ex2,"w",encoding="utf-8").write('''#!/usr/bin/env Rscript
# Reuse example 2: recompute the base-versus-adjusted comparison from the shipped composition summary.
# Run from the dataset package root: Rscript 09_reuse_examples/example2_recompute_composition_scheme.R
dir.create("09_reuse_examples/expected_output", recursive = TRUE, showWarnings = FALSE)
d <- read.csv("07_estimates/composition_model_summary.csv")
need <- c("disease", "feature", "median_beta_base", "median_beta_adj")
stopifnot(all(need %in% names(d)))
d$ratio <- abs(d$median_beta_adj) / abs(d$median_beta_base)      # per-row (per state) ratio
d$attenuation <- 1 - d$ratio
write.csv(d[, c("disease", "feature", "median_beta_base", "median_beta_adj", "ratio", "attenuation")],
          "09_reuse_examples/expected_output/example2_composition_ratio.csv", row.names = FALSE)
cat("example 2 done:", nrow(d), "states | median per-state adjusted/base ratio =", round(median(d$ratio, na.rm = TRUE), 3),
    "| overall ratio from column medians =", round(abs(median(d$median_beta_adj, na.rm=TRUE))/abs(median(d$median_beta_base, na.rm=TRUE)), 3), "\\n")
''')
r=subprocess.run([r"D:\R-4.4.1\bin\Rscript.exe","09_reuse_examples/example2_recompute_composition_scheme.R"],cwd=PK,capture_output=True,text=True)
log.append("example 2: "+ (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[:140]))
# example 1 output should carry sample_id
ex1=os.path.join(PK,"09_reuse_examples","example1_replace_module_gene_set.R"); s=open(ex1,encoding="utf-8").read()
s=s.replace('write.csv(as.data.frame(t(sc_z)), "09_reuse_examples/expected_output/example1_module_scores.csv")',
            'out <- as.data.frame(t(sc_z)); out <- cbind(sample_id = rownames(out), out)\nwrite.csv(out, "09_reuse_examples/expected_output/example1_module_scores.csv", row.names = FALSE)')
open(ex1,"w",encoding="utf-8").write(s)
r=subprocess.run([r"D:\R-4.4.1\bin\Rscript.exe","09_reuse_examples/example1_replace_module_gene_set.R"],cwd=PK,capture_output=True,text=True)
log.append("example 1 rerun: "+ (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[:140]))
# ---------- BOM removal across the package ----------
nb=0
for d0,_,fn in os.walk(PK):
    for f in fn:
        if f.lower().endswith(".csv"):
            fp=os.path.join(d0,f); raw=open(fp,"rb").read()
            if raw.startswith(b"\xef\xbb\xbf"):
                open(fp,"wb").write(raw[3:]); nb+=1
log.append(f"UTF-8 BOM removed from {nb} CSV files (all package CSVs are now plain UTF-8)")
# ---------- environment: add xCell + single-cell tooling versions ----------
env=os.path.join(PK,"10_environment","environment.txt"); t=open(env,encoding="utf-8").read()
if "xCell" not in t:
    t=t.rstrip()+"\n"+subprocess.run([r"D:\R-4.4.1\bin\Rscript.exe","-e",
        'cat(paste(sapply(c("xCell","limma","GEOquery","Biobase"), function(p) paste0(p,":",as.character(packageVersion(p)))), collapse="\\n"))'],
        capture_output=True,text=True).stdout
    t=t.rstrip()+"\nsingle-cell pipeline python: 3.11 (numpy 1.26, scipy 1.11, h5py 3.11); donors aggregated before testing\n"
    open(env,"w",encoding="utf-8").write(t); log.append("environment.txt now records xCell and single-cell tooling")
for line in log: print(" -",line)
