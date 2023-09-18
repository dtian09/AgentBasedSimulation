#This class implements a quit theory of an agent. 
from __future__ import annotations
from core.Theory import Theory
import random

class SocialNetworkQuitTheory(Theory):

    def __init__(self, smokingModel: SmokingModel.SmokingModel):
        super().__init__()
        self.capability=0 #capability of the agent of this theory
        self.opportunity=None #opportunity of the agent of this theory
        self.motivation=None #motivation of the agent of this theory
        self.intention_to_quit=None #probability of quit smoking
        self.smokingModel=smokingModel
        self.threshold=None

    def calculate_proportion_of_smoking_friends(self):
        s=0
        nbs=list(self.smokingModel.graph.adj.get(self.agent))#get the neighbours of the agent
        for nb in nbs:
            if nb.get_current_state()=='smoker':
                s+=1
        return s/len(nbs)

    def do_situation(self):#run the situation mechanism of the agent of this theory
        #situation mechanism: intervention (macro entity) influences the capability of the agent (micro entity)
        #                     the social network determines proportion of smoking friends of the agent
        if (self.smokingModel).intervention==1:
            self.capability = (self.smokingModel).intervention_effect
        else:
            self.capability = 1
        self.agent.proportion_of_smoking_friends=self.calculate_proportion_of_smoking_friends()
        #print('proportion of smoking friends: ',self.agent.proportion_of_smoking_friends)

    def do_action(self):#run the action mechanism of the agent of this theory
        #Set the variable intention_to_quit to a random number drawn from the Normal(0,1).
        #If agent is a smoker at T-1 and capability x intention_to_quit >= threshold
        #   set the state of the agent at T to quitter
        #else
        #   set the state of the agent at T to its state at T-1 
        self.threshold=self.agent.proportion_of_smoking_friends
        self.intention_to_quit = random.uniform(0,1)
        #print('intention_to_quit:',self._intention_to_quit)
        if self.agent.get_current_state() == 'smoker' and self.capability * self.intention_to_quit >= self.threshold:
               self.agent.update_state(state='quitter')#quitter is an agent who is making a quit attempt
        else:
             self.agent.update_state(state=self.agent.get_current_state()) #the state at T is same as the state at T-1 
        
    
        

