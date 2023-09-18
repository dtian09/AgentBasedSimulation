#Program to simulate the influence of a social metwork (friendship network) on the smoking prevalence of the age 16+ population in 2012 Health Survey England 
#1. setup a Watts-Strogatz small world (WS) network (social network) over the population of individuals in HSE2012 STAPM data.
#   https://networkx.org/documentation/stable/reference/generated/networkx.generators.random_graphs.watts_strogatz_graph.html
#2. action mechanism of an agent:
#   threshold of agent = proportion of the agent's smoking friends who are its neighbours in the network
#   If agent is a smoker at T-1 and capability x intention_to_quit >= threshold of agent
#      set the state of the agent at T to quitter
#   else
#      set the state of the agent at T to its state at T-1
# 
###how to run: python main.py <stapm_data_file> network.txt <k> <p>
#stapm_data_file: STAPM data file 'hse2012_stapm.csv'
#k: Each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
#p: the probability of rewiring each edge which links each agent to a node randomly. default value of p = 0.25
#
#Example command: python main.py hse2012_stapm.csv network.txt 2 0.25 
import os
import sys

def run(stapm_data_file,network_file,k,p):
    #stapm_data_file: stapm data file
    #k: each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
    #p: the probability of rewiring each edge
    #generate a social network with STAPM data added using NetworkX library (the network is saved to network.txt)
    #command: python generate_social_network.py hse2012_stapm.csv 2 0.25
    cmd='python3 generate_social_network.py '+stapm_data_file+' '+network_file+' '+str(k)+' '+str(p)
    os.system(cmd)
    #run ABM simulation
    #command: python Person_and_SmokingModel.py props/model.yaml
    cmd='python3 Person_and_SmokingModel.py props/model.yaml'
    os.system(cmd)

if __name__ == "__main__":
    stapm_data_file=sys.argv[1]
    network_file=sys.argv[2]
    #parameters of WS network
    k=sys.argv[3] #k: each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
    p=sys.argv[4] #p: the probability of rewiring each edge
    run(stapm_data_file,network_file,k,p)