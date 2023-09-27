from __future__ import annotations
from core.Theory import Theory
from Level1Attribute import CompositeC, CompositeO, CompositeM
from Level2Attribute import Level2C, Level2O, Level2M
from Person_and_SmokingModel import SmokingModel
from typing import List
from abc import abstractmethod
from checktype import *

class COMBTheory(Theory):

    def __init__(self,smokingModel: SmokingModel,l1:List[Level2C],l2:List[Level2O],l3:List[Level2M]):
        self.capability=0 #capability of the agent of this theory
        self.opportunity=None #opportunity of the agent of this theory
        self.motivation=None #motivation of the agent of this theory
        self.intention_to_quit=None #probability of quit smoking
        self.smokingModel=smokingModel
        self.__compC: CompositeC=None
        self.__compO: CompositeO=None
        self.__compM: CompositeM=None
        check_list_of_Level2C(l1)
        self.__level2C=l1
        check_list_of_Level2O(l2)
        self.__level2O=l2
        check_list_of_Level2M(l3)
        self.__level2M=l3
        self.__behavior=None
    
    @abstractmethod
    def __makeCompC(self):
        #create CompositeC from self.__level2C
        #update __compC
        pass

    @abstractmethod    
    def __makeCompO(self):
        #create CompositeO from self.__level2O
        #update __compO
        pass

    @abstractmethod
    def __makeCompM(self):
        #create CompositeM from self.__level2M
        #update __compM
        pass

    @abstractmethod
    def __doBehaviour(self):
        #update __behaviour
        pass

    def do_situation(self):#run the situation mechanism of the agent of this theory
        pass

    def do_action(self):#run the action mechanism of the agent of this theory
        self.__makeCompC()
        self.__makeCompO()
        self.__makeCompM()
        self.__doBehaviour()




