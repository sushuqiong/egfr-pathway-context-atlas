#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: keep only hash lines in checksums_sha256.txt (so sha256sum -c runs without warnings) and
move the explanatory notes into checksums_README.md."""
import os, shutil, subprocess
PK=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14\dataset_package"
p=os.path.join(PK,"08_qc","checksums_sha256.txt")
lines=[l.rstrip("\r") for l in open(p,encoding="utf-8").read().split("\n") if l.strip() and not l.lstrip().startswith("#")]
open(p,"w",encoding="utf-8",newline="\n").write("\n".join(lines))
print("hash lines:",len(lines))
notes = (
 "# Integrity verification\n\n"
 "`checksums_sha256.txt` lists SHA-256 hashes for every file in this deposit, one line per file in the form\n"
 "hash + two spaces + relative path (forward slashes, LF line endings), so the standard command works from the package root:\n\n"
 "    sha256sum -c 08_qc/checksums_sha256.txt\n\n"
 "Notes\n"
 "- The two verification files (`checksums_sha256.txt` and `file_inventory_and_checksums.csv`) are self-referential: their hashes\n"
 "  were computed before they were finalised, so they are excluded from the check and are marked as self-references in the inventory.\n"
 "- This file contains hash lines only, so `sha256sum -c` produces no formatting warnings.\n"
 "- The `rows` column of `file_inventory_and_checksums.csv` counts data rows, excluding the header.\n"
)
open(os.path.join(PK,"08_qc","checksums_README.md"),"w",encoding="utf-8").write(notes)
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt",cwd=PK,shell=True,capture_output=True,text=True)
bad=[l for l in r.stdout.splitlines() if not l.endswith(": OK")]
print("non-OK lines:", bad if bad else "none")
print("stderr:", r.stderr.strip() or "none")
print("verified files:", sum(1 for l in r.stdout.splitlines() if l.endswith(": OK")))
z=r"C:\Users\fengq\Desktop\★Zenodo上传-就选这个_v14"
shutil.make_archive(z,"zip",PK)
print("zenodo zip MB:", round(os.path.getsize(z+".zip")/1e6,2))
