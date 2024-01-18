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
import random

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
                 yearsSinceQuit=None, 
                 regSmokeTheory=None,
                 quitAttemptTheory=None,
                 quitSuccessTheory=None
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
        self.pNumberOfRecentQuitAttempts=PersonalAttribute(name='pNumberOfRecentQuitAttempts') #pNumberOfRecentQuitAttempts is an imputed variable (STPM does not have information on number of recent quit attempts)
        self.pNumberOfRecentQuitAttempts.addLevel2Attribute(quitAttemptTheory.level2Attributes['mNumberOfRecentQuitAttempts'])
        self.states = states #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 
        self.initBehaviourBufferAndKAndpNumberOfRecentQuitAttempts()#initialize: 
                                                                   #          behaviour buffer which stores the agent's behaviours (COMB and STPM behaviours) over the last 12 months (13 ticks with each tick represents 4 weeks)
                                                                   #          k: number of ticks of maintaining a quit attempt i.e. k counts the behaviours: quit attempt and consecutive quit successes following the quit attempt in the behaviourBuffer 
                                                                   #          pNumberOfRecentQuitAttempts               
        self.pYearsSinceQuit=PersonalAttribute(name='pYearsSinceQuit') #number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
        self.pYearsSinceQuit.setValue(yearsSinceQuit)
        self.tickCounterExSmoker=None #count number of consecutive ticks when the agent stays as an ex-smoker

    def initBehaviourBufferAndKAndpNumberOfRecentQuitAttempts(self):
        #The behaviour buffer stores the agent's behaviours (COMB and STPM behaviours) over the last 12 months (13 ticks with each tick represents 4 weeks)
        #COMB behaviours: 'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure'
        #STPM behaviours: 'relapse', 'no relapse'
        #At each tick, the behaviour buffer (a list) stores one of the 8 behaviours: 'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure', 'relapse' and 'no relapse'
        #(behaviours of a quitter over last 12 months (13 ticks): random behaviour (tick 1)...,random behaviour (tick i-1),quit attempt (tick i), quit success,...,quit success (tick 13)
        #                                                         or 
        #                                                         random behaviour (tick 1),...,random behaviour (tick 12),quit attempt (tick 13))
        #At tick 0, initialize the behaviour buffer of the agent to its historical behaviours as follows:
        #for a quitter in the baseline population (i.e. at tick 0) {
        #  select a random index i of the buffer (0=< i =< 12); 
        #  set the cell at i to 'quit attempt';
        #  set all the cells at i+1,i+2...,12 to 'quit success';
        #  set the cells at 0,...,i-1 to random behaviours;
        # }
        #for a non-quitter in the baseline population {
        #  set each cell of the behaviour buffer to a random behaviour;
        # }
        #Set k to the number of quit attempt and consecutive quit successes following the quit attempt in the behaviourBuffer        
        behaviours=['uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure', 'relapse', 'no relapse']
        self.behaviourBuffer=[i for i in range(0,13)]
        self.k=0
        if self.states[0]=='quitter':
            i=random.randint(0, 12)
            self.behaviourBuffer[i]='quit attempt'
            self.k=1
            for j in range(i+1,13):
                self.behaviourBuffer[j]='quit success'
                self.k+=1
            for q in range(0,i):#set random behaviours to indices: 0, 1,..., i-1
                self.behaviourBuffer[q]=behaviours[random.randint(0, len(behaviours)-1)]
        elif self.states[0]=='never_smoker':
            for i in range(0,13):
                self.behaviourBuffer[i]='no uptake'
        elif self.states[0]=='ex-smoker':
            for i in range(0,13):
                self.behaviourBuffer[i]='no relapse'
        else:#smoker
            for i in range(0,13):
                self.behaviourBuffer[i]=behaviours[random.randint(0, len(behaviours)-1)]
        self.pNumberOfRecentQuitAttempts.setValue(self.behaviourBuffer.count('quit attempt'))

    def updateECigUse(self,eciguse: int):
        self.eCigUse=eciguse

    def setStateOfNextTimeStep(self,state=None):
        self.states.append(state)
    
    def getCurrentState(self):#get the agent's state at the current time step
        return self.states[self.smokingModel.currentTimeStep]
    
    def getCurrentTimeStep(self):
        return self.smokingModel.currentTimeStep
    
    def incrementAge(self):
        self.pAge.setAttribute(self.pAge.value+1)

class SmokingModel(Model):
        def __init__(self, comm, params : Dict):
            super().__init__(comm,params)
            self.comm = comm
            self.context: SharedContext = SharedContext(comm)#create an agent population
            self.sizeOfPopulation=None
            self.rank:int = self.comm.Get_rank()
            self.type:int=0 #type of agent in id (id is a tuple (id,rank,type))
            self.props = params
            self.dataFile: str = self.props["data_file"] #data file containing HSE2012 STAPM data
            self.relapseProbFile = self.props["relapse_prob_file"]
            self.yearOfCurrentTimeStep=self.props["year_of_baseline"]
            self.currentTimeStep=0
            self.stopAt:int = self.props["stop.at"] #final time step (tick) of simulation
            self.runner: SharedScheduleRunner = init_schedule_runner(comm)
            self.smokingPrevalenceL=list()
            self.uptakeBetas={}#hashmap (dictionary) to store betas (coefficients) of the COMB formula of regular smoking theory
            self.attemptBetas={}#hashmap to store betas of the COMB formula of quit attempt theory
            self.successBetas={}#hashmap to store betas of the COMB formula of quit success theory
            self.storeBetasOfCOMBFormulaeIntoMaps()
            self.level2AttributesOfUptakeFormula={'C':[],'O':[],'M':[]} #hashmap to store the level 2 attributes of the COMB formula of regular smoking theory
            self.level2AttributesOfAttemptFormula={'C':[],'O':[],'M':[]} #hashmap to store the level 2 attributes of the COMB formula of quit attempt theory
            self.level2AttributesOfSuccessFormula={'C':[],'O':[],'M':[]} #hashmap to store the level 2 attributes of the COMB formula of quit success theory
            self.storeLevel2AttributesOfCOMBFormulaeIntoMaps()
            self.data=pd.read_csv(self.dataFile,header=0)
            self.relapseProb=pd.read_csv(self.relapseProbFile,header=0)
            self.runningMode=self.props['ABM_mode'] #debug or normal mode
            self.tickCounter=0
            if self.runningMode=='debug':
                self.logfile=open('logfile.txt','a')

        def storeBetasOfCOMBFormulaeIntoMaps(self):
            #store the betas (coefficients) of COMB formulae for regular smoking, quit attempt and quit success theories into hashmaps
            #input: self.pros, a map with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
            #output: uptakeBetas, attemptBetas, successBetas hashmaps with key=level 2 or level 1 attribute, value=beta
            import re
            for key, value in self.pros.items():
                m=re.match('^uptake\.(\w+)\.beta$',key)#uptake.cAlcoholConsumption.beta or uptake.C.beta
                if m!=None:
                   self.uptakeBetas[m.group(1)]=value
                else:
                    m=re.match('^uptake\.bias$', key)
                    if m!=None:
                        self.uptakeBetas['bias']=value
                    else:
                        m=re.match('^attempt\.(\w+)\.beta$',key)
                        if m!=None:
                            self.attemptBetas[m.group(1)]=value
                        else:
                            m=re.match('^attempt\.bias$', key)
                            if m!=None:
                                self.attemptBetas['bias']=value
                            else: 
                                m=re.match('^success\.(\w+)\.beta$',key)
                                if m!=None:
                                    self.successBetas[m.group(1)]=value
                                else:
                                    m=re.match('^success\.bias$', key)
                                    if m!=None:
                                        self.successBetas['bias']=value            
        
        def storeLevel2AttributesOfCOMBFormulaeIntoMaps(self):
            #input: self.pros, a map with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
            #output: level2AttributesOfUptakeFormula, level2AttributesOfAttemptFormula, level2AttributesOfSuccessFormula hashmaps key=C, O or M and value=list of level 2 attributes of key
            import re
            for key in self.pros.keys():
                m=re.match('^uptake\.([com]{1}\w+)\.beta$',key)
                if m!=None:#match uptake.cAlcoholConsumption.beta, uptake.oAlcoholConsumption.beta or uptake.mAlcoholConsumption.beta 
                    level2attribute=m.group(1)
                    m=re.match('^c\w+',level2attribute)
                    if m!=None:#match cAlcoholConsumption
                        self.level2AttributesOfUptakeFormula['C'].append(level2attribute)
                    else:
                        m=re.match('^o\w+',level2attribute)
                        if m!=None:#match oAlcoholConsumption
                            self.level2AttributesOfUptakeFormula['O'].append(level2attribute)
                        else:
                            m=re.match('^m\w+',level2attribute)
                            if m!=None:#match oAlcoholConsumption
                                self.level2AttributesOfUptakeFormula['M'].append(level2attribute)
                            else:
                                sys.exit(level2attribute+' does not match patterns of level2attributes of C, O and M in regular smoking (uptake) formula')
                else:
                    m=re.match('^attempt\.([com]{1}\w+)\.beta$',key)                
                    if m!=None:#match attempt.cAlcoholConsumption.beta, attempt.oAlcoholConsumption.beta or attempt.mAlcoholConsumption.beta 
                        level2attribute=m.group(1)
                        m=re.match('^c\w+',level2attribute)
                        if m!=None:#match cAlcoholConsumption
                            self.level2AttributesOfUptakeFormula['C'].append(level2attribute)
                        else:
                            m=re.match('^o\w+',level2attribute)
                            if m!=None:#match oAlcoholConsumption
                                self.level2AttributesOfUptakeFormula['O'].append(level2attribute)
                            else:
                                m=re.match('^m\w+',level2attribute)
                                if m!=None:#match oAlcoholConsumption
                                    self.level2AttributesOfUptakeFormula['M'].append(level2attribute)
                                else:
                                    sys.exit(level2attribute+' does not match patterns of level2attributes of C, O and M in quit attempt forumla')
                    else:
                        m=re.match('^success\.([com]{1}\w+)\.beta$',key)                
                        if m!=None:#match success.cAlcoholConsumption.beta, success.oAlcoholConsumption.beta or success.mAlcoholConsumption.beta 
                            level2attribute=m.group(1)
                            m=re.match('^c\w+',level2attribute)
                            if m!=None:#match cAlcoholConsumption
                                self.level2AttributesOfUptakeFormula['C'].append(level2attribute)
                            else:
                                m=re.match('^o\w+',level2attribute)
                                if m!=None:#match oAlcoholConsumption
                                    self.level2AttributesOfUptakeFormula['O'].append(level2attribute)
                                else:
                                    m=re.match('^m\w+',level2attribute)
                                    if m!=None:#match oAlcoholConsumption
                                        self.level2AttributesOfUptakeFormula['M'].append(level2attribute)
                                    else:
                                        sys.exit(level2attribute+' does not match patterns of level2attributes of C, O and M in quit success forumla')

        def initPopulation(self):
            (r,_)=self.data.shape
            print('size of agent population:',r)
            self.sizeOfPopulation=r
            for i in range(r):
                regSmokTheory=RegSmokeTheory('regsmoketheory',self,i)
                quitAttemptTheory=QuitAttemptTheory('quitattempttheory',self,i)
                quitSuccessTheory=QuitSuccessTheory('quitsuccesstheory',self,i)
                relapseSTPMTheory=RelapseSTPMTheory('relapseSTPMtheory',self,i)                  
                mediator=COMBTheoryMediator([regSmokTheory,quitAttemptTheory,quitSuccessTheory,relapseSTPMTheory])
                self.context.add(Person(
                               self,
                               i, 
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
                               yearsSinceQuit=self.data.at[i,'pYearsSinceQuit'],#number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
                               states=[self.data.at[i,'state']],
                               regSmokTheory=regSmokTheory,
                               quitAttemptTheory=quitAttemptTheory,
                               quitSuccessTheory=quitSuccessTheory
                                ))
                agent=self.context.agent((i,self.type,self.rank))
                mediator.set_agent(agent)
                agent.setMediator(mediator)                
            self.sizeOfPopulation=(self.context.size()).get(-1)
            print('size of population:',self.sizeOfPopulation)
            p=self.smokingPrevalence()
            print('===statistics of smoking prevalence===')
            print('Time step 0: smoking prevalence='+str(p)+'%.')
            self.smokingPrevalenceL.append(p)
            
        def doSituationalMechanisms(self):#macro entities change internal states of micro entities (agents)
            for agent in self.context.agents(agent_type=self.type):
                agent.doSituation()
        
        def doActionMechanisms(self):#micro entities do actions based on their internal states
            for agent in self.context.agents(agent_type=self.type):
                agent.doAction()

        def doTransformationalMechanisms(self):
            pass

        def doMacroToMacroMechanisms(self):
            pass 
 
        def smokingPrevalence(self):#smoking prevalence at the current time step
            smokers=0
            for agent in self.context.agents(agent_type=self.type):
                if agent.getCurrentState()=='smoker':
                    smokers+=1
            prevalence=np.round(smokers/self.sizeOfPopulation*100,2) #percentage of smokers
            return prevalence
        
        def doPerTick(self):
            self.currentTimeStep+=1
            self.tickCounter+=1
            if self.tickCounter==13:
               self.yearOfCurrentTimeStep+=1
            self.doSituationalMechanisms()
            self.doActionMechanisms()
            self.doTransformationalMechanisms()
            self.doMacroToMacroMechanisms()
            #display smoking prevalence at current time step on screen
            agent=list(self.context.agents(count=1))[0]
            p=self.smokingPrevalence()
            print('Time step '+str(agent.getCurrentTimeStep())+': smoking prevalence='+str(p)+'%.')
            self.smokingPrevalenceL.append(p)
            if self.tickCounter==13:
                self.tickCounter=0
            if self.runningMode=='debug':
                self.logfile.write('year: '+str(self.yearOfCurrentTimeStep)+'\n')
            
        def initSchedule(self):
            self.runner.schedule_repeating_event(1, 1, self.doPerTick)
            self.runner.schedule_stop(self.stopAt)

        def collectData(self):
            f=open('prevalence_of_smoking.csv','w')
            for prev in self.smokingPrevalenceL:
                f.write(str(prev)+',')
            f.close()
            if self.runningMode=='debug':#write states of each agent over the entire simulation period into a csv file               
                self.logfile.write('###states of the agents over all time steps###\n')
                self.logfile.write('id\n')
                for i in range(self.currentTimeStep+1):
                    self.logfile.write(','+str(i))
                self.logfile.write('\n')
                for agent in self.context.agents(agent_type=self.type):
                    self.logfile.write(str(agent.get_id))
                    for i in range(self.currentTimeStep+1):
                        self.logfile.write(','+agent.states[i])
                    self.logfile.write('\n')
                self.logfile.close()

        def init(self):
            self.initPopulation()
            self.initSchedule()

        def run(self):
            self.runner.execute()
            self.collectData()

class COMBTheory(Theory):

    def __init__(self,name,smokingModel):
        self.smokingModel=smokingModel
        self.compC: Level1Attribute=None
        self.compO: Level1Attribute=None
        self.compM: Level1Attribute=None
        self.probBehaviour : float=None
        self.level2Attributes: Dict={}#a hashmap with keys=level 2 attribute names, values=Level2Attribute objects 
        self.power=0 #power within logistic regression: 1/(1+e^power) where power=-(bias+beta1*x1+...,betak*xk)
        self.name=name
        
    def storeLevel2AttributesIntoMap(self,indxOfAgent: int):
        #store the level 2 attributes of agent i from level 2 attributes dataframe of smoking model class into a map <l2AttributeName : string, object : Level2Attribute>  
        level2attributesdata=self.data.filter(regex='^[com]')
        for level2AttributeName in level2attributesdata.columns:
            self.level2Attributes.insert(level2AttributeName,Level2Attribute(name=level2AttributeName,value=self.smokingModel.data.at[indxOfAgent,level2AttributeName]))

    @abstractmethod
    def doSituation(self):#run the situation mechanism of the agent of this theory
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

    def doAction(self):#run the action mechanism of the agent of this theory
        self.makeCompC()
        self.makeCompO()
        self.makeCompM()
        self.doBehaviour()             

class SmokingTheoryMediator(TheoryMediator):
        
    def __init__(self, theoryList:List[COMBTheory]):
        super().__init__(theoryList)
        if len(self.theoryList) == 0: 
            raise Exception(f"{__class__.__name__} require a theoryList with length > 0")
        self.theoryMap={}
        for theory in theoryList:
            self.theoryMap[theory.name]=theory

    def mediateSituation(self):
        if self.agent.getCurrentState() == 'never_smoker': 
           self.theoryMap['regsmoketheory'].doSituation()
        elif self.agent.getCurrentState() == 'smoker': 
           self.theoryMap['quitattempttheory'].doSituation()
        elif self.agent.getCurrentState() == 'quitter':
           self.theoryMap['quitsuccesstheory'].doSituation()
        elif self.agent.getCurrentState() == 'ex-smoker':
            self.theoryMap['relapseSTPMtheory'].doSituation()

    def mediateAction(self):
        #definition of quitting smoking: a smoker transitions to an ex-smoker (i.e. achieve success in quitting) after maintaining a quit attempt for 13 consecutive ticks (52 weeks i.e. 12 months). 
        #                        the sequence of the agent's behaviours when transitioning from smoker to ex-smoker: quit attempt (at t=i, i > 0, state=smoker), quit success (at t=i+1, state=quitter),..., quit success (at t=i+12, state=quitter), relapse or no relapse (at t=i+13, state=ex-smoker)
        ###pseudocode of state transition###
        #At tick t: 
        #for a quitter A, if k < 13, run the quit success theory to calculate the probability of maintaining a quit attempt; if p >= threshold {A stays as a quitter at t+1; k=k+1} else { A transitions to a smoker at t+1}
        #for a quitter A, if k==13, run the quit success theory to calculate the probability of maintaining a quit attempt; if p >= threshold { A transitions to an ex-smoker at t+1; k=0;} else {A transitions to a smoker at t+1}
        #for a smoker A, run the quit attempt theory to calculate the probability of making a quit attempt. If p >= threshold, { A transitions to a quitter at t+1; k=1;} else {A stays as a smoker at t+1}
        #for a never smoker, run the regular smoking theory to calculate the probability of regular smoking; if p >= threshold {A transitions to a smoker at t+1} else { A stays as never smoker or ex-smoker at t+1}
        #for an ex-smoker A, run relapse theory of STPM theory to calculate the probability of relapse; if p>= threshold {A transitions to a smoker at t+1} else { A stays as ex-smoker at t+1}
        #where threshold is a pseudo-random number drawn from uniform(0,1) and p is the probability from the latent composite model.
        if self.agent.getCurrentState() == 'quitter':
           self.theoryMap['quitsuccesstheory'].doAction()
        elif self.agent.getCurrentState() == 'smoker':
           self.theoryMap['quitattempttheory'].doAction()  
        elif self.agent.getCurrentState() == 'never_smoker': 
           self.theoryMap['regsmoketheory'].doAction()   
        elif self.agent.getCurrentState() == 'ex-smoker':
            self.theoryMap['relapseSTPMtheory'].doAction()

class STPMTheory(Theory):
    def __init__(self,name,smokingModel):
        self.smokingModel=smokingModel
        self.name=name

    @abstractmethod
    def doSituation(self):
        pass

    @abstractmethod
    def doAction(self):
        pass

class RelapseSTPMTheory(STPMTheory):
    def __init__(self,name,smokingModel: SmokingModel):
      super().__init__(name,smokingModel)
      self.probRelapse=None

    def doSituation(self):
        #increment age of the agent every 13 ticks
        if self.smokingModel.tickCounter == 13:
            self.agent.incrementAge()
        #retrieve probability of relapse of the matching person from STPM transition probabilities file
        matched=self.smokingModel.relapseProb[(self.smokingModel.relapseProb['age'] == self.agent.pAge.getValue()) & (self.smokingModel.relapseProb['year'] == self.smokingModel.yearOfCurrentTimeStep) & (self.smokingModel.relapseProb['sex']==self.agent.pGender.getValue()) & (self.smokingModel.relapseProb['imd_quintile']==self.agent.pIMDQuintile.getValue()) & (self.smokingModel.relapseProb['time_since_quit']==self.agent.pYearsSinceQuit.getValue())]
        self.probRelapse=float(matched['p_relapse_4wk'])
        
    def doAction(self):
        self.agent.tickCounterExSmoker+=1
        if self.agent.tickCounterExSmoker == 13:
           self.agent.pYearsSinceQuit.setValue(self.agent.pYearsSinceQuit.getValue()+1)
           self.agent.tickCounterExSmoker=0
        if self.probRelapse >=random.uniform(0,1):
           del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
           self.agent.behaviourBuffer.append('relapse') #append the agent's new behaviour to its behaviour buffer 
           self.agent.setStateOfNextTimeStep(state='smoker')
           self.agent.tickCounterExSmoker=0
           self.agent.pYearsSinceQuit.setValue(None)
        else:
           del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
           self.agent.behaviourBuffer.append('no relapse') #append the agent's new behaviour to its behaviour buffer 
           self.agent.setStateOfNextTimeStep(state='ex-smoker')               
        #count the number of quit attempts in the last 12 months and update the agent's variable pNumberOfRecentQuitAttempts
        self.agent.pNumberOfRecentQuitAttempts.setValue(self.agent.behaviourBuffer.count('quit attempt'))
        if self.smokingModel.runningMode=='debug':
            self.smokingModel.logfile.writelines(['agent id: '+str(self.agent.getId())+'\n',
                                                  'state: '+self.agent.getCurrentState()+'\n',
                                                  'age: '+str(self.agent.pAge.getValue())+'\n',
                                                  'buffer: '+str(self.agent.behaviourBuffer)+'\n',
                                                  'pNumberOfRecentQuitAttempts: '+str(self.agent.pNumberOfRecentQuitAttempts.getValue())+'\n',
                                                  'pYearsSinceQuit: '+str(self.agent.pYearsSinceQuit.getValue())])

class RegularSmokingSTPMTheory(STPMTheory):
    def __init__(self,name,smokingModel: SmokingModel,indxOfAgent : int):
      super().__init__(name,smokingModel)

    def doSituation(self):
        pass

    def doAction(self):
        pass
    
class QuitSTPMTheory(STPMTheory):
    def __init__(self,name,smokingModel: SmokingModel,indxOfAgent : int):
      super().__init__(name,smokingModel)

    def doSituation(self):
        pass

    def doAction(self):
        pass
    
class RegSmokeTheory(COMBTheory):

    def __init__(self,name,smokingModel: SmokingModel,indxOfAgent : int):
      super().__init__(name,smokingModel)
      self.compC: Level1Attribute=None
      self.compO: Level1Attribute=None
      self.compM: Level1Attribute=None
      self.level2Attributes: Dict={}#a hashmap with keys=level 2 attribute names, values=Level2Attribute objects   
      self.storeLevel2AttributesIntoMap(indxOfAgent)

    def doSituation(self):
       #increment age of the agent every 13 ticks
       if self.smokingModel.tickCounter == 13:
            self.agent.incrementAge()

    def doLearning(self):
        pass

    def makeCompC(self):
        if self.smokingModel.uptakeBetas.get('C')!=None:
            self.compC=Level1Attribute('C')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfUptakeFormula['C']:
                self.compC.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.uptakeBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compC.setValue(val)
            self.power+=val*self.smokingModel.uptakeBetas.get('C')
        return self.power
    
    def makeCompO(self):
        if self.smokingModel.uptakeBetas.get('O')!=None:  
            self.compO=Level1Attribute('O')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfUptakeFormula['O']:
                self.compO.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.uptakeBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.uptakeBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.uptakeBetas.get('M')!=None:  
            self.compM=Level1Attribute('M')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfUptakeFormula['M']:
                self.compM.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.uptakeBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compM.setValue(val)
            self.power+=val*self.smokingModel.uptakeBetas.get('M')
        return self.power
        
    def doBehaviour(self):    
        #calculate probability of regular smoking uptake using the COMB formula: 
        #prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias)
        #Notes on quitting: a smoker transitions to an ex-smoker (i.e. achieve success in quitting) after maintaining a quit attempt for 3 consecutive ticks (12 weeks).
        self.power+=self.smokingModel.uptakeBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        self.probBehaviour=1/(1+e^self.power)
        #for a never smoker, run the regular smoking theory to calculate the probability of regular smoking; if p >= threshold {A transitions to a smoker at t+1} else { A stays as never smoker or ex-smoker at t+1}
        if self.probBehaviour >=random.uniform(0,1):
            del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            self.agent.behaviourBuffer.append('uptake') #append the agent's new behaviour to its behaviour buffer               
            self.agent.setStateOfNextTimeStep(state='smoker')
        else:
            del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            self.agent.behaviourBuffer.append('no uptake') #append the agent's new behaviour to its behaviour buffer               
            self.agent.setStateOfNextTimeStep(state='never_smoker')
        #count the number of quit attempts in the last 12 months and update the agent's variable pNumberOfRecentQuitAttempts
        self.agent.pNumberOfRecentQuitAttempts.setValue(self.agent.behaviourBuffer.count('quit attempt'))
        if self.smokingModel.runningMode=='debug':
            self.smokingModel.logfile.writelines(['agent id: '+str(self.agent.getId())+'\n',
                                                  'state: '+self.agent.getCurrentState()+'\n',
                                                  'age: '+str(self.agent.pAge.getValue())+'\n',
                                                  'buffer: '+str(self.agent.behaviourBuffer)+'\n',
                                                  'pNumberOfRecentQuitAttempts: '+str(self.agent.pNumberOfRecentQuitAttempts.getValue())+'\n',
                                                  'pYearsSinceQuit: '+str(self.agent.pYearsSinceQuit.getValue())]
                
class QuitAttemptTheory(COMBTheory):

    def __init__(self,name,smokingModel: SmokingModel,indxOfAgent : int):
      super().__init__(name,smokingModel)
      self.compC: Level1Attribute=None
      self.compO: Level1Attribute=None
      self.compM: Level1Attribute=None
      self.level2Attributes: Dict={}#a hashmap with keys=level 2 attribute names, values=Level2Attribute objects   
      self.storeLevel2AttributesIntoMap(indxOfAgent)

    def doSituation(self):
        #increment age of the agent every 13 ticks
        if self.smokingModel.tickCounter == 13:
            self.agent.incrementAge()

    def doLearning(self):
        pass 

    def makeCompC(self):
        if self.smokingModel.attemptBetas.get('C')!=None:
            self.compC=Level1Attribute('C')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfAttemptFormula['C']:
                self.compC.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.attemptBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compC.setValue(val)
            self.power+=val*self.smokingModel.attemptBetas.get('C')
        return self.power
    
    def makeCompO(self):
        if self.smokingModel.attemptBetas.get('O')!=None:  
            self.compO=Level1Attribute('O')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfAttemptFormula['O']:
                self.compO.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.attemptBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.attemptBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.attemptBetas.get('M')!=None:  
            self.compM=Level1Attribute('M')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfAttemptFormula['M']:
                self.compM.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.attemptBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compM.setValue(val)
            self.power+=val*self.smokingModel.attemptBetas.get('M')
        return self.power
    
    def doBehaviour(self):
        #calculate probability of making quit attempt using using the COMB formula: 
        #prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias)
        self.power+=self.smokingModel.attemptBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        self.probBehaviour=1/(1+e^self.power)
        #for a smoker A, run the quit attempt theory to calculate the probability of making a quit attempt. If p >= threshold, { A transitions to a quitter at t+1; k=1;} else {A stays as a smoker at t+1}
        if self.probBehaviour >= random.uniform(0,1):
            del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            self.agent.behaviourBuffer.append('quit attempt') #append the agent's new behaviour to its behaviour buffer
            self.agent.setStateOfNextTimeStep(state='quitter')
            self.agent.k=1
        else:
            del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            self.agent.behaviourBuffer.append('no quit attempt') #append the agent's new behaviour to its behaviour buffer
            self.agent.setStateOfNextTimeStep(state='smoker')
        #count the number of quit attempts in the last 12 months and update the agent's variable pNumberOfRecentQuitAttempts
        self.agent.pNumberOfRecentQuitAttempts.setValue(self.agent.behaviourBuffer.count('quit attempt'))
        if self.smokingModel.runningMode=='debug':
            self.smokingModel.logfile.writelines(['agent id: '+str(self.agent.getId())+'\n',
                                                  'state: '+self.agent.getCurrentState()+'\n',
                                                  'age: '+str(self.agent.pAge.getValue())+'\n',
                                                  'buffer: '+str(self.agent.behaviourBuffer)+'\n',
                                                  'pNumberOfRecentQuitAttempts: '+str(self.agent.pNumberOfRecentQuitAttempts.getValue())+'\n',
                                                  'pYearsSinceQuit: '+str(self.agent.pYearsSinceQuit.getValue())]

class QuitSuccessTheory(COMBTheory):

    def __init__(self,name, smokingModel: SmokingModel,indxOfAgent : int):
      super().__init__(name, smokingModel)
      self.compC: Level1Attribute=None
      self.compO: Level1Attribute=None
      self.compM: Level1Attribute=None
      self.level2Attributes: Dict={}#a hashmap with keys=level 2 attribute names, values=Level2Attribute objects   
      self.storeLevel2AttributesIntoMap(indxOfAgent)

    def doSituation(self):
        #increment age of the agent every 13 ticks
        if self.smokingModel.tickCounter == 13:
            self.agent.incrementAge()

    def doLearning(self):
        pass

    def makeCompC(self):
        if self.smokingModel.successBetas.get('C')!=None:
            self.compC=Level1Attribute('C')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfSuccessFormula['C']:
                self.compC.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.successBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compC.setValue(val)
            self.power+=val*self.smokingModel.successBetas.get('C')
        return self.power
    
    def makeCompO(self):
        if self.smokingModel.successBetas.get('O')!=None:  
            self.compO=Level1Attribute('O')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfSuccessFormula['O']:
                self.compO.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.successBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compO.setValue(val)
            self.power+=val*self.smokingModel.successBetas.get('O')
        return self.power
    
    def makeCompM(self):
        if self.smokingModel.successBetas.get('M')!=None:  
            self.compM=Level1Attribute('M')
            val=0
            for level2AttributeName in self.smokingModel.level2AttributesOfSuccessFormula['M']:
                self.compM.addLevel2Attribute(self.level2Attributes[level2AttributeName])
                beta=self.smokingModel.successBetas[level2AttributeName]
                val+=beta*self.level2Attributes[level2AttributeName].getValue()
            self.compM.setValue(val)
            self.power+=val*self.smokingModel.successBetas.get('M')
        return self.power
    
    def doBehaviour(self):
        #calculate probability of quit success using using the COMB formula:
        #prob=1/(1+e^power) where power = -1 * (C*beta1 + O*beta2 + M*beta3 + bias) 
        self.power+=self.smokingModel.successBetas['bias']
        self.power=-1*self.power
        e=2.71828 #Euler's number
        self.probBehaviour=1/(1+e^self.power)
        #for a quitter A, 
        #  run the quit success theory to calculate the probability of maintaining a quit attempt; 
        #  if k < 13
        #     if p >= threshold
        #       {A performs quit success behaviour at t and stays as a quitter at t+1;
        #        k=k+1;} 
        #     else {A performs quit failure behaviour at t and transitions to a smoker at t+1; 
        #          k=0;}
        #  elseif k==13
        #     if p >= threshold 
        #       {A performs quit success behaviour at t and transitions to an ex-smoker at t+1;} 
        #     else {A transitions to a smoker at t+1; k=0;}    
        if self.agent.k < 13:
            if self.probBehaviour >= random.uniform(0,1):
                del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                self.agent.behaviourBuffer.append('quit success') #append the agent's new behaviour to its behaviour buffer
                self.agent.setStateOfNextTimeStep(state='quitter')
                self.agent.k+=1
            else:
                del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                self.agent.behaviourBuffer.append('quit failure') #append the agent's new behaviour to its behaviour buffer
                self.agent.setStateOfNextTimeStep(state='smoker')
                self.agent.k=0
        elif self.agent.k == 13:
            if self.probBehaviour >= random.uniform(0,1):
                del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                self.agent.behaviourBuffer.append('quit success') #append the agent's new behaviour to its behaviour buffer
                self.agent.setStateOfNextTimeStep(state='ex-smoker')
                self.agent.pYearsSinceQuit.setValue(self.agent.pYearsSinceQuit.getValue()+1)
                self.agent.tickCounterExSmoker=1
            else:
                del self.agent.behaviourBuffer[0] #delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                self.agent.behaviourBuffer.append('quit failure') #append the agent's new behaviour to its behaviour buffer
                self.agent.setStateOfNextTimeStep(state='smoker')
                self.agent.k=0
        #count the number of quit attempts in the last 12 months and update the agent's variable pNumberOfRecentQuitAttempts
        self.agent.pNumberOfRecentQuitAttempts.setValue(self.agent.behaviourBuffer.count('quit attempt'))
        if self.smokingModel.runningMode=='debug':
            self.smokingModel.logfile.writelines(['agent id: '+str(self.agent.getId())+'\n',
                                                  'state: '+self.agent.getCurrentState()+'\n',
                                                  'age: '+str(self.agent.pAge.getValue())+'\n',
                                                  'buffer: '+str(self.agent.behaviourBuffer)+'\n',
                                                  'pNumberOfRecentQuitAttempts: '+str(self.agent.pNumberOfRecentQuitAttempts.getValue())+'\n',
                                                  'pYearsSinceQuit: '+str(self.agent.pYearsSinceQuit.getValue())]
