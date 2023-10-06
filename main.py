#Simulation of smoking behaviour using regular smoking theory or quit attempt theory or quit success theory or e-cigarette quit theory or social network quit theory
#
###The following parameters of the simulation are set in props/model.yaml###
#stapm_data_file: STAPM data file 'hse2012_stapm.csv'
#k: each node is joined with its k nearest neighbors in a ring topology of a social network. minimum value of k: 2
#p: the probability of rewiring each edge in a social network; rewiring each edge randomly links each node to another node.
#stop.at: 12 #the final time step of simulation 
#intervention: 0 (not using intervention) or 1 (use intervention)
#intervention_effect: a number > 1 or a number >0 and <1
#                     (A number >1 increases intention (probability) to quit smoking;
#                      a number >0 and <1 decreases intention to quit smoking;
#                      1 is eqivalent to not using intervention used.)
###To run this simulation using a quit attempt theory, 
#1. Open model.yaml and uncomment the line "quittheory: "quitattempttheory"" and comment the other quit theories
#2. Save model.yaml
#3. Run the command: python main.py props/model.yaml

import os
import sys
from repast4py import parameters

def run(stapm_data_file,theory,k,p):
    #stapm_data_file: stapm data file
    #theory: 'socialnetworkquittheory' or 'ecigquittheory' or 'regularsmokingtheory' or 'quitattempttheory' or 'quitsuccesstheory'
    #k: each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
    #p: the probability of rewiring each edge    
    if theory=='socialnetworkquittheory':
        print(theory)
        #generate a social network with STAPM data added using NetworkX library (the network is saved to network.txt)
        #command: python generate_social_network.py hse2012_stapm.csv 2 0.25
        cmd='python generate_social_network.py '+stapm_data_file+' network.txt '+str(k)+' '+str(p)
        os.system(cmd)
    elif theory=='ecigquittheory':
        print(theory)
    elif theory=='regularsmokingtheory':
        print(theory)
    elif theory=='quitattempttheory':
        print(theory)
    elif theory=='quitsuccesstheory':
        print(theory) 
    else:
        sys.exit('invalid theory:'+theory)
    #run ABM simulation
    cmd='mpirun -n 1 python Person_and_SmokingModel.py props/model.yaml'
    os.system(cmd)

if __name__ == "__main__":
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    theory=params['theory']
    stapm_data_file=params['stapm_data_file']
    #parameters of social network
    k=params['k']
    p=params['p']
    run(stapm_data_file,theory,k,p)