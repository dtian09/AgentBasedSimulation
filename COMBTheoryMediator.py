from typing import List
from core.TheoryMediator import TheoryMediator
from COMBTheory import COMBTheory

class COMBTheoryMediator(TheoryMediator):

    def __init__(self, theory_list:List[COMBTheory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")

    def mediate_situation(self):
        self.theory_list[0].do_situation()

    def mediate_action(self):
        self.theory_list[0].do_action()
