import numpy as np
import pandas as pd
import sys
from typing import Dict
from repast4py.context import SharedContext
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner
from config.definitions import ROOT_DIR
from config.definitions import AgentState
from config.definitions import SubGroup
from mbssm.model import Model
import config.global_variables as g

class SmokingModel(Model):

    def __init__(self, comm, params: Dict):
        super().__init__(comm, params)
        self.comm = comm
        self.context: SharedContext = SharedContext(comm)  # create an agent population
        self.population_counts={}#key=subgroup, value=count of agents of subgroup
        self.init_population_counts()
        self.size_of_population = None
        self.type = 0
        self.rank: int = self.comm.Get_rank()
        self.props = params
        self.data_file: str = self.props["data_file"]  # the baseline synthetic population (STAPM 2013 data)
        self.data = pd.read_csv(f'{ROOT_DIR}/' + self.data_file, encoding='ISO-8859-1')
        self.data = self.replace_missing_value_with_zero(self.data)
        self.relapse_prob_file = f'{ROOT_DIR}/' + self.props["relapse_prob_file"]
        self.year_of_current_time_step = self.props["year_of_baseline"]
        self.year_number = 0
        self.current_time_step = 0
        self.start_year_tick = 1 #the tick of the 1st month of the current year
        self.end_year_tick = 12 #last tick of the 12th month of the current year
        self.stop_at: int = self.props["stop.at"]  # final time step (tick) of simulation
        self.tickInterval=self.props["tickInterval"] #time duration of a tick e.g. 4 weeks
        #cCigAddictStrength[t+1] = round (cCigAddictStrength[t] * exp(lambda*t)), where lambda = 0.0368 and t = 4 (weeks)
        self.lbda=self.props["lambda"] 
        #prob of smoker self identity = 1/(1+alpha*(k*t)^beta) where alpha = 1.1312, beta = 0.500, k = no. of quit successes and t = 4 (weeks)
        self.alpha=self.props["alpha"]
        self.beta=self.props["beta"]    
        self.runner: SharedScheduleRunner = init_schedule_runner(comm)
        self.smoking_prevalence_l = list()
        # hashmap (dictionary) to store betas (coefficients) of the COMB formula of regular smoking theory
        self.uptake_betas = {}
        self.attempt_betas = {}  # hashmap to store betas of the COMB formula of quit attempt theory
        self.success_betas = {}  # hashmap to store betas of the COMB formula of quit success theory
        self.store_betas_of_comb_formulae_into_maps()
        # hashmap to store the level 2 attributes of the COMB formula of regular smoking theory
        self.level2_attributes_of_uptake_formula = {'C': [], 'O': [], 'M': []}
        # hashmap to store the level 2 attributes of the COMB formula of quit attempt theory
        self.level2_attributes_of_attempt_formula = {'C': [], 'O': [], 'M': []}
        # hashmap to store the level 2 attributes of the COMB formula of quit success theory
        self.level2_attributes_of_success_formula = {'C': [], 'O': [], 'M': []}
        self.store_level2_attributes_of_comb_formulae_into_maps()
        # get the list of level 2 attribute names
        self.level2_attributes_names = list(self.data.filter(regex='^[com]').columns)
        self.relapse_prob = pd.read_csv(self.relapse_prob_file, header=0)  # read in STPM relapse probabilities
        self.running_mode = self.props['ABM_mode']  # debug or normal mode
        self.regular_smoking_behaviour = self.props['regular_smoking_behaviour'] #COMB or STPM
        self.quitting_behaviour = self.props['quitting_behaviour'] #COMB or STPM
        if self.regular_smoking_behaviour=='COMB':
            print('This ABM is using the regular smoking COM-B model, ')
        elif self.regular_smoking_behaviour=='STPM':
            print('This ABM is using the STPM initiation transition probabilities, ')
            self.initiation_prob_file = f'{ROOT_DIR}/' + self.props["initiation_prob_file"]
            self.initiation_prob = pd.read_csv(self.initiation_prob_file,header=0)  
        else:
            sys.exit('invalid regular smoking behaviour: '+self.regular_smoking_behaviour)
        if self.quitting_behaviour=='COMB':
            print('quit attempt COM-B model, quit success COM-B model, ')
        elif self.quitting_behaviour=='STPM':
            print('STPM quitting transition probabilities ')
            self.quit_prob_file = f'{ROOT_DIR}/' + self.props["quit_prob_file"]
            self.quit_prob = pd.read_csv(self.quit_prob_file,header=0)   
        else:
            sys.exit('invalid quitting behaviour: '+self.quitting_behaviour)
        print('and the STPM relapse transition probabilities.')
        self.tick_counter = 0
        if self.running_mode == 'debug':
            self.logfile = open(f'{ROOT_DIR}/output/logfile.txt', 'w')
            self.logfile.write('debug mode\n')
            if self.regular_smoking_behaviour=='COMB':
                self.logfile.write('This ABM is using the regular smoking COM-B model, ')
            elif self.regular_smoking_behaviour=='STPM':
                self.logfile.write('the STPM initiation transition probabilities, ')
            if self.quitting_behaviour=='COMB':
                self.logfile.write('the quit attempt COM-B model, quit success COM-B model ')
            elif self.quitting_behaviour=='STPM':
                self.logfile.write('the STPM quitting transition probabilities')
            self.logfile.write('and the STPM relapse transition probabilities.\n')    
    
    @staticmethod
    def replace_missing_value_with_zero(df):
        """replace NaN (missing values) with 0 to ignore the attributes in the COMB formulae (since beta*0 is 0)"""
        return df.fillna(0)

    def store_betas_of_comb_formulae_into_maps(self):
        """store the betas (coefficients) of COMB formulae for regular smoking, quit attempt and quit success
        theories into hashmaps
        input: self.pros, a map with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
        output: uptakeBetas, attemptBetas, successBetas hashmaps with key=level 2 or level 1 attribute, value=beta
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
        input: self.pros, a map with key=uptake.cAlcoholConsumption.beta, value=0.46 or key=uptake.bias value=1
        output: level2AttributesOfUptakeFormula, level2AttributesOfAttemptFormula, level2AttributesOfSuccessFormula
        hashmaps key=C, O or M and value=list of associated level 2 attributes of key
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
                        if m is not None:  # match oAlcoholConsumption
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
        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator, Theories
        from smokingcessation.comb_theory import RegSmokeTheory, QuitAttemptTheory, QuitSuccessTheory
        from smokingcessation.stpm_theory import RelapseSTPMTheory, InitiationSTPMTheory, QuitSTPMTheory
        from smokingcessation.person import Person

        for i in range(self.size_of_population):
            subgroup=None
            init_state = self.data.at[i, 'state']
            if init_state == 'never_smoker':
                states = [AgentState.NEVERSMOKE, AgentState.NEVERSMOKE]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEVERSMOKERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEVERSMOKERFEMALE
            elif init_state == 'ex-smoker':
                states = [AgentState.EXSMOKER, AgentState.EXSMOKER]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.EXSMOKERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.EXSMOKERFEMALE 
            elif init_state == 'smoker':
                states = [AgentState.SMOKER, AgentState.SMOKER]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.SMOKERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.SMOKERFEMALE 
            elif init_state == 'newquitter':
                states = [AgentState.NEWQUITTER, AgentState.NEWQUITTER]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.NEWQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.NEWQUITTERFEMALE 
            elif init_state == 'ongoingquitter1':
                states = [AgentState.ONGOINGQUITTER1, AgentState.ONGOINGQUITTER1]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter2':
                states = [AgentState.ONGOINGQUITTER2, AgentState.ONGOINGQUITTER2]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter3':
                states = [AgentState.ONGOINGQUITTER3, AgentState.ONGOINGQUITTER3]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter4':
                states = [AgentState.ONGOINGQUITTER4, AgentState.ONGOINGQUITTER4]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter5':
                states = [AgentState.ONGOINGQUITTER5, AgentState.ONGOINGQUITTER5]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter6':
                states = [AgentState.ONGOINGQUITTER6, AgentState.ONGOINGQUITTER6]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter7':
                states = [AgentState.ONGOINGQUITTER7, AgentState.ONGOINGQUITTER7]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter8':
                states = [AgentState.ONGOINGQUITTER8, AgentState.ONGOINGQUITTER8]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter9':
                states = [AgentState.ONGOINGQUITTER9, AgentState.ONGOINGQUITTER9]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter10':
                states = [AgentState.ONGOINGQUITTER10, AgentState.ONGOINGQUITTER10]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE 
            elif init_state == 'ongoingquitter11':
                states = [AgentState.ONGOINGQUITTER11, AgentState.ONGOINGQUITTER11]
                if self.data.at[i,'pGender']==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif self.data.at[i,'pGender']==2:#2=female:
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
            self.context.add(Person(
                    self,
                    i,
                    self.type,
                    self.rank,
                    age=self.data.at[i, 'pAge'],
                    gender=self.data.at[i, 'pGender'],
                    cohort=self.data.at[i, 'pCohort'],
                    qimd=self.data.at[i, 'pIMDquintile'],
                    educational_level=self.data.at[i, 'pEducationalLevel'],
                    sep=self.data.at[i, 'pSEP'],
                    region=self.data.at[i, 'pRegion'],
                    social_housing=self.data.at[i, 'pSocialHousing'],
                    mental_health_conds=self.data.at[i, 'pMentalHealthCondition'],
                    alcohol=self.data.at[i, 'pAlcoholConsumption'],
                    expenditure=self.data.at[i, 'pExpenditure'],
                    nrt_use=self.data.at[i, 'pNRTUse'],
                    varenicline_use=self.data.at[i, 'pVareniclineUse'],
                    ecig_use=self.data.at[i, 'pECigUse'],
                    cig_consumption_prequit=self.data.at[i, 'pCigConsumptionPrequit'],
                    years_since_quit=self.data.at[i, 'pYearsSinceQuit'],# number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
                    states=states,
                    reg_smoke_theory=rsmoke_theory,
                    quit_attempt_theory=qattempt_theory,
                    quit_success_theory=qsuccess_theory,
                    regular_smoking_behaviour=self.regular_smoking_behaviour,
                    quitting_behaviour=self.quitting_behaviour))
            mediator = SmokingTheoryMediator({rsmoke_theory, qattempt_theory, qsuccess_theory, relapse_stpm_theory})
            agent = self.context.agent((i, self.type, self.rank))
            agent.set_mediator(mediator)
            self.population_counts[subgroup]+=1

    def init_population_counts(self):
        subgroupsL=[SubGroup.NEVERSMOKERFEMALE,SubGroup.NEVERSMOKERMALE,SubGroup.SMOKERFEMALE,SubGroup.SMOKERMALE,\
                       SubGroup.EXSMOKERFEMALE,SubGroup.EXSMOKERMALE,SubGroup.NEWQUITTERFEMALE,SubGroup.NEWQUITTERMALE,\
                       SubGroup.ONGOINGQUITTERFEMALE,SubGroup.ONGOINGQUITTERMALE]
        for subgroup in subgroupsL:
            self.population_counts[subgroup]=0

    def init_population(self):
        self.tick_counter = 0
        self.current_time_step = 0
        (r, _) = self.data.shape
        print('size of agent population:', r)
        self.size_of_population = r
        self.init_agents()
        self.size_of_population = (self.context.size()).get(-1)
        print('size of population:', self.size_of_population)
        p = self.smoking_prevalence()
        print('===statistics of smoking prevalence===')
        print('Time step 0: year: '+str(self.year_of_current_time_step)+', smoking prevalence=' + str(p) + '%.')
        self.smoking_prevalence_l.append(p)
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

    def calculate_calibration_targets_and_do_situational_mechanisms(self):
        for agent in self.context.agents(agent_type=self.type):
            agent.count_agent_for_whole_population_counts()
            agent.count_agent_for_initiation_subgroups_by_ages_sex()
            agent.count_agent_for_initiation_subgroups_by_ages_imd()
            agent.count_agent_for_quit_subgroups_by_ages_sex()
            agent.count_agent_for_quit_subgroups_by_ages_imd()
            agent.do_situation()

    def do_action_mechanisms(self):
        """micro entities do actions based on their internal states"""
        for agent in self.context.agents(agent_type=self.type):
            agent.do_action()

    def do_transformational_mechanisms(self):
        pass

    def do_macro_to_macro_mechanisms(self):
        pass

    def smoking_prevalence(self):
        """smoking prevalence at the current time step"""
        smokers = 0
        for agent in self.context.agents(agent_type=self.type):
            if agent.get_current_state() == AgentState.SMOKER:
                smokers += 1
        prevalence = np.round(smokers / self.size_of_population * 100, 2)  # percentage of smokers
        return prevalence

    def do_per_tick(self):
        self.current_time_step += 1
        self.tick_counter += 1
        p = self.smoking_prevalence()
        print('Time step ' + str(self.current_time_step) + ', year: '+str(self.year_of_current_time_step)+': smoking prevalence=' + str(p) + '%.')
        self.smoking_prevalence_l.append(p)
        if self.current_time_step == 13:
            self.year_of_current_time_step += 1
            self.year_number += 1
        elif self.current_time_step > 13:
            if self.tick_counter == 12: #each tick is 1 month
               self.year_of_current_time_step += 1
               self.year_number += 1
        self.calculate_calibration_targets_and_do_situational_mechanisms()
        self.file_whole_population_counts.write(self.calculate_counts_of_whole_population())#write whole population counts to file
        self.init_population_counts()
        if self.current_time_step == self.end_year_tick:
            print('write calibration targets to files')
            self.file_initiation_sex.write(self.get_subgroups_of_ages_sex_for_initiation())#write subgroups counts to file
            self.file_initiation_imd.write(self.get_subgroups_of_ages_imd_for_initiation())
            self.file_quit_age_sex.write(self.get_subgroups_of_ages_sex_for_quit())
            self.file_quit_imd.write(self.get_subgroups_of_ages_imd_for_quit())
            g.initialize_global_variables_of_subgroups()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()
        self.do_macro_to_macro_mechanisms()
        if self.current_time_step == self.end_year_tick:
            self.start_year_tick = self.end_year_tick + 1
            self.end_year_tick = self.start_year_tick + 11
        if self.current_time_step == 13:
            self.tick_counter = 0
        elif self.current_time_step > 13:
            if self.tick_counter == 12:
                self.tick_counter = 0
        if self.running_mode == 'debug':
            self.logfile.write('tick: '+str(self.current_time_step)+', year: ' + str(self.year_of_current_time_step) + '\n')
            #for agent in self.context.agents(agent_type=self.type):
            #    self.logfile.writelines(agent.agent_info())

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)
    
    def collect_data(self):
        #save outputs of ABM to files
        self.file_whole_population_counts.close()
        self.file_initiation_sex.close()
        self.file_initiation_imd.close()
        self.file_quit_age_sex.close()
        self.file_quit_imd.close()
        print('whole population counts and subgroups counts for initiation and quitting are saved in the files:\n')
        print('whole_population_counts.csv, '+str(self.filename_initiation_sex)+', '+str(self.filename_initiation_imd)+',\n')
        print(str(self.filename_quit_age_sex)+','+str(self.filename_quit_imd)+'\n')
        f = open('prevalence_of_smoking.csv', 'w')
        for prev in self.smoking_prevalence_l:
            f.write(str(prev) + ',')
        f.close()
        if self.running_mode == 'debug':  # write states of each agent over the entire simulation period into a csv file
            '''
            self.logfile.write('###states of the agents over all time steps###\n')
            self.logfile.write('id')
            for i in range(self.current_time_step + 1):
                self.logfile.write(',' + str(i))
            self.logfile.write('\n')
            for agent in self.context.agents(agent_type=self.type):
                self.logfile.write(str(agent.get_id()))
                for i in range(self.current_time_step + 1):
                    self.logfile.write(',' + agent.states[i].name.lower())
                self.logfile.write('\n')
            '''
            self.logfile.close()

    def init(self):
        self.init_population()
        self.init_schedule()

    def run(self):
        self.runner.execute()
        self.collect_data()
