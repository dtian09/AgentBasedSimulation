#This class implements a quit theory of an agent. 
from __future__ import annotations
from core.Theory import Theory
import repast4py
import random

class QuitTheory(Theory):

    def __init__(self,smokingModel: Person_and_SmokingModel.SmokingModel):
        self.capability=0 #capability of the agent of this theory
        self.opportunity=None #opportunity of the agent of this theory
        self.motivation=None #motivation of the agent of this theory
        self.intention_to_quit=None #probability of quit smoking
        self.smokingModel=smokingModel
        
    def do_situation(self):#run the situation mechanism of the agent of this theory
        #situation mechanism: intervention (macro entity) influences the capability of the agent (micro entity)
        if (self.smokingModel).intervention==1:
            self.capability = (self.smokingModel).intervention_effect
        else:
            self.capability = 1

    def do_action(self):#run the action mechanism of the agent of this theory
        #Set the variable intention_to_quit to a random number drawn from the Normal(0,1).
        #If agent is a smoker at T-1 and capability x intention_to_quit >= threshold
        #   set the state of the agent at T to quitter
        #else
        #   set the state of the agent at T to its state at T-1
        self.intention_to_quit = random.uniform(0,1)
        #print('intention_to_quit:',self._intention_to_quit)
        if self.agent.get_current_state() == 'smoker' and self.capability * self.intention_to_quit >= (self.smokingModel).threshold:
               self.agent.update_state('quitter')
        else:
             self.agent.update_state(self.agent.get_current_state()) #the state at T is same as the state at T-1 




