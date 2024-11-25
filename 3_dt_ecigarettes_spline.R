# script to process STS data and generate bass model for e-cigarette smoking prevalence by subgroups
library(tidyverse)
library(haven) 
library(lubridate) # For date manipulation
library(scales)
library(netdiffuseR)
library(minpack.lm)

serverfolder <- "X:/Shared/"
setwd(serverfolder)

sts <- read_sav("STS data/STS and ATS files Mar 24/Latest omnibus SPSS data file/omni209_39.1_65.2cot_31.3a_25.4s_recodes_95.5sa.sav",
                col_select = c(xwave, month, xyear, quarter, sexz, agez, actage, sgz, ab, `@weight0`, smoker, smokstat, allecig,alldisposable,qimw118_3))
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

# get time series for e-cigarette prevalence 
ecig_prevalence <- sts_sub %>% 
  filter(xyear>=2010) %>% 
  # filter out never smokers - we are not estimating diffusion in this group pre 2021
  filter(smokstat!="Never smoked") %>% 
  # group by date (quarter), smoking status, cohort
  group_by(date_final, smokstat, cohort) %>% 
  # calculate the weighted prevalence of e-cig users 
  summarise(ecig_prevalence = weighted.mean(allecig, `@weight0`, na.rm=T)) %>% 
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
         cat = paste0(smokstat, cohort))

# plot the e-cig time series by cohort and smoking status 
ggplot(ecig_prevalence, aes(x=date_final, y=ecig_prevalence)) + geom_line() + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + 
  theme_bw()

#test <- ecig_prevalence %>% filter(smokstat=="Ex-smoker") %>% filter(cohort=="1981-1990")

#summary(model)
#test$predicted <- predict(model, test$quarter)$y

#ggplot(test, aes(x=quarter)) + 
#  geom_line(aes(y=ecig_prevalence), colour="black") + 
#  geom_line(aes(y=predicted), colour="red")

# estimate all the parameters for smokers + ex-smokers 2010-2020
spline_models <- list()
spline_predicted <- list()
         
for(i in unique(ecig_prevalence$cat)){
  data <- ecig_prevalence %>% filter(cat==i)
  # fit bass model parameters to each subgroup i
  # model <- smooth.spline(data$quarter, data$ecig_prevalence,cv=T, df=5)
  
  # set knots in 2015 (q20) and 2021 (q44)
  model <- lm(ecig_prevalence~bs(quarter,knots=c(20,44)), data=data)
  
  spline_models[[paste(i)]] <- data.frame(model$coefficients)
  spline_models[[paste(i)]]$params <- names(model$coefficients)
  spline_models[[paste(i)]]$cat <- i
  
  # insert those parameters back into bass equation to get predicted values
  data$predicted <- predict(model, data)
  spline_predicted[[paste(i)]] <- data
}

spline_models <- do.call(rbind, spline_models)


spline_func <- function(x, knots) {
  bs(x, knots = knots)
}

# Define the function to predict new values
predict_spline <- function(x, intercept, coefs, knots) {
  preds <- numeric(length(x))
  for (i in seq_along(x)) {
    # Compute spline basis functions for the current x value
    basis_funcs <- c(1, (x[i] - knots[1])^3, (x[i] - knots[2])^3, (x[i] - knots[1])^3 * (x[i] - knots[2])^3)
    # Compute prediction for the current x value
    preds[i] <- intercept + sum(coefs * basis_funcs)
  }
  return(preds)
}




# Extracting intercept and coefficients
intercept <- model_coefficients$model.coefficients[model_coefficients$params == "(Intercept)"]
coefs <- model_coefficients$model.coefficients[model_coefficients$params != "(Intercept)"]
knots <- c(20, 44) # Assuming knots are fixed

predicted_value <- predict_spline(x_value, intercept, coefs, knots)


# process and plot bass predicted values
spline_predicted <- do.call(rbind, spline_predicted)
spline_predicted <- spline_predicted %>% pivot_longer(c(ecig_prevalence,predicted)) %>% 
  mutate(name=case_when(name=="ecig_prevalence"~"observed",
                        name=="predicted"~"predicted"))

ggplot(spline_predicted, aes(x=date_final, y=value, colour=name)) + geom_line(linewidth=1) + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,1) +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14)) +
  ylab("prevalence of e-cigarette use") +
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

ggsave("STS code/e-cigarette diffusion/outputs/cubic_splines_2010_2023.png", dpi=300, width=33, height=18, units="cm")

# now do the same for disposable e-cig use from 2021 onwards
disposable_prevalence <- sts_sub %>% 
  filter(xyear>=2021 & xyear<=2023) %>% 
  # group by date (quarter), smoking status, cohort
  group_by(date_final, smokstat, cohort) %>% 
  # calculate the weighted prevalence of disposable e-cig users 
  summarise(ecig_prevalence = weighted.mean(alldisposable, `@weight0`, na.rm=T)) %>% 
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
         cat = paste0(smokstat,cohort))

# plot the e-cig time series by cohort and smoking status 
ggplot(disposable_prevalence, aes(x=date_final, y=ecig_prevalence)) + geom_line() + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + 
  theme_bw()

# remove individuals with no good evidence of disposable e-cig diffusion
# all cohorts 1940 + ex-smokers from 1941-1960 + never smokers from 1941-1960 + 1961-1980
disposable_prevalence <- disposable_prevalence %>% 
  filter(cohort!="<1940") %>% 
  filter(cat!="Ex-smoker1941-1960") %>% 
  filter(cat!="Never smoked1941-1960") %>% 
  filter(cat!="Never smoked1961-1980") %>% 
  filter(cat!="Never smoked1981-1990")
  

# estimate all the parameters
disposable_parameters <- list()
disposable_predicted <- list()

for(i in unique(disposable_prevalence$cat)){
  data <- disposable_prevalence %>% filter(cat==i)
  # fit bass model parameters to each subgroup i
  disposable_parameters[[paste(i)]] <- fit_bass(data)
  # insert those parameters back into bass equation to get predicted values
  data$predicted <- bass_diffusion(data$quarter, disposable_parameters[[paste(i)]]$p, disposable_parameters[[paste(i)]]$q, disposable_parameters[[paste(i)]]$m)
  disposable_predicted[[paste(i)]] <- data
}

# process and plot bass predicted values
disposable_predicted <- do.call(rbind, disposable_predicted)
disposable_predicted <- disposable_predicted %>% pivot_longer(c(ecig_prevalence,predicted)) %>% 
  mutate(name=case_when(name=="ecig_prevalence"~"observed",
                        name=="predicted"~"predicted"))

ggplot(disposable_predicted, aes(x=date_final, y=value, colour=name)) + geom_line(linewidth=1) + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,NA) +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14)) +
  ylab("prevalence of e-cigarette use") +
  scale_x_date(date_breaks="1 year", labels=date_format("%Y")) + xlab("Year")

ggsave("STS code/e-cigarette diffusion/outputs/bass_firstattempt_2021_2023.png", dpi=300, width=33, height=18, units="cm")

# generate the full e-cig prevalence data to fit to 
ecig_prevalence <- sts_sub %>% 
  filter(xyear>=2010) %>% 
  # filter out never smokers - we are not estimating diffusion in this group pre 2021
  # filter(smokstat!="Never smoked") %>% 
  # group by date (quarter), smoking status, cohort
  group_by(date_final, smokstat, cohort) %>% 
  # calculate the weighted prevalence of e-cig users 
  summarise(ecig_prevalence = weighted.mean(allecig, `@weight0`, na.rm=T)) %>% 
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

# putting it all together?
ecig_parameters <- do.call(rbind,ecig_parameters) %>% mutate(type="e-cig")
disposable_parameters <- do.call(rbind, disposable_parameters) %>% mutate(type="disposable")

parameters <- rbind(ecig_parameters, disposable_parameters) %>% 
  mutate(cat = paste0(smokstat, cohort))

full_predicted <- list()

for(i in unique(ecig_prevalence$cat)){
  data <- ecig_prevalence %>% filter(cat==i)
  # fit bass model parameters to each subgroup i
  ecig_parameters <- parameters %>% filter(cat==i) %>% filter(type=="e-cig")
  disposable_parameters <- parameters %>% filter(cat==i) %>% filter(type=="disposable")
  data$predicted <- generate_combined_curve(unique(data$quarter), ecig_parameters$p[1], ecig_parameters$q[1], ecig_parameters$m[1],
                          disposable_parameters$p[1], disposable_parameters$q[1], disposable_parameters$m[1])
  full_predicted[[paste(i)]] <- data
}

full_predicted <- full_predicted %>% bind_rows() %>% 
  pivot_longer(c(ecig_prevalence,predicted)) %>% 
  mutate(name=case_when(name=="ecig_prevalence"~"observed",
                        name=="predicted"~"predicted"))

ggplot(full_predicted, aes(x=date_final, y=value, colour=name)) + geom_line(size=1) + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,NA) +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14),
        axis.text.x=element_text(angle=45, vjust=1, hjust=1)) +
  ylab("prevalence of e-cigarette use") +
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

ggsave("STS code/e-cigarette diffusion/outputs/bass_firstattempt_fullmodel_90percent.png", dpi=300, width=33, height=18, units="cm")


parameters <- parameters %>%
  mutate(smokstat=factor(smokstat, levels=c("Never smoked","Ex-smoker","Smoker")),
         type = ifelse(type=="disposable","2021-2023","2010-2020"))

# plotting the innovation and imitation terms for each category 
ggplot(parameters, aes(x=p, y=q, group=smokstat)) + 
  geom_label(aes(label=smokstat), size=3,
            nudge_x=0.007, nudge_y=0.05) + 
  geom_point() + 
  facet_grid(cols=vars(cohort), rows=vars(type)) + xlab("Innovation parameter value (p)") + 
  ylab("Imitation parameter value (q)") + 
  theme_bw() + 
  xlim(0,0.08)

# plotting values of m over cohorts
ggplot(parameters, aes(x=cohort, y=m, group=smokstat,colour=smokstat)) +
  geom_point() + geom_line() + 
  theme_bw() + 
  facet_grid(rows=vars(type)) + 
  ylab("market potential 'm'")
ggsave("STS code/e-cigarette diffusion/outputs/values_of_m_100percent.png", dpi=300, width=33, height=18, units="cm")

# do a comparison of disposable / non disposable
compare <- sts_sub %>% 
  filter(xyear>=2010) %>% 
  # filter out never smokers - we are not estimating diffusion in this group pre 2021
  # filter(smokstat!="Never smoked") %>% 
  # group by date (quarter), smoking status, cohort
  group_by(date_final, smokstat, cohort) %>% 
  mutate(non_disposable = ifelse(allecig==1 & alldisposable==0, 1,0)) %>% 
  # calculate the weighted prevalence of e-cig users 
  summarise(ecig_prevalence = weighted.mean(allecig, `@weight0`, na.rm=T),
            disposable_prevalence = weighted.mean(alldisposable, `@weight0`, na.rm=T),
            nondisposable_prevalence = weighted.mean(non_disposable, `@weight0`, na.rm=T)) %>% 
  ungroup() %>% 
  group_by(smokstat, cohort) %>% 
  arrange(date_final,smokstat,cohort) %>% 
  drop_na() %>% 
  # label the quarter so that it starts at 0
  # quarter 1 = January 2010 (this can be modified)
  mutate(quarter = quarter(date_final),
         year = year(date_final),
         year_num = year-min(year),
         quarter = (year_num * 4) + quarter - min(quarter)) %>% 
  pivot_longer(ecig_prevalence:nondisposable_prevalence)

ggplot(compare, aes(x=date_final, y=value, colour=name)) + 
  geom_line(linewidth=1) + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat)) + ylim(0,NA) +
  theme_bw() +
  theme(legend.position="bottom",
        legend.title=element_blank(),
        text = element_text(size=14),
        axis.text.x=element_text(angle=45, vjust=1, hjust=1)) +
  ylab("prevalence of e-cigarette use") +
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

# looks like an exponential decay function might work for non disposable e-cig use?

