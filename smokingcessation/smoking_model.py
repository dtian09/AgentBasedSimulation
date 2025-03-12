import numpy as np
import pandas as pd
import sys
from typing import Dict
from repast4py.context import SharedContext
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner
from config.definitions import ROOT_DIR, AgentState, SubGroup, eCigDiffSubGroup, eCigType
from mbssm.model import Model
import config.global_variables as g
import os
import random
import gc
import ipdb #debugger

class SmokingModel(Model):

    def __init__(self, comm, params: Dict):
        super().__init__(comm, params)
        self.comm = comm
        self.context: SharedContext = SharedContext(comm)  # create an agent population
        self.population_counts={}#key=subgroup, value=count of agents of subgroup
        self.init_population_counts()
        self.size_of_population = None
        self.type = 0 #the type of the agents in the population. all agents have the same type 
        self.rank: int = self.comm.Get_rank()
        self.props = params
        self.age_of_sale=18
        self.seed = self.props["seed"]
        random.seed(self.seed) #set the random seed of ABM
        self.data_file: str = self.props["data_file"]  # the baseline synthetic population (STAPM 2013 data)
        self.regionalSmokingPrevalenceFile = self.props["regional_prevalence"]
        self.regionalSmokingPrevalence=None 
        self.readInRegionalPrevalence()
        self.data = pd.read_csv(f'{ROOT_DIR}/' + self.data_file, encoding='ISO-8859-1')
        self.data = self.replace_missing_value_with_zero(self.data)
        self.relapse_prob_file = f'{ROOT_DIR}/' + self.props["relapse_prob_file"]
        self.relapse_prob = pd.read_csv(self.relapse_prob_file)
        self.death_prob_file = f'{ROOT_DIR}/' + self.props["death_prob_file"]
        self.death_prob = pd.read_csv(self.death_prob_file, encoding='ISO-8859-1')  
        self.year_of_current_time_step = self.props["year_of_baseline"]
        self.year_number = 0
        self.current_time_step = 0
        self.months_counter = 0 #count the number of months of the current year
        self.formatted_month = None #formatted month: Nov-06, Dec-10 etc.
        self.start_year_tick = 1 #tick of January of the current year
        self.end_year_tick = 12 #tick of December of the current year
        self.stop_at: int = self.props["stop.at"]  # final time step (tick) of simulation
        self.tickInterval=self.props["tickInterval"] #time duration of a tick e.g. 4.3 weeks (1 month)
        self.lbda=self.props["lambda"] #cCigAddictStrength[t+1] = round (cCigAddictStrength[t] * exp(lambda*t)), where lambda = 0.0368 and t = 4 (weeks)
        self.alpha=self.props["alpha"] #prob of smoker self identity = 1/(1+alpha*(k*t)^beta) where alpha = 1.1312, beta = 0.500, k = no. of quit successes and t = 4 (weeks)
        self.beta=self.props["beta"]    
        self.runner: SharedScheduleRunner = init_schedule_runner(comm)
        #hashmaps (dictionaries) to store betas (coefficients) of the COMB formula of regular smoking theory, quit attempt theory and quit success theory
        self.uptake_betas = {}
        self.attempt_betas = {}  # hashmap to store betas of the COMB formula of quit attempt theory
        self.success_betas = {}  # hashmap to store betas of the COMB formula of quit success theory
        self.store_betas_of_comb_formulae_into_maps()        
        self.level2_attributes_of_uptake_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of regular smoking theory
        self.level2_attributes_of_attempt_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of quit attempt theory
        self.level2_attributes_of_success_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of quit success theory
        self.store_level2_attributes_of_comb_formulae_into_maps()
        self.level2_attributes_names = list(self.data.filter(regex='^[com]').columns)#get the level 2 attribute names from the data file
        self.running_mode = self.props['ABM_mode']  # debug or normal mode
        self.difference_between_start_time_of_ABM_and_start_time_of_non_disp_diffusions = self.props['difference_between_start_time_of_ABM_and_start_time_of_non_disp_diffusions']
        self.difference_between_start_time_of_ABM_and_start_time_of_disp_diffusions = self.props['difference_between_start_time_of_ABM_and_start_time_of_disp_diffusions']        
        self.agents_to_kill=set() #unique ids of the agents to be killed after iteration through the population during situational mechanism
        if self.running_mode == 'debug':
            self.smoking_prevalence_l = list()
        self.regular_smoking_behaviour = self.props['regular_smoking_behaviour'] #COMB or STPM
        self.quitting_behaviour = self.props['quitting_behaviour'] #COMB or STPM
        if self.regular_smoking_behaviour=='STPM':
            self.initiation_prob_file = f'{ROOT_DIR}/' + self.props["initiation_prob_file"]
            self.initiation_prob = pd.read_csv(self.initiation_prob_file) 
        elif self.regular_smoking_behaviour=='COMB':
            pass
        else:
            sys.exit('invalid regular smoking behaviour: '+self.regular_smoking_behaviour)
        if self.quitting_behaviour=='STPM':
            self.quit_prob_file = f'{ROOT_DIR}/' + self.props["quit_prob_file"]
            self.quit_prob = pd.read_csv(self.quit_prob_file)   
        elif self.quitting_behaviour=='COMB':
            pass
        else:
            sys.exit('invalid quitting behaviour: '+self.quitting_behaviour)
        if not os.path.exists(f'{ROOT_DIR}/output'):
            os.makedirs(f'{ROOT_DIR}/output', exist_ok=True)
        if self.running_mode == 'debug':
            self.logfile = open(f'{ROOT_DIR}/output/logfile.txt', 'w')
            self.logfile.write('debug mode\n')
            if self.regular_smoking_behaviour=='COMB':
                print('This ABM is using the regular smoking COM-B model, ')
                self.logfile.write('This ABM is using the regular smoking COM-B model, ')
            elif self.regular_smoking_behaviour=='STPM':
                print('This ABM is using the STPM initiation transition probabilities, ')
                self.logfile.write('the STPM initiation transition probabilities, ')
            if self.quitting_behaviour=='COMB':
                print('quit attempt COM-B model, quit success COM-B model, ')
                self.logfile.write('the quit attempt COM-B model, quit success COM-B model ')
            elif self.quitting_behaviour=='STPM':
                print('STPM quitting transition probabilities ')
                self.logfile.write('the STPM quitting transition probabilities ')
            print('and the STPM relapse transition probabilities.')
            self.logfile.write('and the STPM relapse transition probabilities.\n')  
            self.ecig_Et = {                                       
                            eCigDiffSubGroup.Exsmokerless1940:[], #ecig prevalence of each tick starting from tick 1 (January)
                            eCigDiffSubGroup.Exsmoker1941_1960:[],
                            eCigDiffSubGroup.Exsmoker1961_1980:[],
                            eCigDiffSubGroup.Exsmoker1981_1990:[],
                            eCigDiffSubGroup.Exsmoker_over1991:[],
                            eCigDiffSubGroup.Smokerless1940:[],
                            eCigDiffSubGroup.Smoker1941_1960:[],
                            eCigDiffSubGroup.Smoker1961_1980:[],
                            eCigDiffSubGroup.Smoker1981_1990:[],
                            eCigDiffSubGroup.Smoker_over1991:[],
                            eCigDiffSubGroup.Neversmoked_over1991:[]}

    def format_month_and_year(self):
        '''
        convert the current month and current year of the ABM to the format: Nov-06, Dec-10 etc. used by regional smoking prevalence file
        '''
        month=self.months_counter
        year=self.year_of_current_time_step
        from datetime import datetime
        self.formatted_month = datetime(year, month, 1).strftime("%b-%y")
    
    def readInRegionalPrevalence(self):
        '''
        read in the regional smoking prevalences between 2011 and 2019 into a dataframe
        '''
        df=pd.read_csv(f'{ROOT_DIR}/' + self.regionalSmokingPrevalenceFile, encoding='ISO-8859-1')
        pattern = r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-1[1-9]$"#match months: Jan-11,Feb-11,...,Dec-19
        self.regionalSmokingPrevalence = df[df["month"].str.match(pattern, na=False)]
        self.regionalSmokingPrevalence = self.regionalSmokingPrevalence[['month','region','prevalence']]
     
    def readInDeathProbabilities(self):
        self.death_prob = pd.read_csv(f'{ROOT_DIR}/' + self.death_prob_file, encoding='ISO-8859-1')    
        print('death prob: ',self.death_prob)

    def init_geographic_regional_prevalence(self):
        from smokingcessation.geographic_smoking_prevalence import GeographicSmokingPrevalence
        from smokingcessation.smoking_regulator_mediator import SmokingRegulatorMediator
        from smokingcessation.geographic_smoking_prevalence_regulator import GeographicSmokingPrevalenceRegulator

        self.geographicSmokingPrevalence = GeographicSmokingPrevalence(self)
        self.geographicSmokingPrevalence.set_mediator(SmokingRegulatorMediator([GeographicSmokingPrevalenceRegulator(self)]))
        
    def init_ecig_diffusion_subgroups(self):
        self.ecig_diff_subgroups={}
        self.ecig_diff_subgroups[eCigDiffSubGroup.Exsmokerless1940]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1941_1960]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1961_1980]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1981_1990]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker_over1991]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Smokerless1940]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1941_1960]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1961_1980]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1981_1990]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Smoker_over1991]=set()
        self.ecig_diff_subgroups[eCigDiffSubGroup.Neversmoked_over1991]=set()
    
    def init_ecig_diffusions(self):
        from smokingcessation.ecig_diffusion import eCigDiffusion
        from smokingcessation.smoking_regulator_mediator import SmokingRegulatorMediator
        from smokingcessation.ecig_regulator import eCigDiffusionRegulator

        self.non_disp_diffusion_models={}#hashmap that contains the subgroups which only use non-disposable e-cigarette and don't use disposable e-cigarette. key=a subgroup which uses non-disposable e-cig, value=the non-disposable diffusion model (a list consisting a non-disposable diffusion model)
        self.disp_diffusion_models={}#hashmap that contains the subgroups which only use disposable e-cigarette and don't use non-disposable e-cigarette. key=a subgroup which only uses disposable e-cig, value=the disposable diffusion model (a list consisting of a disposable diffusion model)
        self.non_disp_and_disp_diffusion_models={}#hashmap that contains the subgroups which use both non-disposable and disposable e-cigarette from 2022. key=a subgroup which uses both non-disposable and disposable e-cig from 2022, value=the non-disposable diffusion model and the disposable diffusion model (a list consisting of 2 diffusion models (non-disposable diffusion model and disposable diffusion model))
        
        #create non-disposable e-cigarette diffusion models
        p=self.props['nondisp_diffusion_exsmoker_less1940.p']
        q=self.props['nondisp_diffusion_exsmoker_less1940.q']
        m=self.props['nondisp_diffusion_exsmoker_less1940.m']
        d=self.props['nondisp_diffusion_exsmoker_less1940.d']        
        self.nondisp_diffusion_exsmoker_less1940 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_exsmoker_less1940.set_subgroup(eCigDiffSubGroup.Exsmokerless1940)
        self.nondisp_diffusion_exsmoker_less1940.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_exsmoker_less1940.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmokerless1940]=[self.nondisp_diffusion_exsmoker_less1940]
        p=self.props['nondisp_diffusion_exsmoker_1941_1960.p']
        q=self.props['nondisp_diffusion_exsmoker_1941_1960.q']
        m=self.props['nondisp_diffusion_exsmoker_1941_1960.m']
        d=self.props['nondisp_diffusion_exsmoker_1941_1960.d']
        self.nondisp_diffusion_exsmoker_1941_1960 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_exsmoker_1941_1960.set_subgroup(eCigDiffSubGroup.Exsmoker1941_1960)
        self.nondisp_diffusion_exsmoker_1941_1960.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_exsmoker_1941_1960.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1941_1960]=[self.nondisp_diffusion_exsmoker_1941_1960]
        p=self.props['nondisp_diffusion_exsmoker_1961_1980.p']
        q=self.props['nondisp_diffusion_exsmoker_1961_1980.q']
        m=self.props['nondisp_diffusion_exsmoker_1961_1980.m']
        d=self.props['nondisp_diffusion_exsmoker_1961_1980.d']
        self.nondisp_diffusion_exsmoker_1961_1980 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_exsmoker_1961_1980.set_subgroup(eCigDiffSubGroup.Exsmoker1961_1980)
        self.nondisp_diffusion_exsmoker_1961_1980.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_exsmoker_1961_1980.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1961_1980]=[self.nondisp_diffusion_exsmoker_1961_1980]
        p=self.props['nondisp_diffusion_exsmoker_1981_1990.p']
        q=self.props['nondisp_diffusion_exsmoker_1981_1990.q']
        m=self.props['nondisp_diffusion_exsmoker_1981_1990.m']
        d=self.props['nondisp_diffusion_exsmoker_1981_1990.d']
        self.nondisp_diffusion_exsmoker_1981_1990 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_exsmoker_1981_1990.set_subgroup(eCigDiffSubGroup.Exsmoker1981_1990)
        self.nondisp_diffusion_exsmoker_1981_1990.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_exsmoker_1981_1990.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1981_1990]=[self.nondisp_diffusion_exsmoker_1981_1990]
        p=self.props['nondisp_diffusion_exsmoker_over1991.p']
        q=self.props['nondisp_diffusion_exsmoker_over1991.q']
        m=self.props['nondisp_diffusion_exsmoker_over1991.m']
        d=self.props['nondisp_diffusion_exsmoker_over1991.d']        
        self.nondisp_diffusion_exsmoker_over1991 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_exsmoker_over1991.set_subgroup(eCigDiffSubGroup.Exsmoker_over1991)
        self.nondisp_diffusion_exsmoker_over1991.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_exsmoker_over1991.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmoker_over1991]=[self.nondisp_diffusion_exsmoker_over1991]        
        p=self.props['nondisp_diffusion_smoker_less1940.p']
        q=self.props['nondisp_diffusion_smoker_less1940.q']
        m=self.props['nondisp_diffusion_smoker_less1940.m']
        d=self.props['nondisp_diffusion_smoker_less1940.d']
        self.nondisp_diffusion_smoker_less1940 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_smoker_less1940.set_subgroup(eCigDiffSubGroup.Smokerless1940)
        self.nondisp_diffusion_smoker_less1940.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_smoker_less1940.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Smokerless1940]=[self.nondisp_diffusion_smoker_less1940]
        p=self.props['nondisp_diffusion_smoker_1941_1960.p']
        q=self.props['nondisp_diffusion_smoker_1941_1960.q']
        m=self.props['nondisp_diffusion_smoker_1941_1960.m']
        d=self.props['nondisp_diffusion_smoker_1941_1960.d']
        self.nondisp_diffusion_smoker_1941_1960 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_smoker_1941_1960.set_subgroup(eCigDiffSubGroup.Smoker1941_1960)
        self.nondisp_diffusion_smoker_1941_1960.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_smoker_1941_1960.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Smoker1941_1960]=[self.nondisp_diffusion_smoker_1941_1960]
        p=self.props['nondisp_diffusion_smoker_1961_1980.p']
        q=self.props['nondisp_diffusion_smoker_1961_1980.q']
        m=self.props['nondisp_diffusion_smoker_1961_1980.m']
        d=self.props['nondisp_diffusion_smoker_1961_1980.d']
        self.nondisp_diffusion_smoker_1961_1980 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_smoker_1961_1980.set_subgroup(eCigDiffSubGroup.Smoker1961_1980)
        self.nondisp_diffusion_smoker_1961_1980.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_smoker_1961_1980.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Smoker1961_1980]=[self.nondisp_diffusion_smoker_1961_1980]
        p=self.props['nondisp_diffusion_smoker_1981_1990.p']
        q=self.props['nondisp_diffusion_smoker_1981_1990.q']
        m=self.props['nondisp_diffusion_smoker_1981_1990.m']
        d=self.props['nondisp_diffusion_smoker_1981_1990.d']   
        self.nondisp_diffusion_smoker_1981_1990 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_smoker_1981_1990.set_subgroup(eCigDiffSubGroup.Smoker1981_1990)
        self.nondisp_diffusion_smoker_1981_1990.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_smoker_1981_1990.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Smoker1981_1990]=[self.nondisp_diffusion_smoker_1981_1990]
        p=self.props['nondisp_diffusion_smoker_over1991.p']
        q=self.props['nondisp_diffusion_smoker_over1991.q']
        m=self.props['nondisp_diffusion_smoker_over1991.m']
        d=self.props['nondisp_diffusion_smoker_over1991.d']
        self.nondisp_diffusion_smoker_over1991 = eCigDiffusion(p, q, m, d, self)
        self.nondisp_diffusion_smoker_over1991.set_subgroup(eCigDiffSubGroup.Smoker_over1991)
        self.nondisp_diffusion_smoker_over1991.set_eCigType(eCigType.Nondisp)
        self.nondisp_diffusion_smoker_over1991.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_diffusion_models[eCigDiffSubGroup.Smoker_over1991]=[self.nondisp_diffusion_smoker_over1991]
        #create disposable e-cigarette diffusion models
        p=self.props['disp_diffusion_exsmoker_1961_1980.p']
        q=self.props['disp_diffusion_exsmoker_1961_1980.q']
        m=self.props['disp_diffusion_exsmoker_1961_1980.m']
        d=self.props['disp_diffusion_exsmoker_1961_1980.d']
        self.disp_diffusion_exsmoker_1961_1980=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_exsmoker_1961_1980.set_subgroup(eCigDiffSubGroup.Exsmoker1961_1980)
        self.disp_diffusion_exsmoker_1961_1980.set_eCigType(eCigType.Disp)
        self.disp_diffusion_exsmoker_1961_1980.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1961_1980]=[self.nondisp_diffusion_exsmoker_1961_1980, self.disp_diffusion_exsmoker_1961_1980]   
        p=self.props['disp_diffusion_exsmoker_1981_1990.p']
        q=self.props['disp_diffusion_exsmoker_1981_1990.q']
        m=self.props['disp_diffusion_exsmoker_1981_1990.m']
        d=self.props['disp_diffusion_exsmoker_1981_1990.d']
        self.disp_diffusion_exsmoker_1981_1990=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_exsmoker_1981_1990.set_subgroup(eCigDiffSubGroup.Exsmoker1981_1990)
        self.disp_diffusion_exsmoker_1981_1990.set_eCigType(eCigType.Disp)
        self.disp_diffusion_exsmoker_1981_1990.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1981_1990]=[self.nondisp_diffusion_exsmoker_1981_1990,self.disp_diffusion_exsmoker_1981_1990]
        p=self.props['disp_diffusion_exsmoker_over1991.p']
        q=self.props['disp_diffusion_exsmoker_over1991.q']
        m=self.props['disp_diffusion_exsmoker_over1991.m']
        d=self.props['disp_diffusion_exsmoker_over1991.d'] 
        self.disp_diffusion_exsmoker_over1991=eCigDiffusion(p, q, m, d, self)    
        self.disp_diffusion_exsmoker_over1991.set_subgroup(eCigDiffSubGroup.Exsmoker_over1991)
        self.disp_diffusion_exsmoker_over1991.set_eCigType(eCigType.Disp)
        self.disp_diffusion_exsmoker_over1991.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Exsmoker_over1991]=[self.nondisp_diffusion_exsmoker_over1991,self.disp_diffusion_exsmoker_over1991]
        p=self.props['disp_diffusion_neversmoker_over1991.p']
        q=self.props['disp_diffusion_neversmoker_over1991.q']
        m=self.props['disp_diffusion_neversmoker_over1991.m']
        d=self.props['disp_diffusion_neversmoker_over1991.d']   
        self.disp_diffusion_neversmoked_over1991=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_neversmoked_over1991.set_subgroup(eCigDiffSubGroup.Neversmoked_over1991)
        self.disp_diffusion_neversmoked_over1991.set_eCigType(eCigType.Disp)
        self.disp_diffusion_neversmoked_over1991.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.disp_diffusion_models[eCigDiffSubGroup.Neversmoked_over1991]=[self.disp_diffusion_neversmoked_over1991]
        p=self.props['disp_diffusion_smoker_1941_1960.p']
        q=self.props['disp_diffusion_smoker_1941_1960.q']
        m=self.props['disp_diffusion_smoker_1941_1960.m']
        d=self.props['disp_diffusion_smoker_1941_1960.d']    
        self.disp_diffusion_smoker_1941_1960=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_smoker_1941_1960.set_subgroup(eCigDiffSubGroup.Smoker1941_1960)
        self.disp_diffusion_smoker_1941_1960.set_eCigType(eCigType.Disp)
        self.disp_diffusion_smoker_1941_1960.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Smoker1941_1960]=[self.nondisp_diffusion_smoker_1941_1960,self.disp_diffusion_smoker_1941_1960]
        p=self.props['disp_diffusion_smoker_1961_1980.p']
        q=self.props['disp_diffusion_smoker_1961_1980.q']
        m=self.props['disp_diffusion_smoker_1961_1980.m']
        d=self.props['disp_diffusion_smoker_1961_1980.d']
        self.disp_diffusion_smoker_1961_1980=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_smoker_1961_1980.set_subgroup(eCigDiffSubGroup.Smoker1961_1980)
        self.disp_diffusion_smoker_1961_1980.set_eCigType(eCigType.Disp)
        self.disp_diffusion_smoker_1961_1980.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Smoker1961_1980]=[self.nondisp_diffusion_smoker_1961_1980,self.disp_diffusion_smoker_1961_1980]
        p=self.props['disp_diffusion_smoker_1981_1990.p']
        q=self.props['disp_diffusion_smoker_1981_1990.q']
        m=self.props['disp_diffusion_smoker_1981_1990.m']
        d=self.props['disp_diffusion_smoker_1981_1990.d']        
        self.disp_diffusion_smoker_1981_1990=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_smoker_1981_1990.set_subgroup(eCigDiffSubGroup.Smoker1981_1990)
        self.disp_diffusion_smoker_1981_1990.set_eCigType(eCigType.Disp)
        self.disp_diffusion_smoker_1981_1990.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Smoker1981_1990]=[self.nondisp_diffusion_smoker_1981_1990,self.disp_diffusion_smoker_1981_1990]
        p=self.props['disp_diffusion_smoker_over1991.p']
        q=self.props['disp_diffusion_smoker_over1991.q']
        m=self.props['disp_diffusion_smoker_over1991.m']
        d=self.props['disp_diffusion_smoker_over1991.d']
        self.disp_diffusion_smoker_over1991=eCigDiffusion(p, q, m, d, self)
        self.disp_diffusion_smoker_over1991.set_subgroup(eCigDiffSubGroup.Smoker_over1991)
        self.disp_diffusion_smoker_over1991.set_eCigType(eCigType.Disp)
        self.disp_diffusion_smoker_over1991.set_mediator(SmokingRegulatorMediator([eCigDiffusionRegulator(self)]))
        self.non_disp_and_disp_diffusion_models[eCigDiffSubGroup.Smoker_over1991]=[self.nondisp_diffusion_smoker_over1991,self.disp_diffusion_smoker_over1991]        
        
    @staticmethod
    def replace_missing_value_with_zero(df):
        """replace NaN (missing values) with 0 to ignore the attributes in the COMB formulae (since beta*0 is 0)"""
        return df.fillna(0)

    def store_betas_of_comb_formulae_into_maps(self):
        """store the betas (coefficients) of COMB formulae for regular smoking, quit attempt and quit success
        theories into hashmaps
        input: self.pros, a map with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
        output: uptakeBetas, attemptBetas, successBetas hashmaps with keys={level 2 attribute, level 1 attribute}, each value=beta
        """
        import re
        for key, value in self.props.items():
            m = re.match('^uptake\.(\w+)\.beta$', key)  # uptake.cAlcoholConsumption.beta or uptake.C.beta
            if m is not None:
                self.uptake_betas[m.group(1)] = value
            else:
                m = re.match('^uptake\.bias$', key)
                if m is not None:
                    self.uptake_betas['bias'] = value
                else:
                    m = re.match('^attempt\.(\w+)\.beta$', key)
                    if m is not None:
                        self.attempt_betas[m.group(1)] = value
                    else:
                        m = re.match('^attempt\.bias$', key)
                        if m is not None:
                            self.attempt_betas['bias'] = value
                        else:
                            m = re.match('^success\.(\w+)\.beta$', key)
                            if m is not None:
                                self.success_betas[m.group(1)] = value
                            else:
                                m = re.match('^success\.bias$', key)
                                if m is not None:
                                    self.success_betas['bias'] = value

    def store_level2_attributes_of_comb_formulae_into_maps(self):
        """
        input: self.pros, a hashmap with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
        output: hashmaps level2AttributesOfUptakeFormula, level2AttributesOfAttemptFormula, level2AttributesOfSuccessFormula
                with keys={C, O, M} and each value=a list of associated level 2 attributes of key
        """
        import re
        for key in self.props.keys():
            m = re.match('^uptake\.([com]{1}\w+)\.beta$', key)
            if m is not None:  # match uptake.cAlcoholConsumption.beta, uptake.oAlcoholConsumption.beta or uptake.mAlcoholConsumption.beta
                level2attribute = m.group(1)
                m = re.match('^c\w+', level2attribute)
                if m is not None:  # match cAlcoholConsumption
                    self.level2_attributes_of_uptake_formula['C'].append(level2attribute)
                else:
                    m = re.match('^o\w+', level2attribute)
                    if m is not None:  # match oAlcoholConsumption
                        self.level2_attributes_of_uptake_formula['O'].append(level2attribute)
                    else:
                        m = re.match('^m\w+', level2attribute)
                        if m is not None:  # match mAlcoholConsumption
                            self.level2_attributes_of_uptake_formula['M'].append(level2attribute)
                        else:
                            sstr = (' does not match patterns of level2attributes of C, O and M in regular smoking '
                                    '(uptake) formula')
                            sys.exit(level2attribute + sstr)
            else:
                m = re.match('^attempt\.([com]{1}\w+)\.beta$', key)
                if m is not None:  # match attempt.cAlcoholConsumption.beta, attempt.oAlcoholConsumption.beta or attempt.mAlcoholConsumption.beta
                    level2attribute = m.group(1)
                    m = re.match('^c\w+', level2attribute)
                    if m is not None:  # match cAlcoholConsumption
                        self.level2_attributes_of_attempt_formula['C'].append(level2attribute)
                    else:
                        m = re.match('^o\w+', level2attribute)
                        if m is not None:  # match oAlcoholConsumption
                            self.level2_attributes_of_attempt_formula['O'].append(level2attribute)
                        else:
                            m = re.match('^m\w+', level2attribute)
                            if m is not None:  # match oAlcoholConsumption
                                self.level2_attributes_of_attempt_formula['M'].append(level2attribute)
                            else:
                                sstr = (' does not match patterns of level2attributes of C, O and M in quit '
                                        'attempt formula')
                                sys.exit(level2attribute + sstr)
                else:
                    m = re.match('^success\.([com]{1}\w+)\.beta$', key)
                    if m is not None:  # match success.cAlcoholConsumption.beta, success.oAlcoholConsumption.beta or success.mAlcoholConsumption.beta
                        level2attribute = m.group(1)
                        m = re.match('^c\w+', level2attribute)
                        if m is not None:  # match cAlcoholConsumption
                            self.level2_attributes_of_success_formula['C'].append(level2attribute)
                        else:
                            m = re.match('^o\w+', level2attribute)
                            if m is not None:  # match oAlcoholConsumption
                                self.level2_attributes_of_success_formula['O'].append(level2attribute)
                            else:
                                m = re.match('^m\w+', level2attribute)
                                if m is not None:  # match oAlcoholConsumption
                                    self.level2_attributes_of_success_formula['M'].append(level2attribute)
                                else:
                                    sstr = (' does not match patterns of level2attributes of C, O and M in quit success'
                                            ' formula')
                                    sys.exit(level2attribute + sstr)
    def init_agents(self):
        '''initialize the baseline agent population at tick 0'''
        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator, Theories
        from smokingcessation.comb_theory import RegSmokeTheory, QuitAttemptTheory, QuitSuccessTheory
        from smokingcessation.stpm_theory import DemographicsSTPMTheory, RelapseSTPMTheory, InitiationSTPMTheory, QuitSTPMTheory
        from smokingcessation.person import Person

        baseline_agents=self.data[self.data['year']==self.year_of_current_time_step]#the current year: year of baseline population 
        (r, _) = baseline_agents.shape
        if r==0:
            sys.exit(F"No baseline population is initialized at year: '{self.year_of_current_time_step}'\n")
        for i in range(r):
            subgroup=None
            init_state = baseline_agents.at[i, 'bState']
            if init_state == 0:
                states = [AgentState.NEVERSMOKE, AgentState.NEVERSMOKE]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEVERSMOKERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEVERSMOKERFEMALE
            elif init_state == 1:
                states = [AgentState.EXSMOKER, AgentState.EXSMOKER]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.EXSMOKERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.EXSMOKERFEMALE 
            elif init_state == 4:
                states = [AgentState.SMOKER, AgentState.SMOKER]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.SMOKERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.SMOKERFEMALE 
            elif init_state == 2:
                states = [AgentState.NEWQUITTER, AgentState.NEWQUITTER]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEWQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEWQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 1:
                states = [AgentState.ONGOINGQUITTER1, AgentState.ONGOINGQUITTER1]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 2:
                states = [AgentState.ONGOINGQUITTER2, AgentState.ONGOINGQUITTER2]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 3:
                states = [AgentState.ONGOINGQUITTER3, AgentState.ONGOINGQUITTER3]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 4:
                states = [AgentState.ONGOINGQUITTER4, AgentState.ONGOINGQUITTER4]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE 
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 5:
                states = [AgentState.ONGOINGQUITTER5, AgentState.ONGOINGQUITTER5]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 6:
                states = [AgentState.ONGOINGQUITTER6, AgentState.ONGOINGQUITTER6]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 7:
                states = [AgentState.ONGOINGQUITTER7, AgentState.ONGOINGQUITTER7]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 8:
                states = [AgentState.ONGOINGQUITTER8, AgentState.ONGOINGQUITTER8]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 9:
                states = [AgentState.ONGOINGQUITTER9, AgentState.ONGOINGQUITTER9]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 10:
                states = [AgentState.ONGOINGQUITTER10, AgentState.ONGOINGQUITTER10]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and baseline_agents.at[i,'bMonthsSinceQuit'] == 11:
                states = [AgentState.ONGOINGQUITTER11, AgentState.ONGOINGQUITTER11]
                if baseline_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif baseline_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE                        
            else:
                raise ValueError(f'{init_state} is not an acceptable agent state')
            if self.regular_smoking_behaviour=='COMB':
                rsmoke_theory = RegSmokeTheory(Theories.REGSMOKE, self, i)
            else:#STPM
                rsmoke_theory = InitiationSTPMTheory(Theories.REGSMOKE, self)
            if self.quitting_behaviour=='COMB':
                qattempt_theory = QuitAttemptTheory(Theories.QUITATTEMPT, self, i)
                qsuccess_theory = QuitSuccessTheory(Theories.QUITSUCCESS, self, i)
            else:#STPM
                qattempt_theory = QuitSTPMTheory(Theories.QUITATTEMPT, self)
                qsuccess_theory = QuitSTPMTheory(Theories.QUITSUCCESS, self)
            relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)
            demographics_theory = DemographicsSTPMTheory(Theories.DemographicsSTPM, self)
            self.context.add(Person(
                    self,
                    i,
                    self.type,
                    self.rank,
                    age=baseline_agents.at[i, 'pAge'],
                    gender=baseline_agents.at[i, 'pGender'],
                    cohort=baseline_agents.at[i, 'pCohort'],
                    qimd=baseline_agents.at[i, 'pIMDquintile'],
                    educational_level=baseline_agents.at[i, 'pEducationalLevel'],
                    sep=baseline_agents.at[i, 'pSEP'],
                    region=baseline_agents.at[i, 'pRegion'],
                    social_housing=baseline_agents.at[i, 'pSocialHousing'],
                    mental_health_conds=baseline_agents.at[i, 'pMentalHealthConditions'],
                    alcohol=baseline_agents.at[i, 'pAlcoholConsumption'],
                    expenditure=baseline_agents.at[i, 'pExpenditure'],
                    prescription_nrt=baseline_agents.at[i, 'pPrescriptionNRT'],
                    over_counter_nrt=baseline_agents.at[i, 'pOverCounterNRT'],
                    use_of_nrt=baseline_agents.at[i, 'pUseOfNRT'],
                    ecig_use=baseline_agents.at[i, 'pECigUse'],
                    ecig_type=baseline_agents.at[i, 'pECigType'],                    
                    varenicline_use=baseline_agents.at[i, 'pVareniclineUse'],
                    cig_consumption=baseline_agents.at[i, 'bCigConsumption'],
                    years_since_quit=baseline_agents.at[i, 'bYearsSinceQuit'],# number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
                    number_of_recent_quit_attempts=baseline_agents.at[i, 'bNumberOfRecentQuitAttempts'],
                    months_since_quit=baseline_agents.at[i, 'bMonthsSinceQuit'],
                    states=states,
                    reg_smoke_theory=rsmoke_theory,
                    quit_attempt_theory=qattempt_theory,
                    quit_success_theory=qsuccess_theory,
                    regular_smoking_behaviour=self.regular_smoking_behaviour,
                    quitting_behaviour=self.quitting_behaviour))
            mediator = SmokingTheoryMediator([rsmoke_theory, qattempt_theory, qsuccess_theory, relapse_stpm_theory, demographics_theory])
            agent = self.context.agent((i, self.type, self.rank))
            agent.set_mediator(mediator)
            self.population_counts[subgroup]+=1

    def init_population_counts(self):
        subgroupsL=[SubGroup.NEVERSMOKERFEMALE,SubGroup.NEVERSMOKERMALE,SubGroup.SMOKERFEMALE,SubGroup.SMOKERMALE,\
                       SubGroup.EXSMOKERFEMALE,SubGroup.EXSMOKERMALE,SubGroup.NEWQUITTERFEMALE,SubGroup.NEWQUITTERMALE,\
                       SubGroup.ONGOINGQUITTERFEMALE,SubGroup.ONGOINGQUITTERMALE]
        for subgroup in subgroupsL:
            self.population_counts[subgroup]=0

    def get_size_of_population(self):#get the size of the current population
        return (self.context.size()).get(-1)

    def init_population(self):
        self.months_counter = 0
        self.current_time_step = 0
        self.init_agents()
        self.size_of_population = self.get_size_of_population()
        #calculate the calibration targets of whole population counts and write into a csv file
        self.file_whole_population_counts=open(f'{ROOT_DIR}/output/whole_population_counts.csv','w')
        self.file_whole_population_counts.write('Tick,Year,Year_num,Total_agent_population_W,N_never_smokers_W,g.N_smokers_W,N_new_quitters_W,N_ongoing_quitters_W,N_ex_smokers_W,Total_agent_population_F,N_never_smokers_F,N_smokers_F,N_new_quitters_F,N_ongoing_quitters_F,N_ex_smokers_F,Total_agent_population_M,N_never_smokers_M,N_smokers_M,N_new_quitters_M,N_ongoing_quitters_M,N_ex_smokers_M\n')
        self.file_whole_population_counts.write(self.calculate_counts_of_whole_population())
        #create csv files for writing counts of subgroups of initiation and quitting
        self.filename_initiation_sex='Initiation_sex.csv'
        self.filename_initiation_imd='Initiation_IMD.csv'
        self.filename_quit_age_sex='Quit_age_sex.csv'
        self.filename_quit_imd='Quit_IMD.csv'
        self.file_initiation_sex=open(f'{ROOT_DIR}/output/'+self.filename_initiation_sex,'w')
        self.file_initiation_sex.write('Tick,Year,Year_num,N_neversmokers_startyear_16-24M,N_neversmokers_endyear_16-24M,N_smokers_endyear_16-24M,N_newquitter_endyear_16-24M,N_ongoingquitter_endyear_16-24M,N_exsmoker_endyear_16-24M,N_dead_endyear_16-24M,N_neversmokers_startyear_16-24F,N_neversmokers_endyear_16-24F,N_smokers_endyear_16-24F,N_newquitter_endyear_16-24F,N_ongoingquitter_endyear_16-24F,N_exsmoker_endyear_16-24F,N_dead_endyear_16-24F\n')
        self.file_initiation_imd=open(f'{ROOT_DIR}/output/'+self.filename_initiation_imd,'w')
        self.file_initiation_imd.write('Tick,Year,Year_num,N_neversmokers_startyear_16-24_IMD1,N_neversmokers_endyear_16-24_IMD1,N_smokers_endyear_16-24_IMD1,N_newquitter_endyear_16-24_IMD1,N_ongoingquitter_endyear_16-24_IMD1,N_exsmoker_endyear_16-24_IMD1,N_dead_endyear_16-24_IMD1,N_neversmokers_startyear_16-24_IMD2,N_neversmokers_endyear_16-24_IMD2,N_smokers_endyear_16-24_IMD2,N_newquitter_endyear_16-24_IMD2,N_ongoingquitter_endyear_16-24_IMD2,N_exsmoker_endyear_16-24_IMD2,N_dead_endyear_16-24_IMD2,N_neversmokers_startyear_16-24_IMD3,N_neversmokers_endyear_16-24_IMD3,N_smokers_endyear_16-24_IMD3,N_newquitter_endyear_16-24_IMD3,N_ongoingquitter_endyear_16-24_IMD3,N_exsmoker_endyear_16-24_IMD3,N_dead_endyear_16-24_IMD3,N_neversmokers_startyear_16-24_IMD4,N_neversmokers_endyear_16-24_IMD4,N_smokers_endyear_16-24_IMD4,N_newquitter_endyear_16-24_IMD4,N_ongoingquitter_endyear_16-24_IMD4,N_exsmoker_endyear_16-24_IMD4,N_dead_endyear_16-24_IMD4,N_neversmokers_startyear_16-24_IMD5,N_neversmokers_endyear_16-24_IMD5,N_smokers_endyear_16-24_IMD5,N_newquitter_endyear_16-24_IMD5,N_ongoingquitter_endyear_16-24_IMD5,N_exsmoker_endyear_16-24_IMD5,N_dead_endyear_16-24_IMD5\n')
        self.file_quit_age_sex=open(f'{ROOT_DIR}/output/'+self.filename_quit_age_sex,'w')
        self.file_quit_age_sex.write('Tick,Year,Year_num,N_smokers_ongoingquitters_newquitters_startyear_25-49M,N_smokers_endyear_25-49M,N_newquitters_endyear_25-49M,N_ongoingquitters_endyear_25-49M,N_dead_endyear_25-49M,N_smokers_ongoingquitters_newquitters_startyear_25-49F,N_smokers_endyear_25-49F,N_newquitters_endyear_25-49F,N_ongoingquitters_endyear_25-49F,N_dead_endyear_25-49F,N_smokers_ongoingquitters_newquitters_startyear_50-74M,N_smokers_endyear_50-74M,N_newquitters_endyear_50-74M,N_ongoingquitters_endyear_50-74M,N_dead_endyear_50-74M,N_smokers_ongoingquitters_newquitters_startyear_50-74F,N_smokers_endyear_50-74F,N_newquitters_endyear_50-74F,N_ongoingquitters_endyear_50-74F,N_dead_endyear_50-74F\n')
        self.file_quit_imd=open(f'{ROOT_DIR}/output/'+self.filename_quit_imd,'w')
        self.file_quit_imd.write('Tick,Year,Year_num,N_smokers_ongoingquitters_newquitters_startyear_25-74_IMD1,N_smokers_endyear_25-74_IMD1,N_newquitters_endyear_25-74_IMD1,N_ongoingquitters_endyear_25-74_IMD1,N_dead_endyear_25-74_IMD1,N_smokers_ongoingquitters_newquitters_startyear_25-74_IMD2,N_smokers_endyear_25-74_IMD2,N_newquitters_endyear_25-74_IMD2,N_ongoingquitters_endyear_25-74_IMD2,N_dead_endyear_25-74_IMD2,N_smokers_ongoingquitters_newquitters_startyear_25-74_IMD3,N_smokers_endyear_25-74_IMD3,N_newquitters_endyear_25-74_IMD3,N_ongoingquitters_endyear_25-74_IMD3,N_dead_endyear_25-74_IMD3,N_smokers_ongoingquitters_newquitters_startyear_25-74_IMD4,N_smokers_endyear_25-74_IMD4,N_newquitters_endyear_25-74_IMD4,N_ongoingquitters_endyear_25-74_IMD4,N_dead_endyear_25-74_IMD4,N_smokers_ongoingquitters_newquitters_startyear_25-74_IMD5,N_smokers_endyear_25-74_IMD5,N_newquitters_endyear_25-74_IMD5,N_ongoingquitters_endyear_25-74_IMD5,N_dead_endyear_25-74_IMD5\n')
        if self.running_mode == 'debug':
            print('size of baseline population:', self.size_of_population)
            p = self.smoking_prevalence()
            print('===statistics of smoking prevalence===')
            print('Time step 0: year: '+str(self.year_of_current_time_step)+', smoking prevalence=' + str(p) + '%.')
            self.smoking_prevalence_l.append(p)
            self.logfile.write('tick: 0, year: ' + str(self.year_of_current_time_step) + '\n')
  
    def calculate_counts_of_whole_population(self):
        c=str(self.current_time_step)+','+str(self.year_of_current_time_step)+','+str(self.year_number)+','+str(self.size_of_population)+\
         ','+str(self.population_counts[SubGroup.NEVERSMOKERFEMALE]+self.population_counts[SubGroup.NEVERSMOKERMALE])+\
         ','+str(self.population_counts[SubGroup.SMOKERFEMALE]+self.population_counts[SubGroup.SMOKERMALE])+\
         ','+str(self.population_counts[SubGroup.NEWQUITTERFEMALE]+self.population_counts[SubGroup.NEWQUITTERMALE])+\
         ','+str(self.population_counts[SubGroup.ONGOINGQUITTERFEMALE]+self.population_counts[SubGroup.ONGOINGQUITTERMALE])+\
         ','+str(self.population_counts[SubGroup.EXSMOKERFEMALE]+self.population_counts[SubGroup.EXSMOKERMALE])+\
         ','+str(self.population_counts[SubGroup.NEVERSMOKERFEMALE]+self.population_counts[SubGroup.SMOKERFEMALE]+self.population_counts[SubGroup.NEWQUITTERFEMALE]+self.population_counts[SubGroup.ONGOINGQUITTERFEMALE]+self.population_counts[SubGroup.EXSMOKERFEMALE])+\
         ','+str(self.population_counts[SubGroup.NEVERSMOKERFEMALE])+\
         ','+str(self.population_counts[SubGroup.SMOKERFEMALE])+\
         ','+str(+self.population_counts[SubGroup.NEWQUITTERFEMALE])+\
         ','+str(self.population_counts[SubGroup.ONGOINGQUITTERFEMALE])+\
         ','+str(self.population_counts[SubGroup.EXSMOKERFEMALE])+\
         ','+str(self.population_counts[SubGroup.NEVERSMOKERMALE]+self.population_counts[SubGroup.SMOKERMALE]+self.population_counts[SubGroup.NEWQUITTERMALE]+self.population_counts[SubGroup.ONGOINGQUITTERMALE]+self.population_counts[SubGroup.EXSMOKERMALE])+\
         ','+str(self.population_counts[SubGroup.NEVERSMOKERMALE])+\
         ','+str(self.population_counts[SubGroup.SMOKERMALE])+\
         ','+str(+self.population_counts[SubGroup.NEWQUITTERMALE])+\
         ','+str(self.population_counts[SubGroup.ONGOINGQUITTERMALE])+\
         ','+str(self.population_counts[SubGroup.EXSMOKERMALE])+'\n'
        return c
    
    def get_subgroups_of_ages_sex_for_initiation(self):
        if self.start_year_tick==1:
            c='0,'
        else:
            c=str(self.start_year_tick)+','
        c+=str(self.year_of_current_time_step)+','+str(self.year_number)+','\
          +str(len(g.N_neversmokers_startyear_ages_M))+','+str(g.N_neversmokers_endyear_ages_M)+','\
          +str(g.N_smokers_endyear_ages_M)+','+str(g.N_newquitter_endyear_ages_M)+','+str(g.N_ongoingquitter_endyear_ages_M)+','\
          +str(g.N_exsmoker_endyear_ages_M)+','+str(g.N_dead_endyear_ages_M)+','+str(len(g.N_neversmokers_startyear_ages_F))+','\
          +str(g.N_neversmokers_endyear_ages_F)+','+str(g.N_smokers_endyear_ages_F)+','+str(g.N_newquitter_endyear_ages_F)+','\
          +str(g.N_ongoingquitter_endyear_ages_F)+','+str(g.N_exsmoker_endyear_ages_F)+','+str(g.N_dead_endyear_ages_F)+'\n'
        return c
    
    def get_subgroups_of_ages_imd_for_initiation(self):
        if self.start_year_tick==1:
            c='0,'
        else:
            c=str(self.start_year_tick)+','
        c+=str(self.year_of_current_time_step)+','+str(self.year_number)+','\
          +str(len(g.N_neversmokers_startyear_ages_IMD1))+','+str(g.N_neversmokers_endyear_ages_IMD1)+','+str(g.N_smokers_endyear_ages_IMD1)+','\
          +str(g.N_newquitter_endyear_ages_IMD1)+','+str(g.N_ongoingquitter_endyear_ages_IMD1)+','+str(g.N_exsmoker_endyear_ages_IMD1)+','+str(g.N_dead_endyear_ages_IMD1)+','\
          +str(len(g.N_neversmokers_startyear_ages_IMD2))+','+str(g.N_neversmokers_endyear_ages_IMD2)+','\
          +str(g.N_smokers_endyear_ages_IMD2)+','+str(g.N_newquitter_endyear_ages_IMD2)+','+str(g.N_ongoingquitter_endyear_ages_IMD2)+','\
          +str(g.N_exsmoker_endyear_ages_IMD2)+','+str(g.N_dead_endyear_ages_IMD2)+','\
          +str(len(g.N_neversmokers_startyear_ages_IMD3))+','+str(g.N_neversmokers_endyear_ages_IMD3)+','+str(g.N_smokers_endyear_ages_IMD3)+','\
          +str(g.N_newquitter_endyear_ages_IMD3)+','+str(g.N_ongoingquitter_endyear_ages_IMD3)+','+str(g.N_exsmoker_endyear_ages_IMD3)+','\
          +str(g.N_dead_endyear_ages_IMD3)+','\
          +str(len(g.N_neversmokers_startyear_ages_IMD4))+','\
          +str(g.N_neversmokers_endyear_ages_IMD4)+','+str(g.N_smokers_endyear_ages_IMD4)+','+str(g.N_newquitter_endyear_ages_IMD4)+','\
          +str(g.N_ongoingquitter_endyear_ages_IMD4)+','+str(g.N_exsmoker_endyear_ages_IMD4)+','+str(g.N_dead_endyear_ages_IMD4)+','\
          +str(len(g.N_neversmokers_startyear_ages_IMD5))+','+str(g.N_neversmokers_endyear_ages_IMD5)+','+str(g.N_smokers_endyear_ages_IMD5)+','\
          +str(g.N_newquitter_endyear_ages_IMD5)+','+str(g.N_ongoingquitter_endyear_ages_IMD5)+','+str(g.N_exsmoker_endyear_ages_IMD5)+','\
          +str(g.N_dead_endyear_ages_IMD5)+'\n'
        return c
    
    def get_subgroups_of_ages_sex_for_quit(self):
        if self.start_year_tick==1:
            c='0,'
        else:
            c=str(self.start_year_tick)+','
        c+=str(self.year_of_current_time_step)+','+str(self.year_number)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M))+','+str(g.N_smokers_endyear_ages1_M)+','\
           +str(g.N_newquitters_endyear_ages1_M)+','+str(g.N_ongoingquitters_endyear_ages1_M)+','\
           +str(g.N_dead_endyear_ages1_M)+','+str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F))+','\
           +str(g.N_smokers_endyear_ages1_F)+','+str(g.N_newquitters_endyear_ages1_F)+','+str(g.N_ongoingquitters_endyear_ages1_F)+','\
           +str(g.N_dead_endyear_ages1_F)+','+str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M))+','+str(g.N_smokers_endyear_ages2_M)+','\
           +str(g.N_newquitters_endyear_ages2_M)+','+str(g.N_ongoingquitters_endyear_ages2_M)+','+str(g.N_dead_endyear_ages2_M)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F))+','+str(g.N_smokers_endyear_ages2_F)+','+str(g.N_newquitters_endyear_ages2_F)+','\
           +str(g.N_ongoingquitters_endyear_ages2_F)+','+str(g.N_dead_endyear_ages2_F)+'\n'
        return c
    
    def get_subgroups_of_ages_imd_for_quit(self):
        if self.start_year_tick==1:
            c='0,'
        else:
            c=str(self.start_year_tick)+','
        c+=str(self.year_of_current_time_step)+','+str(self.year_number)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1))+','+str(g.N_smokers_endyear_ages3_IMD1)+','\
           +str(g.N_newquitters_endyear_ages3_IMD1)+','+str(g.N_ongoingquitters_endyear_ages3_IMD1)+','+str(g.N_dead_endyear_ages3_IMD1)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2))+','+str(g.N_smokers_endyear_ages3_IMD2)+','\
           +str(g.N_newquitters_endyear_ages3_IMD2)+','+str(g.N_ongoingquitters_endyear_ages3_IMD2)+','+str(g.N_dead_endyear_ages3_IMD2)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3))+','+str(g.N_smokers_endyear_ages3_IMD3)+','\
           +str(g.N_newquitters_endyear_ages3_IMD3)+','+str(g.N_ongoingquitters_endyear_ages3_IMD3)+','+str(g.N_dead_endyear_ages3_IMD3)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4))+','+str(g.N_smokers_endyear_ages3_IMD4)+','\
           +str(g.N_newquitters_endyear_ages3_IMD4)+','+str(g.N_ongoingquitters_endyear_ages3_IMD4)+','+str(g.N_dead_endyear_ages3_IMD4)+','\
           +str(len(g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5))+','+str(g.N_smokers_endyear_ages3_IMD5)+','\
           +str(g.N_newquitters_endyear_ages3_IMD5)+','+str(g.N_ongoingquitters_endyear_ages3_IMD5)+','+str(g.N_dead_endyear_ages3_IMD5)+'\n'      
        return c
 
    def set_ecig_diffusion_subgroups_of_agents(self,shuffle_population=False):
        for agent in self.context.agents(agent_type=self.type,shuffle=shuffle_population):    
            agent.set_ecig_diffusion_subgroup_of_agent()                                

    def do_transformational_mechanisms(self):
        '''
        Before 2021, for each subgroup, the e-cigarette prevalence = prevalence of non-disposable ecig
        From 2021, for those subgroups using both non-disposable ecig and disposable ecig, ecig prevalence = prevalece of non-disposable ecig + prevalence of disposable ecig 
                   for those subgroups using either non-disposable ecig or disposable ecig, ecig prevalence = prevalence of non-disposable ecig or disposable ecigarette as appropriate
        '''
        if self.year_of_current_time_step < 2021:#run non-disposable models
           self.ecig_Et[eCigDiffSubGroup.Neversmoked_over1991].append(0) #0 diffusion because never smoked 1991+ group did not use e-cigarette before 2021    
           for diffusion_models in self.diffusion_models_of_this_tick.values():#diffusion_models_of_this_tick.values() returns a list of lists of a non-disposable diffusion model
                   diffusion_model=diffusion_models[0] #diffusion_models is a list consisting of a non-disposable diffusion model
                   diffusion_model.do_transformation()
                   if self.running_mode == 'debug':                
                       self.ecig_Et[diffusion_model.subgroup].append(diffusion_model.Et)
        else:
           for subgroup,diffusion_models in self.diffusion_models_of_this_tick.items(): #diffusion_models a list of lists of two diffusion models (non-disposable diffusion model and disposable diffusion model) or one diffusion model (non-disposable diffusion model or disposable diffusion model)
                   total_prevalence=0
                   for diffusion_model in diffusion_models:
                       diffusion_model.do_transformation()
                       total_prevalence += diffusion_model.Et
                   if self.running_mode == 'debug':
                        self.ecig_Et[subgroup].append(total_prevalence)                                                           

    def do_macro_macro_mechanisms(self):
        '''
        Before 2021, for each subgroup, calculate deltaEt (new adopters) of non-disposable ecig model
        From 2021, for those subgroups using both non-disposable ecig and disposable ecig, calculate deltaEt (new adopters) of non-disposable ecig model and calculate deltaEt (new adopters) of disposable ecig model 
                   for those subgroups using either non-disposable ecig or disposable ecig, calculate deltaEt (new adopters) of non-disposable ecig model or deltaEt (new adopters) of disposable ecig model as appropriate
        '''
        if self.year_of_current_time_step < 2021:
           for diffusion_models in self.diffusion_models_of_this_tick.values():
               for diffusion_model in diffusion_models:    
                   diffusion_model.do_macro_macro()#calculate delatEt of diffusion model  
        else:
           for diffusion_models in self.diffusion_models_of_this_tick.values():
               for diffusion_model in diffusion_models:    
                   diffusion_model.do_macro_macro()
        if self.year_of_current_time_step >= 2011 and self.year_of_current_time_step <= 2019:
            self.geographicSmokingPrevalence.do_macro_macro()                                              

    def do_situation_mechanisms(self):
        for agent in self.context.agents(agent_type=self.type):
            agent.do_situation()   

    def do_action_mechanisms_and_count_population_subgroups(self,shuffle_population=False):  
        for agent in self.context.agents(agent_type=self.type,shuffle=shuffle_population):
            agent.do_action()
            agent.count_agent_for_whole_population_counts()
            agent.count_agent_for_initiation_subgroups_by_ages_sex()
            agent.count_agent_for_initiation_subgroups_by_ages_imd()
            agent.count_agent_for_quit_subgroups_by_ages_sex()
            agent.count_agent_for_quit_subgroups_by_ages_imd()       
  
    def smoking_prevalence(self):
        smokers = 0
        for agent in self.context.agents(agent_type=self.type):
            if agent.get_current_state() == AgentState.SMOKER:
                smokers += 1
        prevalence = np.round(smokers / self.size_of_population * 100, 2)  # percentage of smokers
        return prevalence

    def allocateDiffusionToAgent(self,agent):#change an agent to an ecig user    
        if self.diffusion_models_of_this_tick.get(agent.eCig_diff_subgroup)!=None:
            random.shuffle(self.diffusion_models_of_this_tick[agent.eCig_diff_subgroup])
            for diffusion_model in self.diffusion_models_of_this_tick[agent.eCig_diff_subgroup]:
                if diffusion_model.deltaEt > 0 and agent.p_ecig_use.get_value()==0:
                    diffusion_model.allocateDiffusion(agent)
                elif diffusion_model.deltaEt < 0 and agent.p_ecig_use.get_value()==1 and diffusion_model.ecig_type == agent.ecig_type:
                    diffusion_model.allocateDiffusion(agent)

    def init_new_16_yrs_agents(self):
        '''initialize new 16 years old agents in every January from 2012'''
        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator, Theories
        from smokingcessation.comb_theory import RegSmokeTheory, QuitAttemptTheory, QuitSuccessTheory
        from smokingcessation.stpm_theory import DemographicsSTPMTheory, RelapseSTPMTheory, InitiationSTPMTheory, QuitSTPMTheory
        from smokingcessation.person import Person
    
        new_agents=self.data[self.data['year']==self.year_of_current_time_step]#from 2012
        new_agents.reset_index(drop=True, inplace=True)#reset row index to start from 0
        (r, _) = new_agents.shape
        if r==0:
            print(F"There are no new agents initialized at year: '{self.year_of_current_time_step}'\n")
        for i in range(r):
            #the agents did not exist before the current tick, their states at previous ticks since tick 0 take dummy values e.g. NA
            states=[]
            t=0
            while t < self.current_time_step:#assign the new agents with dummy states for the previous ticks
                states.append(pd.NA)
                t+=1
            subgroup=None
            init_state = new_agents.at[i, 'bState']
            if init_state == 0:
                states.append(AgentState.NEVERSMOKE)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEVERSMOKERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEVERSMOKERFEMALE
            elif init_state == 1:
                states.append(AgentState.EXSMOKER)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.EXSMOKERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.EXSMOKERFEMALE 
            elif init_state == 4:
                states.append(AgentState.SMOKER)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.SMOKERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.SMOKERFEMALE 
            elif init_state == 2:
                states.append(AgentState.NEWQUITTER)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEWQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEWQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 1:
                states.append(AgentState.ONGOINGQUITTER1)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 2:
                states.append(AgentState.ONGOINGQUITTER2)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 3:
                states.append(AgentState.ONGOINGQUITTER3)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 4:
                states.append(AgentState.ONGOINGQUITTER4)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE 
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 5:
                states.append(AgentState.ONGOINGQUITTER5)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 6:
                states.append(AgentState.ONGOINGQUITTER6)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 7:
                states.append(AgentState.ONGOINGQUITTER7)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 8:
                states.append(AgentState.ONGOINGQUITTER8)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 9:
                states.append(AgentState.ONGOINGQUITTER9)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 10:
                states.append(AgentState.ONGOINGQUITTER10)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 3 and new_agents.at[i,'bMonthsSinceQuit'] == 11:
                states.append(AgentState.ONGOINGQUITTER11)
                if new_agents.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif new_agents.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE                        
            else:
                raise ValueError(f'{init_state} is not an acceptable agent state')
            if self.regular_smoking_behaviour=='COMB':
                rsmoke_theory = RegSmokeTheory(Theories.REGSMOKE, self, i)
            else:#STPM
                rsmoke_theory = InitiationSTPMTheory(Theories.REGSMOKE, self)
            if self.quitting_behaviour=='COMB':
                qattempt_theory = QuitAttemptTheory(Theories.QUITATTEMPT, self, i)
                qsuccess_theory = QuitSuccessTheory(Theories.QUITSUCCESS, self, i)
            else:#STPM
                qattempt_theory = QuitSTPMTheory(Theories.QUITATTEMPT, self)
                qsuccess_theory = QuitSTPMTheory(Theories.QUITSUCCESS, self)
            relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)
            demographics_theory = DemographicsSTPMTheory(Theories.DemographicsSTPM, self)
            id=self.size_of_population+i #this agent's id = size of current population + i where i=0,1,2...,new agents-1 and size of baseline population = the largest agent id of the current population + 1
            self.context.add(Person(
                    self,
                    id,
                    self.type,
                    self.rank,
                    age=new_agents.at[i, 'pAge'],
                    gender=new_agents.at[i, 'pGender'],
                    cohort=new_agents.at[i, 'pCohort'],
                    qimd=new_agents.at[i, 'pIMDquintile'],
                    educational_level=new_agents.at[i, 'pEducationalLevel'],
                    sep=new_agents.at[i, 'pSEP'],
                    region=new_agents.at[i, 'pRegion'],
                    social_housing=new_agents.at[i, 'pSocialHousing'],
                    mental_health_conds=new_agents.at[i, 'pMentalHealthConditions'],
                    alcohol=new_agents.at[i, 'pAlcoholConsumption'],
                    expenditure=new_agents.at[i, 'pExpenditure'],
                    prescription_nrt=new_agents.at[i, 'pPrescriptionNRT'],
                    over_counter_nrt=new_agents.at[i, 'pOverCounterNRT'],
                    use_of_nrt=new_agents.at[i, 'pUseOfNRT'],
                    ecig_use=new_agents.at[i, 'pECigUse'],
                    ecig_type=new_agents.at[i, 'pECigType'],                    
                    varenicline_use=new_agents.at[i, 'pVareniclineUse'],
                    cig_consumption=new_agents.at[i, 'bCigConsumption'],
                    years_since_quit=new_agents.at[i, 'bYearsSinceQuit'],# number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
                    number_of_recent_quit_attempts=new_agents.at[i, 'bNumberOfRecentQuitAttempts'],
                    months_since_quit=new_agents.at[i, 'bMonthsSinceQuit'],
                    states=states,
                    reg_smoke_theory=rsmoke_theory,
                    quit_attempt_theory=qattempt_theory,
                    quit_success_theory=qsuccess_theory,
                    regular_smoking_behaviour=self.regular_smoking_behaviour,
                    quitting_behaviour=self.quitting_behaviour))
            mediator = SmokingTheoryMediator([demographics_theory, rsmoke_theory, qattempt_theory, qsuccess_theory, relapse_stpm_theory])
            agent = self.context.agent((id, self.type, self.rank))
            agent.set_mediator(mediator)
            self.population_counts[subgroup]+=1
        self.size_of_population = self.get_size_of_population()
    
    def kill_agents(self):
        for uid in self.agents_to_kill:
            agent=self.context.agent(uid)
            self.context.remove(agent)
            del agent 
            gc.collect()

    def do_per_tick(self):
        self.current_time_step += 1
        self.months_counter += 1
        if self.current_time_step == 13:
            self.year_of_current_time_step += 1
            self.year_number += 1
            #initialize new 16 years old agents in January of 2012
            self.init_new_16_yrs_agents()
            if self.running_mode == 'debug':
                 print('size of current population: ',self.size_of_population)#debug
        elif self.current_time_step > 13:
            if self.months_counter == 12: #each tick is 1 month
               self.year_of_current_time_step += 1
               self.year_number += 1
               #initialize new 16 years old agents in January of 2013,...,final year
               self.init_new_16_yrs_agents()
               if self.running_mode == 'debug':
                  print('size of current population: ',self.size_of_population)#debug
        self.format_month_and_year()
        self.current_time_step_of_non_disp_diffusions = max(0, self.current_time_step - self.difference_between_start_time_of_ABM_and_start_time_of_non_disp_diffusions)       
        self.diffusion_models_of_this_tick={}
        if self.year_of_current_time_step < 2021:#before 2021, run non-disposable diffusion models only 
            self.diffusion_models_of_this_tick = self.non_disp_diffusion_models
        else:#from 2021, run non-disposable and disposable diffusion models of each subgroup where some individuals use non-disposable and others use disposable ecig; run the disposable diffusion model of the subgroup (Neversmoked_over1991) which only uses disposable ecig; run the non-disposable diffusion model of each subgroup which only uses non-disposable ecig
            self.diffusion_models_of_this_tick = self.non_disp_and_disp_diffusion_models #the non-disposable and disposable diffusion models of the subgroups which use both non-disposable and disposable ecig
            self.diffusion_models_of_this_tick[eCigDiffSubGroup.Neversmoked_over1991] = self.disp_diffusion_models[eCigDiffSubGroup.Neversmoked_over1991]#the disposable diffusion model of the subgroup (Neversmoked_over1991) which only uses disposable ecig
            self.diffusion_models_of_this_tick[eCigDiffSubGroup.Exsmokerless1940] = self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmokerless1940]#the non-disposable diffusion model of the subgroup which only uses non-disposable ecig
            self.diffusion_models_of_this_tick[eCigDiffSubGroup.Exsmoker1941_1960] = self.non_disp_diffusion_models[eCigDiffSubGroup.Exsmoker1941_1960]
            self.diffusion_models_of_this_tick[eCigDiffSubGroup.Smokerless1940] = self.non_disp_diffusion_models[eCigDiffSubGroup.Smokerless1940]
            self.current_time_step_of_disp_diffusions = max(0, self.current_time_step - self.difference_between_start_time_of_ABM_and_start_time_of_disp_diffusions)
        self.init_ecig_diffusion_subgroups()#reset subgroups to empty sets
        self.set_ecig_diffusion_subgroups_of_agents(shuffle_population=True)
        self.do_transformational_mechanisms()#compute Et of diffusion models
        self.do_macro_macro_mechanisms()#compute deltaEt of diffusion models; read in geographic regional smoking prevalence of this month for years 2011 and 2019 only.
        self.agents_to_kill=set()
        if self.running_mode == 'debug' and self.months_counter == 12: 
            before_kill_agents = self.get_size_of_population()            
        if self.current_time_step == 23:
           ipdb.set_trace()#debugging break point
        self.do_situation_mechanisms()#create e-cigarette users according to delta E[t]. If 12 months have passed kill some agents based on mortality model and increment surviving agents' ages
        self.kill_agents()#delete the agents of agents_to_kill from the population
        if self.running_mode == 'debug' and self.months_counter == 12:
            after_kill_agents = self.get_size_of_population()
            sstr='killed '+str(before_kill_agents - after_kill_agents)+' agents from the current population.'
            print(sstr)
            self.logfile.write(sstr+'\n')
        ###count population subgroups after doing all the mechanisms (some agents have been killed during situational mechanism)
        self.init_population_counts()#reset population counts to 0
        self.do_action_mechanisms_and_count_population_subgroups() 
        self.file_whole_population_counts.write(self.calculate_counts_of_whole_population())#write whole population counts to file
        if self.current_time_step == self.end_year_tick:
            self.file_initiation_sex.write(self.get_subgroups_of_ages_sex_for_initiation())#write subgroups counts to file
            self.file_initiation_imd.write(self.get_subgroups_of_ages_imd_for_initiation())
            self.file_quit_age_sex.write(self.get_subgroups_of_ages_sex_for_quit())
            self.file_quit_imd.write(self.get_subgroups_of_ages_imd_for_quit())
            g.initialize_global_variables_of_subgroups()     
        ###   
        self.size_of_population = self.get_size_of_population()
        if self.current_time_step == self.end_year_tick:
            self.start_year_tick = self.end_year_tick + 1
            self.end_year_tick = self.start_year_tick + 11
        if self.months_counter == 12:
            self.months_counter = 0
        if self.running_mode == 'debug':
            p = self.smoking_prevalence()
            self.smoking_prevalence_l.append(p)
            self.logfile.write('tick: '+str(self.current_time_step)+', year: ' + str(self.year_of_current_time_step) +': smoking prevalence=' + str(p) + '%.\n')
            print('Time step ' + str(self.current_time_step) + ', year: '+str(self.year_of_current_time_step)+': smoking prevalence=' + str(p) + '%.')      
            for subgroup,diffusion_models in self.diffusion_models_of_this_tick.items():
                for diff_model in diffusion_models:
                    self.logfile.write('diffusion model: subgroup='+str(subgroup)+', subgroup size='+str(len(self.ecig_diff_subgroups[subgroup]))+' e-cig_type='+str(diff_model.ecig_type)+', Et='+str(diff_model.Et)+'\n')
                    self.logfile.write(F"ecig_Et: '{self.ecig_Et[subgroup]}'\n")
            self.logfile.write(F"geographic regional smoking prevalence: '{self.geographicSmokingPrevalence.regionalSmokingPrevalence}'\n")

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def write_ecig_prevalence_to_csv_files(self):
        for subgroup in [(eCigDiffSubGroup.Exsmokerless1940,"Exsmoker_less1940"),
                        (eCigDiffSubGroup.Exsmoker1941_1960,"Exsmoker1941_1960"),
                        (eCigDiffSubGroup.Exsmoker1961_1980,"Exsmoker1961_1980"),
                        (eCigDiffSubGroup.Exsmoker1981_1990,"Exsmoker1981_1990"),
                        (eCigDiffSubGroup.Exsmoker_over1991,"Exsmoker_over1991"),
                        (eCigDiffSubGroup.Smokerless1940,"Smoker_less1940"),
                        (eCigDiffSubGroup.Smoker1941_1960,"Smoker1941_1960"),
                        (eCigDiffSubGroup.Smoker1961_1980,"Smoker1961_1980"),
                        (eCigDiffSubGroup.Smoker1981_1990,"Smoker1981_1990"),
                        (eCigDiffSubGroup.Smoker_over1991,"Smoker_over1991"),
                        (eCigDiffSubGroup.Neversmoked_over1991,"Neversmoked_over1991")]:
            f=open(f'{ROOT_DIR}/output/'+subgroup[1]+'.csv', 'w')            
            ecig_prevalenceL = self.ecig_Et[subgroup[0]]
            f.write(str(ecig_prevalenceL[0]))
            for i in range(1, len(ecig_prevalenceL)):
               f.write(','+str(ecig_prevalenceL[i]))
            f.close()
                        
    def collect_data(self):
        #save outputs of ABM to files
        self.file_whole_population_counts.close()
        self.file_initiation_sex.close()
        self.file_initiation_imd.close()
        self.file_quit_age_sex.close()
        self.file_quit_imd.close()
        if self.running_mode == 'debug':
            print('whole population counts and subgroups counts for initiation and quitting are saved in the files:\n')
            print('whole_population_counts.csv, '+str(self.filename_initiation_sex)+', '+str(self.filename_initiation_imd)+',\n')
            print(str(self.filename_quit_age_sex)+' and '+str(self.filename_quit_imd)+'.\n')
            f=open(f'{ROOT_DIR}/output/prevalence_of_smoking.csv', 'w')
            for prev in self.smoking_prevalence_l:
                f.write(str(prev) + ',')
            f.close()
            self.write_ecig_prevalence_to_csv_files()
            self.logfile.close()

    def init(self):
        self.init_ecig_diffusion_subgroups()
        self.init_ecig_diffusions()
        self.init_geographic_regional_prevalence()
        self.init_population()      
        self.init_schedule()

    def run(self):
        self.runner.execute()
        self.collect_data()
