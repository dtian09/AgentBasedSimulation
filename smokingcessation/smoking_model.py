import numpy as np
import pandas as pd
import sys
from typing import Dict

from repast4py.context import SharedContext
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner

from config.definitions import ROOT_DIR
from config.definitions import AgentState
from mbssm.model import Model
from mbssm.micro_agent import MicroAgent


class SmokingModel(Model):

    def __init__(self, comm, params: Dict):
        super().__init__(comm, params)
        self.comm = comm
        self.context: SharedContext = SharedContext(comm)  # create an agent population
        self.size_of_population = None
        self.rank: int = self.comm.Get_rank()
        self.type: int = 0  # type of agent in id (id is a tuple (id,rank,type))
        self.props = params
        self.data_file: str = self.props["data_file"]  # the baseline synthetic population (STAPM 2013 data)
        self.data = pd.read_csv(f'{ROOT_DIR}/' + self.data_file, encoding='ISO-8859-1')
        self.data = self.replace_missing_value_with_zero(self.data)
        self.relapse_prob_file = f'{ROOT_DIR}/' + self.props["relapse_prob_file"]
        self.year_of_current_time_step = self.props["year_of_baseline"]
        self.current_time_step = 0
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
        self.behaviour_model = self.props['behaviour_model'] #COMB or STPM
        if self.behaviour_model!='COMB':
            if self.behaviour_model!='STPM':
                sys.exit('invalid behaviour model: '+self.behaviour_model) 
        if self.behaviour_model=='COMB':
            print('This ABM is using the COM-B model.')
        elif self.behaviour_model=='STPM':
            print('This ABM is using the STPM model.')
        else:
            sys.exit('invalid behaviour model: '+self.behaviour_model) 
        self.tick_counter = 0
        # hashmap to store net initiation probabilities of ages 16 to 24 by sex and by year and IMD quintile of each tick
        self.net_initiation_probabilities={'male':[],
                                           'female':[],
                                           '2011-2013 and 1_least_deprived':[],
                                           '2014-2016 and 1_least_deprived':[],
                                           '2017-2019 and 1_least_deprived':[],
                                           '2011-2013 and 2':[],
                                           '2014-2016 and 2':[],
                                           '2017-2019 and 2':[],
                                           '2011-2013 and 3':[],
                                           '2014-2016 and 3':[],
                                           '2017-2019 and 3':[],
                                           '2011-2013 and 4':[],
                                           '2014-2016 and 4':[],
                                           '2017-2019 and 4':[],
                                           '2011-2013 and 5_most_deprived':[],
                                           '2014-2016 and 5_most_deprived':[],
                                           '2017-2019 and 5_most_deprived':[]
                                           }
        #hashmap to store the average net initiation probabilities of ages 16 to 24 by sex and by year and IMD quintile of each tick
        self.average_net_initiation_probabilities={'male':[],
                                           'female':[],
                                           '2011-2013 and 1_least_deprived':[],
                                           '2014-2016 and 1_least_deprived':[],
                                           '2017-2019 and 1_least_deprived':[],
                                           '2011-2013 and 2':[],
                                           '2014-2016 and 2':[],
                                           '2017-2019 and 2':[],
                                           '2011-2013 and 3':[],
                                           '2014-2016 and 3':[],
                                           '2017-2019 and 3':[],
                                           '2011-2013 and 4':[],
                                           '2014-2016 and 4':[],
                                           '2017-2019 and 4':[],
                                           '2011-2013 and 5_most_deprived':[],
                                           '2014-2016 and 5_most_deprived':[],
                                           '2017-2019 and 5_most_deprived':[]
                                           }
        # hashmap to store quitting probabilities by sex and age and by year and IMD quintile of each tick
        self.quitting_probabilities={      'male and 25-49':[],
                                           'female and 25-49':[],
                                           'male and 50-74':[],
                                           'female and 50-74':[],                                           
                                           '2011-2013 and 1_least_deprived':[],
                                           '2014-2016 and 1_least_deprived':[],
                                           '2017-2019 and 1_least_deprived':[],
                                           '2011-2013 and 2':[],
                                           '2014-2016 and 2':[],
                                           '2017-2019 and 2':[],
                                           '2011-2013 and 3':[],
                                           '2014-2016 and 3':[],
                                           '2017-2019 and 3':[],
                                           '2011-2013 and 4':[],
                                           '2014-2016 and 4':[],
                                           '2017-2019 and 4':[],
                                           '2011-2013 and 5_most_deprived':[],
                                           '2014-2016 and 5_most_deprived':[],
                                           '2017-2019 and 5_most_deprived':[]
                                    }
        # hashmap to store average quitting probabilities by sex and age and by year and IMD quintile of each tick  
        self.average_quitting_probabilities={      'male and 25-49':[],
                                           'female and 25-49':[],
                                           'male and 50-74':[],
                                           'female and 50-74':[],                                           
                                           '2011-2013 and 1_least_deprived':[],
                                           '2014-2016 and 1_least_deprived':[],
                                           '2017-2019 and 1_least_deprived':[],
                                           '2011-2013 and 2':[],
                                           '2014-2016 and 2':[],
                                           '2017-2019 and 2':[],
                                           '2011-2013 and 3':[],
                                           '2014-2016 and 3':[],
                                           '2017-2019 and 3':[],
                                           '2011-2013 and 4':[],
                                           '2014-2016 and 4':[],
                                           '2017-2019 and 4':[],
                                           '2011-2013 and 5_most_deprived':[],
                                           '2014-2016 and 5_most_deprived':[],
                                           '2017-2019 and 5_most_deprived':[]
                                    }
        if self.running_mode == 'debug':
            self.logfile = open('logfile.txt', 'w')
            self.logfile.write('debug mode\n')

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

    def store_prob_of_regular_smoking_into_hashmap(self, prob_behaviour : float, agent : MicroAgent):
            if agent.p_gender.get_value()==1: #male
               self.net_initiation_probabilities['male'].append(prob_behaviour)
            elif agent.p_gender.get_value()==2: #female
               self.net_initiation_probabilities['female'].append(prob_behaviour)
            else:
               sys.exit('invalid gender: '+str(agent.p_gender.get_value())+'. Expected 1 or 2.')
            self.insert_prob_of_subgroups_by_years_and_imd_quintile_into_hashmap(prob_behaviour, agent, self.net_initiation_probabilities)

    def store_prob_of_quit_attempt_or_quit_success_into_hashmap(self, prob_behaviour : float, agent : MicroAgent):                      
            if agent.p_gender.get_value()==1: #male
                if agent.p_age.get_value()>=25 and agent.p_age.get_value()<=49: 
                  self.quitting_probabilities['male and 25-49'].append(prob_behaviour)
                elif agent.p_age.get_value()>=50 and agent.p_age.get_value()<=74:
                  self.quitting_probabilities['male and 50-74'].append(prob_behaviour)
            elif agent.p_gender.get_value()==2: #female
                if agent.p_age.get_value()>=25 and agent.p_age.get_value()<=49: 
                  self.quitting_probabilities['female and 25-49'].append(prob_behaviour)
                elif agent.p_age.get_value()>=50 and agent.p_age.get_value()<=74:
                  self.quitting_probabilities['female and 50-74'].append(prob_behaviour)
            else:
                sys.exit('invalid gender: '+str(agent.p_gender.get_value())+'. Expected 1 or 2.')
            self.store_prob_of_subgroups_by_years_and_imd_quintile_into_hashmap(prob_behaviour, agent, self.quitting_probabilities)

    def store_prob_of_subgroups_by_years_and_imd_quintile_into_hashmap(self, prob_behaviour : float, agent : MicroAgent, hashmap):
            if agent.p_imd_quintile.get_value()==1:
                if self.year_of_current_time_step>=2011 and self.year_of_current_time_step<=2013:
                   hashmap['2011-2013 and 1_least_deprived'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2014 and self.year_of_current_time_step<=2016:
                   hashmap['2014-2016 and 1_least_deprived'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2017 and self.year_of_current_time_step<=2019:
                   hashmap['2017-2019 and 1_least_deprived'].append(prob_behaviour)
            elif agent.p_imd_quintile.get_value()==2:
                if self.year_of_current_time_step>=2011 and self.year_of_current_time_step<=2013:
                   hashmap['2011-2013 and 2'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2014 and self.year_of_current_time_step<=2016:
                   hashmap['2014-2016 and 2'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2017 and self.year_of_current_time_step<=2019:
                   hashmap['2017-2019 and 2'].append(prob_behaviour)
            elif agent.p_imd_quintile.get_value()==3:
                if self.year_of_current_time_step>=2011 and self.year_of_current_time_step<=2013:
                   hashmap['2011-2013 and 3'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2014 and self.year_of_current_time_step<=2016:
                   hashmap['2014-2016 and 3'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2017 and self.year_of_current_time_step<=2019:
                   hashmap['2017-2019 and 3'].append(prob_behaviour)
            elif agent.p_imd_quintile.get_value()==4:
                if self.year_of_current_time_step>=2011 and self.year_of_current_time_step<=2013:
                   hashmap['2011-2013 and 4'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2014 and self.year_of_current_time_step<=2016:
                   hashmap['2014-2016 and 4'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2017 and self.year_of_current_time_step<=2019:
                   hashmap['2017-2019 and 4'].append(prob_behaviour)
            elif agent.p_imd_quintile.get_value()==5:
                if self.year_of_current_time_step>=2011 and self.year_of_current_time_step<=2013:
                   hashmap['2011-2013 and 5'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2014 and self.year_of_current_time_step<=2016:
                   hashmap['2014-2016 and 5'].append(prob_behaviour)
                elif self.year_of_current_time_step>=2017 and self.year_of_current_time_step<=2019:
                   hashmap['2017-2019 and 5'].append(prob_behaviour)
            else:
                sys.exit('invalid IMD quintile: '+str(agent.p_imd_quintile.get_value())+'. Expected 1, 2, 3, 4 or 5.')

    def init_agents(self):

        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator
        from smokingcessation.smoking_theory_mediator import Theories
        from smokingcessation.comb_theory import RegSmokeTheory
        from smokingcessation.comb_theory import QuitAttemptTheory
        from smokingcessation.comb_theory import QuitSuccessTheory
        from smokingcessation.stpm_theory import RelapseSTPMTheory
        from smokingcessation.person import Person

        for i in range(self.size_of_population):
            if self.behaviour_model=='COMB':
                rsmoke_theory = RegSmokeTheory(Theories.REGSMOKE, self, i)
                qattempt_theory = QuitAttemptTheory(Theories.QUITATTEMPT, self, i)
                qsuccess_theory = QuitSuccessTheory(Theories.QUITSUCCESS, self, i)
                relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)
            else:
                rsmoke_theory = InitiationSTPMTheory(Theories.REGSMOKE, self)
                qattempt_theory = QuitSTPMTheory(Theories.QUITATTEMPT, self)
                qsuccess_theory = QuitSTPMTheory(Theories.QUITSUCCESS, self)
                relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)            
            mediator = SmokingTheoryMediator({rsmoke_theory, qattempt_theory, qsuccess_theory, relapse_stpm_theory})

            init_state = self.data.at[i, 'state']
            if init_state == 'never_smoker':
                states = [AgentState.NEVERSMOKE, AgentState.NEVERSMOKE]
            elif init_state == 'ex-smoker':
                states = [AgentState.EXSMOKER, AgentState.EXSMOKER]
            elif init_state == 'smoker':
                states = [AgentState.SMOKER, AgentState.SMOKER]
            elif init_state == 'newquitter':
                states = [AgentState.NEWQUITTER, AgentState.NEWQUITTER]
            elif init_state == 'ongoingquitter1':
                states = [AgentState.ONGOINGQUITTER1, AgentState.ONGOINGQUITTER1]
            elif init_state == 'ongoingquitter2':
                states = [AgentState.ONGOINGQUITTER2, AgentState.ONGOINGQUITTER2]
            elif init_state == 'ongoingquitter3':
                states = [AgentState.ONGOINGQUITTER3, AgentState.ONGOINGQUITTER3]
            elif init_state == 'ongoingquitter4':
                states = [AgentState.ONGOINGQUITTER4, AgentState.ONGOINGQUITTER4]
            elif init_state == 'ongoingquitter5':
                states = [AgentState.ONGOINGQUITTER5, AgentState.ONGOINGQUITTER5]
            elif init_state == 'ongoingquitter6':
                states = [AgentState.ONGOINGQUITTER6, AgentState.ONGOINGQUITTER6]
            elif init_state == 'ongoingquitter7':
                states = [AgentState.ONGOINGQUITTER7, AgentState.ONGOINGQUITTER7]
            elif init_state == 'ongoingquitter8':
                states = [AgentState.ONGOINGQUITTER8, AgentState.ONGOINGQUITTER8]
            elif init_state == 'ongoingquitter9':
                states = [AgentState.ONGOINGQUITTER9, AgentState.ONGOINGQUITTER9]
            elif init_state == 'ongoingquitter10':
                states = [AgentState.ONGOINGQUITTER10, AgentState.ONGOINGQUITTER10]
            elif init_state == 'ongoingquitter11':
                states = [AgentState.ONGOINGQUITTER11, AgentState.ONGOINGQUITTER11]                        
            else:
                raise ValueError(f'{init_state} is not an acceptable agent state')

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
                years_since_quit=self.data.at[i, 'pYearsSinceQuit'],
                # number of years since quit smoking for an ex-smoker, None for quitter, never_smoker and smoker
                states=states,
                # state at tick 1 is the same as state at tick 0.
                reg_smoke_theory=rsmoke_theory,
                quit_attempt_theory=qattempt_theory,
                quit_success_theory=qsuccess_theory
            ))
            agent = self.context.agent((i, self.type, self.rank))
            # mediator.set_agent(agent)
            agent.set_mediator(mediator)

    def init_population(self):
        (r, _) = self.data.shape
        print('size of agent population:', r)
        self.size_of_population = r
        self.init_agents()
        self.size_of_population = (self.context.size()).get(-1)
        print('size of population:', self.size_of_population)
        p = self.smoking_prevalence()
        print('===statistics of smoking prevalence===')
        print('Time step 0: smoking prevalence=' + str(p) + '%.')
        self.smoking_prevalence_l.append(p)

    def do_situational_mechanisms(self):
        """macro entities change internal states of micro entities (agents)"""
        for agent in self.context.agents(agent_type=self.type):
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
        p = self.smoking_prevalence()
        print('Time step ' + str(self.current_time_step) + ': smoking prevalence=' + str(p) + '%.')
        self.smoking_prevalence_l.append(p)
        self.tick_counter += 1
        if self.tick_counter == 12:#each tick is 1 month
            self.year_of_current_time_step += 1
        if self.running_mode == 'debug':
            self.logfile.write('year: ' + str(self.year_of_current_time_step) + '\n')
        #count sizes of subgroups: N_never_smokers_16-24M, N_ongoing_quitter_16-24M (N1,3+N1,4) etc.
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()
        self.do_macro_to_macro_mechanisms()
        if self.tick_counter == 13:
            self.tick_counter = 0
        for agent in self.context.agents(agent_type=self.type):
            self.logfile.writelines(agent.agent_info())

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def calculate_average_net_initiation_probabilities(self):
        for (k,v) in self.net_initiation_probabilities.items():
            if len(v)>0:
                m=np.mean(v)
            else:#empty list (subgroup does not exist for this tick)
                m='subgroup not exist'
            self.average_net_initiation_probabilities[k].append(m)
            self.net_initiation_probabilities[k]=[]#empty the list to store the net initiation probabilities of next tick     
        return self.average_net_initiation_probabilities
        
    def calculate_average_quitting_probabilities(self):
        for (k,v) in self.quitting_probabilities.items():
            if len(v)>0:
                m=np.mean(v)
            else:#empty list (subgroup does not exist for this tick)
                m='subgroup not exist'            
            self.average_quitting_probabilities[k].append(m)
            self.quitting_probabilities[k]=[]#empty list to store the quitting probabilities of next tick
        return self.average_quitting_probabilities
    
    def collect_data(self):
        f = open('prevalence_of_smoking.csv', 'w')
        for prev in self.smoking_prevalence_l:
            f.write(str(prev) + ',')
        f.close()
        if self.running_mode == 'debug':  # write states of each agent over the entire simulation period into a csv file
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
            self.logfile.close()

    def init(self):
        self.init_population()
        self.init_schedule()

    def run(self):
        self.runner.execute()
        self.collect_data()
