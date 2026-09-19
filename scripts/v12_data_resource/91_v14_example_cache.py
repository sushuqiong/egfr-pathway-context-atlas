#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: make the external reuse example robust - persistent download cache plus retries."""
import os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
old = "gse <- getGEO(ACC, GSEMatrix=TRUE, getGPL=TRUE, destdir=tempdir())"
new = """cache <- file.path(V14, "results", "external_cache"); dir.create(cache, showWarnings=FALSE, recursive=TRUE)
gse <- NULL
for (attempt in 1:4) {
  gse <- tryCatch(getGEO(ACC, GSEMatrix=TRUE, getGPL=TRUE, destdir=cache), error=function(e) { cat("download attempt", attempt, "failed:", conditionMessage(e), "\\n"); NULL })
  if (!is.null(gse)) break
  Sys.sleep(20)
}
if (is.null(gse)) stop("could not download ", ACC, " after four attempts (transient network failure)")"""
for rel in [os.path.join(V14,"scripts","76_v14_external_reuse_example.R"),
            os.path.join(V14,"dataset_package","09_reuse_examples","example3_external_cohort_rebuild.R")]:
    s=open(rel,encoding="utf-8").read()
    if old in s:
        s=s.replace(old,new); open(rel,"w",encoding="utf-8").write(s); print("cache+retry added to", os.path.basename(rel))
    else:
        print("anchor missing in", os.path.basename(rel))
