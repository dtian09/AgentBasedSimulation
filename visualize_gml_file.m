g=read_gml("./results/k=5_p=0_25/graph_k=5.gml");
t=struct2table(g);
t2=struct2table(t.edge);
source=table2array(t2(:,1));
target=table2array(t2(:,2));
source=source+1;%indices start from 1
target=target+1;
g=graph(source,target);
%c=readmatrix("nodes_colour0.csv");
c=readmatrix("nodes_colour1.csv");
%c=readmatrix("nodes_colour2.csv");
%c=readmatrix("nodes_colour3.csv");
h=figure(1);
p=plot(g,'NodeColor',c,'EdgeAlpha',0.1,'Layout','force');
%savefig(h,'graph0_k=5_intervention=1.fig');