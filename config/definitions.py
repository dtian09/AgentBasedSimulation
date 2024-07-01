import os
from enum import Enum

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


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
