from typing import List
from abc import abstractmethod, ABC
from .MicroAgent import MicroAgent
from .Theory import Theory

class TheoryMediator(ABC):

    def __init__(self, theoryList:List[Theory]):
        self.theoryList:List[Theory] = theoryList
        self.agent:MicroAgent = None

    # link agent to this mediator and all theories in the theory list
    def setAgent(self, agent:MicroAgent):
        # Link this mediator to the agent
        self.agent = agent

        # Link each theory to agent
        for theory in self.theoryList:
            theory.setAgent(agent)

    @abstractmethod
    def mediateSituation(self):
        pass

    @abstractmethod
    def mediateAction(self):
        pass
