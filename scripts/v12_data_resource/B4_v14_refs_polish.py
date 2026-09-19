#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (B4): final reference polish (safe version).

* initials rendered as "Surname, A. B." (no stray comma between initials)
* the cBioPortal entry no longer points at the correction notice
* the metafor entry is rebuilt from Crossref (markup and line breaks removed)
* line-break collapsing is applied ONLY inside the reference block
"""
import json, os, re, subprocess
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
def crossref_doi(doi):
    r=subprocess.run(["curl","-sS","--max-time","45","-A","egfr-build/1.0 (mailto:liuaiqun_2004@163.com)",
                      f"https://api.crossref.org/works/{doi}"],capture_output=True,text=True)
    try: return json.loads(r.stdout)["message"]
    except Exception: return None
head,_,rest=md.partition("**References**")
nxt=re.search(r"\n\*\*",rest); tail=rest[nxt.start():] if nxt else "\n"; body=rest[:nxt.start()] if nxt else rest
body=re.sub(r"</?(i|b|sub|sup)>","",body)
chunks=re.split(r"\n(?=\d+\.\s)", body.strip())
entries=[]
for ch in chunks:
    m=re.match(r"^(\d+)\.\s+(.*)$", ch, re.S)
    if m: entries.append((m.group(1), re.sub(r"\s+"," ",m.group(2)).strip()))
if len(entries)<40:                     # safety guard: never overwrite the block with an empty list
    raise SystemExit(f"ABORT: parsed only {len(entries)} reference entries - refusing to rewrite the block")
def fix_initials(t):
    m=re.match(r"^([^\W\d_][\w'\-äöüéèçñáíóúÄÖÜ]+), ((?:[A-Z]\.,?\s*)+)(.*)$", t, re.UNICODE)
    if not m: return t
    sur, inis, restt = m.groups()
    letters=re.findall(r"[A-Z]", inis)
    if not letters: return t
    return f"{sur}, " + " ".join(c+"." for c in letters) + " " + restt.lstrip()
out=[]; notes=[]
for n,t in entries:
    t=fix_initials(t)
    if "bio Cancer Genomics Portal" in t or "bio cancer genomics portal" in t:
        t=("Cerami, E. et al. The cBio Cancer Genomics Portal: An Open Platform for Exploring Multidimensional Cancer "
           "Genomics Data. *Cancer Discov.* **2**, 401-404 (2012). https://doi.org/10.1158/2159-8290.CD-12-0095.")
        notes.append(f"{n}: cBioPortal entry replaced with the primary paper")
    elif "Conducting Meta-Analyses" in t:
        m=crossref_doi("10.18637/jss.v036.i03")
        if m and any("metafor" in (x or "").lower() for x in (m.get("title") or [])):
            au=m.get("author") or []
            a1=f"{au[0].get('family','Viechtbauer')}, {au[0].get('given','W')[0]}." if au else "Viechtbauer, W."
            yr=(m.get("published-print") or m.get("issued") or {}).get("date-parts",[["2010"]])[0][0]
            t=(f"{a1} et al. {m['title'][0].rstrip('.')}. *J. Stat. Softw.* **{m.get('volume','36')}**, "
               f"{m.get('page','1-48')} ({yr}). https://doi.org/{m.get('DOI')}.")
        else:
            t=("Viechtbauer, W. et al. Conducting meta-analyses in R with the metafor package. *J. Stat. Softw.* "
               "**36**, 1-48 (2010). https://doi.org/10.18637/jss.v036.i03.")
        notes.append(f"{n}: metafor entry normalised")
    out.append((n,t))
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in out)+"\n\n"
md=head+block+tail.lstrip("\n")
open(mdp,"w",encoding="utf-8",newline="\n").write(md)
print("notes:", "; ".join(notes) or "none")
print("entries:",len(out),"| with link:",sum(1 for n,t in out if "https://" in t),
      "| with markup:",sum(1 for n,t in out if re.search(r"</?(i|b|sub|sup)>",t)),
      "| with 'Correction':",sum(1 for n,t in out if "Correction" in t))
print("no-link entries:", [n for n,t in out if "https://" not in t] or "none")
for n,t in out[:2]+out[26:28]+out[36:38]+out[45:47]: print(f"  {n}. {t[:148]}")
