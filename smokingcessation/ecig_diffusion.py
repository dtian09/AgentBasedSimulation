from mbssm.macro_entity import MacroEntity
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.person import Person
import numpy as np
from config.definitions import eCigDiffSubGroup

class eCigDiffusion(MacroEntity):
    def __init__(self, p, q, m, d, smoking_model : SmokingModel):
        super().__init__()
        self.p=p
        self.q=q
        self.m=m
        self.d=d
        self.deltaT=1/3 #deltaT is the time difference between two consecutive time steps 
        self.Et=None #initialize e-cig prevalence
        self.deltaEt=None #initialize new e-cig users
        self.smoking_model=smoking_model
        self.subgroup=None #the population subgroup of this e-cigarette diffusion
        self.ecig_type=None #the type of e-cigarette (non-disosable or disposable) represented by this diffusion model

    def set_subgroup(self, subgroup : int):
        self.subgroup=subgroup

    def set_eCigType(self, eCigType : int):
        self.ecig_type=eCigType

    def calculate_Et(self):#calculate E(t), the prevalence of e-cigarette
        #calculate E(t)=1/N * sum(pEcigUse_i) where i is the ith agent; N is size of the population subgroup (e.g. Ex-smoker<1940) of the diffusion model
        if self.subgroup == eCigDiffSubGroup.Exsmokerless1940:
           N=len(self.smoking_model.exsmoker_less_1940)

    def changeInE(self, t):#calculate deltaE(t)
        if self.t > 0:
            self.deltaEt=self.p*(self.m*np.exp(-self.d*t/3)-self.Et)+(self.q*np.exp(self.d*t/3)/self.m)*self.Et*(self.m*np.exp(-self.d*t/3)-self.Et)
            self.deltaEt=self.deltaEt*self.deltaT
            self.deltaEt*len(self.subgroup)
            #sample any fractional agents according to the size of the fraction (e.g. for 8.9 agents, we get 8 agents for certain and the ninth agent with 90% probability).
            #draw a random value v from uniform[0,1]
            #if v >= fraction
            #then deltaEt = integer part of delatEt + 1
            #else deltaEt = integer part of deltaEt
        else:
            self.deltaEt=0

    def allocateDiffusion(self, p : Person): #also decrement deltaEt
        #Input: a person of the subgroup is a non-ecig user
        #threshold = a random value from uniform distribution [0,1]
        #if E(t) >= threshold
        #then agent adapts e-cig
        #else agent does not
     