#!/usr/bin/env python3
"""Fetch TCGA (GDC) molecular context for v3 cancers (PAAD, LIHC/HCC, ESCA/ESCC)
with the EXTENDED atlas gene list (17 modules + TP53). No pandas needed."""
import csv, hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data_raw" / "cbio_v3"
RESULTS = ROOT / "results"
LOGS = ROOT / "logs"
for directory in (RAW, RESULTS, LOGS):
    directory.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.cbioportal.org/api"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
RETRIEVED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
manifest: list[dict] = []; raw_files: list[dict] = []; failures: list[dict] = []

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_json(path: Path, payload: Any):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    raw_files.append({"file": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})

def api(method: str, path: str, *, params=None, json_body=None, raw_name: str) -> Any:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    started = time.time(); error = None; status = None; payload = None
    for attempt in range(1, 4):
        try:
            r = requests.request(method, url, params=params, json=json_body,
                                 headers={**HEADERS, "User-Agent": "EGFR-atlas-v3/1.0"},
                                 timeout=(30, 300))
            status = r.status_code; r.raise_for_status(); payload = r.json(); error = None; break
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"; time.sleep(attempt * 2)
    manifest.append({"source":"cBioPortal","method":method,"url":url,"params":params or {},
                     "retrieved_at_utc":RETRIEVED_AT,"status_code":status,
                     "ok": error is None,"elapsed_seconds": round(time.time()-started,3),
                     "record_count": len(payload) if isinstance(payload, list) else None, "error": error})
    if error is not None:
        failures.append({"stage": raw_name, "error": error, "url": url}); raise RuntimeError(error)
    write_json(RAW / raw_name, payload)
    return payload

def write_csv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

# gene list from atlas extended config + TP53
genes = []
with (ROOT / "config/gene_sets_extended.csv").open(encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        if row["gene"].upper() not in genes:
            genes.append(row["gene"].upper())
for extra in ("TP53",):
    if extra not in genes: genes.append(extra)

CONTEXTS = {
    "LUAD": {"study_id": "luad_tcga_gdc"},
    "CRC":  {"study_id": "coadread_tcga_pan_can_atlas_2018"},
    "STAD": {"study_id": "stad_tcga_gdc"},
    "PAAD": {"study_id": "paad_tcga_gdc"},
    "HCC":  {"study_id": "lihc_tcga_pan_can_atlas_2018"},
    "ESCC": {"study_id": "esca_tcga_gdc"},
}

def resolve_genes() -> dict:
    resolved, rows = {}, []
    for gene in genes:
        recs = api("GET", "genes", params={"keyword": gene, "pageSize": 20}, raw_name=f"gene_lookup_{gene}.json")
        exact = [r for r in recs if r.get("hugoGeneSymbol") == gene]
        if len(exact) != 1 or exact[0].get("entrezGeneId") is None:
            raise RuntimeError(f"gene resolve failed: {gene}")
        resolved[gene] = int(exact[0]["entrezGeneId"])
        rows.append({"gene": gene, "entrez_gene_id": resolved[gene]})
    write_csv(RESULTS / "cbio_v3_gene_id_map.csv", ["gene","entrez_gene_id"], rows)
    return resolved

def flatten(kind, records, context):
    if kind == "expression":
        return [{"context": context, "sample_id": r.get("sampleId"), "patient_id": r.get("patientId"),
                 "gene": genes_entrez_rev.get(int(r.get("entrezGeneId"))) if r.get("entrezGeneId") else r.get("entrezGeneId"),
                 "entrez_gene_id": r.get("entrezGeneId"), "value": r.get("value")} for r in records]
    if kind == "cna":
        return [{"context": context, "sample_id": r.get("sampleId"), "patient_id": r.get("patientId"),
                 "gene": genes_entrez_rev.get(int(r.get("entrezGeneId"))) if r.get("entrezGeneId") else r.get("entrezGeneId"),
                 "value": r.get("value")} for r in records]
    return [{"context": context, "sample_id": r.get("sampleId"), "patient_id": r.get("patientId"),
             "gene": r.get("gene", {}).get("hugoGeneSymbol") if isinstance(r.get("gene"), dict) else r.get("entrezGeneId"),
             "protein_change": r.get("proteinChange"), "mutation_type": r.get("mutationType"),
             "oncogenic": r.get("oncogenic")} for r in records]

def flatten_clin(records, context):
    out = []
    for r in records:
        attr = r.get("clinicalAttribute") or {}
        out.append({"context": context, "patient_id": r.get("patientId"), "sample_id": r.get("sampleId"),
                    "clinical_attribute_id": r.get("clinicalAttributeId"), "display_name": attr.get("displayName"),
                    "datatype": attr.get("datatype"), "value": r.get("value")})
    return out

def main() -> int:
    global genes_entrez, genes_entrez_rev
    gene_ids = resolve_genes()
    genes_entrez_rev = {v: k for k, v in gene_ids.items()}
    entrez_ids = list(gene_ids.values())
    all_rows = {"expression": [], "cna": [], "mut": [], "clin_p": [], "clin_s": []}
    summary = []
    for context, cfg in CONTEXTS.items():
        study_id = cfg["study_id"]
        print(f"[cBio] {context}: {study_id}")
        try:
            study = api("GET", f"studies/{study_id}", raw_name=f"{context}_study.json")
            profiles = api("GET", f"studies/{study_id}/molecular-profiles", params={"projection":"SUMMARY","pageSize":100},
                           raw_name=f"{context}_molecular_profiles.json")
            exp_prof = next((p for p in profiles if p.get("molecularProfileId","").endswith("_mrna_seq_tpm")), None)
            if exp_prof is None:
                exp_prof = next((p for p in profiles if p.get("molecularProfileId","").endswith("_rna_seq_v2_mrna")), None)
            cna_prof = next((p for p in profiles if p.get("molecularProfileId","").endswith("_gistic") and p.get("molecularAlterationType") == "COPY_NUMBER_ALTERATION"), None)
            if cna_prof is None:
                cna_prof = next((p for p in profiles if p.get("molecularProfileId","").endswith("_cna") and p.get("molecularAlterationType") == "COPY_NUMBER_ALTERATION"), None)
            mut_prof = next((p for p in profiles if p.get("molecularProfileId","").endswith("_mutations")), None)
            lists = api("GET", f"studies/{study_id}/sample-lists", raw_name=f"{context}_sample_lists.json")
            def slist(profile_id, fallbacks):
                prefix = study_id + "_"
                for fb in fallbacks:
                    hit = next((x["sampleListId"] for x in lists if x["sampleListId"] == prefix + fb), None)
                    if hit: return hit
                # generic: any list whose id starts with study and ends with fallback
                for fb in fallbacks:
                    hit = next((x["sampleListId"] for x in lists if x["sampleListId"].endswith(fb)), None)
                    if hit: return hit
                return None
            exp_suffix = "_tpm" if (exp_prof and exp_prof.get("molecularProfileId","").endswith("_mrna_seq_tpm")) else "_rna_seq_v2_mrna"
            exp_list = slist(exp_prof, [exp_suffix]) if exp_prof else None
            cna_list = slist(cna_prof, ["_cna", "_gistic"]) if cna_prof else None
            mut_list = slist(mut_prof, ["_sequenced"]) if mut_prof else None
            if exp_prof and exp_list:
                rec = api("POST", f"molecular-profiles/{exp_prof['molecularProfileId']}/molecular-data/fetch",
                          params={"pageSize":100000}, json_body={"sampleListId": exp_list, "entrezGeneIds": entrez_ids},
                          raw_name=f"{context}_expression_raw.json")
                all_rows["expression"].extend(flatten("expression", rec, context))
            if cna_prof and cna_list:
                rec = api("POST", f"molecular-profiles/{cna_prof['molecularProfileId']}/molecular-data/fetch",
                          params={"pageSize":100000}, json_body={"sampleListId": cna_list, "entrezGeneIds": entrez_ids},
                          raw_name=f"{context}_cna_raw.json")
                all_rows["cna"].extend(flatten("cna", rec, context))
            if mut_prof and mut_list:
                rec = api("POST", f"molecular-profiles/{mut_prof['molecularProfileId']}/mutations/fetch",
                          params={"projection":"DETAILED","pageSize":100000},
                          json_body={"sampleListId": mut_list, "entrezGeneIds": entrez_ids},
                          raw_name=f"{context}_mutations_raw.json")
                all_rows["mut"].extend(flatten("mut", rec, context))
            clin_p = api("GET", f"studies/{study_id}/clinical-data", params={"clinicalDataType":"PATIENT","projection":"DETAILED","pageSize":100000},
                         raw_name=f"{context}_clinical_patient_raw.json")
            clin_s = api("GET", f"studies/{study_id}/clinical-data", params={"clinicalDataType":"SAMPLE","projection":"DETAILED","pageSize":100000},
                         raw_name=f"{context}_clinical_sample_raw.json")
            all_rows["clin_p"].extend(flatten_clin(clin_p, context))
            all_rows["clin_s"].extend(flatten_clin(clin_s, context))
            summary.append({"context": context, "study_id": study_id, "study_name": study.get("name"),
                            "expression_profile": exp_prof.get("molecularProfileId") if exp_prof else None,
                            "cna_profile": cna_prof.get("molecularProfileId") if cna_prof else None,
                            "mutation_profile": mut_prof.get("molecularProfileId") if mut_prof else None,
                            "status": "complete"})
        except Exception as exc:
            print(f"[ERR] {context}: {exc}", file=sys.stderr)
            summary.append({"context": context, "study_id": study_id, "status": "failed", "error": str(exc)})
    write_csv(RESULTS / "cbio_v3_expression_gene_sample.csv",
              ["context","sample_id","patient_id","gene","entrez_gene_id","value"], all_rows["expression"])
    write_csv(RESULTS / "cbio_v3_cna_gene_sample.csv",
              ["context","sample_id","patient_id","gene","value"], all_rows["cna"])
    write_csv(RESULTS / "cbio_v3_mutations.csv",
              ["context","sample_id","patient_id","gene","protein_change","mutation_type","oncogenic"], all_rows["mut"])
    write_csv(RESULTS / "cbio_v3_clinical_patient.csv",
              ["context","patient_id","sample_id","clinical_attribute_id","display_name","datatype","value"], all_rows["clin_p"])
    write_csv(RESULTS / "cbio_v3_study_summary.csv",
              ["context","study_id","study_name","expression_profile","cna_profile","mutation_profile","status","error"], summary)
    write_json(RAW / "cbio_v3_request_manifest.json", {"retrieved_at_utc": RETRIEVED_AT, "requests": manifest, "failures": failures})
    write_json(RAW / "cbio_v3_file_manifest.json", {"retrieved_at_utc": RETRIEVED_AT, "files": raw_files})
    print("expression rows:", len(all_rows["expression"]), "cna:", len(all_rows["cna"]),
          "mut:", len(all_rows["mut"]), "clin_p:", len(all_rows["clin_p"]), "failures:", len(failures))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
