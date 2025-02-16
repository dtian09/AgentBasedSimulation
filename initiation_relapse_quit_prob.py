#calculate the monthly initiation probability, relapse probability and quit probability from STPM annual probabilities
import pandas as pd

startyear=2011 #start year of simulation
finalyear=2050 #final year of simulation
stpm_prob_file='../repositorysept23/smoking_state_transition_probabilities_England2.xlsx'
outdir='./data/'
#monthly initiation probability
df=pd.read_excel(stpm_prob_file,sheet_name='Initiation')
df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
p1month=1-(1-df['p_start'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
p1month=pd.DataFrame(p1month)
p1month.columns=['p_start_1month']
df=df.drop(columns=['p_start'])#delete probabilty of initiation of 1 year as it is not needed
df=df.join([p1month])
df.to_csv(outdir+'initiation_prob1month_STPM.csv',index=False)
#monthly relapse probability
df=pd.read_excel(stpm_prob_file,sheet_name='Relapse')
df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
p1month=1-(1-df['p_relapse'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
p1month=pd.DataFrame(p1month)
p1month.columns=['p_relapse_1month']
df=df.drop(columns=['p_relapse'])#delete probabilty of relapse of 1 year as it is not needed
df=df.join([p1month])
df.to_csv(outdir+'relapse_prob1month_STPM.csv',index=False)
#monthly quit probability
df=pd.read_excel(stpm_prob_file,sheet_name='Quit')
df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
p1month=1-(1-df['p_quit'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
p1month=pd.DataFrame(p1month)
p1month.columns=['p_quit_1month']
df=df.drop(columns=['p_quit'])#delete probabilty of initiation of 1 year as it is not needed
df=df.join([p1month])
df.to_csv(outdir+'quit_prob1month_STPM.csv',index=False)

