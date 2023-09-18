from typing import List
from core.Theory import Theory
from core.TheoryMediator import TheoryMediator

class SmokingTheoriesMediator(TheoryMediator):

    def __init__(self, theory_list:List[Theory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")

    def mediate_situation(self):
        self.theory_list[0].do_situation()

    def mediate_action(self):
        self.theory_list[0].do_action()
