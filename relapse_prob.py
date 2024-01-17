#calculate relapse probability of 4 weeks from STPM relapse probability (1 year)
import pandas as pd
import numpy as np

df=pd.read_excel('smoking_state_transition_probabilities_England.xlsx',sheet_name='Relapse')
#get the subset of 2003 (1st year of HSE survey) to 2018 (last year of HSE survey)
df=df[(df['year'] >= 2003) & (df['year'] <= 2018)]
p4wk=1-(1-df['p_relapse'])**(1/13) #p4wk=1-(1-p52wk)^(1/13)
p4wk=pd.DataFrame(p4wk)
p4wk.columns=['p_relapse_4wk']
df=df.drop(columns=['p_relapse'])#delete probabilty of relapse of 1 year as it is not needed
df=df.join([p4wk])
df.to_csv('relapse_prob4wk.csv',index=False)