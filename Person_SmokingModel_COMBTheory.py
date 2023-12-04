from mpi4py import MPI
import numpy as np
from repast4py import parameters
from typing import Dict, List
#import repast4py
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner
from repast4py.context import SharedContext
from core.MicroAgent import MicroAgent
from core.Model import Model
from core.Theory import Theory
from core.TheoryMediator import TheoryMediator
from Level2Attribute import *
import pandas as pd
from checktype import *
from abc import abstractmethod

class Person(MicroAgent):
    def __init__(self, 
                 smokingModel, 
                 id:int, 
                 type:int, 
                 rank:int,
                 age:int=None,
                 gender:str=None, 
                 qimd:float=None,
                 cohort:int=None,
                 educationalLevel:int=None,
                 SEP:int=None,
                 region:int=None,
                 socialHousing:int=None,
                 mentalHealthConds:int=None,
                 alcohol:int=None,
                 expenditure:int=None,
                 NRTUse:int=None,
                 vareniclineUse:int=None,
                 cigConsumptionPrequit:int=None,
                 eCigUse:int=None,
                 states: List=None, 
                 regSmokeTheory=None,
                 quitAttemptTheory=None,
                 quitSuccessTheory=None,
                 ):
        super().__init__(id=id, type=type, rank=rank)
        self.smokingModel=smokingModel
        self.pAge = PersonalAttribute(name='pAge')
        self.pAge.addLevel2Attribute(quitSuccessTheory.level2Attributes['cAge'])
        self.pAge.addLevel2Attribute(regSmokeTheory.level2Attributes['oAge'])
        self.pAge.addLevel2Attribute(quitAttemptTheory.level2Attributes['mAge'])
        self.pAge.setValue(age)
        self.pGender = PersonalAttribute(name='pGender')
        self.pGender.addLevel2Attribute(regSmokeTheory.level2Attributes['mGender'])
        self.pGender.setValue(gender)
        self.pIMDQuintile  = PersonalAttribute(name='pIMDQuintile')
        self.pIMDQuintile.setValue(qimd)
        self.pCohort = PersonalAttribute(name='pCohort')
        self.pCohort.setValue(cohort)
        self.pEducationalLevel = PersonalAttribute(name='pEducationalLevel')
        self.pEducationalLevel.addLevel2Attribute(regSmokeTheory.level2Attributes['oEducationalLevel'])
        self.pEducationalLevel.addLevel2Attribute(quitSuccessTheory.level2Attributes['oEducationalLevel'])
        self.pEducationalLevel.setValue(educationalLevel)
        self.pSEP = PersonalAttribute(name='pSEP')
        self.pSEP.addLevel2Attribute(regSmokeTheory.level2Attributes['oSEP'])
        self.pSEP.addLevel2Attribute(quitSuccessTheory.level2Attributes['oSEP'])
        self.pSEP.setValue(SEP)
        self.pRegion = PersonalAttribute(name='pRegion')
        self.pRegion.setValue(region)
        self.pSocialHousing = PersonalAttribute(name='pSocialHousing')
        self.pSocialHousing.addLevel2Attribute(regSmokeTheory.level2Attributes['oSocialHousing'])
        self.pSocialHousing.addLevel2Attribute(quitAttemptTheory.level2Attributes['oSocialHousing'])
        self.pSocialHousing.addLevel2Attribute(quitSuccessTheory.level2Attributes['oSocialHousing'])
        self.pSocialHousing.setValue(socialHousing)
        self.pMentalHealthConditions = PersonalAttribute(name='pMentalHealthConditions')
        self.pMentalHealthConditions.addLevel2Attribute(regSmokeTheory.level2Attributes['cMentalHealthConditions'])
        self.pMentalHealthConditions.addLevel2Attribute(quitSuccessTheory.level2Attributes['cMentalHealthConditions'])
        self.pMentalHealthConditions.setValue(mentalHealthConds)
        self.pAlcohol = PersonalAttribute(name='pAlcohol')
        self.pAlcohol.addLevel2Attribute(regSmokeTheory.level2Attributes['cAlcohol'])
        self.pAlcohol.addLevel2Attribute(quitSuccessTheory.level2Attributes['cAlcohol'])
        self.pAlcohol.addLevel2Attribute(quitSuccessTheory.level2Attributes['oAlcohol'])
        self.pAlcohol.setValue(alcohol)
        self.pExpenditure = PersonalAttribute(name='pExpenditure')
        self.pExpenditure.addLevel2Attribute(quitAttemptTheory.level2Attributes['mSpendingOnCig'])
        self.pExpenditure.setValue(expenditure)
        self.pNRTUse  = PersonalAttribute(name='pNRTuse')
        self.pNRTUse.addLevel2Attribute(quitSuccessTheory.level2Attributes['cPrescriptionNRT'])
        self.pNRTUse.addLevel2Attribute(quitAttemptTheory.level2Attributes['mUseOfNRT'])
        self.pNRTUse.setValue(NRTUse)
        self.pVareniclineUse = PersonalAttribute(name='pVareniclineUse')
        self.pVareniclineUse.addLevel2Attribute(quitSuccessTheory.level2Attributes['cVareniclineUse'])
        self.pVareniclineUse.setValue(vareniclineUse)
        self.pCigConsumptionPrequit  = PersonalAttribute(name='pCigConsumptionPrequit')
        self.pCigConsumptionPrequit.addLevel2Attribute(quitSuccessTheory.level2Attributes['cCigConsumptionPrequit'])
        self.pCigConsumptionPrequit.setValue(cigConsumptionPrequit)
        self.pECigUse = PersonalAttribute(name='pEcigUse')
        self.pECigUse.addLevel2Attribute(regSmokeTheory.level2Attributes['cEigUse'])
        self.pECigUse.addLevel2Attribute(quitSuccessTheory.level2Attributes['cEigUse'])
        self.pECigUse.setValue(eCigUse)
        self.states = states #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 

    def update_eCigUse(self,eciguse: int):
        self.eCigUse=eciguse

    def update_state(self,state=None):
        self.states.append(state)
    
    def update_proportion_of_smoking_friends(self,proportion_of_smoking_friends=None):
        self.proportion_of_smoking_friends=proportion_of_smoking_friends
    
    def get_current_state(self):
        return self.states[-1]
    
    def get_current_time_step(self):
        return len(self.states)-1
    
    def incrementAge(self):
        self.pAge.setAttribute(self.pAge.value+1)

class SmokingModel(Model):
        def __init__(self, comm, params : Dict):
            self.comm = comm
            self.context: SharedContext = SharedContext(comm)#create an agent population
            self.size_of_population=None
            self.rank:int = self.comm.Get_rank()
            self.type:int=0 #type of agent in id (id is a tuple (id,rank,type))
            self.props = params
            self.data_file: str = self.props["data_file"] #data file containing HSE2012 STAPM data
            self.stop_at:int = self.props["stop.at"] #final time step (tick) of simulation
            self.threshold=self.props["threshold"]
            self.runner: SharedScheduleRunner = init_schedule_runner(comm)
            self.smoking_prevalenceL=list()
            self.regSmokL2AttrBetas,self.regSmokCOMBetas,self.attemptL2AttrBetas,self.attemptCOMBetas,self.successL2AttrBetas,self.successCOMBetas=self.storeCoeffsOfLevel2AttributesAndCOMIntoMaps()
            self.data=pd.read_csv(self.data_file,header=0)
        
        def storeCoeffsOfAttributesIntoMap(self,key):
            betas={}
            betas = self.pros[key]
            l=betas.split(",")
            i=0
            while i <= len(l-2):
                  l2attr=l[i]
                  beta=l[i+1]
                  betas[l2attr]=float(beta)
                  i+=2
            return betas
        
        def storeCoeffsOfLevel2AttributesAndCOMIntoMaps(self):
            #store the betas (coefficients) of level 2 attributes into a hashmap data structure (dictionary) with key=level 2 attribute name, value=beta
            regSmokL2AttrBetas=self.storeCoeffsOfAttributesIntoMap("regSmokLevel2AttributesBetas")
            regSmokCOMBetas=self.storeCoeffsOfAttributesIntoMap("regSmokCOMBetas")
            attemptL2AttrBetas=self.storeCoeffsOfAttributesIntoMap("attemptLevel2AttributesBetas")
            attemptCOMBetas=self.storeCoeffsOfAttributesIntoMap("attemptCOMBetas")
            successL2AttrBetas=self.storeCoeffsOfAttributesIntoMap("successLevel2attributes_betas")
            successCOMBetas=self.storeCoeffsOfAttributesIntoMap("successCOMBetas")            
            return regSmokL2AttrBetas,regSmokCOMBetas,attemptL2AttrBetas,attemptCOMBetas,successL2AttrBetas,successCOMBetas
                        
        def init_population(self):
            (r,_)=self.data.shape
            print('size of agent population:',r)
            self.size_of_population=r
            for i in range(r):
                regSmokTheory=RegSmokeTheory(self,i)
                quitAttemptTheory=QuitAttemptTheory(self,i)
                quitSuccessTheory=QuitSuccessTheory(self,i)                  
                mediator=COMBTheoryMediator([regSmokTheory,quitAttemptTheory,quitSuccessTheory])
                self.context.add(Person(i, 
                               self.type,
                               self.rank,
                               age=int(self.data.at[i,'pAge']),
                               sex=self.data.at[i,'pGender'],
                               cohort=self.data.at[i,'pCohort'],
                               qimd=float(self.data.at[i,'pIMDquintile']),
                               educationalLevel=self.data.at[i,'pEducationalLevel'],
                               SEP=self.data.at[i,'pSEP'],
                               region=self.data.at[i,'pRegion'],
                               socialHousing=self.data.at[i,'pSocialHousing'],
                               mentalHealthCond=self.data.at[i,'pMentalHealthCondition'],
                               alcohol=self.data.at[i,'pAlcohol'],
                               expenditure=self.data.at[i,'pExpenditure'],
                               NRTUse=self.data.at[i,'pNRTUse'],
                               vareniclineUse=self.data.at[i,'pVareniclineUse'],
                               eCigUse=self.data.at[i,'pECigUse'],
                               cigConsumptionPrequit=self.data.at[i,'pCigConsumptionPrequit'],
                               states=[self.data.at[i,'state']],
                               regSmokTheory=regSmokTheory,
                               quitAttemptTheory=quitAttemptTheory,
                               quitSuccessTheory=quitSuccessTheory
                                ))
                agent=self.context.agent((i,self.type,self.rank))
                mediator.set_agent(agent)
                agent.set_mediator(mediator)                
            self.size_of_population=(self.context.size()).get(-1)
            print('size of population:',self.size_of_population)
            p=self.smoking_prevalence()
            print('===statistics of smoking prevalence===')
            print('Time step 0: smoking prevalence='+str(p)+'%.')
            self.smoking_prevalenceL.append(p)
            
        def do_situational_mechanisms(self):#macro entities change internal states of micro entities (agents)
            for agent in self.context.agents(agent_type=self.type):
                agent.do_situation()
        
        def do_action_mechanisms(self):#micro entities do actions based on their internal states
            for agent in self.context.agents(agent_type=self.type):
                agent.do_action()

        def do_transformational_mechanisms(self):
            pass

        def do_macro_to_macro_mechanisms(self):
            pass 
 
        def smoking_prevalence(self):#smoking prevalence at the current time step
            smokers=0
            for agent in self.context.agents(agent_type=self.type):
                if agent.get_current_state()=='smoker':
                    smokers+=1
            prevalence=np.round(smokers/self.size_of_population*100,2) #percentage of smokers
            return prevalence
        
        def eCig_prevalence(self):
            eCigUers=0
            for agent in self.context.agents(agent_type=self.type):
                if agent.eCigUse:
                    eCigUers+=1
            prevalence=np.round(eCigUers/self.size_of_population*100,2) #percentage of e-Cig users
            return prevalence

        def do_per_tick(self):
            self.do_situational_mechanisms()
            self.do_action_mechanisms()
            self.do_transformational_mechanisms()
            self.do_macro_to_macro_mechanisms()
            #display smoking prevalence at current time step on screen
            agent=list(self.context.agents(count=1))[0]
            p=self.smoking_prevalence()
            print('Time step '+str(agent.get_current_time_step())+': smoking prevalence='+str(p)+'%.')
            self.smoking_prevalenceL.append(p)
            
        def init_schedule(self):
            self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
            self.runner.schedule_stop(self.stop_at)

        def collect_data(self):
            f=open('prevalence_of_smoking.csv','w')
            for prev in self.smoking_prevalenceL:
                f.write(str(prev)+',')
            f.close()
        
        def init(self):
            self.init_population()
            self.init_schedule()

        def run(self):
            self.runner.execute()
            self.collect_data()

class COMBTheory(Theory):

    def __init__(self,smokingModel: SmokingModel):
        self.smokingModel=smokingModel
        self.compC: Level1Attribute=None
        self.compO: Level1Attribute=None
        self.compM: Level1Attribute=None
        self.behaviour : float=None
        self.level2Attributes: Dict={}#a hashmap with keys=level 2 attribute names, values=Level2Attribute objects 
        self.power=0 #power within logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
    
    def storeLevel2AttributesIntoMap(self,indx_of_agent: int):
        #store the level 2 attributes of agent i from level 2 attributes dataframe of smoking model class into a map <l2AttributeName : string, object : Level2Attribute>  
        level2attributesdata=self.data.filter(regex='^[com]')
        for level2AttributeName in level2attributesdata.columns:
            self.level2Attributes.insert(level2AttributeName,Level2Attribute(name=level2AttributeName,value=self.smokingModel.data.at[indx_of_agent,level2AttributeName]))

    @abstractmethod
    def do_situation(self):#run the situation mechanism of the agent of this theory
        pass

    @abstractmethod
    def makeCompC(self):
        pass

    @abstractmethod    
    def makeCompO(self):
        pass

    @abstractmethod
    def makeCompM(self):
        pass

    @abstractmethod
    def doBehaviour(self):
        #calculate probability of a behaviour using a logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        pass

    @abstractmethod
    def doLearning(self):
        pass

    def do_action(self):#run the action mechanism of the agent of this theory
        self.makeCompC()
        self.makeCompO()
        self.makeCompM()
        self.doBehaviour()             

class COMBTheoryMediator(TheoryMediator):
        
    def __init__(self, theory_list:List[COMBTheory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")

    def mediate_situation(self):
        for i in range(len(self.theory_list)):
            self.theory_list[i].do_situation()

    def mediate_action(self):
        for i in range(len(self.theory_list)):
            self.theory_list[i].do_action()

class RegSmokeTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,indx_of_agent : int):
      super().__init__(smokingModel)
      self.storeLevel2AttributesIntoMap(indx_of_agent)

    def do_situation(self):
        pass

    def doLearning(self):
        pass

    def makeCompC(self):
        if self.smokingModel.regSmokCOMBetas.get('C')!=None:
            self.compC=Level1Attribute('C')
            self.compC.addLevel2Attribute(self.level2Attributes['cAlcoholConsumption'])
            self.compC.addLevel2Attribute(self.level2Attributes['cEcigaretteUse'])
            self.compC.addLevel2Attribute(self.level2Attributes['cMentalHealthConditions'])
            val=0
            for level2Attribute in self.compC.list:
                beta=self.smokingModel.regSmokL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compC.setValue(val)
            self.power+=val*self.smokingModel.regSmokCOMBetas.get('C')
        return self.power
    
    def makeCompO(self):
        if self.smokingModel.regSmokCOMBetas.get('O')!=None:  
            self.compO=Level1Attribute('O')
            self.compO.addLevel2Attribute(self.level2Attributes['oSocialHousing'])
            self.compO.addLevel2Attribute(self.level2Attributes['oSEP'])
            self.compO.addLevel2Attribute(self.level2Attributes['oAge'])
            val=0
            for level2Attribute in self.compO.list:
                beta=self.smokingModel.regSmokL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.regSmokCOMBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.regSmokCOMBetas.get('M')!=None:
           print('create latent M')
        else:
           print('The regular smoking theory formula does not have latent composite O.')
        return self.power

    def doBehaviour(self):
        #calculate probability of behaviour using a logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        #Notes on quitting: a smoker transitions to an ex-smoker (i.e. achieve success in quitting) after maintaining a quit attempt for 3 consecutive ticks (12 weeks).
        ###pseudocode of state transition
        #At tick t: 
        #if an agent is a never smoker or an ex-smoker, run the regular smoking theory to calculate probability of uptaking regular smoking. If probability >= threshold, the new state of the agent is a smoker.
        #if an agent is a smoker, run the quit attempt theory to calculate the probability of making a quit attempt. If probability >= threshold, the new state of the agent is a quitter. 
        #if an agent is a quitter and was a quitter at ticks t-1 and t-2, run the quit success theory to calculate the probability of maintaining a quit attempt. If probability >= threshold, the new state of the agent is an ex-smoker.
        self.power+=self.smokingModel.regSmokCOMBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        p=1/(1+e^self.power)
        #At tick t:
        #if an agent is a never smoker or ex-smoker, run regular smoking theory to calculate probability of uptaking regular smoking. If probability >= threshold, the new state of the agent is a smoker.
        if self.agent.get_current_state() == 'never_smoker' or self.agent.get_current_state() == 'ex-smoker': 
           if p >= self.threshold:
              self.agent.update_state(state='smoker')
           else:
              self.agent.update_state(state=self.agent.get_current_state())

class QuitAttemptTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,indx_of_agent : int):
      super().__init__(smokingModel)
      self.storeLevel2AttributesIntoMap(indx_of_agent)

    def do_situation(self):#agents use intervention to quit e.g. e-cigarette
        pass

    def doLearning(self):
        pass 

    def makeCompC(self):
        if self.smokingModel.attemptCOMBetas.get('C')!=None:
           print('create latent C')
        else:
           print('The quit attempt theory formula does not have latent composite C.')
        return self.power

    def makeCompO(self):#STS has no data on these level 2 attributes: region smoking, GP advice and smokers in network. They are excluded from the formula.
        if self.smokingModel.attemptCOMBetas.get('O')!=None:
            self.compO=Level1Attribute('O')
            self.compO.addLevel2Attribute(self.level2Attributes['oSocialHousing'])
            val=0
            for level2Attribute in self.compO.list:
                beta=self.smokingModel.attemptL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.attemptCOMBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.attemptCOMBetas.get('M')!=None:  
            self.compM=Level1Attribute('M')
            self.compM.addLevel2Attribute(self.level2Attributes['mIntentionToQuit'])
            self.compM.addLevel2Attribute(self.level2Attributes['mSpendingOnCig'])
            self.compM.addLevel2Attribute(self.level2Attributes['mEnjoymentOfSmoking'])
            self.compM.addLevel2Attribute(self.level2Attributes['mAge'])
            val=0
            for level2Attribute in self.compM.list:
                beta=self.smokingModel.attemptL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compM.setValue(val)
            self.power+=val*self.smokingModel.attemptCOMBetas.get('M')
        return self.power
    
    def doBehaviour(self):
        #calculate probability of behaviour using a logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        self.power+=self.smokingModel.attemptCOMBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        p=1/(1+e^self.power)
        #At tick t:
        #if an agent is a smoker, run the quit attempt theory to calculate the probability of making a quit attempt. If probability >= threshold, the new state of the agent is a quitter. 
        if self.agent.get_current_state() == 'smoker':
            if p >= self.threshold:
               self.agent.update_state(state='quitter')
            else:
               self.agent.update_state(state='smoker')

class QuitSuccessTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,indx_of_agent : int):
      super().__init__(smokingModel)
      self.storeLevel2AttributesIntoMap(indx_of_agent)

    def do_situation(self):
        pass

    def doLearning(self):
        pass

    def makeCompC(self):#STS does not have data on the level 2 attribute 'cigarettes per day'. This is excluded from the formula.
        if self.smokingModel.successCOMBetas.get('C')!=None:
            self.compC=Level1Attribute('C')
            self.compC.addLevel2Attribute(self.level2Attributes['cAlcoholConsumption'])
            self.compC.addLevel2Attribute(self.level2Attributes['cEcigaretteUse'])
            self.compC.addLevel2Attribute(self.level2Attributes['mUseOfNRT'])
            self.compC.addLevel2Attribute(self.level2Attributes['cVareniclineUse'])
            self.compC.addLevel2Attribute(self.level2Attributes['cCigAddictStrength'])            
            self.compC.addLevel2Attribute(self.level2Attributes['cMentalHealthConditions'])
            self.compC.addLevel2Attribute(self.level2Attributes['cAge'])
            val=0
            for level2Attribute in self.compC.list:
                beta=self.smokingModel.successL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compC.setValue(val)
            self.power+=val*self.smokingModel.successCOMBetas.get('C')
        return self.power
    
    def makeCompO(self):#STS has no data on level 2 attributes: smokers in network and region prevalence. They are excluded from the formula.
        if self.smokingModel.successCOMBetas.get('O')!=None:  
            self.compO=Level1Attribute('O')
            self.compO.addLevel2Attribute(self.level2Attributes['oSocialHousing'])
            self.compO.addLevel2Attribute(self.level2Attributes['oSEP'])
            val=0
            for level2Attribute in self.compO.list:
                beta=self.smokingModel.successL2AttrBetas[level2Attribute.name]
                val+=beta*level2Attribute.getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.successCOMBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.successCOMBetas.get('M')!=None:
           print('create latent M')
        else:
           print('The quit success theory formula does not have latent composite M.')
        return self.power

    def doBehaviour(self):
        #calculate probability of quit success using a logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        #Notes on quitting: a smoker transitions to an ex-smoker (i.e. achieve success in quitting) after maintaining a quit attempt for 3 consecutive ticks (12 weeks).
        ###pseudocode of state transition
        #At tick t: 
        #if an agent is a quitter and was a quitter at ticks t-1 and t-2 run the quit success theory to calculate the probability of maintaining a quit attempt. If probability >= threshold, the new state of the agent is an ex-smoker.
        self.power+=self.smokingModel.successCOMBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        p=1/(1+e^self.power)
        current_tick=len(self.agent.states)-1
        if self.agent.get_current_state() == 'quitter' and self.agent.states[current_tick-1] == 'quitter' and self.agent.states[current_tick-2] == 'quitter': 
            if p >= self.threshold:
               self.agent.update_state(state='ex-smoker')
            else:
               self.agent.update_state(state='smoker')
        elif self.agent.get_current_state() == 'quitter' and self.agent.states[current_tick-1] == 'quitter' and self.agent.states[current_tick-2] == 'smoker':
             if p >= self.threshold:
                self.agent.update_state(state='quitter')
             else:
                self.agent.update_state(state='smoker')
        elif self.agent.get_current_state() == 'quitter' and self.agent.states[current_tick-1] = 'smoker':
             if p >= self.threshold:
                self.agent.update_state(state='quitter')
             else:
                self.agent.update_state(state='smoker')