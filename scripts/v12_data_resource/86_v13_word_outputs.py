#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13: Tables_v13.docx (Table 1 + Supplementary S1-S9, booktabs three-line style) and Figure_legends_v13.docx."""
import csv, os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
OUT=os.path.join(V13,"03_tables"); os.makedirs(OUT,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def three_line(doc, headers, rows, font=8.5):
    t=doc.add_table(rows=1+len(rows), cols=len(headers)); t.style=doc.styles['Normal Table']; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    tp=t._tbl.tblPr
    for old in tp.findall(qn('w:tblBorders')): tp.remove(old)
    b=OxmlElement('w:tblBorders')
    for e in ('top','left','bottom','right','insideH','insideV'):
        el=OxmlElement(f'w:{e}'); el.set(qn('w:val'),'nil'); b.append(el)
    tp.append(b)
    def bd(cell, edges, sz=8):
        tcPr=cell._tc.get_or_add_tcPr()
        for old in tcPr.findall(qn('w:tcBorders')): tcPr.remove(old)
        tb=OxmlElement('w:tcBorders')
        for e in ('top','left','bottom','right','insideH','insideV'):
            el=OxmlElement(f'w:{e}')
            if e in edges: el.set(qn('w:val'),'single'); el.set(qn('w:sz'),str(sz)); el.set(qn('w:color'),'000000')
            else: el.set(qn('w:val'),'nil')
            tb.append(el)
        tcPr.append(tb)
    for j,h in enumerate(headers):
        c=t.cell(0,j); c.text=''; r=c.paragraphs[0].add_run(str(h)); r.bold=True; r.font.size=Pt(font); r.font.name='Times New Roman'
        bd(c,{'top','bottom'},12)
    for i,row in enumerate(rows,1):
        for j,v in enumerate(row):
            c=t.cell(i,j); c.text=''; r=c.paragraphs[0].add_run(str(v)); r.font.size=Pt(font); r.font.name='Times New Roman'
            if i==len(rows): bd(c,{'bottom'},12)
    doc.add_paragraph('')
def head(doc,text,level=1):
    h=doc.add_heading(level=level); r=h.add_run(text); r.font.name='Times New Roman'; r.font.color.rgb=RGBColor(0,0,0)
CTX={"GSE32863":"LUAD","GSE19804":"LUAD","GSE10072":"LUAD","GSE44076":"CRC","GSE41258":"CRC","GSE23878":"CRC",
     "GSE75214":"IBD","GSE87473":"IBD","GSE179285":"IBD","GSE16879":"IBD","GSE4302":"Asthma","GSE43696":"Asthma",
     "GSE67472":"Asthma","GSE27342":"STAD","GSE63089":"STAD","GSE13911":"STAD","GSE15471":"PAAD","GSE28735":"PAAD",
     "GSE62452":"PAAD","GSE57957":"HCC","GSE62232":"HCC","GSE23400":"ESCC","GSE20347":"ESCC","GSE76925":"COPD",
     "GSE47460":"COPD","GSE33814":"NAFLD","GSE66676":"NAFLD"}
order=["LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"]
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); cc=[r for r in reg if r["design"]=="case-control"]
agg={}
for r in cc:
    c=CTX.get(r["accession"],"other"); a=agg.setdefault(c,dict(cohorts=0,assays=0,pats=0,paired=0,plats=set(),nopid=0))
    a["cohorts"]+=1; a["assays"]+=int(r["n_assay_records"])
    a["pats"]+=int(r["n_unique_patients"]) if str(r["n_unique_patients"]).isdigit() else 0
    a["paired"]+=int(r["patients_with_both_arms"] or 0) if r["paired_design_used"]=="yes" else 0
    a["plats"].add(r["platform"]); a["nopid"]+=1 if r["patient_identity_available"]=="no" else 0
doc=Document(); st=doc.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(10)
head(doc,"Table 1. Cohort composition of the resource by disease context")
three_line(doc,["Context","Cohorts","Assay records","Patients (with identifiers)","Paired patients","Platforms","Cohorts without patient identifiers"],
           [[c,agg[c]["cohorts"],agg[c]["assays"],agg[c]["pats"],agg[c]["paired"],len(agg[c]["plats"]),agg[c]["nopid"]] for c in order if c in agg])
doc.add_paragraph("Case-control series only (26 cohorts; 2,711 assay records; 1,086 patients with identifiers; 9 cohorts provide no patient identifiers and are analysed unpaired). One treatment-response series (GSE16879, 43 samples) was reviewed and excluded: see Supplementary Table S4 for every exclusion and flag.")
head(doc,"Supplementary Table S1. Cohort registry with design, counts, origin publications and provenance")
s1=[[r["accession"],CTX.get(r["accession"],""),r["platform"],r["n_assay_records"],r["n_unique_patients"],r["n_case"],r["n_control"],
     r["patients_with_both_arms"],r["paired_design_used"],r["patient_identity_available"],r["design"],r["origin_pmid"]] for r in
     sorted(reg,key=lambda x:(order.index(CTX.get(x["accession"],"IBD")) if CTX.get(x["accession"],"IBD") in order else 99,x["accession"]))]
three_line(doc,["Accession","Context","Platform","Assays","Patients","Cases","Controls","Patients with both arms","Paired used","Patient IDs","Design","Origin PMID"],s1,7.5)
cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))
_cc={r["accession"] for r in cc}
cov=[r for r in cov if r["accession"] in _cc]           # case-control cohorts only (26), not the excluded series
mods={}
for r in cov:
    m=r["module"]; c=float(r["coverage"]); d=mods.setdefault(m,dict(members=r["n_members"],minc=1.0,n_inc=0))
    d["minc"]=min(d["minc"],c); d["n_inc"]+=1 if int(r["n_present"])<int(r["n_members"]) else 0
head(doc,"Supplementary Table S2. Module membership and cross-cohort gene coverage")
three_line(doc,["Module","Members","Minimum coverage","Case-control cohorts with incomplete coverage (of 26)"],[ [m,v["members"],f"{v['minc']:.2f}",v["n_inc"]] for m,v in sorted(mods.items(),key=lambda kv:kv[1]["minc"])])
sc_aud=rd(os.path.join(R,"v12_sc_dataset_audit.csv"))
head(doc,"Supplementary Table S3. Single-cell datasets, cells and comparison arms")
three_line(doc,["Dataset","Cells total","Cells used","Donors","Cell types","Arms","Notes"],
           [[r["context"],r["cells_total"],r["cells_used"],r["donors"],r["cell_types"],r["arms"],r["control_kinds"]] for r in sc_aud],8)
head(doc,"Supplementary Table S4. Documented exclusions, flags and design corrections")
three_line(doc,["Item","n","Layer","Reason"],[[r["item"],r["n"],r["layer"],r["reason"]] for r in rd(os.path.join(PK,"08_qc","exclusion_and_flag_log.csv"))],8)
head(doc,"Supplementary Table S5. Decision rules and thresholds applied in validation")
three_line(doc,["Rule","Definition / threshold"],[
 ["Effect size","SMDH (unpaired) or SMCRPH (paired, empirical within-pair correlation); shared denominator sqrt((sd_case^2+sd_control^2)/2); in paired cohorts only complete pairs enter the paired estimate"],
 ["Paired design","metadata-derived: at least four patients contributing both a case and a control sample"],
 ["Meta-analysis","REML with Hartung-Knapp; DerSimonian-Laird, ad hoc Knapp-Hartung, unpaired-only and fixed rho (0.5, 0.7) as sensitivity"],
 ["Composition adjustment","base model is primary; adjusted model adds the four compartment scores on identical samples and is reported as a sensitivity analysis"],
 ["Common-gene sensitivity","re-score with the members present in every cohort; flag when the effect direction disagrees with full-member scoring in >=20% of cohorts; not scorable when fewer than two members are shared; exactly two shared members is reported as low-information"],
 ["Proportional hazards","scaled Schoenfeld residuals (cox.zph) in the age-adjusted model; flagged at p<0.05 (0 of 17 features flagged)"],
 ["Single-cell design","donor-level means; >=3 donors per arm; paired signed-rank when >=5 complete pairs; unpaired only when arms are donor-disjoint; otherwise not testable"],
 ["Multiplicity","Benjamini-Hochberg within context x module x comparison-type families (single-cell) and within context families (meta-analysis)"],
 ["Exact vs rank reproduction","exact = absolute difference of zero in the recomputed statistic; rank = Spearman correlation, never described as exact"],
 ["Mutation status","reported only for samples in the source mutation-profiled list; otherwise labelled not assayed/unknown"]],8)
head(doc,"Supplementary Table S6. Cohort-by-module pairs that are not estimable")
three_line(doc,["Accession","Module","Reason"],[[r["accession"],r["module"],r["reason"]] for r in rd(os.path.join(PK,"07_estimates","not_estimable_pairs.csv"))],8)
head(doc,"Supplementary Table S7. Validation evidence: what was reproduced exactly and what only in rank")
three_line(doc,["Check","Scope","Result","Interpretation"],[
 ["Bulk module scores","3 cohorts (GSE13911, GSE44076, GSE47460); per-sample scores","Spearman 1.00 for every module (per-sample score table in 08_qc)","exact reproduction"],
 ["Bulk cohort effects and standard errors","3 cohorts; 49 effects","maximum absolute difference in effect and standard error = 0","exact reproduction"],
 ["Cox models refitted from shipped scores","LUAD and CRC univariable, squamous oesophageal univariable and age-plus-stage; 68 comparisons","maximum absolute difference in hazard ratio = 0","exact reproduction"],
 ["TCGA patient-level scores rebuilt from gene-level table","3 contexts; 20,451 patient-module pairs","Spearman 0.95-0.98","rank agreement only; residual differences trace to the aggregation order"],
 ["xCell compartment scores recomputed","3 cohorts x 4 compartments","Pearson 0.71-0.95; Spearman 0.48-0.94","substantial agreement; lowest rank agreement for one fibroblast score"],
 ["Cross-cohort direction","165 context-module pairs with >=2 cohorts","112 pairs (68%) share the same sign in every cohort","comparability is partial and quantified"],
 ["Coverage-threshold sensitivity","all / >=0.60 / >=0.80 / >=0.90 coverage","BH-significant states: 13 / 13 / 12 / 6","gradual degradation, not all-or-nothing"]],8)
head(doc,"Supplementary Table S8. Which score layer to use")
three_line(doc,["Question","Layer","File","Caveat"],[
 ["Within-cohort case-control difference","bulk GSVA z-scores","04_modules/sample_module_scores_gsva_z.csv","cohort-internal only; compare across cohorts via effect sizes"],
 ["Patient-level difference across tumour contexts","TCGA member-mean z-scores","07_estimates/per_cohort_effects.csv and the TCGA patient score table","construction rule differs from the bulk layer"],
 ["Cell-type-resolved difference","single-cell member means","06_single_cell/","donor-level means are tested, not cells"],
 ["Composition as descriptor or sensitivity covariate","xCell compartments","05_composition/composition_scores_per_sample.csv","enrichment scores share genes with module scores"]],8)
head(doc,"Supplementary Table S9. Comparability, coupling and collinearity checks")
three_line(doc,["Check","Result"],[
 ["Cross-cohort direction consistency","112 of 165 context-module pairs (68%) have the same effect sign in every contributing cohort"],
 ["Coverage-threshold sensitivity","BH-significant states 13 (all, k=165) / 13 (>=0.60) / 12 (>=0.80, k=147) / 6 (>=0.90, k=130)"],
 ["Module versus xCell signature overlap","all 17 modules share more than 20% of their members with the xCell panel; maximum 100%"],
 ["Collinearity: overall model","R2 of disease status on the four compartment scores: median 0.33, maximum 0.89"],
 ["Collinearity: per-predictor VIF","median 2.09, maximum 4.53; the overall model R-squared (how well the four scores jointly explain disease status) is a different quantity from the per-predictor VIF (how far the scores duplicate one another)"],
 ["Curation flow","27 series with processed matrices; 26 case-control cohorts; 1 treatment-response series excluded; 5 single-cell datasets reviewed (4 used)"]],8)
tp=os.path.join(OUT,"Tables_v13.docx"); doc.save(tp); print("tables:",tp)
L=Document(); st2=L.styles['Normal']; st2.font.name='Times New Roman'; st2.font.size=Pt(11)
head(L,"Figure legends (v13)")
for t,b in [
 ("Figure 1. Resource overview.",
  "(A) Module gene coverage by disease context: the fraction of frozen module members present in each cohort's processed expression matrix. "
  "(B) Assay records, unique patients with available identifiers, and paired patients per context, as three facets. "
  "(C) Single-cell datasets with the comparison arms available in each; the lung dataset is shown as excluded because all of its cells come from tumour tissue and no control arm exists."),
 ("Figure 2. Technical validation of the resource.",
  "(A) Documented exclusions, flags and non-testable comparisons on a logarithmic scale. "
  "(B) The comparison design actually used in the single-cell layer, by test type. "
  "(C) The complete estimates layer: all per-cohort standardized effects, faceted by the measure used, including non-significant results. "
  "(C) The complete estimates layer: all per-cohort standardized effects, faceted by the measure used, including non-significant results."),
 ("Figure 4. Sensitivity analyses.",
  "(A) Common-gene sensitivity of module scoring: Spearman correlation between full-member and common-gene scoring for each module, with flagged modules marked in red and non-scorable modules labelled n.a. "
  "(B) Collinearity between disease status and the four composition scores per cohort, with the median marked."),
 ("Figure 3. Comparability and coupling checks.",
  "(A) Cross-cohort direction consistency for every context-module pair with at least two cohorts: the fraction of cohorts sharing the majority effect direction. "
  "(B) Coverage-threshold sensitivity: the number of cohort-module pairs pooled (light) and the number of states surviving BH control (red) as cohorts below 0.60, 0.80 and 0.90 coverage are excluded. "
  "(C) Fraction of each module's members that lie inside the xCell signature panel, with the 20% level marked, showing that module scores and composition scores share input genes. "
  "(D) Overall model R-squared versus the maximum per-predictor VIF within the disease-status model, illustrating how the two collinearity measures differ."),
 ("Supplementary material.",
  "No supplementary figures are required for this descriptor: the composition sensitivity material is presented in Figure 2 panels D and E, "
  "and the corresponding numerical results are shipped as machine-readable tables in folder 08_qc (common-gene sensitivity, composition "
  "collinearity, per-predictor VIF, module-versus-signature overlap).")]:
    head(L,t,2); L.add_paragraph(b)
lp=os.path.join(OUT,"Figure_legends_v13.docx"); L.save(lp); print("legends:",lp)
