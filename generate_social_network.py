#user interface to generate a social network
#how to run: python generate_social_network.py hse2012_stapm.csv network.txt 2 0.25
import sys
from SocialNetwork import SocialNetwork

stapm_data_file=sys.argv[1]
network_file=sys.argv[2]
#parameters of watts strogatz network
k=sys.argv[3] #Each node is joined with its k nearest neighbors in a ring topology. minimum value of k: 2
p=sys.argv[4] #p: the probability of rewiring each edge. Rewiring some edges of a ring topology makes the network resembles a realistic social network.
print('STAPM data: '+stapm_data_file)
print('network file: '+network_file)
print('parameters of Watts–Strogatz graph algorithm for generating a social network: k='+str(k)+', p='+str(p))
ws_net=SocialNetwork(stapm_data_file=stapm_data_file, n_ranks=1, k=int(k), p=float(p), network_file=network_file)
network_file=ws_net.generate_network_file()