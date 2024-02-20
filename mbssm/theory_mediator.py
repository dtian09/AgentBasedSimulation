from typing import Set
from abc import abstractmethod, ABC

from mbssm.theory import Theory


class TheoryMediator(ABC):

    def __init__(self, theory_list: Set[Theory]):
        self.theory_list: Set[Theory] = theory_list

    @abstractmethod
    def get_current_theory_of_agent(self, agent):
        pass

    @abstractmethod
    def mediate_situation(self, agent):
        pass

    @abstractmethod
    def mediate_action(self, agent):
        pass
