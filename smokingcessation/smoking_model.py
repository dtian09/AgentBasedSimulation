'''
definition of the SmokingModel class which is a subclass of the Model abstract class
SmokingModel class:
    initialises the simulation enviroment of the ABM,
    schedules and executes the mechanisms of the ABM, 
    saves counts of population subgroups to csv files,
    saves e-cigarette diffusion results to csv files (in debug mode), 
    saves detailed information of the simulation of each tick into a logfile (in debug mode). 
'''

import numpy as np
import pandas as pd
from typing import Dict
from mpi4py.MPI import Intracomm
from repast4py.context import SharedContext
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner
from config.definitions import ROOT_DIR, AgentState, SubGroup, eCigDiffSubGroup, eCigType
from mbssm.model import Model
import config.global_variables as g
import os
import random
import gc
# Import the SocialNetwork class
from smokingcessation.social_network import SocialNetwork
#import ipdb #python debugger https://wangchuan.github.io/coding/2017/07/12/ipdb-cheat-sheet.html#command-cheatsheet

class SmokingModel(Model):
    
    def __init__(self, comm: Intracomm, params: Dict):
        super().__init__(comm, params)
        self.running_mode = self.props['ABM_mode']
        if self.running_mode == 'debug':
            self.smoking_prevalence_l = list()
        elif self.running_mode == 'normal':
            pass
        else:
            raise ValueError(f'invalid running mode: {self.running_mode}\nvalid running mode: debug or normal')
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
        self.fixed_agent_ids = self.props["fixed_agent_ids"]
        random.seed(self.seed) #set the random seed of ABM
        self.data_file: str = self.props["data_file"]  #the baseline synthetic population
        self.regionalSmokingPrevalenceFile = self.props["regional_prevalence"]
        self.regionalSmokingPrevalence=None 
        self.readInRegionalPrevalence()
        self.data = pd.read_csv(f'{ROOT_DIR}/' + self.data_file, encoding='ISO-8859-1')
        self.data = self.replace_missing_value_with_zero(self.data)
        self.level2_attributes_names = list(self.data.filter(regex='^[com]').columns)#get the level 2 attribute names from the data file
        self.difference_between_start_time_of_ABM_and_start_time_of_non_disp_diffusions = self.props['difference_between_start_time_of_ABM_and_start_time_of_non_disp_diffusions']
        self.difference_between_start_time_of_ABM_and_start_time_of_disp_diffusions = self.props['difference_between_start_time_of_ABM_and_start_time_of_disp_diffusions']        
        self.agents_to_kill=set() #unique ids of the agents to be killed after iteration through the population during situational mechanism
        self.relapse_prob_file = f'{ROOT_DIR}/' + self.props["relapse_prob_file"]
        self.relapse_prob = pd.read_csv(self.relapse_prob_file)
        self.death_prob_file = f'{ROOT_DIR}/' + self.props["death_prob_file"]
        self.death_prob = pd.read_csv(self.death_prob_file, encoding='ISO-8859-1')
        self.attempt_exogenous_dynamics_file = f'{ROOT_DIR}/' + self.props["attempt_exogenous_dynamics_file"] 
        self.attempt_exogenous_dynamics_data = pd.read_csv(self.attempt_exogenous_dynamics_file, encoding='ISO-8859-1') 
        self.maintenance_exogenous_dynamics_file = f'{ROOT_DIR}/' + self.props["maintenance_exogenous_dynamics_file"] 
        self.maintenance_exogenous_dynamics_data = pd.read_csv(self.maintenance_exogenous_dynamics_file, encoding='ISO-8859-1') 
        self.cig_consumption_percentiles_file = f'{ROOT_DIR}/' + self.props["cig_consumption_percentiles_file"]
        self.cig_consumption_percentiles_data = pd.read_csv(self.cig_consumption_percentiles_file, encoding='ISO-8859-1')
        self.sigma_propensity_GP_advice_attempt = self.props["sigma_propensity_GP_advice_attempt"]
        self.sigma_propensity_NRT_attempt = self.props["sigma_propensity_NRT_attempt"]
        self.sigma_propensity_NRT_maintenance = self.props["sigma_propensity_NRT_maintenance"]
        self.sigma_propensity_behaviour_support_maintenance = self.props["sigma_propensity_behaviour_support_maintenance"]
        self.sigma_propensity_varenicline_maintenance = self.props["sigma_propensity_varenicline_maintenance"]
        self.sigma_propensity_cytisine_maintenance = self.props["sigma_propensity_cytisine_maintenance"]
        self.year_of_current_time_step = self.props["year_of_baseline"] 
        self.year_number = 0
        self.current_time_step = 0
        self.months_counter = 0 #count the number of months of the current year
        self.formatted_month = None #formatted month: Nov-06, Dec-10 etc.
        self.start_year_tick = 1 #tick of January of the current year
        self.end_year_tick = 12 #tick of December of the current year
        self.stop_at: int = self.props["stop.at"]  # final time step (tick) of simulation
        self.tickInterval = self.props["tickInterval"] #time length of a tick (1 month) in weeks
        if self.running_mode == 'debug':
            print('tickInterval: ',self.tickInterval)
        self.lbda=self.props["lambda"] #cCigAddictStrength[t+1] = round (cCigAddictStrength[t] * exp(lambda*t)), where lambda = 0.0368 and t = tick interval (weeks)
        self.alpha=self.props["alpha"] #probability of smoker self identity = 1/(1+alpha*(k*t)^beta) where alpha = 1.1312, beta = 0.500, k = no. of quit maintenancees and t = tick interval (weeks)
        self.beta=self.props["beta"]    
        self.runner: SharedScheduleRunner = init_schedule_runner(comm)
        #hashmaps (dictionaries) to store betas (coefficients) of the COMB formula of regular smoking theory, quit attempt theory and quit maintenance theory
        self.uptake_betas = {}
        self.attempt_betas = {}  # hashmap to store betas of the COMB formula of quit attempt theory
        self.maintenance_betas = {}  # hashmap to store betas of the COMB formula of quit maintenance theory
        self.store_betas_of_comb_formulae_into_maps()        
        self.level2_attributes_of_uptake_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of regular smoking theory
        self.level2_attributes_of_attempt_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of quit attempt theory
        self.level2_attributes_of_maintenance_formula = {'C': [], 'O': [], 'M': []}#hashmap to store the level 2 attributes of the COMB formula of quit maintenance theory
        self.store_level2_attributes_of_comb_formulae_into_maps()
        self.regular_smoking_behaviour = self.props['regular_smoking_behaviour'] #COMB or STPM
        self.quitting_behaviour = self.props['quitting_behaviour'] #COMB or STPM
        if self.regular_smoking_behaviour=='STPM':
            self.initiation_prob_file = f'{ROOT_DIR}/' + self.props["initiation_prob_file"]
            self.initiation_prob = pd.read_csv(self.initiation_prob_file) 
        elif self.regular_smoking_behaviour=='COMB':
            pass
        else:
            raise ValueError(f'invalid regular smoking behaviour: {self.regular_smoking_behaviour}\nvalid behaviour model: COMB or STPM')
        if self.quitting_behaviour=='STPM':
            self.quit_prob_file = f'{ROOT_DIR}/' + self.props["quit_prob_file"]
            self.quit_prob = pd.read_csv(self.quit_prob_file)   
        elif self.quitting_behaviour=='COMB':
            pass
        else:
            raise ValueError(f'invalid quitting behaviour: {self.quitting_behaviour}')
        if not os.path.exists(f'{ROOT_DIR}/output'):
            os.makedirs(f'{ROOT_DIR}/output', exist_ok=True)
        if self.running_mode == 'debug':
            self.logfile = open(f'{ROOT_DIR}/output/logfile.txt', 'w')
            self.logfile.write('debug mode\n')
            if self.regular_smoking_behaviour=='COMB':
                print('This ABM is using the COM-B regular smoking model, ')
                self.logfile.write('This ABM is using the COM-B regular smoking model, ')
            elif self.regular_smoking_behaviour=='STPM':
                print('This ABM is using the STPM initiation transition probabilities, ')
                self.logfile.write('the STPM initiation transition probabilities, ')
            else:
                raise ValueError(f'invalid regular_smoking_behaviour: {self.regular_smoking_behaviour}\nvalid behaviour model: COMB or STPM')
            if self.quitting_behaviour=='COMB':
                print('COM-B quit attempt model, COM-B quit maintenance model, ')
                self.logfile.write('the quit attempt COM-B model, quit maintenance COM-B model ')
            elif self.quitting_behaviour=='STPM':
                print('STPM quitting transition probabilities ')
                self.logfile.write('the STPM quitting transition probabilities ')
            else:
                raise ValueError(f'invalid regular_smoking_behaviour: {self.regular_smoking_behaviour}\nvalid behaviour model: COMB or STPM')
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
            
        # Create social network object (just the object, not the connections yet)
        self.social_network = SocialNetwork(self)
        # Get fixed agent IDs from config, with default if not specified
        self.fixed_agent_ids = self.props["fixed_agent_ids"]
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
     
    def init_geographic_regional_prevalence(self):
        '''
        initialze GeographicSmokingPrevalence macro entity
        '''
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
        """store the betas (coefficients) of COMB formulae for regular smoking, quit attempt and quit maintenance
        theories into hashmaps
        input: self.props, a hashmap representing model.yaml (key=a parameter e.g. uptake.cAlcoholConsumption.beta, value=value of the parameter e.g. 0.46)
        output: uptakeBetas, attemptBetas, maintenanceBetas hashmaps with keys={level 2 attribute, level 1 attribute}, each value=beta
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
                            m = re.match('^maintenance\.(\w+)\.beta$', key)
                            if m is not None:
                                self.maintenance_betas[m.group(1)] = value
                            else:
                                m = re.match('^maintenance\.bias$', key)
                                if m is not None:
                                    self.maintenance_betas['bias'] = value

    def store_level2_attributes_of_comb_formulae_into_maps(self):
        """
        input: self.props, a hashmap representing model.yaml (key=a parameter e.g. uptake.cAlcoholConsumption.beta, value=value of the parameter e.g. 0.46)
        output: hashmaps level2AttributesOfUptakeFormula, level2AttributesOfAttemptFormula, level2AttributesOfMaintenanceFormula
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
                            raise ValueError(level2attribute + sstr)
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
                                raise ValueError(level2attribute + sstr)
                else:
                    m = re.match('^maintenance\.([com]{1}\w+)\.beta$', key)
                    if m is not None:  # match maintenance.cAlcoholConsumption.beta, maintenance.oAlcoholConsumption.beta or maintenance.mAlcoholConsumption.beta
                        level2attribute = m.group(1)
                        m = re.match('^c\w+', level2attribute)
                        if m is not None:  # match cAlcoholConsumption
                            self.level2_attributes_of_maintenance_formula['C'].append(level2attribute)
                        else:
                            m = re.match('^o\w+', level2attribute)
                            if m is not None:  # match oAlcoholConsumption
                                self.level2_attributes_of_maintenance_formula['O'].append(level2attribute)
                            else:
                                m = re.match('^m\w+', level2attribute)
                                if m is not None:  # match oAlcoholConsumption
                                    self.level2_attributes_of_maintenance_formula['M'].append(level2attribute)
                                else:
                                    sstr = (' does not match patterns of level2attributes of C, O and M in quit maintenance'
                                            ' formula')
                                    raise ValueError(level2attribute + sstr)
    def init_agents(self):
        '''initialise the baseline agent population at tick 0'''
        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator, Theories
        from smokingcessation.comb_theory import RegSmokeTheory, QuitAttemptTheory, QuitMaintenanceTheory
        from smokingcessation.stpm_theory import DemographicsSTPMTheory, RelapseSTPMTheory, InitiationSTPMTheory, QuitSTPMTheory
        from smokingcessation.person import Person

        # Load all potential agents from the data file, not just the baseline year
        # the name baseline_agents is kept for consistency with the original code though it really is all agents
        baseline_agents = self.data  
        (r, _) = baseline_agents.shape
        if r==0:
            raise ValueError(F"An empty (size 0) baseline population is initialised at year: '{self.year_of_current_time_step}'\n")
            
        if self.running_mode == 'debug':
            self.logfile.write(f"Loading {r} potential agents from data file\n")
            
        # Track how many of each theory type we create
        rsmoke_theories = 0
        qattempt_theories = 0
        qmaintenance_theories = 0
            
        for i in range(r):
            subgroup = None
            init_state = baseline_agents.at[i, 'bState']
            
            # Extract agent ID and entry year from data
            agent_id = baseline_agents.at[i, 'agentID']
            entry_year = baseline_agents.at[i, 'year']
            
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
                rsmoke_theories += 1
            else:#STPM
                rsmoke_theory = InitiationSTPMTheory(Theories.REGSMOKE, self)
            if self.quitting_behaviour=='COMB':
                qattempt_theory = QuitAttemptTheory(Theories.QUITATTEMPT, self, i)
                qattempt_theories += 1
                qmaintenance_theory = QuitMaintenanceTheory(Theories.QUITMAINTENANCE, self, i)
                qmaintenance_theories += 1
            else:#STPM
                qattempt_theory = QuitSTPMTheory(Theories.QUITATTEMPT, self)
                qattempt_theories += 1
                qmaintenance_theory = QuitSTPMTheory(Theories.QUITMAINTENANCE, self)
                qmaintenance_theories += 1
            relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)
            demographics_theory = DemographicsSTPMTheory(Theories.DemographicsSTPM, self)
            
            # Create the agent
            agent = Person(
                    self,
                    agent_id,  # Use the actual agent ID from the data file
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
                    perc_num=baseline_agents.at[i,"perc_num"],
                    states=states,
                    propensity_receive_GP_advice_attempt=np.random.normal(0,self.sigma_propensity_GP_advice_attempt),
                    propensity_NRT_attempt=np.random.normal(0,self.sigma_propensity_NRT_attempt),
                    propensity_NRT_maintenance = np.random.normal(0,self.sigma_propensity_NRT_maintenance),
                    propensity_behaviour_support_maintenance = np.random.normal(0,self.sigma_propensity_behaviour_support_maintenance),
                    propensity_varenicline_maintenance = np.random.normal(0,self.sigma_propensity_varenicline_maintenance),
                    propensity_cytisine_maintenance = np.random.normal(0,self.sigma_propensity_cytisine_maintenance),                    
                    reg_smoke_theory=rsmoke_theory,
                    quit_attempt_theory=qattempt_theory,
                    quit_maintenance_theory=qmaintenance_theory,
                    regular_smoking_behaviour=self.regular_smoking_behaviour,
                    quitting_behaviour=self.quitting_behaviour,
                    entry_year=entry_year  # Pass the entry year to the agent
            )
                    
            # Add the agent to the context
            self.context.add(agent)
            
            # Set up the theories as direct attributes on the agent
            agent = self.context.agent((agent_id, self.type, self.rank))
            # Set theories as direct attributes on the agent object
            agent.quit_attempt_theory = qattempt_theory
            agent.quit_maintenance_theory = qmaintenance_theory
            
            # Set up the mediator
            mediator = SmokingTheoryMediator([rsmoke_theory, qattempt_theory, qmaintenance_theory, relapse_stpm_theory, demographics_theory])
            agent.set_mediator(mediator)
            
            # Activate the agent if it's from the baseline year
            if entry_year == self.year_of_current_time_step:
                agent.is_active = True
                self.population_counts[subgroup] += 1
        
        self.size_of_population = self.get_size_of_population()
        
        # At the end of the method, after all agents are created
        if self.running_mode == 'debug':
            # Count active agents for logging
            active_agents = sum(1 for agent in self.context.agents() if agent.is_active)
            self.logfile.write(f"Created {r} agents, {active_agents} active for baseline year {self.year_of_current_time_step}\n")
            self.logfile.write(f"Created {rsmoke_theories} regular smoking theories\n")
            self.logfile.write(f"Created {qattempt_theories} quit attempt theories\n")
            self.logfile.write(f"Created {qmaintenance_theories} quit maintenance theories\n")

    def init_population_counts(self):
        subgroupsL=[SubGroup.NEVERSMOKERFEMALE,SubGroup.NEVERSMOKERMALE,SubGroup.SMOKERFEMALE,SubGroup.SMOKERMALE,\
                       SubGroup.EXSMOKERFEMALE,SubGroup.EXSMOKERMALE,SubGroup.NEWQUITTERFEMALE,SubGroup.NEWQUITTERMALE,\
                       SubGroup.ONGOINGQUITTERFEMALE,SubGroup.ONGOINGQUITTERMALE]
        for subgroup in subgroupsL:
            self.population_counts[subgroup]=0

    def get_size_of_population(self):#get the size of the current population
        # Count only active agents rather than all agents in the context
        return sum(1 for agent in self.context.agents() if agent.is_active)

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
        
        # Log all agent states to provide a complete view of population
        if self.running_mode == 'debug':
            self.log_all_agent_states()
        
        if self.running_mode == 'debug':
            print('size of baseline population:', self.size_of_population)
            p = self.smoking_prevalence()
            print('===statistics of smoking prevalence===')
            print('tick 0, year: '+str(self.year_of_current_time_step)+', smoking prevalence=' + str(p) + '%.')
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
            if agent.is_active:  # Only process active agents
                agent.set_ecig_diffusion_subgroup_of_agent()

    def do_transformational_mechanisms(self):
        '''
        Before 2021, for each subgroup, the e-cigarette prevalence = prevalence of non-disposable ecig
        From 2021, for those subgroups using both non-disposable ecig and disposable ecig, ecig prevalence = prevalece of non-disposable ecig + prevalence of disposable ecig 
                   for those subgroups using either non-disposable ecig or disposable ecig, ecig prevalence = prevalence of non-disposable ecig or disposable ecigarette as appropriate
        '''
        if self.year_of_current_time_step < 2021:#run non-disposable models
           if self.running_mode == 'debug':
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
        Between 2011 and 2019, read in the geographic regional smoking prevalence of this month.
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

    def do_situation_mechanisms_and_may_count_population_subgroups(self,
                                                                     do_smoking_behaviour_mechanisms=False,
                                                                     count_population_subgroups=False):
        '''
        if do_smoking_behaviour_mechanisms = True, do situational mechanism of the behaviour model
        if do_smoking_behaviour_mechanisms = False, do situational mechanism of DemographicsSTPMTheory i.e. if December, kill some agents and increase the ages of the surving ones etc.
        '''
        if do_smoking_behaviour_mechanisms==False:
            self.agents_to_kill=set()
        if count_population_subgroups==True:#do situational mechanisms of agents and count population subgroups
            for agent in self.context.agents(agent_type=self.type):
                if agent.is_active:  # Only process active agents
                    agent.do_situation(do_smoking_behaviour_mechanisms=do_smoking_behaviour_mechanisms)
                    agent.count_agent_for_whole_population_counts()
                    agent.count_agent_for_initiation_subgroups_by_ages_sex()
                    agent.count_agent_for_initiation_subgroups_by_ages_imd()
                    agent.count_agent_for_quit_subgroups_by_ages_sex()
                    agent.count_agent_for_quit_subgroups_by_ages_imd() 
        else:#do situational mechanisms of agents only
            for agent in self.context.agents(agent_type=self.type):
                if agent.is_active:  # Only process active agents
                    agent.do_situation(do_smoking_behaviour_mechanisms=do_smoking_behaviour_mechanisms)
        if do_smoking_behaviour_mechanisms==False:
            # Call kill_agents and capture the count of deactivated agents
            deactivated_count = self.kill_agents()
            
            # Only print summary if agents were deactivated and not already done by kill_agents
            if deactivated_count > 0 and self.running_mode != 'debug':
                print(f"\n=== POPULATION DYNAMICS: DEACTIVATION SUMMARY ===")
                print(f"Total agents deactivated: {deactivated_count}")
                print(f"Current population size: {self.get_size_of_population()}")
                
            return deactivated_count
        return 0

    def do_action_mechanisms(self,shuffle_population=False):  
        for agent in self.context.agents(agent_type=self.type,shuffle=shuffle_population):
            if agent.is_active:  # Only process active agents
                agent.do_action()
                  
    def smoking_prevalence(self):
        '''
        calculate the smoking prevalence
        '''
        smokers = 0
        for agent in self.context.agents(agent_type=self.type):
            if agent.is_active and agent.get_current_state() == AgentState.SMOKER:
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
        '''
        Activate agents with entry_year matching the current simulation year.
        This replaces the previous behavior of creating new agents.
        '''
        if self.running_mode == 'debug':
            self.logfile.write(f"\n=== ACTIVATING AGENTS FOR YEAR {self.year_of_current_time_step} ===\n")
            
        activated_count = 0
        activated_by_subgroup = {}
        activated_ids_by_subgroup = {}
        
        # Initialize dictionaries
        for subgroup in SubGroup:
            activated_by_subgroup[subgroup] = 0
            activated_ids_by_subgroup[subgroup] = []
        
        # Find all inactive agents with matching entry_year
        for agent in self.context.agents(agent_type=self.type):
            if not agent.is_active and agent.entry_year == self.year_of_current_time_step:
                # Re-initialize the agent's state history with NA values for past time steps
                # and their initial state for the current time step
                initial_state = agent.b_states[0] if agent.b_states else AgentState.NEVERSMOKE
                
                # Clear existing state history and fill with NA values for past time steps
                agent.b_states = []
                for t in range(self.current_time_step):
                    agent.b_states.append(pd.NA)
                
                # Add the initial state for the current time step
                agent.b_states.append(initial_state)
                
                # Get agent ID
                agent_id = agent.get_id()
                
                if self.running_mode == 'debug':
                    self.logfile.write(f"Initializing agent {agent_id} with initial state {initial_state}\n")
                
                # Activate the agent
                agent.is_active = True
                activated_count += 1
                
                # Determine the agent's subgroup and update population counts
                gender = agent.p_gender.get_value()
                current_state = agent.get_current_state()
                
                # Determine subgroup based on state and gender
                subgroup = None
                if current_state == AgentState.NEVERSMOKE:
                    if gender == 1:  # male
                        subgroup = SubGroup.NEVERSMOKERMALE
                    elif gender == 2:  # female
                        subgroup = SubGroup.NEVERSMOKERFEMALE
                elif current_state == AgentState.EXSMOKER:
                    if gender == 1:
                        subgroup = SubGroup.EXSMOKERMALE
                    elif gender == 2:
                        subgroup = SubGroup.EXSMOKERFEMALE
                elif current_state == AgentState.SMOKER:
                    if gender == 1:
                        subgroup = SubGroup.SMOKERMALE
                    elif gender == 2:
                        subgroup = SubGroup.SMOKERFEMALE
                elif current_state == AgentState.NEWQUITTER:
                    if gender == 1:
                        subgroup = SubGroup.NEWQUITTERMALE
                    elif gender == 2:
                        subgroup = SubGroup.NEWQUITTERFEMALE
                elif current_state in (AgentState.ONGOINGQUITTER1, AgentState.ONGOINGQUITTER2, 
                                      AgentState.ONGOINGQUITTER3, AgentState.ONGOINGQUITTER4,
                                      AgentState.ONGOINGQUITTER5, AgentState.ONGOINGQUITTER6,
                                      AgentState.ONGOINGQUITTER7, AgentState.ONGOINGQUITTER8,
                                      AgentState.ONGOINGQUITTER9, AgentState.ONGOINGQUITTER10,
                                      AgentState.ONGOINGQUITTER11):
                    if gender == 1:
                        subgroup = SubGroup.ONGOINGQUITTERMALE
                    elif gender == 2:
                        subgroup = SubGroup.ONGOINGQUITTERFEMALE
                
                if subgroup:
                    self.population_counts[subgroup] += 1
                    activated_by_subgroup[subgroup] += 1
                    activated_ids_by_subgroup[subgroup].append(agent_id)
        
        if self.running_mode == 'debug':
            self.logfile.write(f"\n=== POPULATION DYNAMICS: ACTIVATION SUMMARY ===\n")
            self.logfile.write(f"Total agents activated for year {self.year_of_current_time_step}: {activated_count}\n\n")
            
            # Log activated agents by subgroup with IDs
            for subgroup, count in activated_by_subgroup.items():
                if count > 0:
                    self.logfile.write(f"Subgroup {subgroup.name}: {count} agents activated\n")
                    ids = activated_ids_by_subgroup[subgroup]
                    # Show all IDs if <= 10, otherwise show first 10
                    if len(ids) <= 10:
                        self.logfile.write(f"  Agent IDs: {ids}\n")
                    else:
                        self.logfile.write(f"  Agent IDs (first 10 of {len(ids)}): {ids[:10]}\n")
            
            self.logfile.write("=== END OF ACTIVATION SUMMARY ===\n\n")
                
        return activated_count  # Return the number of agents activated
    
    def kill_agents(self):
        '''
        Mark agents in agents_to_kill as inactive instead of removing them.
        Provides detailed logging of which agents are deactivated.
        
        Returns:
            int: Number of agents deactivated
        '''
        killed_count = 0
        killed_ids = []
        
        # Group deactivated agents by subgroup if there are many
        killed_by_subgroup = {}
        killed_ids_by_subgroup = {}
        # We don't remove from context anymore to preserve network structure
            #self.context.remove(agent)
            #del agent
        # Instead, mark the agent as inactive

        # First pass - collect basic information
        for uid in self.agents_to_kill:
            agent = self.context.agent(uid)
            if agent:
                # Add to killed list
                killed_count += 1
                killed_ids.append(uid)
                
                # Try to get agent's subgroup for organization if there are many
                try:
                    gender = agent.p_gender.get_value()
                    current_state = agent.get_current_state()
                    
                    # Simplified subgroup determination based on state and gender
                    subgroup = None
                    if gender == 1:  # male
                        subgroup = "MALE"
                    elif gender == 2:  # female
                        subgroup = "FEMALE"
                    
                    # Initialize subgroup in dictionaries if not already present
                    if subgroup not in killed_by_subgroup:
                        killed_by_subgroup[subgroup] = 0
                        killed_ids_by_subgroup[subgroup] = []
                    
                    # Update counts and lists
                    killed_by_subgroup[subgroup] += 1
                    killed_ids_by_subgroup[subgroup].append(uid)
                except:
                    pass  # If unable to determine subgroup, simply skip grouping
                
                # Mark as inactive instead of removing
                agent.is_active = False
                
                # Log individual deactivation for debugging if needed
                if self.running_mode == 'debug':
                    self.logfile.write(f"Agent {uid} marked as inactive (deactivated)\n")
        
        # Detailed logging of killed agents
        if self.running_mode == 'debug' and killed_count > 0:
            summary_header = f"=== POPULATION DYNAMICS: DEACTIVATION SUMMARY ==="
            summary_count = f"Total agents deactivated: {killed_count}"
            
            # Log to file
            self.logfile.write(f"\n{summary_header}\n")
            self.logfile.write(f"{summary_count}\n\n")
            
            # Also print to terminal for visibility
            print(f"{summary_header}")
            print(f"{summary_count}")
            
            if killed_count <= 10:
                # If 10 or fewer agents killed, log all IDs
                self.logfile.write(f"All deactivated agent IDs: {killed_ids}\n")
            else:
                # If more than 10 killed, log by subgroup
                for subgroup, count in killed_by_subgroup.items():
                    self.logfile.write(f"Subgroup {subgroup}: {count} agents deactivated\n")
                    ids = killed_ids_by_subgroup[subgroup]
                    # Show first 10 IDs if more than 10
                    if len(ids) <= 10:
                        self.logfile.write(f"  Agent IDs: {ids}\n")
                    else:
                        self.logfile.write(f"  Agent IDs (first 10 of {len(ids)}): {ids[:10]}\n")
                
                # Add a summary of all deactivated IDs (first 10)
                self.logfile.write(f"\nAll deactivated agent IDs (first 10 of {killed_count}): {killed_ids[:10]}\n")
            
            self.logfile.write("=== END OF DEACTIVATION SUMMARY ===\n\n")
        
        # Clear the agents_to_kill set for the next round
        self.agents_to_kill.clear()
        gc.collect()
        
        # Return the count of agents deactivated
        return killed_count

    def do_per_tick(self):
        '''
        do_per_tick is executed at each tick from tick 1 to execute the mechanisms of the ABM.
        '''
        self.current_time_step += 1
        self.months_counter += 1
        if self.current_time_step >= 13:
            if self.months_counter == 1: #January from 2012 (tick 13)
               self.year_of_current_time_step += 1
               self.year_number += 1
               activated_agents = self.init_new_16_yrs_agents() #Activate agents for the current year
               if self.running_mode == 'debug':
                    print(f"\n=== POPULATION DYNAMICS: ACTIVATION SUMMARY ===")
                    print(f"Total agents activated for year {self.year_of_current_time_step}: {activated_agents}")
                    print(f"Current population size: {self.get_size_of_population()}")
                    
                    # Still log to file for reference
                    self.logfile.write('tick '+str(self.current_time_step)+', '+str(activated_agents)+' agents activated for year '+str(self.year_of_current_time_step)+', size of population: '+str(self.get_size_of_population())+'\n')
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
        self.do_situation_mechanisms_and_may_count_population_subgroups(do_smoking_behaviour_mechanisms=True, count_population_subgroups=False)#create e-cigarette users according to delta E[t]. If 12 months have passed kill some agents based on mortality model and increment surviving agents' ages
        self.do_action_mechanisms() 
        self.init_population_counts()#reset population counts to 0
        ###kill some agents and count population subgroups
        self.do_situation_mechanisms_and_may_count_population_subgroups(do_smoking_behaviour_mechanisms=False, count_population_subgroups=True)        
        self.file_whole_population_counts.write(self.calculate_counts_of_whole_population())#write whole population counts to file
        if self.current_time_step == self.end_year_tick:
            self.file_initiation_sex.write(self.get_subgroups_of_ages_sex_for_initiation())#write subgroups counts to file
            self.file_initiation_imd.write(self.get_subgroups_of_ages_imd_for_initiation())
            self.file_quit_age_sex.write(self.get_subgroups_of_ages_sex_for_quit())
            self.file_quit_imd.write(self.get_subgroups_of_ages_imd_for_quit())
            g.initialise_global_variables_of_subgroups()     
        ###   
        self.size_of_population = self.get_size_of_population()
        if self.running_mode == 'debug':
            p = self.smoking_prevalence()
            self.smoking_prevalence_l.append(p)
            self.logfile.write('tick '+str(self.current_time_step)+', year: ' + str(self.year_of_current_time_step) +': smoking prevalence=' + str(p) + '%.\n')
            print('tick '+str(self.current_time_step) + ', year: '+str(self.year_of_current_time_step)+': smoking prevalence=' + str(p) + '%.')      
            for subgroup,diffusion_models in self.diffusion_models_of_this_tick.items():
                for diff_model in diffusion_models:
                    self.logfile.write('e-cigarette diffusion model: e-cig_type='+str(diff_model.ecig_type)+', subgroup='+str(subgroup)+', subgroup size='+str(len(self.ecig_diff_subgroups[subgroup]))+', Et='+str(diff_model.Et)+'\n')
                self.logfile.write(F"e-cigarette prevalence of this subgroup of each tick: '{self.ecig_Et[subgroup]}'\n")
            #self.logfile.write(F"geographic regional smoking prevalence: '{self.geographicSmokingPrevalence.regionalSmokingPrevalence}'\n")
            
            # Remove the misleading "killed X agents" message - this info now comes from kill_agents directly
            # if self.months_counter == 12:
            #    sstr='killed '+str(len(self.agents_to_kill))+' agents'
            #    self.logfile.write(sstr+'\n')
            #    print(sstr)
            
            # Always show current population size
            self.logfile.write('size of population: '+str(self.size_of_population)+'\n')
            print('size of population: '+str(self.size_of_population))

            # Log network stats for all agents in our fixed sample at each tick
            if self.social_network is not None:
                active_agents = {agent.get_id(): agent for agent in self.context.agents(agent_type=self.type) if hasattr(agent, 'is_active') and agent.is_active}
                self.logfile.write("\n=== NETWORK STATISTICS FOR FIXED SAMPLE AGENTS (PER TICK) ===\n")
                logged_count = 0
                for agent_id in self.fixed_agent_ids:
                    if agent_id in active_agents:
                        agent = active_agents[agent_id]
                        state = agent.get_current_state()
                        # Convert iterator to list to get length
                        neighbours = list(self.social_network.get_neighbours(agent))
                        self.logfile.write(f"Agent {agent_id} network stats: total alters={len(neighbours)}, "
                                          f"active alters={self.social_network.count_active_neighbours(agent)}, "
                                          f"active smoking alters={self.social_network.count_smoking_neighbours(agent)}, "
                                          f"state={state}\n")
                        logged_count += 1
                self.logfile.write(f"Logged network stats for {logged_count} agents from our fixed sample at tick {self.current_time_step}\n")
                
        if self.current_time_step == self.end_year_tick:
            self.start_year_tick = self.end_year_tick + 1
            self.end_year_tick = self.start_year_tick + 11
        if self.months_counter == 12:
            self.months_counter = 0
        
    def init_schedule(self):
        '''
        schedule do_per_tick function to start at tick 1 and repeat every tick until the last tick.
        '''
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def write_ecig_prevalence_to_csv_files(self):
        '''
        write e-cigarette prevalence of subgroups to csv files
        '''
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
        '''save outputs of ABM to files'''
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
        '''initialise the ABM'''
        if self.running_mode == 'debug':
            self.logfile.write("Starting ABM initialisation\n")
            
        self.init_ecig_diffusion_subgroups()
        self.init_ecig_diffusions()
        self.init_geographic_regional_prevalence()
        
        if self.running_mode == 'debug':
            self.logfile.write("Initialising agent population\n")
            
        self.init_population()
        
        if self.running_mode == 'debug':
            self.logfile.write(f"Population initialised with {self.size_of_population} agents\n")
        
        # Load the network structure after all agents are initialised
        if "network_file" in self.props:
            network_path = f'{ROOT_DIR}/{self.props["network_file"]}'
            
            if self.running_mode == 'debug':
                self.logfile.write(f"Loading network from {network_path}\n")
                
            self.social_network.initialise_network(network_path)
        else:
            if self.running_mode == 'debug':
                self.logfile.write("No network file specified in properties\n")
        
        # Update agent theories with network reference
        if self.running_mode == 'debug':
            self.logfile.write("Preparing to update agent theories with network reference\n")
            
        self.update_theories_with_network()
        
        if self.running_mode == 'debug':
            self.logfile.write("Initialising schedule\n")
            
        self.init_schedule()
        
        if self.running_mode == 'debug':
            self.logfile.write("ABM initialisation complete\n")

    def run(self):
        self.runner.execute()
        self.collect_data()

    def update_theories_with_network(self):
        """Pass network reference to all potentially relevant agent theories."""
        # Ensure the social network is actually created and initialised
        if self.social_network is None or self.social_network.network is None:
            if self.running_mode == 'debug':
                self.logfile.write("Social network not initialised, skipping theory update.\n")
            return

        if self.running_mode == 'debug':
            self.logfile.write("Updating agent theories with network reference...\n")
            
            # Count total agents in context
            total_agents = sum(1 for _ in self.context.agents())
            self.logfile.write(f"Total agents in context: {total_agents}\n")
            
            # Count how many agents have is_active attribute
            has_is_active = sum(1 for agent in self.context.agents() if hasattr(agent, 'is_active'))
            self.logfile.write(f"Agents with is_active attribute: {has_is_active}\n")
            
            # Count how many agents are active
            active_agents = sum(1 for agent in self.context.agents() if hasattr(agent, 'is_active') and agent.is_active)
            self.logfile.write(f"Active agents: {active_agents}\n")
            
            # Count how many agents have the theory attributes
            has_quit_attempt = sum(1 for agent in self.context.agents() if hasattr(agent, 'quit_attempt_theory'))
            has_quit_maintenance = sum(1 for agent in self.context.agents() if hasattr(agent, 'quit_maintenance_theory'))
            self.logfile.write(f"Agents with quit_attempt_theory: {has_quit_attempt}\n")
            self.logfile.write(f"Agents with quit_maintenance_theory: {has_quit_maintenance}\n")
        
        updated_count = 0
        theory_missing_count = 0
        inactive_count = 0
        
        for agent in self.context.agents():
            # Ensure all agents have is_active attribute and are active
            if not hasattr(agent, 'is_active'):
                agent.is_active = True
                if self.running_mode == 'debug':
                    self.logfile.write(f"Added is_active attribute to agent {agent.get_id()}\n")
            
            # Even if agent is marked as inactive, we'll update its theories
            # to ensure network data is collected
            need_theory_update = False
                
            if hasattr(agent, 'quit_attempt_theory'):
                agent.quit_attempt_theory.network = self.social_network
                need_theory_update = True
                
            if hasattr(agent, 'quit_maintenance_theory'):
                agent.quit_maintenance_theory.network = self.social_network
                need_theory_update = True
            
            if need_theory_update:
                updated_count += 1
                # Debug log for each agent theory that was updated
                if self.running_mode == 'debug' and self.rank == 0 and updated_count <= 5:  # Limit to first 5 to avoid flooding log
                    self.logfile.write(f"Updated network for agent {agent.get_id()} theories\n")
            else:
                theory_missing_count += 1
                if self.running_mode == 'debug' and theory_missing_count <= 5:
                    self.logfile.write(f"Agent {agent.get_id()} is missing theories\n")
            
            # If agent was inactive, count it
            if hasattr(agent, 'is_active') and not agent.is_active:
                inactive_count += 1
        
        if self.running_mode == 'debug':
            self.logfile.write(f"Found {theory_missing_count} agents missing theories\n")
            self.logfile.write(f"Found {inactive_count} inactive agents\n")
            self.logfile.write(f"Finished updating theories with network reference for {updated_count} agents.\n")
            
            # Log network stats for all agents
            self.log_all_agent_network_stats()

    def log_all_agent_states(self):
        """
        Log the states of all agents in the population, providing a complete picture
        of the population composition at initialization (tick 0).
        This ensures all agent states, including NEVERSMOKE and EXSMOKER, are visible in the logs.
        """
        if self.running_mode == 'debug':
            self.logfile.write("\n=== COMPLETE POPULATION STATE DISTRIBUTION AT INITIALIZATION ===\n")
            # Count states
            state_counts = {state: 0 for state in AgentState}
            
            # First pass - count states
            for agent in self.context.agents(agent_type=self.type):
                state = agent.get_current_state()
                state_counts[state] += 1
            
            # Log the counts
            total = sum(state_counts.values())
            for state, count in state_counts.items():
                percentage = (count / total) * 100 if total > 0 else 0
                self.logfile.write(f"{state.name}: {count} agents ({percentage:.2f}%)\n")
                
            # Log sample agents of each state (up to 5 per state)
            self.logfile.write("\n=== SAMPLE AGENTS FROM EACH STATE ===\n")
            state_samples = {state: [] for state in AgentState}
            
            # Second pass - collect sample agents
            for agent in self.context.agents(agent_type=self.type):
                state = agent.get_current_state()
                if len(state_samples[state]) < 5:  # Limit to 5 samples per state
                    state_samples[state].append(agent.get_id())
            
            # Log the samples
            for state, agent_ids in state_samples.items():
                if agent_ids:  # Only log states that have agents
                    self.logfile.write(f"{state.name} agents (sample): {agent_ids}\n")
            
            self.logfile.write("=== END OF POPULATION STATE REPORT ===\n\n")

    def log_all_agent_network_stats(self):
        """
        Log network statistics for a fixed set of agents.
        Only logs when agents from our fixed sample are active.
        """
        if self.running_mode == 'debug' and self.current_time_step % 12 == 0:  # Only log once per year
            self.logfile.write("\n=== NETWORK STATISTICS FOR FIXED SAMPLE AGENTS ===\n")
            
            # Get all active agents and their IDs for quick lookup
            active_agents = {agent.get_id(): agent for agent in self.context.agents(agent_type=self.type) if agent.is_active}
            
            # Log stats for our fixed set of agents if they are active
            logged_count = 0
            for agent_id in self.fixed_agent_ids:
                if agent_id in active_agents:
                    agent = active_agents[agent_id]
                    state = agent.get_current_state()
                    self.logfile.write(f"\n--- Network stats for agent {agent_id} (state: {state.name}) ---\n")
                    self.social_network.log_network_stats(agent)
                    logged_count += 1
            
            self.logfile.write(f"\nShowing {logged_count} agents from our fixed sample (IDs: {self.fixed_agent_ids})\n")
            self.logfile.write(f"Current time step: {self.current_time_step} (Year: {self.year_of_current_time_step})\n")
            self.logfile.write("=== END OF NETWORK STATISTICS ===\n\n")