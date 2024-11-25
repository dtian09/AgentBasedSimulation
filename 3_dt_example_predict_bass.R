library(tidyverse)

setwd("X:/Shared/")

parameters <- read_csv("code/ABM_software/smokingABM/diffusion_parameters.csv")

# functions to generate the predicted values of e-cigarette prevalence
# function to generate the combined curve
generate_combined_curve <- function(quarters, p1, q1, m1, d1, p2, q2, m2, d2){
  adopters <- numeric(length(quarters))
  for (i in 1:length(quarters)) {
    if(is.na(p2)){
      adopters[i] <- bass_diffusion_decline(quarters[i], p1, q1, m1, d1)
    } else if(is.na(p1) & quarters[i] >= 43){
      adopters[i] <- bass_diffusion_decline(quarters[i] - 43, p2, q2, m2, d2)
    } else if (quarters[i] < 44) {
      adopters[i] <- bass_diffusion_decline(quarters[i], p1, q1, m1, d1)
    } else {
      adopters[i] <- bass_diffusion_decline(43, p1, q1, m1, d1) +
        bass_diffusion_decline(quarters[i] - 43, p2, q2, m2, d2)
    }
  }
  return(adopters)
}

# basic bass diffusion model 
bass_diffusion <- function(t, p, q, m) {
  adopters <- m * (1 - exp(-(p + q) * t)) / (1 + (p / q) * exp(-(p + q) * t))
  return(adopters)
}

bass_diffusion_decline <- function(t, p, q, m,d) {
  m <- m * exp(-d * t)
  adopters <- m * (1 - exp(-(p + q) * t)) / (1 + (p / q) * exp(-(p + q) * t))
  return(adopters)
}

# set up data to impute e-cigarette prevalence into - as an example
fulldata <- data.frame(expand.grid(cohort=unique(parameters$cohort),
                                   smokstat=unique(parameters$smokstat),
                               date_final=seq.Date(from=as.Date("2011-01-01"), to=as.Date("2034-01-01"), by="quarter"))) %>% 
  mutate(quarter = quarter(date_final),
         year = year(date_final),
         year_num = year-min(year),
         quarter = (year_num * 4) + quarter - min(quarter),
         cat=paste0(smokstat,cohort))

full_predicted <- list()

for(i in unique(fulldata$cat)){
  data <- fulldata %>% filter(cat==i)
# extract parameters for e-cigarettes (pre 2021)
  ecig_parameters <- parameters %>% filter(cat==i) %>% filter(type=="e-cig")
  # extract parameters for disposable (post 2021)
  disposable_parameters <- parameters %>% filter(cat==i) %>% filter(type=="disposable")
  data$predicted <- generate_combined_curve(unique(data$quarter), ecig_parameters$p[1], ecig_parameters$q[1], ecig_parameters$m[1], ecig_parameters$d[1],
                                            disposable_parameters$p[1], disposable_parameters$q[1], disposable_parameters$m[1], disposable_parameters$d[1])
  full_predicted[[paste(i)]] <- data
}

full_predicted <- full_predicted %>% bind_rows()

ggplot(full_predicted, aes(x=date_final, y=predicted))  + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat), scales="free") + ylim(0,0.8) +
  theme_bw() +
  geom_line(size=1) + 
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14),
        axis.text.x=element_text(angle=45, vjust=1, hjust=1)) +
  ylab("prevalence of e-cigarette use") + 
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

