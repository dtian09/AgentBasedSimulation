#Simulation of smoking cessation using an e-Cigarette quit theory or a social network quit theory
#running command: python SmokingModel.py props/model.yaml
    
from mpi4py import MPI
import numpy as np
from repast4py import parameters
import sys 
from typing import Dict, List
#import repast4py
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner
from repast4py.context import SharedContext
from repast4py.network import read_network, UndirectedSharedNetwork
from core.MicroAgent import MicroAgent
from core.Model import Model
from core.Theory import Theory
from core.TheoryMediator import TheoryMediator
from core.MacroEntity import MacroEntity
from SocialNetworkQuitTheory import SocialNetworkQuitTheory
from SmokingTheoriesMediator import SmokingTheoriesMediator
import networkx as nx
from Level2Attribute import Level2C, Level2O, Level2M
import pandas as pd
from checktype import *
from abc import abstractmethod

class Person(MicroAgent):
    def __init__(self, id:int, type:int, rank:int, age:int=None, sex:str=None, qimd:float=None, states: List=None, proportion_of_smoking_friends: float=None, level2C: List[Level2C]=[], level2O: List[Level2O]=[], level2M: List[Level2M]=[], eCigUse:bool=False):
        super().__init__(id=id, type=type, rank=rank)
        self.age=age
        self.sex=sex
        self.qimd=qimd
        self.states = states #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 
        self.proportion_of_smoking_friends=proportion_of_smoking_friends 
        self.eCigUse=eCigUse
        #check_list_of_Level2C(level2C)
        #check_list_of_Level2O(level2O)
        #check_list_of_Level2M(level2M)        
        self.l1: List = level2C #Level2C attributes 
        self.l2: List = level2O #Level2O attributes
        self.l3: List = level2M #Level2M attributes

    def update_eCigUse(self,eciguse: int):
        self.eCigUse=eciguse

    def update(self,id,type,rank,age,sex,qimd,states,proportion_of_smoking_friends,eCigUse):
        self.id=id
        self.type=type
        self.uid_rank=rank
        self.age=age
        self.sex=sex
        self.qimd=qimd
        self.states=states
        self.proportion_of_smoking_friends=proportion_of_smoking_friends
        self.eCigUse=eCigUse
            
    def update_state(self,state=None):
        self.states.append(state)
    
    def update_proportion_of_smoking_friends(self,proportion_of_smoking_friends=None):
        self.proportion_of_smoking_friends=proportion_of_smoking_friends
    
    def get_current_state(self):
        return self.states[-1]
    
    def get_current_time_step(self):
        return len(self.states)-1
    
    def save(self):
        """Saves the state of this agent as tuple.

        A non-ghost agent will save its state using this
        method, and any ghost agents of this agent will
        be updated with that data.

        Returns:
            The agent's state
        """
        return (self.id,self.type,self.uid_rank,self.age,self.sex,self.qimd,self.states,self.proportion_of_smoking_friends, self.level2C, self.level2O, self.level2M, self.eCigUse)

class eCigDiffusion(MacroEntity):
        def __init__(self):
            super().__init__()
            self.Et:float=None #e-cig prevalence at t
            self.deltaEt:float=None #no. of new e-cig users at t
            self.p=None
            self.q=None
            self.m=None
            self.deltaT=4/52
    
        def do_transformation(self):
            pass

        def changeInE(self):#diffusion model which outputs deltaEt
             pass
        
        def allocateDiffusion(self, p: Person):#decrement deltaEt by 1 after allocating e-cig to a new user
             pass

class eCigQuitTheory(Theory):
        def __init__(self):
            super().__init__()
            self.e : eCigDiffusion = eCigDiffusion()

        def do_situation(self):
             self.e.allocateDiffusion(self.agent)
        
        def do_action(self):
             #print('do_action does nothing')
             self.agent.update_state(state=self.agent.get_current_state())
             
class SmokingModel(Model):
        def __init__(self, comm, params : Dict):
            self.comm = comm
            self.context: SharedContext = SharedContext(comm)#create an agent population
            self.size_of_population=None
            self.rank:int = self.comm.Get_rank()
            self.type:int=0 #type of agent in id (id is a tuple (id,rank,type))
            self.props = params
            self.stapm_data_file: str = self.props["stapm_data_file"] #data file containing HSE2012 STAPM data
            self.stop_at:int = self.props["stop.at"]
            self.intervention:int = self.props["intervention"]
            self.intervention_effect:float = self.props["intervention_effect"]
            self.network_file = 'network.txt' 
            self.runner: SharedScheduleRunner = init_schedule_runner(comm)
            self.graph = None #the NetworkX graph object of the network in the network_file
            self.display_parameters_settings()
            self.nodes_color=None #color of nodes for matlab plot function
            self.smoking_prevalenceL=list()
            self.statistics_of_smoking_friends=list()
            self.theory=self.props["theory"]

        def display_parameters_settings(self):
            print('stop at time step:',str(self.stop_at))
            print('intervention:',str(self.intervention))
            print('intervention effect:',str(self.intervention_effect))
        
        def init_population(self):
            import pandas as pd
            data=pd.read_csv(self.stapm_data_file,header=0)
            (r,_)=data.shape
            self.size_of_population=r
            for i in range(r):
                agent = Person(i, self.type, self.rank, age=int(data.iat[i,0]), sex=data.iat[i,1], qimd=float(data.iat[i,2]),states=[data.iat[i,3]],level2C=[],level2O=[],level2M=[])
                if self.theory=='ecigquittheory':
                    mediator=SmokingTheoriesMediator([eCigQuitTheory()])
                elif self.theory=='regularsmokingtheory':
                    mediator=COMBTheoryMediator([RegSmokeTheory(self,l1=[],l2=[],l3=[])])
                elif self.theory=='quitattempttheory':
                    mediator=COMBTheoryMediator([QuitAttemptTheory(self,l2=[],l3=[])])
                elif self.theory=='quitsuccesstheory':
                    mediator=COMBTheoryMediator([QuitSuccessTheory(self,l1=[],l2=[],l3=[])])
                mediator.set_agent(agent)
                agent.set_mediator(mediator)                
                self.context.add(agent)
        
        def init_agents(self):
            if self.theory=='socialnetworkquittheory':
                self.graph=self.add_network_to_context_as_projection(self.context,self.network_file) #create a Repast4py network and get its NetworkX Graph object
                for agent in self.context.agents(agent_type=self.type):
                    theory=SocialNetworkQuitTheory(self)
                    mediator = SmokingTheoriesMediator([theory])
                    mediator.set_agent(agent)#link this agent to this mediator
                    agent.set_mediator(mediator)
                    agent.proportion_of_smoking_friends=theory.calculate_proportion_of_smoking_friends()
            else:
                self.init_population()
            self.size_of_population=(self.context.size()).get(-1)
            print('size of population:',self.size_of_population)
            self.nodes_color=np.zeros((self.size_of_population,3),dtype=int)
            p=self.smoking_prevalence()
            print('===statistics of smoking prevalence===')
            print('Time step 0: smoking prevalence='+str(p)+'%.')
            self.smoking_prevalenceL.append(p)
            if self.theory=='socialnetworkquittheory':
                (average_p,sd,min,max) = self.calculate_statistics_of_smoking_friends()
                self.statistics_of_smoking_friends.append((average_p,sd,min,max))
                self.generate_Gephi_network_files_and_nodes_colour_files()

        def add_network_to_context_as_projection(self,context,network_file): #read the network from network_file to add the network to context as projection
            read_network(network_file, context, self.create_Person, self.restore_Person)#add the network from network_file to context as projection
            net: UndirectedSharedNetwork = context.get_projection('ws_network')#get the Repast4py UndirectedSharedNetwork of the context
            return net.graph #return the NetworkX graph object of this Repast4py UndirectedSharedNetwork

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
                if agent.get_current_state()=='smoker':#the current state is at end of list of states
                    smokers+=1
            prevalence=np.round(smokers/self.size_of_population*100,2) #percentage of smokers
            return prevalence
        
        def calculate_statistics_of_smoking_friends(self):
            #average proportion of smoking friends of agents (%) at a time step
            #std, minimum and maximum of proportions of smoking friends of agents at a time step
            s=0
            l=[]
            for agent in self.context.agents(agent_type=self.type):
                p=agent.proportion_of_smoking_friends*100
                s+=p
                l.append(p)
            average_p=np.round(s/self.size_of_population,2)
            return (average_p,np.round(np.std(l),2),np.round(np.min(l),2),np.round(np.max(l),2))

        def generate_Gephi_network_files_and_nodes_colour_files(self):#generate nodesi.csv, edgesi.csv and nodes_colouri.csv at a time step i
            #input: self.context, self.graph
            #output: nodesi.csv (nodes.csv at ith time step)
            #        edgesi.csv (edges.csv at ith time step)
            ###format of nodes.csv
            #Id;Label;State
            #name1;name1;smoker
            #name2;name2;non-smoker
            #name3;name3;smoker
            ###format of edges.csv
            #Source;Target;Type
            #name1;Committee1;Undirected
            #name2;Committee1;Undirected
            #name3;Committee1;Undirected
            agent=list(self.context.agents(count=1))[0]
            nodesfile='nodes'+str(agent.get_current_time_step())+'.csv'
            nodes_colour_file='nodes_colour'+str(agent.get_current_time_step())+'.csv'#input to visualize_gml_file.m
            f=open(nodesfile,'w')
            f.write("Id;Label;State\n")
            for agent in self.context.agents(agent_type=self.type):
                id=str(agent.id)
                if agent.get_current_state()=='smoker':#the current state is at end of list of states
                    f.write(id+';'+id+';'+'smoker\n')
                    self.nodes_color[agent.id,:]=[1,0,0] #red
                else:
                    f.write(id+';'+id+';'+'non-smoker\n')#non-smoker: ex-smoker, never smoker and quitter 
                    self.nodes_color[agent.id,:]=[0,0,1] #blue
            f.close()
            np.savetxt(nodes_colour_file,self.nodes_color,delimiter=',',fmt='%i')
            edgesfile='edges'+str(agent.get_current_time_step())+'.csv'
            f=open(edgesfile,'w')
            f.write("Source;Target;Type\n")
            for edge in list(nx.edges(self.graph)):
                node1=edge[0]
                node2=edge[1]
                id=str(node1.id)
                id2=str(node2.id)
                f.write(id+";"+id2+";"+"Undirected\n")
            f.close()

        def eCig_prevalence(self):
            eCigUers=0
            for agent in self.context.agents(agent_type=self.type):
                if agent.eCigUse:
                    eCigUers+=1
            prevalence=np.round(eCigUers/self.size_of_population*100,2) #percentage of e-Cig users
            return prevalence

        def create_Person(self,id, type, rank, age, sex, qimd, states, proportion_of_smoking_friends, level2C, level2O, level2M, eCigUse):#create a Person object
            return Person(id, type, rank, age=age, sex=sex, qimd=qimd, states=states, proportion_of_smoking_friends=proportion_of_smoking_friends, level2C=level2C, level2O=level2O, level2M=level2M, eCigUse=eCigUse)

        def restore_Person(self,agent_data):
                id=agent_data[0]
                type=agent_data[1]
                rank=agent_data[2]
                age=agent_data[3]
                sex=agent_data[4]
                qimd=agent_data[5]
                states=agent_data[6]
                proportion_of_smoking_friends=agent_data[7]
                eCigUse=agent_data[8]
                return Person(id, type, rank, age=age, sex=sex, qimd=qimd, states=states, proportion_of_smoking_friends=proportion_of_smoking_friends, level2C=level2C, level2O=level2O, level2M=level2M, eCigUse=eCigUse)

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
            if self.theory=='socialnetworkquittheory':
                average_p,sd,min,max = self.calculate_statistics_of_smoking_friends()
                self.statistics_of_smoking_friends.append((average_p,sd,min,max))
                self.generate_Gephi_network_files_and_nodes_colour_files()
            self.context.synchronize(self.restore_Person)

        def display_statistics_of_smoking_friends(self):
            print('===statistics of the smoking friends of the agents===')
            i=0
            for average_p,sd,min,max in self.statistics_of_smoking_friends:
                print('Time step '+str(i)+': average proportion of smoking friends of each agent='+str(average_p)+'%, standard deviation of proportions of smoking friends of agents='+str(sd)+'%, minimum proportion of smoking friends of agents='+str(min)+'%, maximum proportion of smoking friends of agents='+str(max)+'%')
                i+=1

        def init_schedule(self):
            self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
            self.runner.schedule_stop(self.stop_at)

        def collect_data(self):
            if self.theory=="socialnetworkquittheory":#save results of social network quit theory based simulation to file(s)
                f=open('prevalence_of_smoking_and_average_proportion_of_smoking_friends.csv','w')#write prevalence of smoking and average proportion of smoking friends to a csv file
                f.write('prevalence of smoking:\n')
                for prev in self.smoking_prevalenceL:
                    f.write(str(prev)+',')
                f.write('\n')
                f.write('average proportion of smoking friends:\n')
                for average_p,_,_,_ in self.statistics_of_smoking_friends:
                    f.write(str(average_p)+',')
                f.write('\n')
                f.close()
            else:    
                f=open('prevalence_of_smoking.csv','w')#for non-social network based simulation, write prevalence of smoking to a csv file
                for prev in self.smoking_prevalenceL:
                    f.write(str(prev)+',')
                f.close()
        
        def init(self):
            self.init_agents()
            self.init_schedule()

        def run(self):
            self.runner.execute()
            if self.theory=='socialnetworkquittheory':
                self.display_statistics_of_smoking_friends()
            self.collect_data()

class COMBTheory(Theory):

    def __init__(self,smokingModel: SmokingModel,l1:List[Level2C]=[],l2:List[Level2O]=[],l3:List[Level2M]=[]):
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
    def makeCompC(self):
        #create CompositeC from self.__level2C
        #update __compC
        pass

    @abstractmethod    
    def makeCompO(self):
        #create CompositeO from self.__level2O
        #update __compO
        pass

    @abstractmethod
    def makeCompM(self):
        #create CompositeM from self.__level2M
        #update __compM
        pass

    @abstractmethod
    def doBehaviour(self):
        #update __behaviour
        pass

    @abstractmethod
    def doLearning(self):
        pass

    def do_situation(self):#run the situation mechanism of the agent of this theory
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
        self.theory_list[0].do_situation()

    def mediate_action(self):
        self.theory_list[0].do_action()

class RegSmokeTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,l1:List[Level2C]=[],l2:List[Level2O]=[],l3:List[Level2M]=[]):
      super().__init__(smokingModel, l1=l1, l2=l2, l3=l3)

    def makeCompC(self):
        #make compositeC from self.__level2C
        pass

    def makeCompO(self):
        #make compositeO from self.__level2O
        pass

    def makeCompM(self):
        #make compositeM from self.__level2M
        pass

    def doLearning(self):
        pass 

    def doBehaviour(self):
        #print('doBehaviour does nothing')
        self.agent.update_state(state=self.agent.get_current_state())
        
    def do_situation(self):
        pass

class QuitAttemptTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,l2:List[Level2O]=[],l3:List[Level2M]=[]):
      super().__init__(smokingModel, l1=[], l2=l2, l3=l3)

    def makeCompC(self):
        pass
    
    def makeCompO(self):
        #make compositeO from self.__level2O
        pass

    def makeCompM(self):
        #make compositeM from self.__level2M
        pass

    def doBehaviour(self):
        #print('doBehaviour does nothing')
        self.agent.update_state(state=self.agent.get_current_state())
        
    def do_situation(self):
        pass

    def doLearning(self):
        pass 

class QuitSuccessTheory(COMBTheory):

    def __init__(self,smokingModel: SmokingModel,l1:List[Level2C]=[],l2:List[Level2O]=[],l3:List[Level2M]=[]):
      super().__init__(smokingModel, l1=l1, l2=l2, l3=l3)

    def makeCompC(self):
        #make compositeC from self.__level2C
        pass

    def makeCompO(self):
        #make compositeO from self.__level2O
        pass

    def makeCompM(self):
        #make compositeM from self.__level2M
        pass

    def doBehaviour(self):
        #print('doBehaviour does nothing')
        self.agent.update_state(state=self.agent.get_current_state())
        
    def do_situation(self):
        pass

    def doLearning(self):
        pass 

def main():
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    model = SmokingModel(MPI.COMM_WORLD, params)
    model.init()
    model.run()

if __name__ == "__main__":
    main()
