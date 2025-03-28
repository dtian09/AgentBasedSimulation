'''
this tool plots the annual e-cig prevalence of subgroups stored in csv files (output of diffusion models of ABM)
'''
import matplotlib.pyplot as plt
import csv

def read_prevalence_file_into_list(filename):
    with open(filename, mode='r') as file:
      reader = csv.reader(file)
      # Read the single line into a list
      Et = next(reader)  # `next(reader)` fetches the first row
    if Et[-1]=='':
        del(Et[-1]) #remove any empty string at end of list
    return Et

def create_folder(folder_path):
    import os
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def plot_prevalence():
        #dir='./output (ticks=years deltaEt = 0 at tick0)/'
        #dir='./output (all COM-B models deltaEt = ecig users in baseline population at tick0)/'
        dir='./output/'
        outdir = dir+'plots' #folder to create for plots of 
        #dir='./output2/'
        #outdir = dir+'plots_of_quarters_prevalence' #folder to create for plots
        create_folder(outdir)
        filename = dir+'Exsmoker_less1940.csv' #ecig prevalence of every January from start to end of simulation
        #filename = dir+'Exsmoker_less1940_quarters.csv'
        exsmokerless1940=read_prevalence_file_into_list(filename)
        filename = dir+'Exsmoker1941_1960.csv'
        #filename = dir+'Exsmoker1941_1960_quarters.csv'
        exsmoker1941_1960=read_prevalence_file_into_list(filename)
        filename = dir+'Exsmoker1961_1980.csv'
        #filename = dir+'Exsmoker1961_1980_quarters.csv'
        exsmoker1961_1980=read_prevalence_file_into_list(filename)
        filename = dir+'Exsmoker1981_1990.csv'
        #filename = dir+'Exsmoker1981_1990_quarters.csv'
        exsmoker1981_1990=read_prevalence_file_into_list(filename)
        filename = dir+'Exsmoker_over1991.csv'
        #filename = dir+'Exsmoker_over1991_quarters.csv'
        exsmoker_over1991=read_prevalence_file_into_list(filename)
        filename = dir+'Smoker_less1940.csv'
        #filename = dir+'Smoker_less1940_quarters.csv'
        smokerless1940=read_prevalence_file_into_list(filename)
        filename = dir+'Smoker1941_1960.csv'
        #filename = dir+'Smoker1941_1960_quarters.csv'
        smoker1941_1960=read_prevalence_file_into_list(filename)
        filename = dir+'Smoker1961_1980.csv'
        #filename = dir+'Smoker1961_1980_quarters.csv'
        smoker1961_1980=read_prevalence_file_into_list(filename)
        filename = dir+'Smoker1981_1990.csv'
        #filename = dir+'Smoker1981_1990_quarters.csv'
        smoker1981_1990=read_prevalence_file_into_list(filename)
        filename = dir+'Smoker_over1991.csv'
        #filename = dir+'Smoker_over1991_quarters.csv'
        smoker_over1991=read_prevalence_file_into_list(filename)
        filename = dir+'Neversmoked_over1991.csv'
        #filename = dir+'Neversmoked_over1991_quarters.csv'
        neversmoked_over1991=read_prevalence_file_into_list(filename)
        for subgroup in [(exsmokerless1940,"Exsmoker_less1940"),
                        (exsmoker1941_1960,"Exsmoker1941_1960"),
                        (exsmoker1961_1980,"Exsmoker1961_1980"),
                        (exsmoker1981_1990,"Exsmoker1981_1990"),
                        (exsmoker_over1991,"Exsmoker_over1991"),
                        (smokerless1940,"Smoker_less1940"),
                        (smoker1941_1960,"Smoker1941_1960"),
                        (smoker1961_1980,"Smoker1961_1980"),
                        (smoker1981_1990,"Smoker1981_1990"),
                        (smoker_over1991,"Smoker_over1991"),
                        (neversmoked_over1991,"Neversmoked_over1991")]:
            Et=subgroup[0]
            Et = [float(prev) for prev in Et]
            #print(f"Et: '{Et}'")            
            plt.figure()#create a new figure for each plot
            plt.plot([x+1 for x in range(0,len(Et))], Et, ".-", color='blue', markerfacecolor='red', markeredgecolor='red')
            xtick_positions=[]
            xtick_labels=[]
            xtick=1
            year = 2010
            while xtick <= len(Et):
                xtick_positions.append(xtick)
                xtick+=2
                xtick_labels.append(year)
                year+=2
            plt.xticks(xtick_positions, xtick_labels)
            ytick_positions = [y/10 for y in range(0,11)]
            ytick_labels = ytick_positions
            plt.yticks(ytick_positions, ytick_labels)
            plt.title(subgroup[1])
            plt.xlabel("Year")
            plt.ylabel("Prevalence of e-cigarette use")
            plt.savefig(outdir+'/ecig_prevalence_'+subgroup[1]+'.jpeg', format='jpeg')
        print(F"Plots were saved to '{outdir}'.")

if __name__ == "__main__":
    plot_prevalence()
