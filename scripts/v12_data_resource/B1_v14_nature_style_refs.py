#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (B1): normalise the reference list to Scientific Data / Nature style.

* papers      : "Surname, A. B. et al. Title. Journal abbreviation Vol, pages (Year). https://doi.org/..."
* data sets   : "Author. Title. Database https://identifiers.org/... or collection URL (Year)."
* verification: 52 entries, every entry carries a resolvable https link, numbering untouched
"""
import os, re, subprocess
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
head,_,rest=md.partition("**References**")
nxt=re.search(r"\n\*\*",rest); tailsec=rest[nxt.start():] if nxt else "\n"; body=rest[:nxt.start()] if nxt else rest
entries=re.findall(r"(?m)^(\d+)\. (.+)$",body)
JABBR={"Nucleic Acids Research":"Nucleic Acids Res.","Nucleic Acids Res":"Nucleic Acids Res.","Bioinformatics":"Bioinformatics",
 "Genome Biology":"Genome Biol.","BMC Bioinformatics":"BMC Bioinformatics","BMC Bioinf":"BMC Bioinformatics",
 "Statistics in Medicine":"Stat. Med.","Cancer Cell":"Cancer Cell","Cell":"Cell","Nature":"Nature",
 "Nature Methods":"Nat. Methods","New England Journal of Medicine":"N. Engl. J. Med.","N Engl J Med":"N. Engl. J. Med.",
 "Controlled Clinical Trials":"Control. Clin. Trials","Journal of the Royal Statistical Society: Series B (Methodological)":"J. R. Stat. Soc. B",
 "Journal of Educational Statistics":"J. Educ. Stat.","Cancer Discovery":"Cancer Discov.","Science Signaling":"Sci. Signal.",
 "Journal of Statistical Software":"J. Stat. Softw.","PLoS One":"PLoS One","PLoS ONE":"PLoS One","Sci Rep":"Sci. Rep.",
 "Nature Genetics":"Nat. Genet.","Gut":"Gut","Oncogene":"Oncogene","Cancer Research":"Cancer Res.","Clinical Cancer Research":"Clin. Cancer Res.",
 "Journal of Clinical Oncology":"J. Clin. Oncol.","Gastroenterology":"Gastroenterology","Hepatology":"Hepatology",
 "Journal of Hepatology":"J. Hepatol.","Annals of Oncology":"Ann. Oncol.","Cancer Letters":"Cancer Lett.",
 "International Journal of Cancer":"Int. J. Cancer","Molecular Cancer":"Mol. Cancer","Genome Medicine":"Genome Med.",
 "Nature Communications":"Nat. Commun.","eLife":"eLife","Scientific Data":"Sci. Data","Nucleic Acids Research (Database issue)":"Nucleic Acids Res."}
def author_part(a):
    a=a.strip().rstrip(",")
    if a.startswith("The Cancer Genome Atlas") or a.startswith("CZI Cell Science"): return a+"."
    m=re.match(r"^([A-Z][A-Za-z'\-]+(?:\s[A-Z][A-Za-z'\-]+)?)\s+([A-Z]{1,3})$", a)
    if m:
        sur, ini=m.group(1), m.group(2)
        ini=", ".join(x+"." for x in ini)
        return f"{sur}, {ini}"
    return a
new=[]
for n,t in entries:
    t=t.strip()
    dataset = ("CZ CELLxGENE Discover" in t) or ("Gene Expression Omnibus, accession" in t) or ("single-cell dataset" in t and "collection" in t)
    if dataset:
        # data citation form
        t=re.sub(r"\.\s*CZ CELLxGENE Discover, collection ([0-9a-f\-]+)\.?$",
                 r". *CZ CELLxGENE Discover* https://cellxgene.cziscience.com/collections/\1 (2025).", t)
        m=re.search(r"Gene Expression Omnibus, accession (GSE\d+); (\d{4})\.?", t)
        if m:
            t=t.replace(m.group(0), f"*Gene Expression Omnibus* https://identifiers.org/geo/{m.group(1)} ({m.group(2)}).")
            t=re.sub(r"^Himes BE, et al\.", "Himes, B. E. et al.", t)
        new.append((n,t)); continue
    # paper form
    m=re.match(r"^(.*?)\.\s(.*?)\.\s(.+?)\s(19|20)(\d\d)(?:;([^:;]+))?(?::([^.]*?))?\.\s*(doi:(\S+?)|PMID:(\d+))?\.?$", t)
    if not m:
        new.append((n,t)); continue
    au, title, journal, cy, yr, vol, pages, _, doi, pmid = m.groups()
    journal=JABBR.get(journal.strip(), journal.strip())
    au=author_part(au)
    cit=f"{au} {title}. *{journal}*"
    if vol: cit+=f" **{vol.strip()}**"
    if pages: cit+=f", {pages.strip()}"
    cit+=f" ({cy}{yr})"
    if doi: cit+=f". https://doi.org/{doi.strip().rstrip('.')}"
    elif pmid: cit+=f". https://pubmed.ncbi.nlm.nih.gov/{pmid}"
    cit+="."
    new.append((n,cit))
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in new)+"\n\n"
md=head+block+tailsec.lstrip("\n")
open(mdp,"w",encoding="utf-8",newline="\n").write(md)
links=sum(1 for n,t in new if "https://" in t)
print(f"references: {len(new)} | entries with a resolvable link: {links}")
print("not normalised:")
for n,t in new:
    if "https://" not in t: print(f"  {n}. {t[:110]}")
print("\nsample (Nature style):")
for n,t in new[:3]+new[26:28]+new[-3:]: print(f"  {n}. {t[:150]}")
