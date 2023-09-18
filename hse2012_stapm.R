library(hseclean)
library(tidyverse)

hse2012_stapm<-read_2012(root="y:/",
                         file="/Consumption_TA/HSE/Health Survey for England (HSE)/HSE 2012/UKDA-7480-tab/tab/hse2012ai.tab",
                         select_cols = c("tobalc", "all")[2]
)

#select age, sex, IMD quintile and states of agents in HSE 2012. These are used to initialize agent population in ABM software V0.1
smoker_and_ex_smoker_and_never_smoker<-hse2012_stapm %>%
  drop_na(cigst1) %>%
  filter(age>=16) %>%
  mutate(state = as.factor(ifelse(cigst1==4,'smoker',ifelse(cigst1 %in% c(2,3),'ex-smoker',ifelse(cigst1==1,'never_smoker','NA')))),
         sex = recode(sex,"1"="male","2"="female")
  ) %>%
  drop_na(state) %>%
  dplyr::select(age, sex, qimd, state)

write.csv(smoker_and_ex_smoker_and_never_smoker,file="U:/smoking cessation/ABM software/code_v0.1/hse2012_stapm.csv",row.names=F)
