#program to update a Gephi exported gml file to the states of a nodes file
#input: a gml file exported by Gephi
#       a nodes file output by SmokingModel_v0_3.py
#update the states of nodes in a gml file to the states of the nodes file
#format of nodes file
#Id;Label;State
#0;0;non-smoker
#1;1;smoker

import networkx as nx

if __name__:   
    #gml_file=sys.argv[1]
    #nodes_file=sys.argv[2]
    #output_file=sys.argv[3] #the updated gephi gml file name e.g. graph2.gml for the gml file at time step 2
    gml_file="./results/k=2_p=0_25/graph0.gml"
    #nodes_file="./results/k=2_p=0_25/nodes1.csv"
    #output_file="./results/k=2_p=0_25/graph1.gml"
    nodes_file="./results/k=2_p=0_25/nodes2.csv"
    output_file="./results/k=2_p=0_25/graph2.gml"    
    #nodes_file="./results/k=2_p=0_25/nodes3.csv"
    #output_file="./results/k=2_p=0_25/graph3.gml"
    g=nx.read_gml(gml_file)
    nodesL = [line.strip() for line in open(nodes_file)]
    del nodesL[0]
    for node in nodesL:
        l=node.split(';')
        id=l[0]
        state=l[2]
        g.nodes[id]['state']=state
        if state=='smoker':
           g.nodes[id]['graphics']['fill']='#ff1023'#red
        else:
           g.nodes[id]['graphics']['fill']='#0017fa'#blue
    nx.write_gml(g,output_file)
