library(ggplot2) #for plotting
library(scales) #for date format
library(dplyr) # for data manipulation
library(tidyr)

#wd <- "~/Desktop/e-cigarette_diffusion/"
wd <- "X:/Shared/code/ABM_software/smokingABM/monthly diffusion models"
setwd(wd)

# read in the data 
data <- read.csv("X:/Shared/code/ABM_software/smokingABM/monthly diffusion models/monthly_bass_observed_predicted.csv")
#check any missing months of each subgroup of data (each subgroup should contain months 0 to 288)
d2<-subset(data, smokstat == "Ex-smoker" & cohort == "<1940")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Ex-smoker" & cohort == "1941-1960")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Ex-smoker" & cohort == "1961-1980")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Ex-smoker" & cohort == "1981-1990")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Ex-smoker" & cohort == "1991+")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Smoker" & cohort == "<1940")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Smoker" & cohort == "1941-1960")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Smoker" & cohort == "1961-1980")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Smoker" & cohort == "1981-1990")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Smoker" & cohort == "1991+")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Never smoked" & cohort == "<1940")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Never smoked" & cohort == "1941-1960")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Never smoked" & cohort == "1961-1980")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Never smoked" & cohort == "1981-1990")
setdiff(c(0:288),unique(d2$month))
d2<-subset(data, smokstat == "Never smoked" & cohort == "1991+")
setdiff(c(0:288),unique(d2$month))
outputfolder<-"X:/Shared/code/ABM_software/smokingABM/output/"
exsmoker_less1940 <- scan(paste0(outputfolder,"Exsmoker_less1940.csv"),sep = ",", what = numeric())
exsmoker1941_1960 <- scan(paste0(outputfolder,"Exsmoker1941_1960.csv"),sep = ",", what = numeric())
exsmoker1961_1980 <- scan(paste0(outputfolder,"Exsmoker1961_1980.csv"),sep = ",", what = numeric())
exsmoker1981_1990 <- scan(paste0(outputfolder,"Exsmoker1981_1990.csv"),sep = ",", what = numeric())
neversmoked_over1991 <- scan(paste0(outputfolder,"Neversmoked_over1991.csv"),sep = ",", what = numeric())
neversmoked_over1991[c(1:131)] <- rep(NA,131) 
smoker_less1940 <- scan(paste0(outputfolder,"Smoker_less1940.csv"),sep = ",", what = numeric())
smoker1941_1960 <- scan(paste0(outputfolder,"Smoker1941_1960.csv"),sep = ",", what = numeric())
smoker1961_1980 <- scan(paste0(outputfolder,"Smoker1961_1980.csv"),sep = ",", what = numeric())
smoker1981_1990 <- scan(paste0(outputfolder,"Smoker1981_1990.csv"),sep = ",", what = numeric())
smoker_over1991 <- scan(paste0(outputfolder,"Smoker_over1991.csv"),sep = ",", what = numeric())
exsmoker_over1991 <- scan(paste0(outputfolder,"Exsmoker_over1991.csv"),sep = ",", what = numeric())
indx_of_values_to_remove <- c(29,31,33,35,37,123) #the values at these indices were removed from each subgroup in monthly_bass_observed_predicted.csv
exsmoker_less1940 <- exsmoker_less1940[-indx_of_values_to_remove]
exsmoker1941_1960 <- exsmoker1941_1960[-indx_of_values_to_remove]
exsmoker1961_1980 <- exsmoker1961_1980[-indx_of_values_to_remove]
exsmoker1981_1990 <- exsmoker1981_1990[-indx_of_values_to_remove]
neversmoked_over1991 <- neversmoked_over1991[-indx_of_values_to_remove]
neversmoked_less1940 <- rep(NA, length(neversmoked_over1991))
neversmoked_1941_1960 <- rep(NA, length(neversmoked_over1991))
neversmoked_1961_1980 <- rep(NA, length(neversmoked_over1991))
neversmoked_1981_1990 <- rep(NA, length(neversmoked_over1991))
indx_of_values_to_remove2 <- c(29,31,33,35,37,123, 124, 126, 141, 158, 169, 171)
smoker_less1940 <- smoker_less1940[-indx_of_values_to_remove2]
smoker1941_1960 <- smoker1941_1960[-indx_of_values_to_remove]
smoker1961_1980 <- smoker1961_1980[-indx_of_values_to_remove]
smoker1981_1990 <- smoker1981_1990[-indx_of_values_to_remove]
smoker_over1991 <- smoker_over1991[-indx_of_values_to_remove]
indx_of_values_to_remove3 <- c(1,29,31,33,35,37,123)
exsmoker_over1991 <- exsmoker_over1991[-indx_of_values_to_remove3]
#Merge the vectors together in the following order:
#Ex-smoker	<1940
#Ex-smoker	1941-1960
#Ex-smoker	1961-1980
#Ex-smoker	1981-1990
#Never smoked	<1940
#Never smoked	1941-1960
#Never smoked	1961-1980
#Never smoked	1981-1990
#Never smoked	1991+
#Smoker	<1940
#Smoker	1941-1960
#Smoker	1961-1980
#Smoker	1981-1990
#Smoker	1991+
#Ex-smoker 1991+ (in monthly_bass_observed_predicted.csv, Ex-smoker 1991+ diffusions start from tick 1 (February) onwards only; diffusions of other groups start from tick 0 (January))

v<-c(exsmoker_less1940,
     exsmoker1941_1960,
     exsmoker1961_1980,
     exsmoker1981_1990,
     neversmoked_less1940,
     neversmoked_1941_1960,
     neversmoked_1961_1980,
     neversmoked_1981_1990,
     neversmoked_over1991,
     smoker_less1940, 
     smoker1941_1960,
     smoker1961_1980, 
     smoker1981_1990, 
     smoker_over1991,
     exsmoker_over1991)

data$predicted_ABM <- v

# make sure the date variable is in date format for easy plot labelling
data$date_final <- as.Date(data$date_final)

data <- data %>% pivot_longer(c(observed,predicted,predicted_ABM))

####Add random noise to the 'predicted' column
#set.seed(123) # For reproducibility
#data$predicted_noisy <- data$predicted + runif(n = nrow(data), min = 0.001, max = 0.1)
# Check and convert 'predicted' to numeric
#data$predicted <- as.numeric(as.character(data$predicted))
# Impute NA values in 'predicted' with 0
#data$predicted[is.na(data$predicted)] <- 0
#data$predicted_noisy[is.na(data$predicted_noisy)] <- 0
#data <- data %>% pivot_longer(observed:predicted)
#data <- data %>% pivot_longer(c(observed,predicted_noisy))
#data <- data %>% pivot_longer(c(predicted,predicted_noisy))
#data <- data %>% pivot_longer(c(observed,predicted,predicted_noisy))

data$lowerCI <- ifelse(data$name=="predicted" | data$name=="predicted_ABM", NA, data$lowerCI)
data$upperCI <- ifelse(data$name=="predicted" | data$name=="predicted_ABM", NA, data$upperCI)

# draw plot 
ggplot(data, aes(x=date_final, y=value, colour=name))  + 
  facet_grid(cols=vars(cohort), rows=vars(smokstat), scales="free") + ylim(0,0.8) +
  theme_bw() +
  geom_ribbon(aes(ymin=upperCI, ymax=lowerCI, fill=name), colour=NA, alpha=0.7) + #add error ribbon
  geom_line(linewidth=1) + #add plot line 
  theme(legend.position="bottom", #alter legend and axis text
        legend.title=element_blank(),
        text = element_text(size=14),
        axis.text.x=element_text(angle=45, vjust=1, hjust=1)) +
  ylab("prevalence of e-cigarette use") + 
  #set a vertical line for where the disposable model is added in
  geom_vline(aes(xintercept=as.numeric(as.Date("2021-01-01"))), colour="black", linetype="dashed") + 
  scale_x_date(date_breaks="2 years", labels=date_format("%Y")) + xlab("Year")

# save plot as png file
#ggsave("monthly_bass_combined_projections_ABM.png", dpi=300, width=33, height=18, units="cm")
ggsave("monthly_bass_combined_projections_ABM_subgroup_replicated10times.png", dpi=300, width=33, height=18, units="cm")
