import sys 
import pandas as pd
import networkx as nx
from repast4py.network import write_network
from core.MacroEntity import MacroEntity

class SocialNetwork(MacroEntity):
    def __init__(self, stapm_data_file:str=None, n_ranks:int=1, k:int=None, p:float=None, network_file:str=None):
        super().__init__()
        self.stapm_data_file=stapm_data_file
        self.n_ranks=n_ranks
        self.network_file=network_file
        #parameters of WS network
        self.k=k #Each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
        self.p=p #the probability of rewiring each edge

    def generate_network_file(self):
        #Generates a watts strogatz network with STAPM data added to its nodes   
        data=pd.read_csv(self.stapm_data_file,header=0)
        (n_agents,_)=data.shape       
        g = nx.watts_strogatz_graph(n_agents, self.k, self.p)
        pos = nx.spring_layout(g, iterations=15, seed=1721)
        nx.draw_networkx(g, pos=pos)
        nx.write_gml(g, "graph_k="+str(self.k)+".gml")#input to visualize_gml_file.m
        #print('The graph of the network is saved to: ',"graph_k="+str(self.k)+".gml")
        write_network(g, 'ws_network', self.network_file, self.n_ranks,partition_method='random', rng='default')#write the network to a file in a format that can be read by the repast4py.network.read_network() function.
        network_file=self.add_STAPM_data_to_network(self.network_file,self.stapm_data_file)#add the STAPM data (e.g. age, sex, imd quintile and state) to the nodes (agents) of the network
        return network_file
    
    def add_STAPM_data_to_network(self,fname,stapm_data_file):
        #STAPM data: sex, age, imd quintile and state is added to each node
        #The following attributes of agents are also added to each node: 
        #       proportion of smoking friends: None
        #       COMB attributes (level2C, level2O, level2M attributes): None
        #       eCigUse: None
        #e.g. 
        #friend_network 0
        #1 0 1 {"age": 23, "sex": "male", "imd quintile": 5, "states": ["smoker"], "proportion_of_smoking_friends": "None", "level2C": "None", "level2O": "None", "level2M": "None", "eCigUse": "None"}
        #2 0 1 {"age": 24, "sex": "female", "imd quintile": 1, "states": ["never_smoker"], "proportion_of_smoking_friends": "None", "level2C": "None", "level2O": "None", "level2M": "None", "eCigUse": "None"}
        #3 0 0 {"age": 30, "sex": "male", "imd quintile": 5, "states": ["ex-smoker"], "proportion_of_smoking_friends": "None", "level2C": "None", "level2O": "None", "level2M": "None", "eCigUse": "None"}
        net_fileL = [line.strip() for line in open(fname)]
        f=open(fname,'w')
        data=pd.read_csv(stapm_data_file,header=0)
        (r,_)=data.shape
        for i in range(r):
            age=int(data.iat[i,0])
            sex=data.iat[i,1]
            qimd=float(data.iat[i,2])
            state=data.iat[i,3]
            attrs=" {\"age\":"+str(age)+", \"sex\": \""+sex+"\", \"qimd\": "+str(qimd)+", \"states\": [\""+state+"\"]"+", \"proportion_of_smoking_friends\": \"None\""+", \"level2C\": \"None\""+", \"level2O\": \"None\""+", \"level2M\": \"None\""+", \"eCigUse\": \"None\"}"
            net_fileL[i+1]=net_fileL[i+1]+attrs
        for j in range(len(net_fileL)):
            f.write(net_fileL[j]+'\n')
        f.close()
        return fname
    
    def do_transformation(self):
        transformational_mechanism=None


