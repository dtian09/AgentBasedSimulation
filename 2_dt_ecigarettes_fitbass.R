# script to process STS data and generate bass model for e-cigarette smoking prevalence by subgroups
library(tidyverse)
library(haven) 
library(lubridate) # For date manipulation
library(scales)
library(netdiffuseR)
library(minpack.lm)
library(plotrix)

serverfolder <- "x:/shared/"
setwd(serverfolder)

source("X:/Shared/code/ABM_software/smokingABM/0_dt_bass_functions.R")

sts <- read_sav("STS data/STS and ATS files May 24/Latest omnibus SPSS data file/omni211_39.1_65.2cot_31.3a_25.4s_recodes_97.5sa.sav",
                col_select = c(xwave, month, xyear, quarter, sexz, agez, actage, sgz, ab, `@weight0`, smoker, smokstat, allecig,alldisposable,qimw118_3))

write.csv(sts,file='sts.csv',row.names=F)

sts <- read.csv('sts.csv')

sts_sub <- sts %>% 
  dplyr::select(xwave, xyear, sexz, agez, actage, sgz, ab, `@weight0`, smoker, smokstat, allecig, alldisposable, qimw118_3)

dates <- sts %>% dplyr::select(xwave, month, xyear, quarter) %>% distinct()

convert_quarter_to_month <- function(quarter) {
  # Map quarter to corresponding labels
  month_labels <- c("Oct", "Jan", "Apr", "July")
  index <- (quarter - 1) %% 4 + 1
  return(month_labels[index])
}

dates$labelled_quarter <- convert_quarter_to_month(dates$quarter)
dates$monthyear <- paste0(dates$labelled_quarter, "-", dates$xyear)
dates$date_final <- as.Date(paste0("01-", dates$monthyear), format = "%d-%b-%Y")

dates <- dates %>% dplyr::select(xwave, date_final)

# join the date back up with the subset STS data 
sts_sub <- left_join(sts_sub, dates)

# define categories for subgroups - sex, smoking status and birth cohorrt 
sts_sub <- sts_sub %>% 
  mutate(smokstat=ifelse(smokstat==0, "Never smoked",
                         ifelse(smokstat==1, "Ex-smoker",
                                ifelse(smokstat==2, "Ex-smoker",
                                       ifelse(smokstat==3,"Smoker", NA)))),
        birthyear = xyear-actage,
        cohort = cut(birthyear,
                     breaks=c(0,1940,1960,1980,1990,2020),
                     labels=c("<1940","1941-1960","1961-1980","1981-1990","1991+")))

# 
# # get time series for non-disposable e-cigarette prevalence after 2010
# ecig_prevalence <- sts_sub %>% 
#   mutate(cat = paste0(smokstat, cohort)) %>% 
#   filter(xyear>=2010) %>% 
#   # filter out never smokers - we are not estimating diffusion in this group pre 2021
#   filter(smokstat!="Never smoked") %>%
#   # group by date (quarter), smoking status, cohort
#   group_by(date_final, smokstat, cohort) %>% 
#   mutate(alldisposable=ifelse(is.na(alldisposable), 0, alldisposable)) %>% 
#   filter(alldisposable==0) %>% 
#   # calculate the weighted prevalence of e-cig users 
#   summarise(ecig_prevalence = weighted.mean(allecig, `@weight0`, na.rm=T)) %>% 
#   ungroup() %>% 
#   group_by(smokstat, cohort) %>% 
#   arrange(date_final,smokstat,cohort) %>% 
#   drop_na() %>% 
  # label the quarter so that it starts at 0
  # quarter 1 = January 2010 (this can be modified)
#   mutate(quarter = quarter(date_final),
#          year = year(date_final),
#          year_num = year-min(year),
#          quarter = (year_num * 4) + quarter - min(quarter),
#          cat = paste0(smokstat, cohort))
# 
# # plot the e-cig time series by cohort and smoking status 
# ggplot(ecig_prevalence, aes(x=date_final, y=ecig_prevalence)) + geom_line() + 
#   facet_grid(cols=vars(cohort), rows=vars(smokstat)) + 
#   theme_bw()
# 
# 
# 
# # estimate all the parameters for smokers + ex-smokers 2010-2020
# ecig_parameters <- list()
# ecig_predicted <- list()
#          
# for(i in unique(ecig_prevalence$cat)){
#   data <- ecig_prevalence %>% filter(cat==i)
#   # fit bass model parameters to each subgroup i
#   # ecig_parameters[[paste(i)]] <- fit_bass(data)
#   
#   ecig_parameters[[paste(i)]] <- fit_bass_decline(data)
#   
#   # insert those parameters back into bass equation to get predicted values
#   data$predicted <- bass_diffusion_decline(data$quarter, ecig_parameters[[paste(i)]]$p, 
#                                    ecig_parameters[[paste(i)]]$q, 
#                                    ecig_parameters[[paste(i)]]$m,
#                                    ecig_parameters[[paste(i)]]$d)
#   ecig_predicted[[paste(i)]] <- data
# }
# 
# # process and plot bass predicted values
# ecig_predicted <- do.call(rbind, ecig_predicted)
# ecig_predicted <- ecig_predicted %>% pivot_longer(c(ecig_prevalence,predicted)) %>% 
#   mutate(name=case_when(name=="ecig_prevalence"~"observed",
#                         name=="predicted"~"predicted"))
# 
# ggplot(ecig_predicted, aes(x=date_final, y=value, colour=name)) + geom_line(linewidth=1) + 
#   facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,1) +
#   theme_bw() +
#   theme(legend.position="bottom",
#         legend.title=element_blank(),
#         text = element_text(size=14)) +
#   ylab("prevalence of e-cigarette use") +
#   scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")
# 
# ggsave("X:/Shared/code/ABM_software/smokingABM/bass_withdecline_2011_2024.png", dpi=300, width=33, height=18, units="cm")
# 
# # now do the same for disposable e-cig use from 2021 onwards
# disposable_prevalence <- sts_sub %>% 
#   filter(xyear>=2021 & xyear<=2024) %>% 
#   # group by date (quarter), smoking status, cohort
#   group_by(date_final, smokstat, cohort) %>% 
#   # calculate the weighted prevalence of disposable e-cig users 
#   summarise(ecig_prevalence = weighted.mean(alldisposable, `@weight0`, na.rm=T),
#             allecig = weighted.mean(allecig, `@weight0`, na.rm=T)) %>% 
#   ungroup() %>% 
#   group_by(smokstat, cohort) %>% 
#   arrange(date_final,smokstat,cohort) %>% 
#   drop_na() %>% 
#   # label the quarter so that it starts at 0
#   # quarter 1 = January 2010 (this can be modified)
#   mutate(quarter = quarter(date_final),
#          year = year(date_final),
#          year_num = year-min(year),
#          quarter = (year_num * 4) + quarter - min(quarter),
#          cat = paste0(smokstat,cohort))
# 
# # plot the e-cig time series by cohort and smoking status 
# ggplot(disposable_prevalence, aes(x=date_final, y=ecig_prevalence)) + geom_line() + 
#   facet_grid(cols=vars(cohort), rows=vars(smokstat)) + 
#   theme_bw()
# 
# # remove individuals with no good evidence of disposable e-cig diffusion
# # all cohorts <1940 + ex-smokers from 1941-1960 + never smokers from 1941-1960 + 1961-1980
# disposable_prevalence <- disposable_prevalence %>% 
#   filter(cohort!="<1940") %>% 
#   filter(cat!="Ex-smoker1941-1960") %>% 
#   filter(cat!="Never smoked1941-1960") %>% 
#   filter(cat!="Never smoked1961-1980") %>% 
#   filter(cat!="Never smoked1981-1990")
# 
# # estimate all the parameters
# disposable_parameters <- list()
# disposable_predicted <- list()
# 
# for(i in unique(disposable_prevalence$cat)){
#   data <- disposable_prevalence %>% filter(cat==i)
#   # fit bass model parameters to each subgroup i
#   prop <- 0.06
#   disposable_parameters[[paste(i)]] <- fit_bass(data,prop)
#   # insert those parameters back into bass equation to get predicted values
#   data$predicted <- bass_diffusion(data$quarter, disposable_parameters[[paste(i)]]$p, disposable_parameters[[paste(i)]]$q, disposable_parameters[[paste(i)]]$m)
#   disposable_predicted[[paste(i)]] <- data
# }
# 
# # process and plot bass predicted values
# disposable_predicted <- do.call(rbind, disposable_predicted)
# disposable_predicted <- disposable_predicted %>% pivot_longer(c(ecig_prevalence,predicted)) %>% 
#   mutate(name=case_when(name=="ecig_prevalence"~"observed",
#                         name=="predicted"~"predicted"))
# 
# ggplot(disposable_predicted, aes(x=date_final, y=value, colour=name)) + geom_line(linewidth=1) + 
#   facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,NA) +
#   theme_bw() +
#   theme(legend.position="bottom",
#         legend.title=element_blank(),
#         text = element_text(size=14)) +
#   ylab("prevalence of e-cigarette use") +
#   scale_x_date(date_breaks="1 year", labels=date_format("%Y")) + xlab("Year")
# 
# ggsave("X:/Shared/code/ABM_software/smokingABM/bass_disposable_2021_2024.png", dpi=300, width=33, height=18, units="cm")
# 
# 
# generate the full e-cig prevalence data (non-disposable and disposable e-cigarette prevalence) to fit to 
ecig_prevalence <- sts_sub %>% 
  filter(xyear>=2010) %>% 
  # filter out never smokers - we are not estimating diffusion in this group pre 2021
  # filter(smokstat!="Never smoked") %>% 
  # group by date (quarter), smoking status, cohort
  group_by(date_final, smokstat, cohort) %>% 
  # calculate the weighted prevalence of e-cig users 
  summarise(ecig_prevalence = weighted.mean(allecig, `@weight0`, na.rm=T),
            se = std.error(allecig)) %>% 
  ungroup() %>% 
  group_by(smokstat, cohort) %>% 
  arrange(date_final,smokstat,cohort) %>% 
  drop_na() %>% 
  # label the quarter so that it starts at 0
  # quarter 1 = January 2010 (this can be modified)
  mutate(quarter = quarter(date_final),
         year = year(date_final),
         year_num = year-min(year),
         quarter = (year_num * 4) + quarter - min(quarter),
         cat = paste0(smokstat, cohort),
         ecig_prevalence = ifelse(smokstat=="Never smoked" & cohort!="1991+", NA, ecig_prevalence))

full_predicted <- list()


# # putting it all together?
# ecig_parameters <- do.call(rbind,ecig_parameters) %>% mutate(type="e-cig")
# disposable_parameters <- do.call(rbind, disposable_parameters) %>% mutate(type="disposable",d=0)
# 
# parameters <- rbind(ecig_parameters, disposable_parameters) %>% 
#   mutate(cat = paste0(smokstat, cohort)) %>% distinct()
# 
# write.csv(parameters,"X:/Shared/code/ABM_software/smokingABM/diffusion_parameters.csv",row.names=F)

parameters <- read.csv("U:/smoking cessation/ABM software/charlotte/diffusion_parameters.csv")
  
remove_trailing_na <- function(vec){
  return (rev(rev(vec)[!is.na(rev(vec))]))
}

get_ABM_Bass_model_predictions <- function(){
  serverfolder <- "X:/Shared/code/ABM_software/smokingABM/output2/"
  setwd(serverfolder)
  ht <- list() #hashtable with key=subgroup and value=vector of predicted prevalence 
  cat = c('Ex-smoker<1940','Ex-smoker1941-1960','Ex-smoker1961-1980','Ex-smoker1981-1990',   
               'Ex-smoker1991+','Never smoked<1940','Never smoked1941-1960','Never smoked1961-1980',
               'Never smoked1981-1990','Never smoked1991+','Smoker<1940','Smoker1941-1960',      
               'Smoker1961-1980','Smoker1981-1990','Smoker1991+')
  exsmokerless1940 <- scan("Exsmoker_less1940_quarters.csv", sep = ",", what = numeric())
  ht[['Ex-smoker<1940']] <- remove_trailing_na(exsmokerless1940)
  exsmoker1941_1960 <- scan("Exsmoker1941_1960_quarters.csv", sep = ",", what = numeric())
  ht[['Ex-smoker1941-1960']] <- remove_trailing_na(exsmoker1941_1960)
  exsmoker1961_1980 <- scan("Exsmoker1961_1980_quarters.csv", sep = ",", what = numeric())
  ht[['Ex-smoker1961-1980']] <- remove_trailing_na(exsmoker1961_1980)
  exsmoker1981_1990 <- scan("Exsmoker1981_1990_quarters.csv", sep = ",", what = numeric())
  ht[['Ex-smoker1981-1990']] <- remove_trailing_na(exsmoker1981_1990)
  exsmokerover1991 <- scan("Exsmoker_over1991_quarters.csv", sep = ",", what = numeric())
  ht[['Ex-smoker1991+']] <- remove_trailing_na(exsmokerover1991)
  ht[['Never smoked<1940']] <- numeric(length(exsmokerless1940)) #vector of 0s
  ht[['Never smoked1941-1960']] <- numeric(length(exsmokerless1940)) #vector of 0s
  ht[['Never smoked1961-1980']] <- numeric(length(exsmokerless1940)) #vector of 0s
  ht[['Never smoked1981-1990']] <- numeric(length(exsmokerless1940)) #vector of 0s
  neversmokedover1991 <- scan("Neversmoked_over1991_quarters.csv", sep = ",", what = numeric())
  ht[['Never smoked1991+']] <- remove_trailing_na(neversmokedover1991)
  smokerless1940 <- scan("Smoker_less1940_quarters.csv", sep = ",", what = numeric())
  ht[['Smoker<1940']] <- remove_trailing_na(smokerless1940)
  smoker1941_1960 <- scan("Smoker1941_1960_quarters.csv", sep = ",", what = numeric())
  ht[['Smoker1941-1960']] <- remove_trailing_na(smoker1941_1960)
  smoker1961_1980 <- scan("Smoker1961_1980_quarters.csv", sep = ",", what = numeric())
  ht[['Smoker1961-1980']] <- remove_trailing_na(smoker1961_1980)
  smoker1981_1990 <- scan("Smoker1981_1990_quarters.csv", sep = ",", what = numeric())
  ht[['Smoker1981-1990']] <- remove_trailing_na(smoker1981_1990)
  smokerover1991 <- scan("Smoker_over1991_quarters.csv", sep = ",", what = numeric())
  ht[['Smoker1991+']] <- remove_trailing_na(smokerover1991)
  return(ht)
}

pred_ABM_Bass_model<-get_ABM_Bass_model_predictions()

for(i in unique(ecig_prevalence$cat)){
  data <- ecig_prevalence %>% filter(cat==i)
  futuredates <- seq.Date(from=tail(data$date_final,1), to =as.Date("2026-01-01"), by="quarter")
  futuredata <- expand.grid(date_final=futuredates, smokstat=unique(data$smokstat), cohort=unique(data$cohort),
                           ecig_prevalence=NA, quarter=NA, year=NA, year_num=NA, cat=i)
  data <- rbind(data, futuredata)
  data <- data %>%
    mutate(quarter = quarter(date_final),
            year = year(date_final),
            year_num = year-min(year),
            quarter = (year_num * 4) + quarter - min(quarter)) %>% 
    distinct(quarter, .keep_all = TRUE)
  # fit bass model parameters to each subgroup i
  ecig_parameters <- parameters %>% filter(cat==i) %>% filter(type=="e-cig")
  disposable_parameters <- parameters %>% filter(cat==i) %>% filter(type=="disposable")
  data$predicted <- generate_combined_curve(unique(data$quarter), ecig_parameters$p[1], ecig_parameters$q[1], ecig_parameters$m[1], ecig_parameters$d[1],
                          disposable_parameters$p[1], disposable_parameters$q[1], disposable_parameters$m[1], disposable_parameters$d[1])
  #print(length(data$predicted))
  ###add prediction of the ABM Bass model to data
  data$predicted_ABM_Bass_model <- pred_ABM_Bass_model[[i]]
  ###
  full_predicted[[paste(i)]] <- data
}

full_predicted <- full_predicted %>% bind_rows() %>% 
  pivot_longer(c(ecig_prevalence,predicted,predicted_ABM_Bass_model)) %>% 
  mutate(name=case_when(name=="ecig_prevalence"~"observed",
                        name=="predicted"~"predicted",
                        name=="predicted_ABM_Bass_model"~"predicted_by_ABM_Bass_model"))

full_predicted$lower <- ifelse(full_predicted$name=="predicted", NA,
                               ifelse(full_predicted$name=="predicted_by_ABM_Bass_model", NA,
                                    full_predicted$value - (1.96*full_predicted$se)))
full_predicted$upper <- ifelse(full_predicted$name=="predicted", NA,
                               ifelse(full_predicted$name=="predicted_by_ABM_Bass_model", NA,
                                    full_predicted$value + (1.96*full_predicted$se)))

full_predicted$upper <- ifelse(full_predicted$upper > 1, 0.8, full_predicted$upper)

ggplot(full_predicted, aes(x=date_final, y=value, colour=name))  + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat), scales="free") + ylim(0,0.8) +
  theme_bw() +
  geom_ribbon(aes(ymin=upper, ymax=lower, fill=name), colour=NA, alpha=0.7) + 
  geom_line(size=1) + 
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14),
        axis.text.x=element_text(angle=45, vjust=1, hjust=1)) +
  ylab("prevalence of e-cigarette use") + 
  geom_vline(aes(xintercept=as.numeric(as.Date("2021-01-01"))), colour="black", linetype="dashed") + 
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

ggsave("X:/Shared/code/ABM_software/smokingABM/bassmodel_predictions_2yrs_combinedmodels_and_ABM_Bass_model.png", dpi=300, width=33, height=18, units="cm")
