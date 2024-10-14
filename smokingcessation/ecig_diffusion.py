from mbssm.macro_entity import MacroEntity
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.person import Person
import numpy as np
import random

class eCigDiffusion(MacroEntity):
    def __init__(self, p, q, m, d, smoking_model : SmokingModel):
        super().__init__()
        self.p=p
        self.q=q
        self.m=m
        self.d=d
        self.deltaT=1/3 #deltaT is the time difference in quarters between two consecutive time steps (months) of ABM
        self.Et=0 #initialize e-cig prevalence at tick 0
        self.deltaEt=0 #initialize new e-cig users at tick 0
        self.smoking_model=smoking_model
        self.subgroup=None #the population subgroup of this e-cigarette diffusion model
        self.ecig_type=None #the type of e-cigarette (non-disosable or disposable) modelled by this diffusion model
        self.deltaEt_agents=[] #if deltaEt > 0, deltEt_agents is the list of the agents of this subgroup who will become e-cig users when allocateDiffusion method is called iteratively; if deltaEt < 0, deltEt_agents is the list of the e-cig users who will become non-e-cig users when allocateDiffusion method is called iteratively. 
        self.ecig_users=0

    def set_subgroup(self, subgroup : int):
        self.subgroup=subgroup

    def set_eCigType(self, eCigType : int):
        self.ecig_type=eCigType

    def calculate_ecig_users(self):
        for agent_id in self.smoking_model.ecig_diff_subgroups[self.subgroup]:
            agent=self.smoking_model.context.agent((agent_id, self.smoking_model.type, self.smoking_model.rank))
            self.ecig_users += agent.p_ecig_use.get_value()
    
    def calculate_Et(self):#calculate E(t), the prevalence of e-cigarette
        #calculate E(t)=1/N * sum(pEcigUse_i) where i is the ith agent; N is size of the population subgroup (e.g. Ex-smoker<1940) of the diffusion model
        self.calculate_ecig_users()
        if len(self.smoking_model.ecig_diff_subgroups[self.subgroup]) > 0:
            return self.ecig_users/len(self.smoking_model.ecig_diff_subgroups[self.subgroup])
        else:
            return 0
        
    def changeInE(self, t):#calculate deltaE(t) where t in months
        if t > 0:
            self.deltaEt=self.p*(self.m*np.exp(-self.d*t/3)-self.Et)+(self.q*np.exp(self.d*t/3)/self.m)*self.Et*(self.m*np.exp(-self.d*t/3)-self.Et)
            self.deltaEt=self.deltaEt*self.deltaT
            #sample any fractional agents according to the size of the fractional part of deltaEt (e.g. for 8.9 agents, we get 8 agents for certain and the ninth agent with 90% probability).
            #draw a random value r from uniform[0,1]
            #if r <= fraction part
            #then deltaEt = integer part of delatEt + 1
            #else deltaEt = integer part of deltaEt
            fraction_part = self.deltaEt % 1 
            if fraction_part > 0:
                if random.uniform(0, 1) <= fraction_part:
                    self.deltaEt=int(self.deltaEt) + 1
            else:
                self.deltaEt=int(self.deltaEt)
        else:
            self.deltaEt=0
        self.deltaEt_agents=[] #reset to empty list

    def allocateDiffusion(self, p : Person):
        if self.deltaEt > 0:#change this agent to an ecig user
            p.p_ecig_use.set_value(1)
            p.ecig_type = self.ecig_type
            self.deltaEt -=1 #update number of new ecig users to create
            self.deltaEt_agents.remove(p.get_id())
        elif self.deltaEt < 0: #change this agent to non-ecig user
            p.p_ecig_use.set_value(0)
            p.ecig_type = None  
            self.deltaEt +=1 #update number of new non-ecig users to create
            self.deltaEt_agents.remove(p.get_id())