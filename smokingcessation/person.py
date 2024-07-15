import random
from typing import List
from config.definitions import *
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.attribute import PersonalAttribute
from mbssm.micro_agent import MicroAgent

class Person(MicroAgent):
    def __init__(self,
                 smoking_model: SmokingModel,
                 id: int,
                 type: int,
                 rank: int,
                 age: int = None,
                 gender: str = None,
                 qimd: float = None,
                 cohort: int = None,
                 educational_level: int = None,
                 sep: int = None,
                 region: int = None,
                 social_housing: int = None,
                 mental_health_conds: int = None,
                 alcohol: int = None,
                 expenditure: int = None,
                 nrt_use: int = None,
                 varenicline_use: int = None,
                 cig_consumption_prequit: int = None,
                 ecig_use: int = None,
                 states: List[AgentState] = None,
                 years_since_quit=None,
                 reg_smoke_theory=None,
                 quit_attempt_theory=None,
                 quit_success_theory=None
                 ):
        super().__init__(id=id, type=type, rank=rank)
        self.smoking_model = smoking_model
        self.p_age = PersonalAttribute(name='pAge') 
        self.p_age.set_value(age)
        self.p_gender = PersonalAttribute(name='pGender')
        self.p_gender.set_value(gender)
        self.p_imd_quintile = PersonalAttribute(name='pIMDQuintile')
        self.p_imd_quintile.set_value(qimd)
        self.p_cohort = PersonalAttribute(name='pCohort')
        self.p_cohort.set_value(cohort)
        self.p_educational_level = PersonalAttribute(name='pEducationalLevel')
        self.p_educational_level.set_value(educational_level)
        self.p_sep = PersonalAttribute(name='pSEP')
        self.p_sep.set_value(sep)
        self.p_region = PersonalAttribute(name='pRegion')
        self.p_region.set_value(region)
        self.p_social_housing = PersonalAttribute(name='pSocialHousing')
        self.p_social_housing.set_value(social_housing)
        self.p_mental_health_conditions = PersonalAttribute(name='pMentalHealthConditions')
        self.p_mental_health_conditions.set_value(mental_health_conds)
        self.p_alcohol_consumption = PersonalAttribute(name='pAlcoholConsumption')
        self.p_alcohol_consumption.set_value(alcohol)
        self.p_expenditure = PersonalAttribute(name='pExpenditure')
        self.p_expenditure.set_value(expenditure)
        self.p_nrt_use = PersonalAttribute(name='pNRTuse')
        self.p_nrt_use.set_value(nrt_use)
        self.p_varenicline_use = PersonalAttribute(name='pVareniclineUse')
        self.p_varenicline_use.set_value(varenicline_use)
        self.p_cig_consumption_prequit = PersonalAttribute(name='pCigConsumptionPrequit')
        self.p_cig_consumption_prequit.set_value(cig_consumption_prequit)
        self.p_ecig_use = PersonalAttribute(name='pECigUse')
        self.p_ecig_use.set_value(ecig_use)
        # pNumberOfRecentQuitAttempts is an imputed variable
        # (STPM does not have information on number of recent quit attempts)
        self.p_number_of_recent_quit_attempts = PersonalAttribute(name='pNumberOfRecentQuitAttempts')
        if reg_smoke_theory!=None and quit_attempt_theory!=None and quit_success_theory!=None:
            self.p_age.add_level2_attribute(quit_success_theory.level2_attributes['cAge'])
            self.p_age.add_level2_attribute(reg_smoke_theory.level2_attributes['oAge'])
            self.p_age.add_level2_attribute(quit_attempt_theory.level2_attributes['mAge'])
            self.p_age.set_value(age)
            self.p_gender.add_level2_attribute(reg_smoke_theory.level2_attributes['mGender'])
            self.p_gender.set_value(gender)
            self.p_educational_level.add_level2_attribute(reg_smoke_theory.level2_attributes['oEducationalLevel'])
            self.p_educational_level.add_level2_attribute(quit_success_theory.level2_attributes['oEducationalLevel'])
            self.p_educational_level.set_value(educational_level)
            self.p_sep.add_level2_attribute(reg_smoke_theory.level2_attributes['oSEP'])
            self.p_sep.add_level2_attribute(quit_success_theory.level2_attributes['oSEP'])
            self.p_sep.set_value(sep)
            self.p_social_housing.add_level2_attribute(reg_smoke_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.add_level2_attribute(quit_attempt_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.add_level2_attribute(quit_success_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.set_value(social_housing)
            self.p_mental_health_conditions.add_level2_attribute(reg_smoke_theory.level2_attributes['cMentalHealthConditions'])
            self.p_mental_health_conditions.add_level2_attribute(quit_success_theory.level2_attributes['cMentalHealthConditions'])
            self.p_mental_health_conditions.set_value(mental_health_conds)
            self.p_alcohol_consumption.add_level2_attribute(reg_smoke_theory.level2_attributes['cAlcoholConsumption'])
            self.p_alcohol_consumption.add_level2_attribute(quit_success_theory.level2_attributes['cAlcoholConsumption'])
            self.p_alcohol_consumption.add_level2_attribute(quit_success_theory.level2_attributes['oAlcoholConsumption'])
            self.p_alcohol_consumption.set_value(alcohol)
            self.p_expenditure.add_level2_attribute(quit_attempt_theory.level2_attributes['mSpendingOnCig'])
            self.p_expenditure.set_value(expenditure)
            self.p_nrt_use.add_level2_attribute(quit_success_theory.level2_attributes['cPrescriptionNRT'])
            self.p_nrt_use.add_level2_attribute(quit_attempt_theory.level2_attributes['mUseOfNRT'])
            self.p_nrt_use.set_value(nrt_use)
            self.p_varenicline_use.add_level2_attribute(quit_success_theory.level2_attributes['cVareniclineUse'])
            self.p_varenicline_use.set_value(varenicline_use)
            self.p_cig_consumption_prequit.add_level2_attribute(quit_success_theory.level2_attributes['cCigConsumptionPrequit'])
            self.p_cig_consumption_prequit.set_value(cig_consumption_prequit)
            self.p_ecig_use.add_level2_attribute(reg_smoke_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.add_level2_attribute(quit_success_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.set_value(ecig_use)
            self.p_number_of_recent_quit_attempts.add_level2_attribute(quit_attempt_theory.level2_attributes['mNumberOfRecentQuitAttempts'])
        # list of states. states[t] is the self's state at time step t (t=0,1,...,current time step) with
        # t=0 representing the beginning of the simulation.
        self.states = states
        self.behaviour_buffer = None
        self.k = None
        self.ecig_use = None
        self.init_behaviour_buffer_and_k_and_p_number_of_recent_quit_attempts()  # initialize:

        # behaviour buffer which stores the self's behaviours (COMB and STPM behaviours) over the last 12 months
        # k: number of consecutive quit successes following the last quit attempt in the behaviourBuffer to end of the
        # behaviourBuffer pNumberOfRecentQuitAttempts

        self.p_years_since_quit = PersonalAttribute(
            # number of years since quit smoking for an ex-smoker, NA for quitter, never_smoker and smoker
            name='pYearsSinceQuit')
        self.p_years_since_quit.set_value(years_since_quit)
        self.tick_counter_ex_smoker = 0  # count number of consecutive ticks when the self stays as an ex-smoker

    def init_behaviour_buffer_and_k_and_p_number_of_recent_quit_attempts(self):
        """
        The behaviour buffer stores the self's behaviours (COMB and STPM behaviours) over the last 12 months
        (12 ticks with each tick represents 1 month)
        COMB behaviours: 'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure'
        STPM behaviours: 'relapse', 'no relapse'
        At each tick, the behaviour buffer (a list) stores one of the 8 behaviours:
        'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure', 'relapse' and 'no relapse'
        (behaviours of a quitter over last 12 months (12 ticks):
            random behaviour (tick 1)..., random behaviour (tick i-1), quit attempt (tick i), quit success,..., quit success (tick 12)
            or
            random behaviour (tick 1),...,random behaviour (tick 12),quit attempt (tick 12))
        At tick 0, initialize the behaviour buffer of the self to its historical behaviours as follows:
        or a quitter in the baseline population (i.e. at tick 0) {
            select a random index i of the buffer (0=< i =< 11);
            set the cell at i to 'quit attempt';
            set all the cells at i+1,i+2...,11 to 'quit success';
            set the cells at 0,...,i-1 to random behaviours;
        }
        for a non-quitter in the baseline population {
            set each cell of the behaviour buffer to a random behaviour;
        }
        k: count of number of consecutive quit successes done at the current state
        Initialize k to the number of consecutive quit successes following the last quit attempt in the behaviourBuffer
        to the end of the behaviourBuffer
        """

        behaviours = [e for e in AgentBehaviour]
        self.behaviour_buffer = [behaviours[random.randint(0, len(behaviours) - 1)] for _ in range(0, 12)]
        self.k = 0
        if self.states[0] == AgentState.NEWQUITTER:
            i = random.randint(0, 12)
            self.behaviour_buffer[i] = AgentBehaviour.QUITATTEMPT
            for j in range(i + 1, 12):
                self.behaviour_buffer[j] = AgentBehaviour.QUITSUCCESS
                self.k += 1
            for q in range(0, i):  # set random behaviours to indices: 0, 1,..., i-1
                self.behaviour_buffer[q] = behaviours[random.randint(0, len(behaviours) - 1)]
        elif self.states[0] == AgentState.NEVERSMOKE:
            for i in range(0, 12):
                self.behaviour_buffer[i] = AgentBehaviour.NOUPTAKE
        elif self.states[0] == AgentState.EXSMOKER:
            for i in range(0, 12):
                self.behaviour_buffer[i] = AgentBehaviour.NORELAPSE
        elif self.states[0] == AgentState.SMOKER:
            for i in range(0, 12):
                self.behaviour_buffer[i] = behaviours[random.randint(0, len(behaviours) - 1)]
        else:
            raise ValueError(f'{self.states[0]} is not an acceptable self state')
        self.p_number_of_recent_quit_attempts.set_value(self.count_behaviour(AgentBehaviour.QUITATTEMPT))

    def update_ec_ig_use(self, eciguse: int):
        self.ecig_use = eciguse

    def set_state_of_next_time_step(self, state: AgentState):
        if not isinstance(state, AgentState):
            raise ValueError(f'{state} is not an acceptable self state')
        self.states.append(state)

    def get_previous_state(self):
        if self.smoking_model.current_time_step > 0:
            return self.states[self.smoking_model.get_current_time_step-1]
        else:
            return self.states[0]
        
    def get_current_state(self):  # get the self's state at the current time step
        return self.states[self.smoking_model.current_time_step]

    def get_current_time_step(self):
        return self.smoking_model.current_time_step

    def increment_age(self):
        self.p_age.set_value(self.p_age.value + 1)

    def add_behaviour(self, behaviour: AgentBehaviour):
        if not isinstance(behaviour, AgentBehaviour):
            raise ValueError(f'{behaviour} is not an acceptable self behaviour')
        self.behaviour_buffer.append(behaviour)

    def delete_oldest_behaviour(self):
        if len(self.behaviour_buffer) > 0:
            del self.behaviour_buffer[0]
        else:
            raise ValueError('Attempting to delete a behaviour from an empty buffer')

    def count_behaviour(self, behaviour: AgentBehaviour):
        if not isinstance(behaviour, AgentBehaviour):
            raise ValueError(f'{behaviour} is not an acceptable self behaviour')
        return self.behaviour_buffer.count(behaviour)

    def get_current_theory_of_agent(self):
        return self.get_mediator().get_current_theory_of_agent(self)

    def agent_info(self):
        current_theory = self.get_mediator().get_current_theory_of_agent(self)
        prob_behaviour = current_theory.prob_behaviour
        threshold = current_theory.threshold
        current_time_step = self.smoking_model.current_time_step
        current_year = self.smoking_model.year_of_current_time_step

        res = ['self id: ' + str(self.get_id()) + '\n',
               'state: ' + self.get_current_state().name.lower() + '\n',
               'age: ' + str(self.p_age.get_value()) + '\n',
               'behaviour: ' + self.behaviour_buffer[len(self.behaviour_buffer) - 1].name.lower() + '\n',
               'behaviour buffer: ' + str([e.name.lower() for e in self.behaviour_buffer]) + '\n',
               'p_number_of_recent_quit_attempts: ' + str(self.p_number_of_recent_quit_attempts.get_value()) + '\n',
               'p_years_since_quit: ' + str(self.p_years_since_quit.get_value()) + '\n',
               'probability of behaviour: ' + str(prob_behaviour) + '\n',
               'threshold: ' + str(threshold) + '\n',
               'time step: ' + str(current_time_step) + '\n',
               'year: ' + str(current_year)+'\n']
        return res
    
    def add_duplicate_agent_to_context2(self):
        #add a duplicate object of this agent to context2 in order to do the whole population count at this tick
        if self.smoking_model.current_time_step > 1:#context2 at tick 0 is identical to context2 at tick 1
            self.smoking_model.context2.add(MicroAgent(self.get_id(), self.get_current_state(), self.uid_rank))

    def count_agent_for_subgroups_of_ages_sex_for_initiation(self):#count agents of the subgroups (age and sex) of Table 1 initiation based on this agent's state
        #count this agent for subgroups of ages and sex for initiation
        cstate = self.get_current_state()
        if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
            if cstate == AgentState.NEVERSMOKE:
                if self.pGender.get_value()==1 and agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound:
                        N_neversmokers_startyear_ages_M.add(self.get_id())
                elif self.pGender.get_value()==2 and agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound:
                        N_neversmokers_startyear_ages_F.add(self.get_id())
        elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
                if cstate == AgentState.NEVERSMOKE:
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_neversmokers_endyear_ages_M += 1
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_neversmokers_endyear_ages_F += 1
                elif cstate == AgentState.SMOKER:                                                
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_smokers_endyear_ages_M += 1                     
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_smokers_endyear_ages_F += 1       
                elif cstate == AgentState.NEWQUITTER:
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_newquitter_endyear_ages_M += 1
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_newquitter_endyear_ages_F += 1  
                elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                                AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                                AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                                AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_ongoingquitter_endyear_ages_M += 1                   
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_ongoingquitter_endyear_ages_F += 1       
                elif cstate == AgentState.EXSMOKER:
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_exsmoker_endyear_ages_M += 1
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_exsmoker_endyear_ages_F += 1  
                elif cstate == AgentState.DEAD:
                    if self.get_id() in N_neversmokers_startyear_ages_M:
                            N_dead_endyear_ages_M += 1
                    elif self.get_id() in N_neversmokers_startyear_ages_F:
                            N_dead_endyear_ages_F += 1
                else:
                    raise ValueError(f'{cstate} is not an acceptable self state')

def count_agent_for_subgroups_of_ages_sex_imd_for_initiation(self):#count agents of the subgroups of Table 2 intiation by age, sex and IMD based on this agent's state
    #count this agent for subgroups of ages, sex and imd for quit
    cstate = self.get_current_state()
    if self.smoking_model.current_time_step == self.smoking_model.start_year_tick:
        if cstate == AgentState.NEVERSMOKE:
           if self.pGender.get_value()==1 and agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound:
                        if self.p_imd_quintile==1:
                            N_neversmokers_startyear_ages_M_IMD1.add(self.get_id())
                        elif self.p_imd_quintile==2:
                            N_neversmokers_startyear_ages_M_IMD2.add(self.get_id())
                        elif self.p_imd_quintile==3:
                            N_neversmokers_startyear_ages_M_IMD3.add(self.get_id())
                        elif self.p_imd_quintile==4:
                            N_neversmokers_startyear_ages_M_IMD4.add(self.get_id())
                        else:
                            N_neversmokers_startyear_ages_M_IMD5.add(self.get_id())
           elif self.pGender.get_value()==2 and agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound:
                        if self.p_imd_quintile==1:
                            N_neversmokers_startyear_ages_F_IMD1.add(self.get_id())
                        elif self.p_imd_quintile==2:
                            N_neversmokers_startyear_ages_F_IMD2.add(self.get_id())
                        elif self.p_imd_quintile==3:
                            N_neversmokers_startyear_ages_F_IMD3.add(self.get_id())
                        elif self.p_imd_quintile==4:
                            N_neversmokers_startyear_ages_F_IMD4.add(self.get_id())
                        else:
                            N_neversmokers_startyear_ages_F_IMD5.add(self.get_id())
    elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
            if cstate == AgentState.NEVERSMOKE:
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                    N_neversmokers_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                    N_neversmokers_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                    N_neversmokers_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                    N_neversmokers_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                    N_neversmokers_endyear_ages_M_IMD5 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                    N_neversmokers_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                                    N_neversmokers_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                                    N_neversmokers_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                                    N_neversmokers_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                                    N_neversmokers_endyear_ages_F_IMD5 += 1
            elif cstate == AgentState.SMOKER:                                                
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                N_smokers_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                N_smokers_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                N_smokers_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                N_smokers_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                N_smokers_endyear_ages_M_IMD5 += 1                            
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                N_smokers_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                            N_smokers_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                            N_smokers_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                            N_smokers_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                            N_smokers_endyear_ages_F_IMD5 += 1   
            elif cstate == AgentState.NEWQUITTER:
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                    N_newquitter_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                    N_newquitter_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                    N_newquitter_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                    N_newquitter_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                    N_newquitter_endyear_ages_M_IMD5 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                    N_newquitter_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                                    N_newquitter_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                                    N_newquitter_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                                    N_newquitter_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                                    N_newquitter_endyear_ages_F_IMD5 += 1    
            elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                    N_ongoingquitter_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                    N_ongoingquitter_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                    N_ongoingquitter_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                    N_ongogingquitter_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                    N_ongoingquitter_endyear_ages_M_IMD5 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                    N_ongoingquitter_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                                    N_ongoingquitter_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                                    N_ongoingquitter_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                                    N_ongogingquitter_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                                    N_ongoingquitter_endyear_ages_F_IMD5 += 1
            elif cstate == AgentState.EXSMOKER:
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                    N_exsmoker_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                    N_exsmoker_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                    N_exsmoker_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                    N_exsmoker_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                    N_exsmoker_endyear_ages_M_IMD5 += 1  
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                    N_exsmoker_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                                    N_exsmoker_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                                    N_exsmoker_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                                    N_exsmoker_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                                    N_exsmoker_endyear_ages_F_IMD5 += 1
            elif cstate == AgentState.DEAD:
                        if self.get_id() in N_neversmokers_startyear_ages_M_IMD1:
                                    N_dead_endyear_ages_M_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD2:
                                    N_dead_endyear_ages_M_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD3:
                                    N_dead_endyear_ages_M_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD4:
                                    N_dead_endyear_ages_M_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_M_IMD5:
                                    N_dead_endyear_ages_M_IMD5 += 1 
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD1:
                                    N_dead_endyear_ages_F_IMD1 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD2:
                                    N_dead_endyear_ages_F_IMD2 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD3:
                                    N_dead_endyear_ages_F_IMD3 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD4:
                                    N_dead_endyear_ages_F_IMD4 += 1
                        elif self.get_id() in N_neversmokers_startyear_ages_F_IMD5:
                                    N_dead_endyear_ages_F_IMD5 += 1 
            else:
                raise ValueError(f'{cstate} is not an acceptable self state')
    
def count_agent_for_subgroups_of_ages_sex_for_quit(self):#count agents of the subgroups of Table 3 quit by age and sex based on this agent's state
    #count this agent for subgroups of ages and sex for quit
    cstate = self.get_current_state()
    if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
            if cstate in (AgentState.SMOKER,AgentState.NEWQUITTER,AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                        if self.pGender.get_value()==1 and agelowerbound1 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound1:
                                N_smokers_ongoingquitters_newquitters_startyear_ages1_M.add(self.get_id())
                        elif self.pGender.get_value()==1 and agelowerbound2 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound2:
                                N_smokers_ongoingquitters_newquitters_startyear_ages2_M.add(self.get_id()) 
                        elif self.pGender.get_value()==2 and agelowerbound1 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound1:
                                N_smokers_ongoingquitters_newquitters_startyear_ages1_F.add(self.get_id())
                        elif self.pGender.get_value()==2 and agelowerbound2 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound2:
                                N_smokers_ongoingquitters_newquitters_startyear_ages2_F.add(self.get_id())       
    elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
            if cstate == AgentState.SMOKER:
                  if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                        N_smokers_endyear_ages1_M +=1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                        N_smokers_endyear_ages2_M += 1                  
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                        N_smokers_endyear_ages1_F += 1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                        N_smokers_endyear_ages2_F += 1
            elif cstate == AgentState.NEWQUITTER:
                  if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                        N_newquitters_endyear_ages1_M +=1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                        N_newquitters_endyear_ages2_M += 1                  
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                        N_newquitters_endyear_ages1_F += 1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                        N_newquitters_endyear_ages2_F += 1
            elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                  if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                        N_ongoingquitters_endyear_ages1_M +=1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                        N_ongoingquitters_endyear_ages2_M += 1                  
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                        N_ongoingquitters_endyear_ages1_F += 1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                        N_ongoingquitters_endyear_ages2_F += 1
            elif cstate == AgentState.DEAD:
                  if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                        N_dead_endyear_ages1_M +=1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                        N_dead_endyear_ages2_M += 1                  
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                        N_dead_endyear_ages1_F += 1
                  elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                        N_dead_endyear_ages2_F += 1 

def count_agent_for_subgroups_of_ages_imd_for_quit(self):#count agents of the subgroups of Table 4 quit by age and IMD based on this agent's state
    #count this agent for subgroups of ages and imd for quit
    cstate = self.get_current_state()
    if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
        if cstate in (AgentState.SMOKER,AgentState.NEWQUITTER,AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                if self.p_imd_quintile==1 and agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound3:
                        N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1.add(self.get_id())
                elif self.p_imd_quintile==2 and agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound3:
                        N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2.add(self.get_id())
                elif self.p_imd_quintile==3 and agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound3:
                        N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3.add(self.get_id())
                elif self.p_imd_quintile==4 and agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound3:
                        N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4.add(self.get_id())
                elif self.p_imd_quintile==5 and agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= ageupperbound3:
                        N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5.add(self.get_id())
    elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
        if cstate == AgentState.SMOKER:
                if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1:
                        N_smokers_endyear_ages_IMD1 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2:
                        N_smokers_endyear_ages_IMD2 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3:
                        N_smokers_endyear_ages_IMD3 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4:
                        N_smokers_endyear_ages_IMD4 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5:
                        N_smokers_endyear_ages_IMD5 += 1
        elif cstate == AgentState.NEWQUITTER:
                if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1:
                        N_newquitters_endyear_ages_IMD1 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2:
                        N_newquitters_endyear_ages_IMD2 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3:
                        N_newquitters_endyear_ages_IMD3 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4:
                        N_newquitters_endyear_ages_IMD4 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5:
                        N_newquitters_endyear_ages_IMD5 += 1
        elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1:
                        N_ongoingquitters_endyear_ages_IMD1 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2:
                        N_ongoingquitters_endyear_ages_IMD2 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3:
                        N_ongoingquitters_endyear_ages_IMD3 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4:
                        N_ongoingquitters_endyear_ages_IMD4 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5:
                        N_ongoingquitters_endyear_ages_IMD5 += 1
        elif cstate == AgentState.DEAD:
                if self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD1:
                        N_dead_endyear_ages_IMD1 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD2:
                        N_dead_endyear_ages_IMD2 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD3:
                        N_dead_endyear_ages_IMD3 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD4:
                        N_dead_endyear_ages_IMD4 += 1
                elif self.get_id() in N_smokers_ongoingquitters_newquitters_startyear_ages_IMD5:
                        N_dead_endyear_ages_IMD5 += 1
