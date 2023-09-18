import repast4py
from core.MicroAgent import MicroAgent
from core.Model import Model
from QuitTheory import QuitTheory
from SmokingTheoriesMediator import SmokingTheoriesMediator
import pandas as pd
from typing import Dict, List
import numpy as np

#to do: define SmokingModel as subclass of Model class
class SmokingModel():

    def __init__(self, comm, params: Dict):
        self.comm = comm
        #self.context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)#create an agent population
        super().conte
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

    #to do: complete the methods below:

    def init_agents(self):
        #create a population of agents using hse2012_stapm
    
    def do_situational_mechanisms(self):#macro entities change internal states of micro entities (agents)

    def do_action_mechanisms(self):#micro entities do actions based on their internal states
   
    def smoking_prevalence(self):#smoking prevalence at the current time step
        
    def do_per_tick(self):
        #call do_situational_mechanisms()
        #call do_action_mechanisms()
        #display smoking prevalence at current time step on screen
        
    def init_schedule(self):
        #set the event of the schedule which repeats each time step
        #self.runner.schedule_stop(self.stop_at)

    def run(self):
        self.runner.execute()

#to do: define Person as a subclass of MicroAgent
class Person():
    def __init__(self, id:int, type:int, rank:int, age:int=None, sex:str=None, qimd:float=None, state:str=None):
        super().__init__(id=id, type=type, rank=rank)
        self.age=age
        self.sex=sex
        self.qimd=qimd 
        self.states: List = [state] #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 
    
    #to do: complete the methods  
    def update_state(self,state):
       #update state of agent at time step by appending the new state to the list of states
    
    def get_current_state(self):
        #return current state of agent
    
    def get_current_time_step(self):
        #return current time step
