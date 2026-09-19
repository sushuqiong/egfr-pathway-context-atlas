#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: resolve the landmark references by exact title against Crossref, accepting only a high-similarity match."""
import difflib, json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
def crossref_title(title, rows=5):
    url="https://api.crossref.org/works?rows=%d&query.bibliographic=%s" % (rows, urllib.parse.quote(title))
    r=subprocess.run(["curl","-sS","--max-time","45","-A","egfr-resource-build/1.0 (mailto:liuaiqun_2004@163.com)",url],
                     capture_output=True,text=True)
    try: return json.loads(r.stdout)["message"]["items"]
    except Exception: return []
def pick(title, minratio=0.85):
    best=None; bestr=0; cands=[]
    for it in crossref_title(title):
        t=(it.get("title") or [""])[0]
        r=difflib.SequenceMatcher(None, t.lower(), title.lower()).ratio()
        cands.append((round(r,3), t[:70], (it.get("container-title") or [""])[0]))
        if r>bestr: bestr=r; best=it
    if best and bestr>=minratio:
        auth=best.get("author") or []
        first=(" ".join(x for x in [auth[0].get("family",""), (auth[0].get("given","") or " ")[:1]+"."] if x)).strip() if auth else "Unknown"
        yr=""
        for k in ("published-print","published-online","issued"):
            if best.get(k,{}).get("date-parts"): yr=str(best[k]["date-parts"][0][0]); break
        return dict(first_author=first,n_authors=len(auth),title=(best.get("title") or [""])[0].strip().rstrip("."),
                    journal=(best.get("container-title") or [""])[0],year=yr,volume=best.get("volume",""),
                    pages=best.get("page",""),doi=best.get("DOI","")), round(bestr,3), cands[:3]
    return None, round(bestr,3), cands[:3]
EXACT={
 "tcga_luad": "Comprehensive molecular profiling of lung adenocarcinoma",
 "tcga_crc":  "Comprehensive molecular characterization of human colon and rectal cancer",
 "tcga_stad": "Comprehensive molecular characterization of gastric adenocarcinoma",
 "tcga_paad": "Integrated genomic characterization of pancreatic ductal adenocarcinoma",
 "tcga_lihc": "Comprehensive and integrative genomic characterization of hepatocellular carcinoma",
 "tcga_esca": "Integrated genomic characterization of oesophageal carcinoma",
 "scipy":     "SciPy 1.0: fundamental algorithms for scientific computing in Python",
 "gdc":       "Toward a shared vision for cancer genomic data",
 "dl1986":    "Meta-analysis in clinical trials",
 "kh2003":    "Improved tests for a random effects meta-regression with a single covariate",
}
# dl1986 and kh2003 need an extra guard: the 1986 original (Control Clin Trials) and Stat Med 2003
GUARD={"dl1986":("controlled clinical trials","1986"),"kh2003":("statistics in medicine","2003"),
       "tcga_lihc":("cell","2017"),"tcga_paad":("cancer cell","2017"),"tcga_esca":("nature","2017"),
       "scipy":("nature methods","2020"),"gdc":("new england","2016")}
merged=meta.get("crossref",{}); added=[]
for key,title in EXACT.items():
    got,score,cands=pick(title)
    if got and key in GUARD:
        j,yr=GUARD[key]
        if j not in (got["journal"] or "").lower() or got["year"]!=yr:
            print(f"  {key:10s} rejected (journal/year mismatch: {got['journal']} {got['year']})")
            got=None
    if got:
        merged[key]=got; added.append(key)
        print(f"  {key:10s} OK  {score}  {got['first_author']} {got['year']} {got['journal'][:26]}")
    else:
        print(f"  {key:10s} unresolved (best={score}) candidates={cands}")
    time.sleep(0.3)
meta["crossref"]=merged
json.dump(meta, open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
print("\nadded:",len(added),"| total validated:",len(merged),"| keys:", sorted(merged))
