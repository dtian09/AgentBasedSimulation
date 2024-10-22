###declaration of global variables to represent calibration targets
#Initiation of age cateory=[agelowerbound,ageupperbound] by sex)
agelowerbound=16
ageupperbound=24
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
#Initiation of age cateory=[agelowerbound,ageupperbound] by IMD)
N_neversmokers_startyear_ages_IMD1=set()
N_neversmokers_endyear_ages_IMD1=0
N_smokers_endyear_ages_IMD1=0
N_newquitter_endyear_ages_IMD1=0
N_ongoingquitter_endyear_ages_IMD1=0
N_exsmoker_endyear_ages_IMD1=0
N_dead_endyear_ages_IMD1=0
N_neversmokers_startyear_ages_IMD2=set()
N_neversmokers_endyear_ages_IMD2=0
N_smokers_endyear_ages_IMD2=0
N_newquitter_endyear_ages_IMD2=0
N_ongoingquitter_endyear_ages_IMD2=0
N_exsmoker_endyear_ages_IMD2=0
N_dead_endyear_ages_IMD2=0
N_neversmokers_startyear_ages_IMD3=set()
N_neversmokers_endyear_ages_IMD3=0
N_smokers_endyear_ages_IMD3=0
N_newquitter_endyear_ages_IMD3=0
N_ongoingquitter_endyear_ages_IMD3=0
N_exsmoker_endyear_ages_IMD3=0
N_dead_endyear_ages_IMD3=0
N_neversmokers_startyear_ages_IMD4=set()
N_neversmokers_endyear_ages_IMD4=0
N_smokers_endyear_ages_IMD4=0
N_newquitter_endyear_ages_IMD4=0
N_ongoingquitter_endyear_ages_IMD4=0
N_exsmoker_endyear_ages_IMD4=0
N_dead_endyear_ages_IMD4=0
N_neversmokers_startyear_ages_IMD5=set()
N_neversmokers_endyear_ages_IMD5=0
N_smokers_endyear_ages_IMD5=0
N_newquitter_endyear_ages_IMD5=0
N_ongoingquitter_endyear_ages_IMD5=0
N_exsmoker_endyear_ages_IMD5=0
N_dead_endyear_ages_IMD5=0
#Quitting of age cateory1=[agelowerbound1,ageupperbound1] by sex)
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
#Quitting of age cateory2=[agelowerbound2,ageupperbound2] by sex)
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
#Quitting of age cateory=[agelowerbound3,ageupperbound3] by IMD)
agelowerbound3=25
ageupperbound3=74
N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1=set()
N_smokers_endyear_ages3_IMD1=0
N_newquitters_endyear_ages3_IMD1=0
N_ongoingquitters_endyear_ages3_IMD1=0
N_dead_endyear_ages3_IMD1=0
N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2=set()
N_smokers_endyear_ages3_IMD2=0
N_newquitters_endyear_ages3_IMD2=0
N_ongoingquitters_endyear_ages3_IMD2=0
N_dead_endyear_ages3_IMD2=0
N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3=set()
N_smokers_endyear_ages3_IMD3=0
N_newquitters_endyear_ages3_IMD3=0
N_ongoingquitters_endyear_ages3_IMD3=0
N_dead_endyear_ages3_IMD3=0
N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4=set()
N_smokers_endyear_ages3_IMD4=0
N_newquitters_endyear_ages3_IMD4=0
N_ongoingquitters_endyear_ages3_IMD4=0
N_dead_endyear_ages3_IMD4=0
N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5=set()
N_smokers_endyear_ages3_IMD5=0
N_newquitters_endyear_ages3_IMD5=0
N_ongoingquitters_endyear_ages3_IMD5=0
N_dead_endyear_ages3_IMD5=0

def initialize_global_variables_of_subgroups():
    #Initiation of age cateory=[agelowerbound,ageupperbound] by sex)
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
    #Initiation of age cateory=[agelowerbound,ageupperbound] by IMD)
    global N_neversmokers_startyear_ages_IMD1
    global N_neversmokers_endyear_ages_IMD1
    global N_smokers_endyear_ages_IMD1
    global N_newquitter_endyear_ages_IMD1
    global N_ongoingquitter_endyear_ages_IMD1
    global N_exsmoker_endyear_ages_IMD1
    global N_dead_endyear_ages_IMD1
    global N_neversmokers_startyear_ages_IMD2
    global N_neversmokers_endyear_ages_IMD2
    global N_smokers_endyear_ages_IMD2
    global N_newquitter_endyear_ages_IMD2
    global N_ongoingquitter_endyear_ages_IMD2
    global N_exsmoker_endyear_ages_IMD2
    global N_dead_endyear_ages_IMD2
    global N_neversmokers_startyear_ages_IMD3
    global N_neversmokers_endyear_ages_IMD3
    global N_smokers_endyear_ages_IMD3
    global N_newquitter_endyear_ages_IMD3
    global N_ongoingquitter_endyear_ages_IMD3
    global N_exsmoker_endyear_ages_IMD3
    global N_dead_endyear_ages_IMD3
    global N_neversmokers_startyear_ages_IMD4
    global N_neversmokers_endyear_ages_IMD4
    global N_smokers_endyear_ages_IMD4
    global N_newquitter_endyear_ages_IMD4
    global N_ongoingquitter_endyear_ages_IMD4
    global N_exsmoker_endyear_ages_IMD4
    global N_dead_endyear_ages_IMD4
    global N_neversmokers_startyear_ages_IMD5
    global N_neversmokers_endyear_ages_IMD5
    global N_smokers_endyear_ages_IMD5
    global N_newquitter_endyear_ages_IMD5
    global N_ongoingquitter_endyear_ages_IMD5
    global N_exsmoker_endyear_ages_IMD5
    global N_dead_endyear_ages_IMD5

    N_neversmokers_startyear_ages_IMD1=set()
    N_neversmokers_endyear_ages_IMD1=0
    N_smokers_endyear_ages_IMD1=0
    N_newquitter_endyear_ages_IMD1=0
    N_ongoingquitter_endyear_ages_IMD1=0
    N_exsmoker_endyear_ages_IMD1=0
    N_dead_endyear_ages_IMD1=0
    N_neversmokers_startyear_ages_IMD2=set()
    N_neversmokers_endyear_ages_IMD2=0
    N_smokers_endyear_ages_IMD2=0
    N_newquitter_endyear_ages_IMD2=0
    N_ongoingquitter_endyear_ages_IMD2=0
    N_exsmoker_endyear_ages_IMD2=0
    N_dead_endyear_ages_IMD2=0
    N_neversmokers_startyear_ages_IMD3=set()
    N_neversmokers_endyear_ages_IMD3=0
    N_smokers_endyear_ages_IMD3=0
    N_newquitter_endyear_ages_IMD3=0
    N_ongoingquitter_endyear_ages_IMD3=0
    N_exsmoker_endyear_ages_IMD3=0
    N_dead_endyear_ages_IMD3=0
    N_neversmokers_startyear_ages_IMD4=set()
    N_neversmokers_endyear_ages_IMD4=0
    N_smokers_endyear_ages_IMD4=0
    N_newquitter_endyear_ages_IMD4=0
    N_ongoingquitter_endyear_ages_IMD4=0
    N_exsmoker_endyear_ages_IMD4=0
    N_dead_endyear_ages_IMD4=0
    N_neversmokers_startyear_ages_IMD5=set()
    N_neversmokers_endyear_ages_IMD5=0
    N_smokers_endyear_ages_IMD5=0
    N_newquitter_endyear_ages_IMD5=0
    N_ongoingquitter_endyear_ages_IMD5=0
    N_exsmoker_endyear_ages_IMD5=0
    N_dead_endyear_ages_IMD5=0
    #Quitting of age cateory1=[agelowerbound1,ageupperbound1] by sex)
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
    #Quitting of age cateory2=[agelowerbound2,ageupperbound2] by sex)
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
    #Quitting of age cateory=[agelowerbound3,ageupperbound3] by IMD)
    global N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1
    global N_smokers_endyear_ages3_IMD1
    global N_newquitters_endyear_ages3_IMD1
    global N_ongoingquitters_endyear_ages3_IMD1
    global N_dead_endyear_ages3_IMD1
    global N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2
    global N_smokers_endyear_ages3_IMD2
    global N_newquitters_endyear_ages3_IMD2
    global N_ongoingquitters_endyear_ages3_IMD2
    global N_dead_endyear_ages3_IMD2
    global N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3
    global N_smokers_endyear_ages3_IMD3
    global N_newquitters_endyear_ages3_IMD3
    global N_ongoingquitters_endyear_ages3_IMD3
    global N_dead_endyear_ages3_IMD3
    global N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4
    global N_smokers_endyear_ages3_IMD4
    global N_newquitters_endyear_ages3_IMD4
    global N_ongoingquitters_endyear_ages3_IMD4
    global N_dead_endyear_ages3_IMD4
    global N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5
    global N_smokers_endyear_ages3_IMD5
    global N_newquitters_endyear_ages3_IMD5
    global N_ongoingquitters_endyear_ages3_IMD5
    global N_dead_endyear_ages3_IMD5

    N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1=set()
    N_smokers_endyear_ages3_IMD1=0
    N_newquitters_endyear_ages3_IMD1=0
    N_ongoingquitters_endyear_ages3_IMD1=0
    N_dead_endyear_ages3_IMD1=0
    N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2=set()
    N_smokers_endyear_ages3_IMD2=0
    N_newquitters_endyear_ages3_IMD2=0
    N_ongoingquitters_endyear_ages3_IMD2=0
    N_dead_endyear_ages3_IMD2=0
    N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3=set()
    N_smokers_endyear_ages3_IMD3=0
    N_newquitters_endyear_ages3_IMD3=0
    N_ongoingquitters_endyear_ages3_IMD3=0
    N_dead_endyear_ages3_IMD3=0
    N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4=set()
    N_smokers_endyear_ages3_IMD4=0
    N_newquitters_endyear_ages3_IMD4=0
    N_ongoingquitters_endyear_ages3_IMD4=0
    N_dead_endyear_ages3_IMD4=0
    N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5=set()
    N_smokers_endyear_ages3_IMD5=0
    N_newquitters_endyear_ages3_IMD5=0
    N_ongoingquitters_endyear_ages3_IMD5=0
    N_dead_endyear_ages3_IMD5=0
