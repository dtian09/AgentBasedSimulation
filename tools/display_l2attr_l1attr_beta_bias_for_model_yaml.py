'''
this tool displays the betas of the Level 2 attributes of the data dictionary and Level 1 attributes (C, O and M) in the following format (used in model.yaml):

uptake.oAge.beta: 0.1
attempt.oAge.beta: 0.1
success.oAge.beta: 0.1
uptake.C.beta: 0.1
uptake.O.beta: 0.1
uptake.M.beta: 0.1
uptake.bias: 0.1
etc.

The output displayed can be copied into model.yaml and the betas and biases can be set to the actual values.

running command: python display_l2attr_l1attr_beta_bias_for_model_yaml.py
'''
import warnings
warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression, and has match groups.*")
import pandas as pd

data_dictionary='/mnt/u/smoking_cessation/data dictionary/Data dictionary for CRUK smoking ABM v2.xlsx'
df=pd.read_excel(data_dictionary,sheet_name='Just PRSM variables - MASTER')
attributes=df['synthetic population variables needed']

clevel2_attributes = attributes[attributes.str.contains(r'^(c[A-Z])', na=False)]#get the capability (c) related level 2 attribute names from the data dictionary e.g. cAge
uptake_clevel2_attributes = 'uptake.' + clevel2_attributes.astype(str) + '.beta' #clevel2_attributes of regular smoking uptake
attempt_clevel2_attributes = 'attempt.' + clevel2_attributes.astype(str) + '.beta' #clevel2_attributes of quit attempt 
maintenance_clevel2_attributes = 'maintenance.'+ clevel2_attributes.astype(str) + '.beta' #clevel2_attributes of quit maintenance

olevel2_attributes = attributes[attributes.str.contains(r'^(o[A-Z])', na=False)]#get the opportunity (o) related level 2 attribute names from the data dictionary e.g. oAge
uptake_olevel2_attributes = 'uptake.' + olevel2_attributes.astype(str) + '.beta' #olevel2_attributes of regular smoking uptake
attempt_olevel2_attributes = 'attempt.' + olevel2_attributes.astype(str) + '.beta' #olevel2_attributes of quit attempt 
maintenance_olevel2_attributes = 'maintenance.'+ olevel2_attributes.astype(str) + '.beta' #olevel2_attributes of quit maintenance

mlevel2_attributes = attributes[attributes.str.contains(r'^(m[A-Z])', na=False)]#get the opportunity (m) related level 2 attribute names from the data dictionary e.g. oAge
uptake_mlevel2_attributes = 'uptake.' + mlevel2_attributes.astype(str) + '.beta' #mlevel2_attributes of regular smoking uptake
attempt_mlevel2_attributes = 'attempt.' + mlevel2_attributes.astype(str) + '.beta' #mlevel2_attributes of quit attempt 
maintenance_mlevel2_attributes = 'maintenance.'+ mlevel2_attributes.astype(str) + '.beta' #mlevel2_attributes of quit maintenance

for item in list(uptake_clevel2_attributes):
    print(item+': 0.1')
print()
for item in list(uptake_olevel2_attributes):
    print(item+': 0.1')
print()
for item in list(uptake_mlevel2_attributes):
    print(item+': 0.1')
print()
level1_attributes='uptake.C.beta: 0.1\n' \
'uptake.O.beta: 0.1\n' \
'uptake.M.beta: 0.1\n' \
'uptake.bias: 0.1'
print(level1_attributes+'\n')

for item in list(attempt_clevel2_attributes):
    print(item+': 0.1')
print()
for item in list(attempt_olevel2_attributes):
    print(item+': 0.1')
print()
for item in list(attempt_mlevel2_attributes):
    print(item+': 0.1')
print()
level1_attributes='attempt.C.beta: 0.1\n' \
'attempt.O.beta: 0.1\n' \
'attempt.M.beta: 0.1\n' \
'attempt.bias: 0.1'
print(level1_attributes+'\n')

for item in list(maintenance_clevel2_attributes):
    print(item+': 0.1')
print()
for item in list(maintenance_olevel2_attributes):
    print(item+': 0.1')
print()
for item in list(maintenance_mlevel2_attributes):
    print(item+': 0.1')
print()
level1_attributes='maintenance.C.beta: 0.1\n' \
'maintenance.O.beta: 0.1\n' \
'maintenance.M.beta: 0.1\n' \
'maintenance.bias: 0.1'
print(level1_attributes)