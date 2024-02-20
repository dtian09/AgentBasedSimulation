import numpy as np
import pandas as pd
import sys
from typing import Dict

from repast4py.context import SharedContext
from repast4py.schedule import SharedScheduleRunner, init_schedule_runner

from config.definitions import AgentState
from mbssm.model import Model
from config.definitions import ROOT_DIR


class SmokingModel(Model):

    def __init__(self, comm, params: Dict):
        super().__init__(comm, params)
        self.comm = comm
        self.context: SharedContext = SharedContext(comm)  # create an agent population
        self.size_of_population = None
        self.rank: int = self.comm.Get_rank()
        self.type: int = 0  # type of agent in id (id is a tuple (id,rank,type))
        self.props = params
        self.data_file: str = self.props["data_file"]  # the baseline synthetic population (STAPM 2012 data)
        self.data = pd.read_csv(f'{ROOT_DIR}/' + self.data_file, encoding='ISO-8859-1')
        self.data = self.replace_missing_value_with_zero(self.data)
        self.relapse_prob_file = f'{ROOT_DIR}/' + self.props["relapse_prob_file"]
        self.year_of_current_time_step = self.props["year_of_baseline"]
        self.current_time_step = 0
        self.stop_at: int = self.props["stop.at"]  # final time step (tick) of simulation
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
        self.tick_counter = 0
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

    def init_agents(self):

        from smokingcessation.smoking_theory_mediator import SmokingTheoryMediator
        from smokingcessation.smoking_theory_mediator import Theories
        from smokingcessation.comb_theory import RegSmokeTheory
        from smokingcessation.comb_theory import QuitAttemptTheory
        from smokingcessation.comb_theory import QuitSuccessTheory
        from smokingcessation.stpm_theory import RelapseSTPMTheory
        from smokingcessation.person import Person

        for i in range(self.size_of_population):
            rsmoke_theory = RegSmokeTheory(Theories.REGSMOKE, self, i)
            qattempt_theory = QuitAttemptTheory(Theories.QUITATTEMPT, self, i)
            qsuccess_theory = QuitSuccessTheory(Theories.QUITSUCCESS, self, i)
            relapse_stpm_theory = RelapseSTPMTheory(Theories.RELAPSESSTPM, self)
            mediator = SmokingTheoryMediator({rsmoke_theory, qattempt_theory, qsuccess_theory, relapse_stpm_theory})

            init_state = self.data.at[i, 'state']
            if init_state == 'never_smoker':
                states = [AgentState.NEVERSMOKE, AgentState.NEVERSMOKE]
            elif init_state == 'ex-smoker':
                states = [AgentState.EXSMOKER, AgentState.EXSMOKER]
            elif init_state == 'smoker':
                states = [AgentState.SMOKER, AgentState.SMOKER]
            elif init_state == 'quitter':
                states = [AgentState.QUITTER, AgentState.QUITTER]
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
            theory = agent.get_current_theory_of_agent()
            self.logfile.writelines(agent.agent_info())

    def do_action_mechanisms(self):
        """micro entities do actions based on their internal states"""
        for agent in self.context.agents(agent_type=self.type):
            agent.do_action()
            self.logfile.writelines(agent.agent_info())

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
        if self.tick_counter == 13:
            self.year_of_current_time_step += 1
        if self.running_mode == 'debug':
            self.logfile.write('year: ' + str(self.year_of_current_time_step) + '\n')
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()
        self.do_macro_to_macro_mechanisms()
        if self.tick_counter == 13:
            self.tick_counter = 0

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

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
