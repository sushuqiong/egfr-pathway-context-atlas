#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (B2): rebuild every reference entry from its structured metadata in Scientific Data / Nature style.

Each existing entry is matched back to a metadata record by longest title containment; the entry is then
re-rendered from the record's fields. Data sets are rendered as data citations with a resolvable link.
"""
import json, os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
pool=[]
for k,m in meta["crossref"].items(): pool.append((m.get("title",""),m,"tool"))
for pm,s in meta["summaries"].items(): pool.append((s.get("title",""),s,"cohort"))
def norm(x): return re.sub(r"[^a-z0-9 ]"," ",x.lower())
def au_nature(a, many):
    a=(a or "").strip().rstrip(".")
    if a.startswith("The Cancer Genome Atlas"): return "The Cancer Genome Atlas Research Network."
    if a.startswith("CZI Cell Science"): return "CZI Cell Science Program."
    if a.startswith("R Core"): return "R Core Team."
    m=re.match(r"^([A-Z][A-Za-z'\-]+)\s+([A-Z]{1,3})$", a)
    if m:
        sur, ini=m.groups(); ini=", ".join(c+"." for c in ini)
        return f"{sur}, {ini}" + (" et al." if many else "")
    return (a+"." if not a.endswith(".") else a) + (" et al." if many else "")
JABBR={"Nucleic Acids Research":"Nucleic Acids Res.","Bioinformatics":"Bioinformatics","Genome Biology":"Genome Biol.",
 "BMC Bioinformatics":"BMC Bioinformatics","Statistics in Medicine":"Stat. Med.","Cancer Cell":"Cancer Cell","Cell":"Cell",
 "Nature":"Nature","Nature Methods":"Nat. Methods","New England Journal of Medicine":"N. Engl. J. Med.",
 "Controlled Clinical Trials":"Control. Clin. Trials","Journal of the Royal Statistical Society: Series B (Methodological)":"J. R. Stat. Soc. B",
 "Journal of Educational Statistics":"J. Educ. Stat.","Cancer Discovery":"Cancer Discov.","Science Signaling":"Sci. Signal.",
 "Journal of Statistical Software":"J. Stat. Softw.","PLoS One":"PLoS One","Cancer Research":"Cancer Res.",
 "Clinical Cancer Research":"Clin. Cancer Res.","Journal of Clinical Oncology":"J. Clin. Oncol.","Gut":"Gut",
 "Annals of Oncology":"Ann. Oncol.","International Journal of Cancer":"Int. J. Cancer","Genome Medicine":"Genome Med.",
 "Nature Communications":"Nat. Commun.","Scientific Data":"Sci. Data","Oncogene":"Oncogene","Hepatology":"Hepatology"}
head,_,rest=md.partition("**References**")
nxt=re.search(r"\n\*\*",rest); tailsec=rest[nxt.start():] if nxt else "\n"; body=rest[:nxt.start()] if nxt else rest
entries=re.findall(r"(?m)^(\d+)\. (.+)$",body)
out=[]; unmatched=[]; matched=0
for n,t in entries:
    if "CZ CELLxGENE Discover" in t and "collection" in t:
        m=re.search(r"collection ([0-9a-f\-]+)",t); label=t.split(". ")[0]
        out.append((n, f"CZI Cell Science Program. {label}. *CZ CELLxGENE Discover* "
                       f"https://cellxgene.cziscience.com/collections/{m.group(1)} (2025)." if m else t)); continue
    if "Gene Expression Omnibus, accession" in t or "GSE193816" in t:
        m=re.search(r"(GSE\d+)",t)
        out.append((n, f"Himes, B. E. et al. RNA-seq transcriptome profiling of airway epithelial cells from subjects with asthma. "
                       f"*Gene Expression Omnibus* https://identifiers.org/geo/{m.group(1)} (2022)." if m else t)); continue
    if t.startswith("R Core Team"):
        out.append((n,"R Core Team. R: a language and environment for statistical computing, version 4.4.1. "
                      "*R Foundation for Statistical Computing* https://www.R-project.org (2024).")); continue
    ntl=norm(t); best=None; bestlen=0
    for title,rec,kind in pool:
        tl=norm(title)
        if len(tl)>25 and tl in ntl and len(tl)>bestlen: best=rec; bestlen=len(tl); bestkind=kind
    if not best:
        unmatched.append((n,t)); out.append((n,t)); continue
    matched+=1
    many=(best.get("n_authors") or 0)>1
    au=au_nature(best.get("first_author",""), many)
    title=best["title"].rstrip(".")
    journal=JABBR.get(best.get("journal","").strip(), best.get("journal","").strip())
    cit=f"{au} {title}. *{journal}*" if journal else f"{au} {title}."
    if best.get("volume"): cit+=f" **{best['volume'].strip()}**"
    if best.get("pages"): cit+=f", {best['pages'].strip()}"
    if best.get("year"): cit+=f" ({best['year']})"
    if best.get("doi"): cit+=f". https://doi.org/{best['doi']}"
    elif best.get("pmid"): cit+=f". https://pubmed.ncbi.nlm.nih.gov/{best['pmid']}"
    cit+="."
    out.append((n,cit))
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in out)+"\n\n"
md=head+block+tailsec.lstrip("\n"); open(mdp,"w",encoding="utf-8",newline="\n").write(md)
print(f"entries: {len(out)} | rebuilt from metadata: {matched} | data citations/software: {len(out)-matched-len(unmatched)} | unmatched: {len(unmatched)}")
for n,t in unmatched: print(f"  unmatched {n}: {t[:110]}")
print("\nsample:")
for n,t in out[:3]+out[35:38]+out[-3:]: print(f"  {n}. {t[:155]}")
print("\nwith resolvable link:", sum(1 for n,t in out if "https://" in t), "/", len(out))
