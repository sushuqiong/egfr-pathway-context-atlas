#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (B3): fix the three references that could not be matched automatically, and normalise author
rendering for names containing diacritics."""
import json, os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
cr=meta["crossref"]; summ=meta["summaries"]
def au(a, many=True):
    a=(a or "").strip().rstrip(".")
    if a.startswith("The Cancer Genome Atlas"): return "The Cancer Genome Atlas Research Network."
    m=re.match(r"^([^\W\d_][\w'\-äöüéèçñáíóúÄÖÜ]+)\s+([A-Z]{1,3})$", a, re.UNICODE)
    if m:
        sur,ini=m.groups(); ini=", ".join(c+"." for c in ini)
        return f"{sur}, {ini}" + (" et al." if many else "")
    return a+"."+(" et al." if many else "")
def cite(title, journal, year, vol="", pages="", doi="", pmid="", author="", many=True, jab=""):
    c=f"{au(author,many)} {title.rstrip('.')}. *{jab or journal}*"
    if vol: c+=f" **{vol}**"
    if pages: c+=f", {pages}"
    if year: c+=f" ({year})"
    if doi: c+=f". https://doi.org/{doi}"
    elif pmid: c+=f". https://pubmed.ncbi.nlm.nih.gov/{pmid}"
    return c+"."
fixes={}
ch=[s for s in summ.values() if s["first_author"].startswith("Christenson")]
if ch:
    s=ch[0]
    fixes["Christenson"]=cite(s["title"],s["journal"],s["year"],s["volume"],s["pages"],s["doi"],pmid=s.get("pmid",""),author=s["first_author"],many=s["n_authors"]>1)
m=cr.get("cbio1") or {}
fixes["cBio cancer genomics portal"]=cite(m.get("title","The cBio Cancer Genomics Portal: An Open Platform for Exploring Multidimensional Cancer Genomics Data"),
    m.get("journal","Cancer Discov"),m.get("year","2012"),m.get("volume","2"),m.get("pages","401-404"),
    m.get("doi","10.1158/2159-8290.CD-12-0095"),author="Cerami E")
mf=cr.get("metafor") or {}
fixes["Conducting Meta-Analyses"]=cite(mf.get("title","Conducting Meta-Analyses in R with the metafor Package"),
    mf.get("journal","J. Stat. Softw."),mf.get("year","2010"),mf.get("volume","36"),mf.get("pages","1-48"),mf.get("doi",""),author="Viechtbauer W")
head,_,rest=md.partition("**References**")
nxt=re.search(r"\n\*\*",rest); tail=rest[nxt.start():] if nxt else "\n"; body=rest[:nxt.start()] if nxt else rest
entries=re.findall(r"(?m)^(\d+)\. (.+)$",body)
out=[]; fixed=[]
for n,t in entries:
    hit=None
    for key,c in fixes.items():
        if key.lower() in t.lower(): hit=c; break
    # also normalise any author pattern "Surname X. et al." produced with the earlier ASCII-only rule
    if not hit:
        t=re.sub(r"^([^\W\d_][\w'\-äöüéèçñáíóúÄÖÜ]+) ([A-Z]{1,3})\. et al\.", lambda m: au(m.group(1)+" "+m.group(2)), t)
        t=re.sub(r"^([^\W\d_][\w'\-äöüéèçñáíóúÄÖÜ]+) ([A-Z]{1,3})\. ", lambda m: au(m.group(1)+" "+m.group(2), many=False)+" ", t)
    out.append((n, hit if hit else t))
    if hit: fixed.append(n)
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in out)+"\n\n"
md=head+block+tail.lstrip("\n"); open(mdp,"w",encoding="utf-8",newline="\n").write(md)
print("entries:",len(out),"| directly fixed:",fixed,"| with link:",sum(1 for n,t in out if "https://" in t))
for n,t in out:
    if "https://" not in t: print("  no link:",n,t[:100])
print("\nsample of the fixed entries and author normalisation:")
for n,t in out[26:28]+out[36:38]+out[45:47]+out[50:52]: print(f"  {n}. {t[:150]}")
