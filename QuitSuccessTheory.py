from __future__ import annotations
from Level2Attribute import Level2C, Level2O, Level2M
from typing import List
import COMBTheory 
from checktype import *
from Person_and_SmokingModel import SmokingModel

class QuitSuccessTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,l1:List[Level2C],l2:List[Level2O],l3:List[Level2M]):
      super().__init__(smokingModel, l1, l2, l3)

    def __makeCompC():
        #make compositeC from self.level2C
        pass

    def __makeCompO():
        #make compositeO from self.level2O
        pass

    def __makeCompM():
        #make compositeM from self.level2M
        pass

    def __doBehaviour(self):
        pass

    def do_situation(self):
        pass

    def dolearning(self):
        pass 



