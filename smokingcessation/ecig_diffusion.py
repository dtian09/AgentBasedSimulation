'''
definition of eCigDiffusion class which is a subclass of the MacroEntity class.
'''
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
        self.deltaT=1 #deltaT is the time difference in quarters between two consecutive time steps (months) of ABM
        self.Et=0 #default value 0
        self.deltaEt=0
        self.ecig_users=0
        self.smoking_model=smoking_model
        self.subgroup=None #the population subgroup of this e-cigarette diffusion model
        self.ecig_type=None #the type of e-cigarette (non-disosable or disposable) modelled by this diffusion model
       
    def set_subgroup(self, subgroup : int):
        self.subgroup=subgroup

    def set_eCigType(self, eCigType : int):
        self.ecig_type=eCigType
    
    def allocateDiffusion(self, p : Person):#allocateDiffusion method is called by do_situation method of the COM-BTheory class or STPMTheory class to change this agent to an e-cigarette user or a non-e-cigarette user
        if self.deltaEt > 0:#change this agent to an ecig user
            p.p_ecig_use.set_value(1)
            p.ecig_type = self.ecig_type
            self.deltaEt -=1 #decrease number of new ecig users to create
        elif self.deltaEt < 0: #change this agent to non-ecig user
            p.p_ecig_use.set_value(0)
            p.ecig_type = None  
            self.deltaEt +=1 #decrease number of new non-ecig users to create

    def calculate_ecig_users(self):#calculate number of e-cigarette users
        #calculate_ecig_users is called by calculate_Et method which is called by do_transformation method of eCigDiffusionRegulator class
        self.ecig_users=0
        for agent_id in self.smoking_model.ecig_diff_subgroups[self.subgroup]:
            agent=self.smoking_model.context.agent((agent_id, self.smoking_model.type, self.smoking_model.rank))
            if agent.ecig_type == self.ecig_type:
                self.ecig_users += agent.p_ecig_use.get_value()

    def calculate_Et(self):#calculate the prevalence of e-cigarette (proportion of e-cigarette users)
        #calculate E(t)=1/N * sum(pEcigUse_i) where i is the ith agent; N is size of the population subgroup (e.g. Ex-smoker<1940) of the diffusion model
        #calculate_Et is called by do_transformation method of eCigDiffusionRegulator class
        self.calculate_ecig_users()
        if len(self.smoking_model.ecig_diff_subgroups[self.subgroup]) > 0:
            self.Et=self.ecig_users/len(self.smoking_model.ecig_diff_subgroups[self.subgroup])
        else:
            self.Et=0
        
    def changeInE(self, t):#calculate deltaE(t) of next time step t where t in months (time scale of the ABM)
        #changeInE is called by do_macro_macro method of eCigDiffusionRegulator class
        if t > 0:
            self.deltaEt=self.p*(self.m*np.exp(-self.d*t)-self.Et)+(self.q*np.exp(self.d*t)/self.m)*self.Et*(self.m*np.exp(-self.d*t)-self.Et)
            self.deltaEt=self.deltaEt*self.deltaT*len(self.smoking_model.ecig_diff_subgroups[self.subgroup])
            #sample any fractional agents according to the size of the fractional part of deltaEt (e.g. for 8.9 agents, we get 8 agents for certain and the ninth agent with 90% probability).
            if self.deltaEt > 0:#change deltaEt non-e-cigarette users to e-cigarette users 
                fraction_part = self.deltaEt % 1 
                if fraction_part > 0:
                    if random.uniform(0, 1) <= fraction_part:
                        self.deltaEt=int(self.deltaEt) + 1 #to create a user
            elif self.deltaEt < 0:#change |delta Et| e-cigarette users to e-cigarette non-users
                fraction_part = abs(self.deltaEt) % 1 
                if fraction_part > 0:
                    if random.uniform(0, 1) <= fraction_part: 
                        self.deltaEt=int(self.deltaEt) - 1 #to create an non-user

