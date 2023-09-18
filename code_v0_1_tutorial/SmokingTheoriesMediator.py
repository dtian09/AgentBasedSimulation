from typing import List
from core.Theory import Theory
from core.TheoryMediator import TheoryMediator

#to do: define SmokingTheoriesMediator as subclass of TheoryMediator class
class SmokingTheoriesMediator():

    def __init__(self, theory_list:List[Theory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")
    
    #to do: complete the methods below
    def mediate_situation(self):
        
    def mediate_action(self):
        