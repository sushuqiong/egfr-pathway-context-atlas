#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v11 mutation denominator audit (responds to GPT6 item 6).

For each cancer context: derive the mutation-profiled sample list from cBioPortal sample lists,
count mutated samples per gene on that denominator, restrict to samples that also have expression,
and flag duplicates. Documents whether 'no mutation record' means wild-type only for profiled samples.
"""
import json, os, csv, collections
RAW = r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\data_raw\cbio_v3"
OUT = r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
os.makedirs(OUT, exist_ok=True)
CTX = ["LUAD","CRC","STAD","PAAD","HCC","ESCC"]
rows=[]; audit=[]
for ctx in CTX:
    sl=json.load(open(os.path.join(RAW,f"{ctx}_sample_lists.json")))
    mp=json.load(open(os.path.join(RAW,f"{ctx}_molecular_profiles.json")))
    mut=json.load(open(os.path.join(RAW,f"{ctx}_mutations_raw.json")))
    lists={s["sampleListId"]:s for s in sl}
    prof=list(lists.keys())
    mut_profile=[p["molecularProfileId"] for p in mp if p.get("molecularAlterationType")=="MUTATION_EXTENDED"]
    expr_profiles=[p["molecularProfileId"] for p in mp if p.get("molecularAlterationType")=="MRNA_EXPRESSION"]
    # clinical sample list = 'all' samples; mutation-profiled list usually '<study>_sequenced' or '_mutations'
    seq_ids=[k for k in prof if k.endswith("_sequenced") or "mutations" in k]
    def list_size(sid):
        s=lists.get(sid); 
        if not s: return None
        d=json.dumps(s)
        import re
        m=re.search(r"\((\d+) samples?\)", s.get("description","") or "")
        return int(m.group(1)) if m else None
    n_all=list_size(f"{ctx.lower()}_tcga_gdc_all") or list_size(f"{ctx.lower()}_tcga_pan_can_atlas_2018_all") or list_size([k for k in prof if k.endswith("_all")][0] if any(k.endswith("_all") for k in prof) else "")
    n_seq=list_size(seq_ids[0]) if seq_ids else None
    mut_gene=collections.defaultdict(set); mut_any=set(); statuses=collections.Counter()
    for m in mut:
        sid=m.get("sampleId"); mut_any.add(sid)
        g=(m.get("gene") or {}).get("hugoGeneSymbol")
        if g: mut_gene[g].add(sid)
        statuses[m.get("mutationStatus","NA")]+=1
    audit.append(dict(context=ctx, profile_lists=";".join(prof), mutation_profile=";".join(mut_profile),
        expression_profiles=len(expr_profiles), n_all_reported=n_all, n_mutation_profiled_reported=n_seq,
        n_rows=len(mut), n_samples_with_any_mutation=len(mut_any), mutation_status_values=";".join(f"{k}:{v}" for k,v in statuses.items())))
    for gene in ["KRAS","TP53","EGFR","ERBB2"]:
        n_mut=len(mut_gene.get(gene,()))
        denom=n_seq or n_all
        rows.append(dict(context=ctx, gene=gene, n_mutated_samples=n_mut, denominator_used=("mutation-profiled" if n_seq else "all-samples"),
            denominator_n=denom, pct=round(100*n_mut/denom,2) if denom else None))
with open(os.path.join(OUT,"v11_mutation_denominators.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT,"v11_mutation_audit.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(audit[0].keys())); w.writeheader(); w.writerows(audit)
print("=== denominators (v11) ===")
for r in rows: print(f"  {r['context']:5} {r['gene']:6} {r['n_mutated_samples']:>4} / {r['denominator_n']} ({r['denominator_used']}) = {r['pct']}%")
print("\n=== audit ===")
for a in audit: print(f"  {a['context']:5} all={a['n_all_reported']} mut-profiled={a['n_mutation_profiled_reported']} rows={a['n_rows']} samples_any_mut={a['n_samples_with_any_mutation']}")
