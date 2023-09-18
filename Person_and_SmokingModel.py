import repast4py
from core.MicroAgent import MicroAgent
from core.Model import Model
from QuitTheory import QuitTheory
from SmokingTheoriesMediator import SmokingTheoriesMediator
import pandas as pd
from typing import Dict, List
import numpy as np

class SmokingModel(Model):

    def __init__(self, comm, params: Dict):
        self.comm = comm
        self.context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)#create an agent population
        self.size_of_population=None
        self.rank:int = self.comm.Get_rank()
        self.type:int=0 #type of agent in id (id is a tuple (id,rank,type))
        self.props = params
        self.stapm_data_file: str = self.props["stapm_data_file"] #data file containing HSE2012 STAPM data
        self.stop_at:int = self.props["stop.at"]
        self.intervention:int = self.props["intervention"]
        self.intervention_effect:float = self.props["intervention_effect"]
        self.threshold:float = self.props["threshold"]
        self.runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(self.comm)
        self.display_parameters_settings()

    def display_parameters_settings(self):
        print('STAPM data file:',self.stapm_data_file)
        print('stop at time step:',str(self.stop_at))
        print('intervention:',str(self.intervention))
        print('intervention effect:',str(self.intervention_effect))
        print('threshold:',str(self.threshold))

    def init_agents(self):
        #create a population of agents using hse2013_stapm
        data=pd.read_csv(self.stapm_data_file,header=0)
        (r,_)=data.shape
        self.size_of_population=r
        print('size of the population of agents in STAPM data file:',str(self.size_of_population))
        for i in range(r):
            agent = Person(i, self.type, self.rank, age=int(data.iat[i,0]), sex=data.iat[i,1], qimd=float(data.iat[i,2]),state=data.iat[i,3])
            theory = QuitTheory(self)
            mediator = SmokingTheoriesMediator([theory])
            agent.set_mediator(mediator)
            mediator.set_agent(agent)#link this agent to this mediator
            self.context.add(agent)
        agent=self.context.agent((0, 0, self.type))
        print('At time step: 0, smoking prevalence='+str(self.smoking_prevalence())+'%.')

    def do_situational_mechanisms(self):#macro entities change internal states of micro entities (agents)
        for agent in self.context.agents(agent_type=self.type):
            agent.do_situation()
    
    def do_action_mechanisms(self):#micro entities do actions based on their internal states
        for agent in self.context.agents(agent_type=self.type):
            agent.do_action()
   
    def smoking_prevalence(self):#smoking prevalence at the current time step
        smokers=0
        for agent in self.context.agents(agent_type=self.type):
            if agent.get_current_state()=='smoker':#the current state is at end of list of states
                smokers+=1
        prevalence=np.round(smokers/self.size_of_population,2) * 100
        return prevalence
    
    def do_per_tick(self):
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        #display smoking prevalence at current time step on screen
        agent=self.context.agent((0, 0, self.type))
        print('At time step: '+str(agent.get_current_time_step())+', smoking prevalence='+str(self.smoking_prevalence())+'%.')

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def run(self):
        self.runner.execute()

class Person(MicroAgent):
    def __init__(self, id:int, type:int, rank:int, age:int=None, sex:str=None, qimd:float=None, state:str=None):
        super().__init__(id=id, type=type, rank=rank)
        self.age=age
        self.sex=sex
        self.qimd=qimd 
        self.states: List = [state] #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 
    
    def update_state(self,state):#update state of agent at time step by appending the new state to the list of states
        self.states.append(state)
    
    def get_current_state(self):
        return self.states[-1]
    
    def get_current_time_step(self):
        return len(self.states)-1
