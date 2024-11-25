# script to process STS data and generate bass model for e-cigarette smoking prevalence by subgroups
library(tidyverse)
library(haven) 
library(lubridate) # For date manipulation
library(scales)
library(netdiffuseR)

serverfolder <- "/Volumes/shared/niaaa_cascade1/Shared/STS data/STS and ATS files Dec 23/Latest omnibus SPSS data file"
# folder will need to be updated when new waves of STS come out 
setwd(serverfolder)

sts <- read_sav("omni206_39.1_65.2cot_31.3a_25.4s_recodes_92.5sa.sav")
                # col_select = c(xwave, month, xyear, quarter, sexz, agez, actage, sgz, ab, `@weight0`, smoker, smokstat,usingecig, allecig,qimw118_3))

sts_sub <- sts %>% 
  dplyr::select(xwave, xyear, sexz, agez, actage, sgz, ab, `@weight0`, smoker, smokstat, allecig, alldisposable, usingecig, qimw118_3)

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

# now calculate prevalence of e-cigarette users for whole population - subset after wave 85
sts_sub <- sts_sub %>% filter(xwave>=86) %>% 
  mutate(sexz = ifelse(sexz==1, "Men","Women"),
         smokstat=ifelse(smokstat==0, "Never smoked",
                         ifelse(smokstat==1, "Ex-smoker",
                                ifelse(smokstat==2, "Ex-smoker",
                                       ifelse(smokstat==3,"Smoker", NA)))),
         disposable = ifelse(qimw118_3==2, "disposable",
                             ifelse(qimw118_3>2, "non-disposable",NA)),
         agecat = cut(actage,
                      breaks=c(0,24,34,44,54,64,100),
                      labels=c("16-24","25-34","35-44","45-54","55-64","65+")),
         sgz = ifelse(sgz==1, "AB",
                      ifelse(sgz==2,"C1",ifelse(sgz==3, "C2",
                                                ifelse(sgz==4, "D","E")))),
         ab = ifelse(ab==1 | ab==2, "ABC1","C2DE"),
         age_new = cut(actage,
                       breaks=c(0,24,34,44,54,64,100),
                       labels=c("16-24","25-34","35-44","45-54","55-64","65+")),
         age_new = case_when(agez==1 ~ "16-24",
                             agez==2 ~ "25-34",
                             agez==3 ~ "35-44",
                             agez==4 ~ "45-54",
                             agez==5 ~ "55-64",
                             agez==6 ~ "65+", .default=age_new),
         agecat_youngmidold = case_when(
           age_new == "16-24" ~ "16-24",
           age_new == "25-34" | age_new == "35-44" | age_new=="45-54" ~ "25-54",
           age_new=="55-64" | age_new=="65+" ~ "55+"),
        birthyear = xyear-actage,
        cohort = cut(birthyear,
                     breaks=c(0,1930,1940,1950,1960,1970,1980,1990,2000,2020),
                     labels=c("<1930","1931-1940","1941-1950","1951-1960",
                              "1961-1970","1971-1980","1981-1990","1991-2000","2001+")),
        cohort = cut(birthyear,
                     breaks=c(0,1940,1960,1980,1990,2020),
                     labels=c("<1940","1941-1960","1961-1980","1981-1990","1991+")))

# calculate overall prevalence of e-cigarette use by cohort
ecigs_prevalence <- sts_sub %>% 
  group_by(xyear, cohort, smokstat) %>% 
  mutate(disposable = ifelse(disposable=="disposable", 1,
                             ifelse(disposable=="non-disposable", 0, NA))) %>% 
  # filter(disposable=="disposable") %>% 
  summarise(observed = weighted.mean(allecig, `@weight0`, na.rm=T),
            n=n(),
            se = sqrt((observed*(1-observed))/n),
            lower = observed - (1.96*se),
            lower = ifelse(lower<0, 0, lower),
            upper = observed + (1.96*se)
            ) %>%
  drop_na()

prevalencebycohort <- ggplot(ecigs_prevalence, aes(x=xyear, y=observed)) + 
  geom_line(linewidth=1) + facet_grid(cols=vars(cohort), rows=vars(smokstat), scales="free") +
  geom_ribbon(aes(ymin=lower, ymax=upper), colour=NA, alpha=0.5) +
  theme_bw() + 
  xlab("Year") +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(), 
        text = element_text(size=14)) + ylim(0,NA) + 
  scale_y_continuous(labels=scales::percent, limits=c(0,NA)) +
  scale_x_continuous(labels=c("2013","2015","2017","2019","2021","2023"),
                     breaks=c(2013,2015,2017,2019,2021,2023)) +
  
  ylab("Prevalence of e-cigarettes use")

prevalencebycohort

disposableprevalence <- sts_sub %>% 
  group_by(xyear, cohort, smokstat) %>% 
  # filter(allecig==1) %>% 
  mutate(disposable = ifelse(disposable=="disposable", 1,
                             ifelse(disposable=="non-disposable", 0, 
                                    ifelse(allecig==0 & xyear>=2016, 0, NA)))) %>% 
  # filter(disposable=="disposable") %>% 
  summarise(observed = weighted.mean(alldisposable, `@weight0`, na.rm=T),
            n=n(),
            se = sqrt((observed*(1-observed))/n),
            lower = observed - (1.96*se),
            lower = ifelse(lower<0, 0, lower),
            upper = observed + (1.96*se)
  ) %>%
  drop_na()

disposablebycohort <- ggplot(disposableprevalence, aes(x=xyear, y=observed)) + 
  geom_line(linewidth=1) + facet_grid(cols=vars(cohort), rows=vars(smokstat),) +
  geom_ribbon(aes(ymin=lower, ymax=upper), colour=NA, alpha=0.5) +
  theme_bw() + 
  xlab("Year") +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(), 
        text = element_text(size=14)) + ylim(0,NA) + 
  scale_y_continuous(labels=scales::percent, limits=c(0,NA)) +
  scale_x_continuous(labels=c("2013","2015","2017","2019","2021","2023"),
                     breaks=c(2013,2015,2017,2019,2021,2023)) +
  
  ylab("Prevalence of disposable e-cigarette use")
disposablebycohort

setwd("~/Desktop/STS")

ggsave("disposable_prevalence_cohort.png", disposablebycohort, dpi=300, width=50, height=25, units="cm")

ecigs_prevalence <- sts_sub %>% 
  group_by(date_final, cohort, smokstat, ab,allecig, disposable) %>% 
  count(wt=`@weight0`) %>% 
  filter(allecig==1) %>% drop_na()

# now calculate all ecigarette use for smokers pre wave 85 
sts_sub <- sts  %>% 
  mutate(sexz = ifelse(sexz==1, "Men","Women"),
         smokstat=ifelse(smokstat==0, "Never smoked",
                         ifelse(smokstat==1, "Ex-smoker",
                                ifelse(smokstat==2, "Ex-smoker",
                                       ifelse(smokstat==3,"Smoker", NA)))),
         disposable = ifelse(qimw118_3==2, "disposable",
                             ifelse(qimw118_3>2, "non-disposable",NA)),
         agecat = cut(actage,
                      breaks=c(0,24,34,44,54,64,100),
                      labels=c("16-24","25-34","35-44","45-54","55-64","65+")),
         sgz = ifelse(sgz==1, "AB",
                      ifelse(sgz==2,"C1",ifelse(sgz==3, "C2",
                                                ifelse(sgz==4, "D","E")))),
         ab = ifelse(ab==1 | ab==2, "ABC1","C2DE"),
         age_new = cut(actage,
                       breaks=c(0,24,34,44,54,64,100),
                       labels=c("16-24","25-34","35-44","45-54","55-64","65+")),
         age_new = case_when(agez==1 ~ "16-24",
                             agez==2 ~ "25-34",
                             agez==3 ~ "35-44",
                             agez==4 ~ "45-54",
                             agez==5 ~ "55-64",
                             agez==6 ~ "65+", .default=age_new),
         agecat_youngmidold = case_when(
           age_new == "16-24" ~ "16-24",
           age_new == "25-34" | age_new == "35-44" | age_new=="45-54" ~ "25-54",
           age_new=="55-64" | age_new=="65+" ~ "55+"),
         birthyear = xyear-actage,
         cohort = cut(birthyear,
                      breaks=c(0,1930,1940,1950,1960,1970,1980,1990,2000,2020),
                      labels=c("<1930","1931-1940","1941-1950","1951-1960",
                               "1961-1970","1971-1980","1981-1990","1991-2000","2001+")),
         cohort = cut(birthyear,
                      breaks=c(0,1940,1960,1980,1990,2020),
                      labels=c("<1940","1941-1960","1961-1980","1981-1990","1991+")))

ecigs_prevalence <- sts_sub %>% 
  group_by(xyear, cohort, smokstat) %>% 
  # filter(disposable=="disposable") %>% 
  summarise(observed = weighted.mean(usingecig, `@weight0`, na.rm=T),
            n=n(),
            se = sqrt((observed*(1-observed))/n),
            lower = observed - (1.96*se),
            lower = ifelse(lower<0, 0, lower),
            upper = observed + (1.96*se)
  ) %>%
  drop_na() %>% filter(smokstat!="Never smoked") %>% filter(xyear>=2009)

prevalencebycohort <- ggplot(ecigs_prevalence, aes(x=xyear, y=observed, colour=smokstat)) + 
  geom_line(linewidth=1) + facet_grid(cols=vars(cohort), scales="free") +
  geom_ribbon(aes(ymin=lower, ymax=upper, fill=smokstat), colour=NA, alpha=0.5) +
  theme_bw() + 
  xlab("Year") +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(), 
        text = element_text(size=14)) + ylim(0,NA) + 
  scale_y_continuous(labels=scales::percent, limits=c(0,NA)) +
  scale_x_continuous(labels=c("2006","2010","2014","2018","2022"),
                     breaks=c(2006,2010,2014,2018,2022)) +
  
  ylab("Prevalence of e-cigarettes use")
prevalencebycohort

ggsave("ecig_prevalence_cohort_smokers.png", prevalencebycohort, dpi=300, width=50, height=25, units="cm")

test <- ecigs_prevalence %>% 
  filter(smokstat=="Smoker" & cohort=="1961-1980")
