'''
This script creates the following STPM probabilities files as input to the ABM:

initiation_prob1month_STPM.csv,
relapse_prob1month_STPM.csv
quit_prob1month_STPM.csv
death_probs_abm_integer.csv

Input: smoking_state_transition_probabilities_England2.xlsx
       death_probs_abm.csv
Output: initiation_prob1month_STPM.csv,
        relapse_prob1month_STPM.csv
        quit_prob1month_STPM.csv
        death_probs_abm_integer.csv
Operations:
        Calculate the monthly initiation probability, relapse probability and quit probability from STPM annual initiation probabilities, relapse probabilities, quit probabilities and death probabilities
        Replace 'Male' with 1, 'Female' with 2, '1_least_deprived' with 1 and '5_most_deprived' with 5 

usage: python initiation_relapse_quit_death_prob.py
'''
import pandas as pd

startyear=2011 #start year of simulation
finalyear=2050 #final year of simulation
outdir='./data/'
stpm_prob_file='./smoking_state_transition_probabilities_England2.xlsx'
death_prob_file='./death_probs_abm.csv'

def calculate_monthly_initiation_probability():
    df=pd.read_excel(stpm_prob_file,sheet_name='Initiation')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_start'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_start_1month']
    df=df.drop(columns=['p_start'])#delete probabilty of initiation of 1 year as it is not needed
    df=df.join([p1month])
    df.to_csv(outdir+'initiation_prob1month_STPM.csv',index=False)

def calculate_monthly_relapse_probability():
    df=pd.read_excel(stpm_prob_file,sheet_name='Relapse')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_relapse'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_relapse_1month']
    df=df.drop(columns=['p_relapse'])#delete probabilty of relapse of 1 year as it is not needed
    df=df.join([p1month])
    df.to_csv(outdir+'relapse_prob1month_STPM.csv',index=False)

def calculate_monthly_quit_probability():
    df=pd.read_excel(stpm_prob_file,sheet_name='Quit')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_quit'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_quit_1month']
    df=df.drop(columns=['p_quit'])#delete probabilty of initiation of 1 year as it is not needed
    df=df.join([p1month])
    df.to_csv(outdir+'quit_prob1month_STPM.csv',index=False)

def replace_values_of_death_prob_file():
    df=pd.read_csv(death_prob_file)
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    df.to_csv(outdir+'death_probs_abm_integer.csv',index=False)

replace_values_of_death_prob_file()
