#to run the simulation on command line: mpirun -n 1 python SmokingModel_v0_3.py props/model.yaml
    
from mpi4py import MPI
import numpy as np
from repast4py.network import read_network, UndirectedSharedNetwork
from repast4py import parameters
from repast4py import context
import sys 
import repast4py
from core.MicroAgent import MicroAgent
from core.Model import Model
from SocialNetworkQuitTheory import SocialNetworkQuitTheory
from SmokingTheoriesMediator import SmokingTheoriesMediator
from typing import Dict, List
import networkx as nx
        
class Person(MicroAgent):
    def __init__(self, id:int, type:int, rank:int, age:int=None, sex:str=None, qimd:float=None, states: List =None, proportion_of_smoking_friends: float=None):
        super().__init__(id=id, type=type, rank=rank)
        self.age=age
        self.sex=sex
        self.qimd=qimd
        self.states = states #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation. 
        self.proportion_of_smoking_friends=proportion_of_smoking_friends #proportion of the agent's friends who smoke

    def update_state(self,state=None,proportion_of_smoking_friends=None):#update state of agent at time step by appending the new state to the list of states
        self.states.append(state)
        if proportion_of_smoking_friends!=None:
            self.proportion_of_smoking_friends=proportion_of_smoking_friends
         
    def get_current_state(self):
        return self.states[-1]
    
    def get_current_time_step(self):
        return len(self.states)-1
    
    def update(self,age,sex,qimd,states,proportion_of_smoking_friends):
        self.age=age
        self.sex=sex
        self.qimd=qimd
        self.states=states
        self.proportion_of_smoking_friends=proportion_of_smoking_friends
    
    def save(self):
        """Saves the state of this agent as tuple.

        A non-ghost agent will save its state using this
        method, and any ghost agents of this agent will
        be updated with that data.

        Returns:
            The agent's state
        """
        return (self.id,self.type,self.uid_rank,self.age,self.sex,self.qimd,self.states,self.proportion_of_smoking_friends)

class SmokingModel(Model):
    def __init__(self, comm, params: Dict):
        self.context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)#create an agent population
        self.size_of_population=None
        self.type:int=0 #type of agent in id (id is a tuple (id,rank,type))
        self.props = params
        self.stop_at:int = self.props["stop.at"]
        self.intervention:int = self.props["intervention"]
        self.intervention_effect:float = self.props["intervention_effect"]
        self.network_file = 'network.txt' 
        self.runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(comm)
        self.graph = None #the NetworkX graph object of the network in the network_file
        self.display_parameters_settings()
        self.nodes_color=None #color of nodes for matlab plot function
        self.smoking_prevalenceL=list()
        self.statistics_of_smoking_friends=list()

    def display_parameters_settings(self):
        print('stop at time step:',str(self.stop_at))
        print('intervention:',str(self.intervention))
        print('intervention effect:',str(self.intervention_effect))
        
    def create_Person(self,nid, type, rank, age, sex, qimd, states):#create a Person object
            return Person(nid, type, rank, age=age, sex=sex, qimd=qimd, states=states)

    def restore_Person(self,agent_data):#agent_data is the tuple returned by save method
            id=agent_data[0]
            type=agent_data[1]
            rank=agent_data[2]
            age=agent_data[3]
            sex=agent_data[4]
            qimd=agent_data[5]
            states=agent_data[6]
            proportion_of_smoking_friends=agent_data[7]
            return Person(id, type, rank, age=age, sex=sex, qimd=qimd, states=states, proportion_of_smoking_friends=proportion_of_smoking_friends)

    def add_network_to_context_as_projection(self,context,network_file): #read the network from network_file to add the network to context as projection
        read_network(network_file, context, self.create_Person, self.restore_Person)#add the network from network_file to context as projection
        net: UndirectedSharedNetwork = context.get_projection('ws_network')#get the Repast4py UndirectedSharedNetwork of the context
        return net.graph #return the NetworkX graph object of this Repast4py UndirectedSharedNetwork

    def init_agents(self):
        self.graph=self.add_network_to_context_as_projection(self.context,self.network_file) #create a Repast4py network and get its NetworkX Graph object
        self.size_of_population=(self.context.size()).get(-1)
        print('size of population:',self.size_of_population)
        self.nodes_color=np.zeros((self.size_of_population,3),dtype=int)
        for agent in self.context.agents(agent_type=self.type):
            theory = SocialNetworkQuitTheory(self)
            mediator = SmokingTheoriesMediator([theory])
            agent.set_mediator(mediator)
            mediator.set_agent(agent)#link this agent to this mediator
            agent.proportion_of_smoking_friends=theory.calculate_proportion_of_smoking_friends()
        p=self.smoking_prevalence()
        print('At time step: 0 (beginning of simulation), smoking prevalence='+str(p)+'%.')
        self.smoking_prevalenceL.append(p)
        (average_p,sd,min,max) = self.calculate_statistics_of_smoking_friends()
        self.statistics_of_smoking_friends.append((average_p,sd,min,max))
        self.generate_Gephi_network_files_and_nodes_colour_files()

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

    def do_per_tick(self):
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        #display smoking prevalence at current time step on screen
        agent=list(self.context.agents(count=1))[0]
        p=self.smoking_prevalence()
        print('At time step: '+str(agent.get_current_time_step())+' (after doing situation mechanism and action mechanism): smoking prevalence='+str(p)+'%.')
        self.smoking_prevalenceL.append(p)
        average_p,sd,min,max = self.calculate_statistics_of_smoking_friends()
        self.statistics_of_smoking_friends.append((average_p,sd,min,max))
        self.generate_Gephi_network_files_and_nodes_colour_files()
        self.context.synchronize(self.restore_Person)

    def display_statistics_of_smoking_friends(self):
        i=0
        for average_p,sd,min,max in self.statistics_of_smoking_friends:
            print('At time step '+str(i)+' (before doing situation mechanism and action mechanism): average proportion of smoking friends of each agent='+str(average_p)+'%, std='+str(sd)+'%, min='+str(min)+'%, max='+str(max)+'%')
            i+=1

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def run(self):
        self.runner.execute()
        self.display_statistics_of_smoking_friends()
        f=open('prevalence_of_smoking_and_average_proportion_of_smoking_friends.csv','w')#write prevalence of smoking and average proportion of smoking friends to csv file for plotting
        f.write('prevalence of smoking:\n')
        for prev in self.smoking_prevalenceL:
            f.write(str(prev)+',')
        f.write('\n')
        f.write('average proportion of smoking friends:\n')
        for average_p,_,_,_ in self.statistics_of_smoking_friends:
            f.write(str(average_p)+',')
        f.write('\n')
        f.close()
         
def main():
    parser = repast4py.parameters.create_args_parser()
    args = parser.parse_args()
    params = repast4py.parameters.init_params(args.parameters_file, args.parameters)
    model = SmokingModel(MPI.COMM_WORLD, params)
    model.init_agents()
    model.init_schedule()
    model.run()

if __name__ == "__main__":
    main()

