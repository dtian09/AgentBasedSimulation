'''
defining the abstract class TheoryMediator
'''
from typing import List
from abc import abstractmethod, ABC

from mbssm.theory import Theory


class TheoryMediator(ABC):

    def __init__(self, theory_list: List[Theory]):
        self.theory_list: List[Theory] = theory_list

    @abstractmethod
    def mediate_situation(self, agent):
        pass

    @abstractmethod
    def mediate_action(self, agent):
        pass
