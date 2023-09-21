#Simulation of quitting smoking using either an e-cigarette quit theory or a social network quit theory
####Social Network Quit Theory####
#Program to simulate smoking behaviour of agents in a small world network representing a friendship network
#Simulation of the effect of an agents' proportion of smoking friends on the agent's decision to quit smoking  
#1. setup a Watts-Strogatz small world network (network of friends) over the population of individuals in HSE2012 STAPM data.
#   https://networkx.org/documentation/stable/reference/generated/networkx.generators.random_graphs.watts_strogatz_graph.html
#2. action mechanism of an agent:
#   threshold of agent = proportion of the agent's smoking friends who are connected to the agent by one edge (its neighbours)
#   If agent is a smoker at T-1 and capability x intention_to_quit >= threshold of agent
#      set the state of the agent at T to quitter
#   else
#      set the state of the agent at T to its state at T-1
# 
#stapm_data_file: STAPM data file 'hse2012_stapm.csv'
#k: Each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
#p: the probability of rewiring each edge which links each agent to a node randomly.
#
#To run this simulation using a social network quit theory, 
#1. Open model.yaml and uncomment the line "quittheory: "socialnetworkquittheory"" and comment the line "quittheory: "ecigquittheory""
#2. Save model.yaml
#3. Run the command: python main.py props/model.yaml

import os
import sys
from repast4py import parameters

def run(stapm_data_file,quittheory,k,p):
    #stapm_data_file: stapm data file
    #quittheory: 'socialnetworkquittheory' or 'ecigquittheory'
    #k: each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
    #p: the probability of rewiring each edge
    
    if quittheory=='socialnetworkquittheory':
        print(quittheory)
        #generate a social network with STAPM data added using NetworkX library (the network is saved to network.txt)
        #command: python generate_social_network.py hse2012_stapm.csv 2 0.25
        cmd='python generate_social_network.py '+stapm_data_file+' network.txt '+str(k)+' '+str(p)
        os.system(cmd)
    elif quittheory=='ecigquittheory':
        print(quittheory)
    else:
        sys.exit('invalid quit theory:'+quittheory)
    
    #run ABM simulation
    #command: python Person_and_SmokingModel.py props/model.yaml
    cmd='python Person_and_SmokingModel.py props/model.yaml'
    os.system(cmd)

if __name__ == "__main__":
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    quittheory=params['quittheory']
    stapm_data_file=params['stapm_data_file']
    #parameters of social network
    k=params['k']
    p=params['p']
    run(stapm_data_file,quittheory,k,p)