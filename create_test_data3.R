#1. Create a baseline population of ABM to verify e-cig diffusions of ABM (non-disposable diffusions start from January 2010) by:
#   enriching STS quarter 1 2010 population with some STPM variables
#2. Count the e-cig users of e-cig diffusion subgroups at the start time of non-disposable diffusions (and disposable diffusions (start on quarter 1 2022)) in order to initialize the diffusion models of the ABM at tick 0.
#
library(hseclean)
library(tidyverse)
library(haven)

wd<-"X:/Shared/code/ABM_software/smokingABM/"
setwd(wd)

source("create_test_data_functions.R")

sts <- read_sav("X:/Shared/STS data/STS and ATS files Mar 24/Latest omnibus SPSS data file/omni209_39.1_65.2cot_31.3a_25.4s_recodes_95.5sa.sav",
                col_select = c(xwave, month, xyear, quarter, sexz, actage, sgz, ab, smoker, smokstat, allecig, alldisposable, qspend_1, chac, basecpd3, sturge, q632x4, behc, qmotiv3, qmotiv4, q632b7_1, q632e9))

sts_sub <- sts %>% 
  dplyr::select(xwave, month, xyear, quarter, sexz, actage, sgz, ab, smoker, smokstat, allecig, alldisposable, qspend_1, chac, basecpd3, sturge, q632x4, behc, qmotiv3, qmotiv4, q632b7_1, q632e9)

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
  drop_na(smokstat) %>%
  mutate(smokstat=ifelse(smokstat==0, "never_smoker",
                         ifelse(smokstat==1, "ex-smoker",
                                ifelse(smokstat==2, "ex-smoker",
                                       ifelse(smokstat==3,"smoker", NA)))),
         birthyear = xyear-actage,
         cohort = cut(birthyear,
                      breaks=c(0,1940,1960,1980,1990,2020),
                      #labels=c("<1940","1941-1960","1961-1980","1981-1990","1991+")))
                      labels=c("0","1","2","3","4")))
                      
sts2010_jan <- sts_sub %>% filter(date_final=='2010-01-01') #non disposable ecig start at 2010
sts2022_jan <- sts_sub %>% filter(date_final=='2022-01-01') #disposable ecig start at 2020

#count ecig users of non-disposable ecig diffusion models
ecigusers_exsmokerless1940 <- sts2010_jan %>% filter(smokstat=='ex-smoker',cohort=='0', allecig==1)
nrow(ecigusers_exsmokerless1940)  
ecigusers_exsmoker1941to1960 <- sts2010_jan %>% filter(smokstat=='ex-smoker',cohort=='1', allecig==1)  
nrow(ecigusers_exsmoker1941to1960)
ecigusers_smokerless1940 <- sts2010_jan %>% filter(smokstat=='smoker',cohort=='0', allecig==1)
nrow(ecigusers_smokerless1940)
ecigusers_smoker1941to1960 <- sts2010_jan %>% filter(smokstat=='smoker',cohort=='1', allecig==1)
nrow(ecigusers_smoker1941to1960)
ecigusers_smoker1961to1980 <- sts2010_jan %>% filter(smokstat=='smoker',cohort=='2', allecig==1)
nrow(ecigusers_smoker1961to1980)
#count ecig users of disposable ecig diffusion models
ecigusers_exsmoker1961to1980 <- sts2022_jan %>% filter(smokstat=='ex-smoker',cohort=='2', allecig==1, alldisposable==1)
nrow(ecigusers_exsmoker1961to1980)
ecigusers_exsmoker1981to1990 <- sts2022_jan %>% filter(smokstat=='ex-smoker',cohort=='3', allecig==1, alldisposable==1)
nrow(ecigusers_exsmoker1981to1990)
ecigusers_exsmokerover1991 <- sts2022_jan %>% filter(smokstat=='ex-smoker',cohort=='4', allecig==1, alldisposable==1)
nrow(ecigusers_exsmokerover1991)
ecigusers_nevermokerover1991 <- sts2022_jan %>% filter(smokstat=='never-smoker',cohort=='4', allecig==1, alldisposable==1)
nrow(ecigusers_nevermokerover1991)
ecigusers_smoker1941to1960 <- sts2022_jan %>% filter(smokstat=='smoker',cohort=='1', allecig==1, alldisposable==1)  
nrow(ecigusers_smoker1941to1960)
ecigusers_smoker1961to1980 <- sts2022_jan %>% filter(smokstat=='smoker',cohort=='2', allecig==1, alldisposable==1)  
nrow(ecigusers_smoker1961to1980)
ecigusers_smoker1981to1990 <- sts2022_jan %>% filter(smokstat=='smoker',cohort=='3', allecig==1, alldisposable==1)  
nrow(ecigusers_smoker1981to1990)
ecigusers_smokerover1991 <- sts2022_jan %>% filter(smokstat=='smoker',cohort=='4', allecig==1, alldisposable==1)  
nrow(ecigusers_smokerover1991)

#rename some attributes as personal attributes
sts2010_jan <- sts2010_jan %>%
               rename(state=smokstat,
                             pAge=actage,
                             pGender=sexz,
                             pCohort=cohort,
                             pExpenditure=qspend_1,
                             pVareniclineUse=chac,
                             pCigConsumptionPrequit=basecpd3,
                             pECigUse=allecig
                            )
#enrich the STS data with some STPM variables as personal attributes
hse2012_stapm<-read_2012(root="x:/",
                         file="Shared/HSE data/HSE2012/UKDA-7480-tab/tab/hse2012ai.tab"
                        )
sts2010_jan$pIMDquintile=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("qimd"))
sts2010_jan$pEducationalLevel=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("topqual3"))
sts2010_jan$pSEP=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("nssec3"))
sts2010_jan$pRegion=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("gor1"))
sts2010_jan$pSocialHousing=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("tenureb"))
sts2010_jan$pMentalHealthCondition=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("illaff7"))
sts2010_jan$pAlcoholConsumption=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("alcbase"))
sts2010_jan$pNRTUse=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("nicot"))
sts2010_jan$pYearsSinceQuit=select_random_values_of_variable(sts2010_jan,hse2012_stapm,c("endsmoke"))
#add the associated level 2 attributes of the personal attributes to the selected data
#table of associated level 2 attributes: https://docs.google.com/document/d/1h8MFvetOZEOIcEHD7Bckfbc63AoQQZfFSNIA30HpCMw/edit
sts2010_jan <- sts2010_jan %>%
  mutate(cAge=pAge,
         oAge=pAge,
         mAge=pAge,
         mGender=pGender,
         oEducationalLevel=pEducationalLevel,
         oSEP=pSEP,
         oGeographicLocality=pRegion,
         oSocialHousing=pSocialHousing,
         cMentalHealthConditions=pMentalHealthCondition,
         cAlcoholConsumption=pAlcoholConsumption,
         oAlcoholConsumption=pAlcoholConsumption,
         cPrescriptionNRT=pNRTUse,
         mUseOfNRT=pNRTUse,
         cEcigaretteUse=pECigUse,
         cCigConsumptionPrequit=pCigConsumptionPrequit,
         #oExpenditurePerStick (missing in STS data)
         #mExpenditurePerStick (missing in STS data)
         mSpendingOnCig=pExpenditure,
         cVareniclineUse=pVareniclineUse
         )

sts2010_jan <- sts2010_jan %>%
  rename(cCigAddictStrength=sturge,
         mEnjoymentOfSmoking=q632x4,
         cUseOfBehaviourSupport=behc,
         mIntentionToQuit=qmotiv3,
         mDesireToStopSmoking=qmotiv4,
         mNumberOfRecentQuitAttempts=q632b7_1,
         mSmokerIdentity=q632e9
        )

#vars<-c("pAge","pGender","pIMDquintile","pCohort","pEducationalLevel","pSEP","pRegion","pSocialHousing","pMentalHealthCondition","pAlcoholConsumption","pNRTUse","pExpenditure","pECigUse","pVareniclineUse","pYearsSinceQuit","cAge","oAge","mAge","mGender","oEducationalLevel","oSEP","oGeographicLocality","oSocialHousing","cMentalHealthConditions","cAlcoholConsumption","oAlcoholConsumption","cPrescriptionNRT","mUseOfNRT","cEcigaretteUse","cCigConsumptionPrequit","mSpendingOnCig","cVareniclineUse","cCigAddictStrength","mEnjoymentOfSmoking","cUseOfBehaviourSupport","mIntentionToQuit","mDesireToStopSmoking","mNumberOfRecentQuitAttempts","mSmokerIdentity")
#sts2010_jan<-convert_to_integer_type(sts2010_jan,vars)
write.csv(sts2010_jan,file="X:/Shared/code/ABM_software/smokingABM/testdata_STS2010_Jan_enriched_with_STPM_data.csv",row.names=F)

#replicate the population a few times
df <- read.csv("X:/Shared/code/ABM_software/smokingABM/data/testdata_STS2010_Jan_enriched_with_STPM_data.csv")
increase_population_k_times <- function(df,k){   
  for(i in 1:k-1){
     df<-rbind(df, df)
  }
  return(df)
}
k<-10 #increase the population k times
df2<-increase_population_k_times(df,k)
write.csv(df2,file=paste0("X:/Shared/code/ABM_software/smokingABM/data/testdata",as.character(k),"_STS2010_Jan_enriched_with_STPM_data.csv"))
