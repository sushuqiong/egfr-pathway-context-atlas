suppressPackageStartupMessages({library(dplyr); library(ggplot2)})
con <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR的v13/results/v13_qc_cross_cohort_consistency.csv", stringsAsFactors=FALSE)
A <- con %>% filter(k>=2) %>% mutate(concordance=as.numeric(as.character(concordance))) %>%
  filter(is.finite(concordance), !is.na(disease), disease!="") %>%
  arrange(disease, desc(concordance)) %>% mutate(label=paste0(disease,": ",feature))
cat("rows:", nrow(A), "| n_distinct label:", n_distinct(A$label), "| class:", class(A$concordance), "\n")
p <- ggplot(A, aes(concordance, reorder(label, concordance))) + geom_col(width=.6, fill="#3C6E9F") +
  facet_wrap(~disease, scales="free_y", ncol=3) + scale_x_continuous(limits=c(0.4,1.02))
ggsave("C:/Users/fengq/Desktop/EGFR/EGFR的v13/results/_dbg_pA.png", p, width=6.7, height=4, dpi=100)
cat("done\n")
