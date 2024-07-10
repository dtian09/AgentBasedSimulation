import os
from enum import Enum

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

#subgroups (calibration targets) as global variables
#Table 1 (initiation age 16-24 by sex)
agelowerbound=16
ageupperbound=24
N_neversmokers_startyear_ages_M=set()
N_neversmokers_endyear_ages_M=set()
N_smokers_endyear_ages_M=set()
N_newquitter_endyear_ages_M=set()
N_ongoingquitter_endyear_ages_M=set()
N_exsmoker_endyear_ages_M=set()
N_dead_endyear_ages_M=set()
N_neversmokers_startyear_ages_F=set()
N_neversmokers_endyear_ages_F=set()
N_smokers_endyear_ages_F=set()	
N_newquitter_endyear_ages_F=set()
N_ongoingquitter_endyear_ages_F=set()
N_exsmoker_endyear_ages_F=set()
N_dead_endyear_ages_F=set()

class SubGroup(Enum):
    """
    define the subgroups (calibration targets) in whole population counts 
    """
    NEVERSMOKERFEMALE = 1
    NEVERSMOKERMALE = 2
    SMOKERFEMALE = 3
    SMOKERMALE = 4
    EXSMOKERFEMALE = 5
    EXSMOKERMALE = 6
    NEWQUITTERFEMALE = 7
    NEWQUITTERMALE = 8
    ONGOINGQUITTERFEMALE = 9
    ONGOINGQUITTERMALE = 10
    DEAD = 11


class Theories(Enum):
    """
    Enum class that lists the available theories
    """
    REGSMOKE = 1
    QUITATTEMPT = 2
    QUITSUCCESS = 3
    RELAPSESSTPM = 4


class AgentState(Enum):
    """
    Enum class that lists the available agent states
    """
    NEVERSMOKE = 1
    SMOKER = 2
    NEWQUITTER = 3
    ONGOINGQUITTER1=4
    ONGOINGQUITTER2=5
    ONGOINGQUITTER3=6
    ONGOINGQUITTER4=7
    ONGOINGQUITTER5=8
    ONGOINGQUITTER6=9
    ONGOINGQUITTER7=10
    ONGOINGQUITTER8=11
    ONGOINGQUITTER9=12
    ONGOINGQUITTER10=13
    ONGOINGQUITTER11=14
    EXSMOKER = 15


class AgentBehaviour(Enum):
    """
    Enum class that lists the available agent behaviours
    """
    UPTAKE = 1
    NOUPTAKE = 2
    QUITATTEMPT = 3
    NOQUITEATTEMPT = 4
    QUITSUCCESS = 5
    QUITFAILURE = 6
    RELAPSE = 7
    NORELAPSE = 8
