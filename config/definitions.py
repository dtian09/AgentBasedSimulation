import os
from enum import Enum, IntEnum

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

class eCigType(IntEnum):
    "define types of e-cigarette"
    Nondisp = 1
    Disp = 2

class eCigDiffSubGroup(IntEnum):
    """
    define the subgroups of non-disposable and disposable e-cigarette diffusion models
    """
    Exsmokerless1940 = 1
    Exsmoker1941_1960 = 2
    Exsmoker1961_1980 = 3
    Exsmoker1981_1990 = 4
    Exsmoker_over1991 = 5
    Smokerless1940 = 6
    Smoker1941_1960 = 7
    Smoker1961_1980 = 8
    Smoker1981_1990 = 9
    Smoker_over1991 = 10
    Neversmoked_over1991 = 11

class SubGroup(IntEnum):
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

class Theories(Enum):
    """
    Enum class that lists the available theories
    """
    REGSMOKE = 1
    QUITATTEMPT = 2
    QUITSUCCESS = 3
    RELAPSESSTPM = 4
    DemographicsSTPM = 5

#class Regulators(Enum):
#    """
#    Enum class that lists the available regulators of macro entities
#    """
#    eCigDiffReg = 1
#    SocialNetworkReg = 2 

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
    DEAD = 16


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
