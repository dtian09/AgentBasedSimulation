from typing import List
from abc import abstractmethod, ABCMeta
from .MicroAgent import MicroAgent
from .Theory import Theory

class TheoryMediator(metaclass=ABCMeta):

    def __init__(self, theory_list:List[Theory]):
        self.theory_list:List[Theory] = theory_list
        self.agent:MicroAgent = None

    # link agent to this mediator and all theories in the theory list
    def set_agent(self, agent:MicroAgent):
        # Link this mediator to the agent
        self.agent = agent

        # Link each theory to agent
        for theory in self.theory_list:
            theory.set_agent(agent)

    @abstractmethod
    def mediate_situation(self):
        pass

    @abstractmethod
    def mediate_action(self):
        pass
