%plot prevalence of smoking and average proportion of smoking friends of each agent.
x=(0:12);
%intervention=0
prevalence_smoking=[18.94,5.22,2.24,1.12,0.6,0.3,0.19,0.1,0.04,0.01,0.0,0.0,0.0];
average_prop_of_smoking_friends=[18.73,18.73,5.04,2.16,1.07,0.53,0.28,0.18,0.07,0.03,0.01,0.0,0.0];
%%%intervention=1
%prevalence_smoking=[18.94,2.7,0.34,0.02,0.01,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0];
%average_prop_of_smoking_friends=[18.98,18.98,2.64,0.3,0.04,0.03,0.0,0.0,0.0,0.0,0.0,0.0,0.0];
plot(x,prevalence_smoking,'-+r',LineWidth=1);
hold on
plot(x,average_prop_of_smoking_friends,'-+b',LineWidth=1);
xlabel('Time steps','FontWeight','bold','FontSize',14);
ylabel('Percentage','FontWeight','bold','FontSize',14);
ax = gca;
ax.FontSize = 13;
ax.FontWeight='bold';
ax.XTick=0:1:12;
legend('Prevalence of Smoking','Average Proportion of Smoking Friends of Each Agent','Location','NE');
%title('Relationship of Prevalence of Smoking and Average Proportion of Smoking Friends of Each Agent');