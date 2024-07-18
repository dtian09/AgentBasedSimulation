###definition of global variables to represent calibration targets

#define the age group of Table 1 (initiation age 16-24 by sex) and Table 2 (initiation age 16-24 by IMD+sex)
agelowerbound=16
ageupperbound=24
#initialize subgroups (calibration targets) of Table 1 (initiation age 16-24 by sex)
N_neversmokers_startyear_ages_M=set()
N_neversmokers_endyear_ages_M=0
N_smokers_endyear_ages_M=0
N_newquitter_endyear_ages_M=0
N_ongoingquitter_endyear_ages_M=0
N_exsmoker_endyear_ages_M=0
N_dead_endyear_ages_M=0
N_neversmokers_startyear_ages_F=set()
N_neversmokers_endyear_ages_F=0
N_smokers_endyear_ages_F=0	
N_newquitter_endyear_ages_F=0
N_ongoingquitter_endyear_ages_F=0
N_exsmoker_endyear_ages_F=0
N_dead_endyear_ages_F=0
#initialize subgroups (calibration targets) of Table 2 (initiation age 16-24 by IMD+sex)
N_neversmokers_startyear_ages_M_IMD1=set()
N_neversmokers_endyear_ages_M_IMD1=0
N_smokers_endyear_ages_M_IMD1=0
N_newquitter_endyear_ages_M_IMD1=0
N_ongoingquitter_endyear_ages_M_IMD1=0
N_exsmoker_endyear_ages_M_IMD1=0
N_dead_endyear_ages_M_IMD1=0
N_neversmokers_startyear_ages_F_IMD1=set()
N_neversmokers_endyear_ages_F_IMD1=0
N_smokers_endyear_ages_F_IMD1=0
N_newquitter_endyear_ages_F_IMD1=0
N_ongoingquitter_endyear_ages_F_IMD1=0
N_exsmoker_endyear_ages_F_IMD1=0
N_dead_endyear_ages_F_IMD1=0
N_neversmokers_startyear_ages_M_IMD2=set()
N_neversmokers_endyear_ages_M_IMD2=0
N_smokers_endyear_ages_M_IMD2=0
N_newquitter_endyear_ages_M_IMD2=0
N_ongoingquitter_endyear_ages_M_IMD2=0
N_exsmoker_endyear_ages_M_IMD2=0
N_dead_endyear_ages_M_IMD2=0
N_neversmokers_startyear_ages_F_IMD2=set()
N_neversmokers_endyear_ages_F_IMD2=0
N_smokers_endyear_ages_F_IMD2=0
N_newquitter_endyear_ages_F_IMD2=0
N_ongoingquitter_endyear_ages_F_IMD2=0
N_exsmoker_endyear_ages_F_IMD2=0
N_dead_endyear_ages_F_IMD2=0
N_neversmokers_startyear_ages_M_IMD3=set()
N_neversmokers_endyear_ages_M_IMD3=0
N_smokers_endyear_ages_M_IMD3=0
N_newquitter_endyear_ages_M_IMD3=0
N_ongoingquitter_endyear_ages_M_IMD3=0
N_exsmoker_endyear_ages_M_IMD3=0
N_dead_endyear_ages_M_IMD3=0
N_neversmokers_startyear_ages_F_IMD3=set()
N_neversmokers_endyear_ages_F_IMD3=0
N_smokers_endyear_ages_F_IMD3=0
N_newquitter_endyear_ages_F_IMD3=0
N_ongoingquitter_endyear_ages_F_IMD3=0
N_exsmoker_endyear_ages_F_IMD3=0
N_dead_endyear_ages_F_IMD3=0
N_neversmokers_startyear_ages_M_IMD4=set()
N_neversmokers_endyear_ages_M_IMD4=0
N_smokers_endyear_ages_M_IMD4=0
N_newquitter_endyear_ages_M_IMD4=0
N_ongoingquitter_endyear_ages_M_IMD4=0
N_exsmoker_endyear_ages_M_IMD4=0
N_dead_endyear_ages_M_IMD4=0
N_neversmokers_startyear_ages_F_IMD4=set()
N_neversmokers_endyear_ages_F_IMD4=0
N_smokers_endyear_ages_F_IMD4=0
N_newquitter_endyear_ages_F_IMD4=0
N_ongoingquitter_endyear_ages_F_IMD4=0
N_exsmoker_endyear_ages_F_IMD4=0
N_neversmokers_startyear_ages_M_IMD5=set()
N_neversmokers_endyear_ages_M_IMD5=0
N_smokers_endyear_ages_M_IMD5=0
N_newquitter_endyear_ages_M_IMD5=0
N_ongoingquitter_endyear_ages_M_IMD5=0
N_exsmoker_endyear_ages_M_IMD5=0
N_dead_endyear_ages_M_IMD5=0
N_neversmokers_startyear_ages_F_IMD5=set()
N_neversmokers_endyear_ages_F_IMD5=0
N_smokers_endyear_ages_F_IMD5=0
N_newquitter_endyear_ages_F_IMD5=0
N_ongoingquitter_endyear_ages_F_IMD5=0
N_exsmoker_endyear_ages_F_IMD5=0
N_dead_endyear_ages_F_IMD5=0
#initialize subgroups (calibration targets) Table 3 (quit by age + sex)
#define age group1
agelowerbound1=25
ageupperbound1=49
N_smokers_ongoingquitters_newquitters_startyear_ages1_M=set()
N_smokers_endyear_ages1_M=0
N_newquitters_endyear_ages1_M=0
N_ongoingquitters_endyear_ages1_M=0
N_dead_endyear_ages1_M=0
N_smokers_ongoingquitters_newquitters_startyear_ages1_F=set()
N_smokers_endyear_ages1_F=0
N_newquitters_endyear_ages1_F=0
N_ongoingquitters_endyear_ages1_F=0
N_dead_endyear_ages1_F=0
#define age group2
agelowerbound2=50
ageupperbound2=74
N_smokers_ongoingquitters_newquitters_startyear_ages2_M=set()
N_smokers_endyear_ages2_M=0
N_newquitters_endyear_ages2_M=0
N_ongoingquitters_endyear_ages2_M=0
N_dead_endyear_ages2_M=0
N_smokers_ongoingquitters_newquitters_startyear_ages2_F=set()
N_smokers_endyear_ages2_F=0
N_newquitters_endyear_ages2_F=0
N_ongoingquitters_endyear_ages2_F=0
N_dead_endyear_ages2_F=0
#initialize subgroups (calibration targets) of Table 4 (quit age 25-74 by IMD)
#define age group for Table 4
agelowerbound3=25
ageupperbound3=74
N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1=set()
N_smokers_endyear_ages_IMD1=0
N_newquitters_endyear_ages_IMD1=0
N_ongoingquitters_endyear_ages_IMD1=0
N_dead_endyear_ages_IMD1=0
N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2=set()
N_smokers_endyear_ages_IMD2=0
N_newquitters_endyear_ages_IMD2=0
N_ongoingquitters_endyear_ages_IMD2=0
N_dead_endyear_ages_IMD2=0
N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3=set()
N_smokers_endyear_ages_IMD3=0
N_newquitters_endyear_ages_IMD3=0
N_ongoingquitters_endyear_ages_IMD3=0
N_dead_endyear_ages_IMD3=0
N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4=set()
N_smokers_endyear_ages_IMD4=0
N_newquitters_endyear_ages_IMD4=0
N_ongoingquitters_endyear_ages_IMD4=0
N_dead_endyear_ages_IMD4=0
N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5=set()
N_smokers_endyear_ages_IMD5=0
N_newquitters_endyear_ages_IMD5=0
N_ongoingquitters_endyear_ages_IMD5=0
N_dead_endyear_ages_IMD5=0

def initialize_global_variables_of_subgroups():
    #Table 1 (initiation age 16-24 by sex)
    global N_neversmokers_startyear_ages_M
    global N_neversmokers_endyear_ages_M
    global N_smokers_endyear_ages_M
    global N_newquitter_endyear_ages_M
    global N_ongoingquitter_endyear_ages_M
    global N_exsmoker_endyear_ages_M
    global N_dead_endyear_ages_M
    global N_neversmokers_startyear_ages_F
    global N_neversmokers_endyear_ages_F
    global N_smokers_endyear_ages_F	
    global N_newquitter_endyear_ages_F
    global N_ongoingquitter_endyear_ages_F
    global N_exsmoker_endyear_ages_F
    global N_dead_endyear_ages_F
    
    N_neversmokers_startyear_ages_M=set()
    N_neversmokers_endyear_ages_M=0
    N_smokers_endyear_ages_M=0
    N_newquitter_endyear_ages_M=0
    N_ongoingquitter_endyear_ages_M=0
    N_exsmoker_endyear_ages_M=0
    N_dead_endyear_ages_M=0
    N_neversmokers_startyear_ages_F=set()
    N_neversmokers_endyear_ages_F=0
    N_smokers_endyear_ages_F=0	
    N_newquitter_endyear_ages_F=0
    N_ongoingquitter_endyear_ages_F=0
    N_exsmoker_endyear_ages_F=0
    N_dead_endyear_ages_F=0
    #Table 2 (initiation age 16-24 by IMD+sex)
    global N_neversmokers_startyear_ages_M_IMD1
    global N_neversmokers_endyear_ages_M_IMD1
    global N_smokers_endyear_ages_M_IMD1
    global N_newquitter_endyear_ages_M_IMD1
    global N_ongoingquitter_endyear_ages_M_IMD1
    global N_exsmoker_endyear_ages_M_IMD1
    global N_dead_endyear_ages_M_IMD1
    global N_neversmokers_startyear_ages_F_IMD1
    global N_neversmokers_endyear_ages_F_IMD1
    global N_smokers_endyear_ages_F_IMD1
    global N_newquitter_endyear_ages_F_IMD1
    global N_ongoingquitter_endyear_ages_F_IMD1
    global N_exsmoker_endyear_ages_F_IMD1
    global N_dead_endyear_ages_F_IMD1
    global N_neversmokers_startyear_ages_M_IMD2
    global N_neversmokers_endyear_ages_M_IMD2
    global N_smokers_endyear_ages_M_IMD2
    global N_newquitter_endyear_ages_M_IMD2
    global N_ongoingquitter_endyear_ages_M_IMD2
    global N_exsmoker_endyear_ages_M_IMD2
    global N_dead_endyear_ages_M_IMD2
    global N_neversmokers_startyear_ages_F_IMD2
    global N_neversmokers_endyear_ages_F_IMD2
    global N_smokers_endyear_ages_F_IMD2
    global N_newquitter_endyear_ages_F_IMD2
    global N_ongoingquitter_endyear_ages_F_IMD2
    global N_exsmoker_endyear_ages_F_IMD2
    global N_dead_endyear_ages_F_IMD2
    global N_neversmokers_startyear_ages_M_IMD3
    global N_neversmokers_endyear_ages_M_IMD3
    global N_smokers_endyear_ages_M_IMD3
    global N_newquitter_endyear_ages_M_IMD3
    global N_ongoingquitter_endyear_ages_M_IMD3
    global N_exsmoker_endyear_ages_M_IMD3
    global N_dead_endyear_ages_M_IMD3
    global N_neversmokers_startyear_ages_F_IMD3
    global N_neversmokers_endyear_ages_F_IMD3
    global N_smokers_endyear_ages_F_IMD3
    global N_newquitter_endyear_ages_F_IMD3
    global N_ongoingquitter_endyear_ages_F_IMD3
    global N_exsmoker_endyear_ages_F_IMD3
    global N_dead_endyear_ages_F_IMD3
    global N_neversmokers_startyear_ages_M_IMD4
    global N_neversmokers_endyear_ages_M_IMD4
    global N_smokers_endyear_ages_M_IMD4
    global N_newquitter_endyear_ages_M_IMD4
    global N_ongoingquitter_endyear_ages_M_IMD4
    global N_exsmoker_endyear_ages_M_IMD4
    global N_dead_endyear_ages_M_IMD4
    global N_neversmokers_startyear_ages_F_IMD4
    global N_neversmokers_endyear_ages_F_IMD4
    global N_smokers_endyear_ages_F_IMD4
    global N_newquitter_endyear_ages_F_IMD4
    global N_ongoingquitter_endyear_ages_F_IMD4
    global N_exsmoker_endyear_ages_F_IMD4
    global N_neversmokers_startyear_ages_M_IMD5
    global N_neversmokers_endyear_ages_M_IMD5
    global N_smokers_endyear_ages_M_IMD5
    global N_newquitter_endyear_ages_M_IMD5
    global N_ongoingquitter_endyear_ages_M_IMD5
    global N_exsmoker_endyear_ages_M_IMD5
    global N_dead_endyear_ages_M_IMD5
    global N_neversmokers_startyear_ages_F_IMD5
    global N_neversmokers_endyear_ages_F_IMD5
    global N_smokers_endyear_ages_F_IMD5
    global N_newquitter_endyear_ages_F_IMD5
    global N_ongoingquitter_endyear_ages_F_IMD5
    global N_exsmoker_endyear_ages_F_IMD5
    global N_dead_endyear_ages_F_IMD5

    N_neversmokers_startyear_ages_M_IMD1=set()
    N_neversmokers_endyear_ages_M_IMD1=0
    N_smokers_endyear_ages_M_IMD1=0
    N_newquitter_endyear_ages_M_IMD1=0
    N_ongoingquitter_endyear_ages_M_IMD1=0
    N_exsmoker_endyear_ages_M_IMD1=0
    N_dead_endyear_ages_M_IMD1=0
    N_neversmokers_startyear_ages_F_IMD1=set()
    N_neversmokers_endyear_ages_F_IMD1=0
    N_smokers_endyear_ages_F_IMD1=0
    N_newquitter_endyear_ages_F_IMD1=0
    N_ongoingquitter_endyear_ages_F_IMD1=0
    N_exsmoker_endyear_ages_F_IMD1=0
    N_dead_endyear_ages_F_IMD1=0
    N_neversmokers_startyear_ages_M_IMD2=set()
    N_neversmokers_endyear_ages_M_IMD2=0
    N_smokers_endyear_ages_M_IMD2=0
    N_newquitter_endyear_ages_M_IMD2=0
    N_ongoingquitter_endyear_ages_M_IMD2=0
    N_exsmoker_endyear_ages_M_IMD2=0
    N_dead_endyear_ages_M_IMD2=0
    N_neversmokers_startyear_ages_F_IMD2=set()
    N_neversmokers_endyear_ages_F_IMD2=0
    N_smokers_endyear_ages_F_IMD2=0
    N_newquitter_endyear_ages_F_IMD2=0
    N_ongoingquitter_endyear_ages_F_IMD2=0
    N_exsmoker_endyear_ages_F_IMD2=0
    N_dead_endyear_ages_F_IMD2=0
    N_neversmokers_startyear_ages_M_IMD3=set()
    N_neversmokers_endyear_ages_M_IMD3=0
    N_smokers_endyear_ages_M_IMD3=0
    N_newquitter_endyear_ages_M_IMD3=0
    N_ongoingquitter_endyear_ages_M_IMD3=0
    N_exsmoker_endyear_ages_M_IMD3=0
    N_dead_endyear_ages_M_IMD3=0
    N_neversmokers_startyear_ages_F_IMD3=set()
    N_neversmokers_endyear_ages_F_IMD3=0
    N_smokers_endyear_ages_F_IMD3=0
    N_newquitter_endyear_ages_F_IMD3=0
    N_ongoingquitter_endyear_ages_F_IMD3=0
    N_exsmoker_endyear_ages_F_IMD3=0
    N_dead_endyear_ages_F_IMD3=0
    N_neversmokers_startyear_ages_M_IMD4=set()
    N_neversmokers_endyear_ages_M_IMD4=0
    N_smokers_endyear_ages_M_IMD4=0
    N_newquitter_endyear_ages_M_IMD4=0
    N_ongoingquitter_endyear_ages_M_IMD4=0
    N_exsmoker_endyear_ages_M_IMD4=0
    N_dead_endyear_ages_M_IMD4=0
    N_neversmokers_startyear_ages_F_IMD4=set()
    N_neversmokers_endyear_ages_F_IMD4=0
    N_smokers_endyear_ages_F_IMD4=0
    N_newquitter_endyear_ages_F_IMD4=0
    N_ongoingquitter_endyear_ages_F_IMD4=0
    N_exsmoker_endyear_ages_F_IMD4=0
    N_neversmokers_startyear_ages_M_IMD5=set()
    N_neversmokers_endyear_ages_M_IMD5=0
    N_smokers_endyear_ages_M_IMD5=0
    N_newquitter_endyear_ages_M_IMD5=0
    N_ongoingquitter_endyear_ages_M_IMD5=0
    N_exsmoker_endyear_ages_M_IMD5=0
    N_dead_endyear_ages_M_IMD5=0
    N_neversmokers_startyear_ages_F_IMD5=set()
    N_neversmokers_endyear_ages_F_IMD5=0
    N_smokers_endyear_ages_F_IMD5=0
    N_newquitter_endyear_ages_F_IMD5=0
    N_ongoingquitter_endyear_ages_F_IMD5=0
    N_exsmoker_endyear_ages_F_IMD5=0
    N_dead_endyear_ages_F_IMD5=0
    #Table 3 (quit by age + sex)
    global N_smokers_ongoingquitters_newquitters_startyear_ages1_M
    global N_smokers_endyear_ages1_M
    global N_newquitters_endyear_ages1_M
    global N_ongoingquitters_endyear_ages1_M
    global N_dead_endyear_ages1_M
    global N_smokers_ongoingquitters_newquitters_startyear_ages1_F
    global N_smokers_endyear_ages1_F
    global N_newquitters_endyear_ages1_F
    global N_ongoingquitters_endyear_ages1_F
    global N_dead_endyear_ages1_F
    global N_smokers_ongoingquitters_newquitters_startyear_ages2_M
    global N_smokers_endyear_ages2_M
    global N_newquitters_endyear_ages2_M
    global N_ongoingquitters_endyear_ages2_M
    global N_dead_endyear_ages2_M
    global N_smokers_ongoingquitters_newquitters_startyear_ages2_F
    global N_smokers_endyear_ages2_F
    global N_newquitters_endyear_ages2_F
    global N_ongoingquitters_endyear_ages2_F
    global N_dead_endyear_ages2_F

    N_smokers_ongoingquitters_newquitters_startyear_ages1_M=set()
    N_smokers_endyear_ages1_M=0
    N_newquitters_endyear_ages1_M=0
    N_ongoingquitters_endyear_ages1_M=0
    N_dead_endyear_ages1_M=0
    N_smokers_ongoingquitters_newquitters_startyear_ages1_F=set()
    N_smokers_endyear_ages1_F=0
    N_newquitters_endyear_ages1_F=0
    N_ongoingquitters_endyear_ages1_F=0
    N_dead_endyear_ages1_F=0
    N_smokers_ongoingquitters_newquitters_startyear_ages2_M=set()
    N_smokers_endyear_ages2_M=0
    N_newquitters_endyear_ages2_M=0
    N_ongoingquitters_endyear_ages2_M=0
    N_dead_endyear_ages2_M=0
    N_smokers_ongoingquitters_newquitters_startyear_ages2_F=set()
    N_smokers_endyear_ages2_F=0
    N_newquitters_endyear_ages2_F=0
    N_ongoingquitters_endyear_ages2_F=0
    N_dead_endyear_ages2_F=0
    #Table 4 (quit age 25-74 by IMD)
    global N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1
    global N_smokers_endyear_ages_IMD1
    global N_newquitters_endyear_ages_IMD1
    global N_ongoingquitters_endyear_ages_IMD1
    global N_dead_endyear_ages_IMD1
    global N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2
    global N_smokers_endyear_ages_IMD2
    global N_newquitters_endyear_ages_IMD2
    global N_ongoingquitters_endyear_ages_IMD2
    global N_dead_endyear_ages_IMD2
    global N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3
    global N_smokers_endyear_ages_IMD3
    global N_newquitters_endyear_ages_IMD3
    global N_ongoingquitters_endyear_ages_IMD3
    global N_dead_endyear_ages_IMD3
    global N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4
    global N_smokers_endyear_ages_IMD4
    global N_newquitters_endyear_ages_IMD4
    global N_ongoingquitters_endyear_ages_IMD4
    global N_dead_endyear_ages_IMD4
    global N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5
    global N_smokers_endyear_ages_IMD5
    global N_newquitters_endyear_ages_IMD5
    global N_ongoingquitters_endyear_ages_IMD5
    global N_dead_endyear_ages_IMD5

    N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1=set()
    N_smokers_endyear_ages_IMD1=0
    N_newquitters_endyear_ages_IMD1=0
    N_ongoingquitters_endyear_ages_IMD1=0
    N_dead_endyear_ages_IMD1=0
    N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2=set()
    N_smokers_endyear_ages_IMD2=0
    N_newquitters_endyear_ages_IMD2=0
    N_ongoingquitters_endyear_ages_IMD2=0
    N_dead_endyear_ages_IMD2=0
    N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3=set()
    N_smokers_endyear_ages_IMD3=0
    N_newquitters_endyear_ages_IMD3=0
    N_ongoingquitters_endyear_ages_IMD3=0
    N_dead_endyear_ages_IMD3=0
    N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4=set()
    N_smokers_endyear_ages_IMD4=0
    N_newquitters_endyear_ages_IMD4=0
    N_ongoingquitters_endyear_ages_IMD4=0
    N_dead_endyear_ages_IMD4=0
    N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5=set()
    N_smokers_endyear_ages_IMD5=0
    N_newquitters_endyear_ages_IMD5=0
    N_ongoingquitters_endyear_ages_IMD5=0
    N_dead_endyear_ages_IMD5=0
