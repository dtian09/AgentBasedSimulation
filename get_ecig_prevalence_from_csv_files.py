#get quarterly e-cigarette prevalence and the prevalence of each Januray from all the monthly prevalence (csv file) 
#then, write the quarterly e-cigarette and the prevalence of each Januray into csv files
import sys
module_dir = "X:/Shared/code/ABM_software/smokingABM/"
sys.path.append(module_dir)
from plot_annual_ecig_diffusions import read_prevalence_file_into_list, create_folder

def write_ecig_prevalence_to_csv_files():
        dir='X:/Shared/code/ABM_software/smokingABM/output/'
        outdir='X:/Shared/code/ABM_software/smokingABM/output2/'
        filename=dir+'Exsmoker_less1940_all_months.csv'
        Exsmoker_less1940 = read_prevalence_file_into_list(filename)
        filename=dir+'Exsmoker_over1991_all_months.csv'
        Exsmoker_over1991 = read_prevalence_file_into_list(filename)
        filename=dir+'Exsmoker1941_1960_all_months.csv'
        Exsmoker1941_1960 = read_prevalence_file_into_list(filename)
        filename=dir+'Exsmoker1961_1980_all_months.csv'
        Exsmoker1961_1980 = read_prevalence_file_into_list(filename)
        filename=dir+'Exsmoker1981_1990_all_months.csv'
        Exsmoker1981_1990 = read_prevalence_file_into_list(filename)
        filename=dir+'Neversmoked_over1991_all_months.csv'
        Neversmoked_over1991 = read_prevalence_file_into_list(filename)
        filename=dir+'Smoker_less1940_all_months.csv'
        Smoker_less1940 = read_prevalence_file_into_list(filename)
        filename=dir+'Smoker_over1991_all_months.csv'
        Smoker_over1991= read_prevalence_file_into_list(filename)
        filename = dir +'Smoker1941_1960_all_months.csv'
        Smoker1941_1960 = read_prevalence_file_into_list(filename)
        filename = dir + 'Smoker1961_1980_all_months.csv'
        Smoker1961_1980 = read_prevalence_file_into_list(filename)
        filename = dir + 'Smoker1981_1990_all_months.csv'
        Smoker1981_1990 = read_prevalence_file_into_list(filename)
        filename = dir + 'Smoker_over1991_all_months.csv'
        Smoker_over1991 = read_prevalence_file_into_list(filename)
        ecig_Et={"Exsmoker_less1940" : Exsmoker_less1940,
                                "Exsmoker1941_1960" : Exsmoker1941_1960,
                                "Exsmoker1961_1980" : Exsmoker1961_1980,
                                "Exsmoker1981_1990" : Exsmoker1981_1990,
                                "Exsmoker_over1991" : Exsmoker_over1991,
                                "Smoker_less1940" : Smoker_less1940,
                                "Smoker1941_1960" : Smoker1941_1960,
                                "Smoker1961_1980" : Smoker1961_1980,
                                "Smoker1981_1990" : Smoker1981_1990,
                                "Smoker_over1991" : Smoker_over1991,
                                "Neversmoked_over1991" : Neversmoked_over1991 }
        start_time_of_disp_diffusions=146
        stop_at = 195        
        create_folder(outdir)
        l=[0 for _ in range(0,start_time_of_disp_diffusions-1)] 
        Neversmoked_over1991= l + Neversmoked_over1991 #neversmoker1991+ only used disposable ecig from 2022 and did not use ecig before 2022
        indices_to_plot=[] #indices of ecig_Et list to plot diffusions
        quarter_indices=[] #indices of quarters 
        indx=0 #index of next January (index 0 of ecig_Et list is 1st January)
        #quarter_indx=2 #index of next quarter (index 2 is 1st March and quarter1)
        quarter_indx=0 #index of next quarter (index 0 is 1st January and quarter1)
        while indx+1 <= stop_at:
            indices_to_plot.append(indx)
            indx+=12 #indx of next January
        while quarter_indx+1 <= stop_at:
            quarter_indices.append(quarter_indx)
            quarter_indx+=3
        for subgroup in ["Exsmoker_less1940",
                        "Exsmoker1941_1960",
                        "Exsmoker1961_1980",
                        "Exsmoker1981_1990",
                        "Exsmoker_over1991",
                        "Smoker_less1940",
                        "Smoker1941_1960",
                        "Smoker1961_1980",
                        "Smoker1981_1990",
                        "Smoker_over1991",
                        "Neversmoked_over1991"]:            
            f=open(outdir+subgroup+'.csv', 'w')
            f2=open(outdir+subgroup+'_quarters.csv', 'w')
            f.write(str(ecig_Et[subgroup][indices_to_plot[0]]))
            i=1
            while i < len(indices_to_plot):                
                f.write(','+str(ecig_Et[subgroup][indices_to_plot[i]]))
                i+=1
            f2.write(str(ecig_Et[subgroup][quarter_indices[0]]))
            i2=1
            while i2 < len(quarter_indices):
                f2.write(','+str(ecig_Et[subgroup][quarter_indices[i2]]))
                i2+=1
            f.close()
            f2.close()
        print('ecig prevalence saved to '+outdir)

if __name__ == "__main__":
    write_ecig_prevalence_to_csv_files()