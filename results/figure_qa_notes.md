# Figure layout QA: how to reproduce and how to read the output

Two shipped scripts inspect the four figures without a vision model:

* `11_code/64_v14_figure_qa_final.py` - page size, canvas clipping (ink touching an edge) and candidate
  text collisions. Two OCR word boxes on the same line whose intersection contains ink are reported as a
  candidate collision; a pair is *dismissed* when the two boxes are adjacent and their concatenation forms a
  number, because OCR routinely splits decimals (for example 0.94 into 0.9 and 4).
* `11_code/77_v14_figure_review.py` - label completeness (panel letters and context labels), print-size
  legibility (the image is halved and re-read), text over high-variance background, forbidden legend or title
  strips in the outer bands, margins and contrast.

Result for the shipped figures: Fig1 17.0 x 23.6 cm, Fig2 17.0 x 20.8 cm, Fig3 17.0 x 21.8 cm,
Fig4 17.0 x 18.8 cm, all at 300 dpi, no clipping and no legend or title strip (outer-band ink coverage
0.14-0.47, against a legend threshold of 0.55).

Known, verified false positives:

1. `64` reports one candidate collision in Fig3 for the pair ('RAS_MAPK', '>'): the OCR box of the module
   label swallowed a thin axis line. Pixel inspection of the intersection shows the glyphs are separated; the
   short label is drawn left of the axis line and does not touch it.
2. `77` reports a minimum contrast below its own threshold of 3 for Fig1 (1.80), Fig3 (1.58) and Fig4 (1.66).
   Every flagged token is a single-character OCR fragment ('5', '+', 'a', '&', '-') produced by the dashed
   reference lines and scatter points, not a text label; tokens with no ink variation are excluded by the
   script, and the remaining labels are drawn in #1A1A1A on white.

Both scripts are conservative by design: they flag for human review rather than certifying a figure.
