#create a synthetic population for ABM simulation
#use hseclean library to pre-process HSE data. The pre-processed data is STAPM data.
library(hseclean)
library(tidyverse)

#HSE 2012 data has no quitters as HSE has no information about the number of quit attempts from 2011 to 2015.
hse2012_stapm<-read_2012(root="x:/",
                         file="Shared/HSE data/HSE2012/UKDA-7480-tab/tab/hse2012ai.tab",
                         select_cols = c("tobalc", "all")[2]
                         )
#create variable 'cohort' using clean_age function (https://stapm.github.io/hseclean/reference/clean_age.html) 
#birth cohort variable takes single years of birth: 1923, 1924,...,2012 
hse2012_stapm <- clean_age(hse2012_stapm)
#merge values of cohort into groups: 1900-1909, 1910-1919 etc (coded 0, 1, etc) 
cohortcuts=c(1900,
             1909,
             1910,
             1919,
             1920,
             1929,
             1930,
             1939,
             1940,
             1949,
             1950,
             1959,
             1960,
             1969,
             1970,
             1979,
             1980,
             1989,
             1990,
             1999,
             2000,
             2009,
             2010,
             2019)
n<-length(cohortcuts)-1
cohortlabs=c()
for(i in 1:n){
  cohortlabs[i]<-toString(i-1)#cohort labels: 0, 1, 2,...
}
#select the personal attributes and the state variable
smoker_and_ex_smoker_and_never_smoker<-hse2012_stapm %>%
        drop_na(cigst1) %>%
        filter(age>=16) %>%
        mutate(state = as.factor(ifelse(cigst1==4,'smoker',ifelse(cigst1 %in% c(2,3),'ex-smoker',ifelse(cigst1==1,'never_smoker','NA')))),
               sex = recode(sex,"1"="male","2"="female")
               ) %>%
        drop_na(state) %>%
        dplyr::select(age,
                      sex,
                      qimd,
                      state,
                      cohort,
                      topqual3,
                      nssec3,
                      gor1,
                      tenureb,
                      illaff7,
                      alcbase,
                      nicot
                      ) %>%
        mutate(cohort = cut(cohort, breaks=cohortcuts, labels=cohortlabs)) %>%
        dplyr::rename(pAge=age,
                      pGender=sex,
                      pIMDquintile=qimd,
                      pCohort=cohort,
                      pEducationalLevel=topqual3,
                      pSEP=nssec3,
                      pRegion=gor1,
                      pSocialHousing=tenureb,
                      pMentalHealthCondition=illaff7,
                      pAlcohol=alcbase,
                      pNRTUse=nicot
                      )
#add pExpenditure: HSE has no expenditure variable, STS has variable qspend_1 (spending on cigarette per week)
d<-read_rds(file="X:/Shared/STS data/STS and ATS files August 23/STS and ATS files August 23/Latest omnibus SPSS data file/wave202.rds")
df2012 <- d %>% filter(xyear==2012) %>% mutate(ids=1:nrow(.))

select_random_values_of_variable <-function(df,df2,vars) {
  #select n random values of variables (vars) of df2 where n is number of rows of df
  vals<-unique(df2[[vars[1]]])
  vals2<-na.omit(vals)
  if(is_empty(vals2)==F) {
    return(sample(vals2,replace=T,size=nrow(df)))
  }
  else
  {print('all NAN')
   return(vals)}
}
smoker_and_ex_smoker_and_never_smoker$pExpenditure=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("qspend_1"))
smoker_and_ex_smoker_and_never_smoker$pECigUse=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("allecig"))
smoker_and_ex_smoker_and_never_smoker$pVareniclineUse=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("chac"))
smoker_and_ex_smoker_and_never_smoker$pCigConsumptionPrequit=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("basecpd3"))
smoker_and_ex_smoker_and_never_smoker$pYearsSinceQuit=rep('None',nrow(smoker_and_ex_smoker_and_never_smoker))
#add associated level 2 attributes of the personal attributes to the test data
#table of associated level 2 attributes: https://docs.google.com/document/d/1h8MFvetOZEOIcEHD7Bckfbc63AoQQZfFSNIA30HpCMw/edit
smoker_and_ex_smoker_and_never_smoker<-smoker_and_ex_smoker_and_never_smoker %>%
        mutate(cAge=pAge,
               oAge=pAge,
               mAge=pAge,
               mGender=pGender,
               oEducationalLevel=pEducationalLevel,
               oSEP=pSEP,
               oGeographicLocality=pRegion,
               oSocialHousing=pSocialHousing,
               cMentalHealthConditions=pMentalHealthCondition,
               cAlcoholConsumption=pAlcohol,
               oAlcoholConsumption=pAlcohol,
               cPrescriptionNRT=pNRTUse,
               mUseOfNRT=pNRTUse,
               cEcigaretteUse=pECigUse,
               cCigConsumptionPrequit=pCigConsumptionPrequit,
               #oExpenditurePerStick (missing in STS data)
               #mExpenditurePerStick (missing in STS data)
               mSpendingOnCig=pExpenditure,
               cVareniclineUse=pVareniclineUse
        )
###add the remaining level 2 attributes (from STS data) to the test dataset
#for each individual in the population, randomly choose a value from each level 2 attribute
#oPrevalenceOfSmokingInGeographicLocality (missing in STS data)
#o%OfSmokersInSocialNetwork (missing in STS data)
#oEaseOfAccess (missing in STS data)
#oParentalSmoking (missing in STS data)
#cImpulsivity (missing in STS data)
#mPro-smokingAttitude (missing in STS data)
#mExperimentation (missing in STS data)
#cUnderstandingOfSmokingHarms (missing in STS data)
#mExSmokerSelfIdentity (missing in STS data)
#oSmokingCessationPromptsTriggers (missing in STS data)
#mSelfEfficacy (missing in STS data)
smoker_and_ex_smoker_and_never_smoker$cCigAddictStrength=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("sturge"))#sturge or ftnd1
smoker_and_ex_smoker_and_never_smoker$mEnjoymentOfSmoking=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("q632x4"))
smoker_and_ex_smoker_and_never_smoker$cUseOfBehaviourSupport=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("behc"))
smoker_and_ex_smoker_and_never_smoker$mIntentionToQuit=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("qmotiv3"))
smoker_and_ex_smoker_and_never_smoker$mDesireToStopSmoking=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("qmotiv4"))
smoker_and_ex_smoker_and_never_smoker$mNumberOfRecentQuitAttempts=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2012,c("q632b7_1"))
df2008 <- d %>% filter(xyear==2008) %>% mutate(ids=1:nrow(.))#q632e9 is in waves 6 to 28 only
smoker_and_ex_smoker_and_never_smoker$mSmokerIdentity=select_random_values_of_variable(smoker_and_ex_smoker_and_never_smoker,df2008,c("q632e9"))
write.csv(smoker_and_ex_smoker_and_never_smoker,file="X:/Shared/code/ABM_software/repositorysept23/testdata.csv",row.names=F)

