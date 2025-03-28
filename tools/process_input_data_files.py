'''
This tool outputs one of the following files (input data files to the ABM) based on the given input:

initiation_prob1month_STPM.csv
 or
relapse_prob1month_STPM.csv
 or
quit_prob1month_STPM.csv
 or
death_probs_abm_integers.csv
 or
table_attempts_dynamic_extended_integers.csv
 or
table_maintenance_dynamic_extended_integers.csv

Input: smoking_state_transition_probabilities_England2.xlsx
        or
       death_probs_abm.csv
        or
       table_attempts_dynamic_extended.csv
         or
       table_maintenance_dynamic_extended.csv

Output: initiation_prob1month_STPM.csv
         or
        relapse_prob1month_STPM.csv
         or
        quit_prob1month_STPM.csv
         or
        death_probs_abm_integers.csv
         or
        table_attempts_dynamic_extended_integers.csv
         or
        table_maintenance_dynamic_extended_integers.csv

Operations:
        Calculate the monthly initiation probability, 
        relapse probability and quit probability from STPM annual initiation probabilities, 
        relapse probabilities, quit probabilities and death probabilities
        Replace 'Male' with 1, 'Female' with 2, '1_least_deprived' with 1 and '5_most_deprived' with 5 (for all probabilities)  
How to use:

At the end of the script, only call the relevant function(s) and comment out the other function calls using '#').
e.g. the following lines call calculate_monthly_initiation_probability and calculate_monthly_relapse_probability() to output initiation_prob1month_STPM.csv and relapse_prob1month_STPM.csv

calculate_monthly_initiation_probability()
calculate_monthly_relapse_probability()
#calculate_monthly_quit_probability()
#replace_values_of_death_prob_file()
#replace_values_of_exogenous_dynamics_file(attempt_exogenous_dynamics_file,attempt_exogenous_dynamics_file2)
#replace_values_of_exogenous_dynamics_file(maintenance_exogenous_dynamics_file,maintenance_exogenous_dynamics_file2)

running command: python process_input_data_files.py
'''
import pandas as pd

startyear=2011 #start year of simulation
finalyear=2050 #final year of simulation
#set directories of input data files
indir='/mnt/u/smoking_cessation/STPM/'
indir2='/mnt/u/smoking_cessation/dynamic_exogenous_variables/'
#set directory of output files
outdir='../data/'
#specify the input and output
stpm_prob_file=indir+'smoking_state_transition_probabilities_England2.xlsx'
death_prob_file=indir+'death_probs_abm.csv'
attempt_exogenous_dynamics_file=indir2+'table_attempts_dynamic_extended.csv'
attempt_exogenous_dynamics_file2=outdir+'table_attempts_dynamic_extended_integers.csv'
maintenance_exogenous_dynamics_file=indir2+'table_maintenance_dynamic_extended.csv'
maintenance_exogenous_dynamics_file2=outdir+'table_maintenance_dynamic_extended_integers.csv'

def calculate_monthly_initiation_probability():
    print('Running calculate_monthly_initiation_probability()')
    df=pd.read_excel(stpm_prob_file,sheet_name='Initiation')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_start'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_start_1month']
    df=df.drop(columns=['p_start'])#delete probabilty of initiation of 1 year as it is not needed
    df=df.join([p1month])
    outfile=outdir+'initiation_prob1month_STPM.csv'
    df.to_csv(outfile,index=False)
    print('output file: '+outfile)

def calculate_monthly_relapse_probability():
    print('Running calculate_monthly_relapse_probability()')
    df=pd.read_excel(stpm_prob_file,sheet_name='Relapse')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_relapse'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_relapse_1month']
    df=df.drop(columns=['p_relapse'])#delete probabilty of relapse of 1 year as it is not needed
    df=df.join([p1month])
    outfile=outdir+'relapse_prob1month_STPM.csv'
    df.to_csv(outfile,index=False)
    print('output file: '+outfile)

def calculate_monthly_quit_probability():
    print('Running calculate_monthly_quit_probability()')
    df=pd.read_excel(stpm_prob_file,sheet_name='Quit')
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    p1month=1-(1-df['p_quit'])**(1/12) #p4wk=1-(1-p52wk)^(1/12)
    p1month=pd.DataFrame(p1month)
    p1month.columns=['p_quit_1month']
    df=df.drop(columns=['p_quit'])#delete probabilty of initiation of 1 year as it is not needed
    df=df.join([p1month])
    outfile=outdir+'quit_prob1month_STPM.csv'
    df.to_csv(outfile,index=False)
    print('output file: '+outfile)

def replace_values_of_death_prob_file():
    print("Running replace_values_of_death_prob_file()")
    df=pd.read_csv(death_prob_file)
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1,'5_most_deprived': 5})
    outfile=outdir+'death_probs_abm_integer.csv'
    df.to_csv(outfile,index=False)
    print('output file: '+outfile)

def replace_values_of_exogenous_dynamics_file(exogenous_dynamics_file,outfile):
    print("Running replace_values_of_exogenous_dynamics_file(exogenous_dynamics_file,outfile)")
    df=pd.read_csv(exogenous_dynamics_file)
    df=df[(df['year'] >= startyear) & (df['year'] <= finalyear)]
    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
    df['social grade'] = df['social grade'].replace({'ABC1': 0,'C2DE': 1})
    df.to_csv(outdir+outfile,index=False)
    print('output file: '+outfile)

calculate_monthly_initiation_probability()
calculate_monthly_relapse_probability()
#calculate_monthly_quit_probability()
#replace_values_of_death_prob_file()
#replace_values_of_exogenous_dynamics_file(attempt_exogenous_dynamics_file,attempt_exogenous_dynamics_file2)
#replace_values_of_exogenous_dynamics_file(maintenance_exogenous_dynamics_file,maintenance_exogenous_dynamics_file2)
