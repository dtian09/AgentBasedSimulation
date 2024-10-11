import random
from typing import List
from config.definitions import *
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.attribute import PersonalAttribute
from mbssm.micro_agent import MicroAgent
import config.global_variables as g

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
                 quit_success_theory=None,
                 regular_smoking_behaviour=None,#regular smoking COMB model or STPM intiation transition probabilities
                 quitting_behaviour=None #quit attempt COMB model or STPM quitting transition probabilities
                 ):
        super().__init__(id=id, type=type, rank=rank)
        self.smoking_model = smoking_model        
        self.states = states #list of states. states[t] is the self's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation.
        self.behaviour_buffer = None
        self.k = None
        self.tick_counter_ex_smoker = 0  # count number of consecutive ticks when the self stays as an ex-smoker
        self.init_behaviour_buffer_and_k() #initialize: the behaviour buffer which stores the self's behaviours (COMB and STPM behaviours) over the last 12 months
                                           #            k, number of consecutive quit successes following the last quit attempt in the behaviourBuffer to end of the
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
        self.p_number_of_recent_quit_attempts = PersonalAttribute(name='pNumberOfRecentQuitAttempts')
        self.p_number_of_recent_quit_attempts.set_value(self.count_behaviour(AgentBehaviour.QUITATTEMPT))       
        self.p_years_since_quit = PersonalAttribute(
                # number of years since quit smoking for an ex-smoker, NA for quitter, never_smoker and smoker
                name='pYearsSinceQuit')
        self.p_years_since_quit.set_value(years_since_quit)
        self.eCig_diff_subgroup=None
        self.ecig_type=None           
        if regular_smoking_behaviour=='COMB':#if the regular smoking COMB model is used by the ABM, add its Level 2 attributes associated with the personal attributes to their lists
            self.p_age.add_level2_attribute(reg_smoke_theory.level2_attributes['oAge'])
            self.p_age.set_value(age)
            self.p_gender.add_level2_attribute(reg_smoke_theory.level2_attributes['mGender'])
            self.p_gender.set_value(gender)
            self.p_educational_level.add_level2_attribute(reg_smoke_theory.level2_attributes['oEducationalLevel'])
            self.p_educational_level.set_value(educational_level)
            self.p_sep.add_level2_attribute(reg_smoke_theory.level2_attributes['oSEP'])
            self.p_sep.set_value(sep)
            self.p_social_housing.add_level2_attribute(reg_smoke_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.set_value(social_housing)
            self.p_mental_health_conditions.add_level2_attribute(reg_smoke_theory.level2_attributes['cMentalHealthConditions'])
            self.p_mental_health_conditions.set_value(mental_health_conds)
            self.p_alcohol_consumption.add_level2_attribute(reg_smoke_theory.level2_attributes['cAlcoholConsumption'])
            self.p_alcohol_consumption.set_value(alcohol)
            self.p_expenditure.set_value(expenditure)
            self.p_nrt_use.set_value(nrt_use)
            self.p_varenicline_use.set_value(varenicline_use)
            self.p_cig_consumption_prequit.set_value(cig_consumption_prequit)
            self.p_ecig_use.add_level2_attribute(reg_smoke_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.set_value(ecig_use)
        if quitting_behaviour=='COMB':#if quit attempt COM-B model and quit success COM-B model are used by this ABM, add their Level 2 attributes associated with the personal attributes to the personal attributes' lists
            self.p_age.add_level2_attribute(quit_success_theory.level2_attributes['cAge'])
            self.p_age.add_level2_attribute(quit_attempt_theory.level2_attributes['mAge'])
            self.p_age.set_value(age)
            self.p_educational_level.add_level2_attribute(quit_success_theory.level2_attributes['oEducationalLevel'])
            self.p_educational_level.set_value(educational_level)
            self.p_sep.add_level2_attribute(quit_success_theory.level2_attributes['oSEP'])
            self.p_sep.set_value(sep)
            self.p_social_housing.add_level2_attribute(quit_attempt_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.add_level2_attribute(quit_success_theory.level2_attributes['oSocialHousing'])
            self.p_social_housing.set_value(social_housing)
            self.p_mental_health_conditions.add_level2_attribute(quit_success_theory.level2_attributes['cMentalHealthConditions'])
            self.p_mental_health_conditions.set_value(mental_health_conds)
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
            self.p_ecig_use.add_level2_attribute(quit_success_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.set_value(ecig_use)
            self.p_number_of_recent_quit_attempts.add_level2_attribute(quit_attempt_theory.level2_attributes['mNumberOfRecentQuitAttempts'])
            self.p_number_of_recent_quit_attempts.set_value(self.count_behaviour(AgentBehaviour.QUITATTEMPT))       
        
    def init_behaviour_buffer_and_k(self):
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
        Initialize k to the number of consecutive quit successes following the last quit attempt in the behaviour_buffer
        to the end of the behaviourBuffer
        """
        behaviours = [e for e in AgentBehaviour]
        self.behaviour_buffer = [behaviours[random.randint(0, len(behaviours) - 1)] for _ in range(0, 12)]
        self.k = 0
        if self.states[0] == AgentState.NEWQUITTER:
            i = random.randint(0, 11)
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
        elif self.states[0] in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
            for i in range(0, 12):
                self.behaviour_buffer[i] = behaviours[random.randint(0, len(behaviours) - 1)]    
        else:
            raise ValueError(f'{self.states[0]} is not an acceptable self state')

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
    
    def count_agent_for_whole_population_counts(self):
        cstate = self.get_current_state()
        gender = self.p_gender.get_value()
        if cstate == AgentState.NEVERSMOKE:
                if gender==1:#1=male
                    subgroup=SubGroup.NEVERSMOKERMALE
                elif gender==2:#2=female:
                    subgroup=SubGroup.NEVERSMOKERFEMALE
        elif cstate == AgentState.EXSMOKER:
                if gender==1:#1=male
                    subgroup=SubGroup.EXSMOKERMALE
                elif gender==2:#2=female:
                    subgroup=SubGroup.EXSMOKERFEMALE 
        elif cstate == AgentState.SMOKER:
                if gender==1:#1=male
                    subgroup=SubGroup.SMOKERMALE
                elif gender==2:#2=female:
                    subgroup=SubGroup.SMOKERFEMALE 
        elif cstate == AgentState.NEWQUITTER:
                if gender==1:#1=male
                    subgroup=SubGroup.NEWQUITTERMALE
                elif gender==2:#2=female:
                    subgroup=SubGroup.NEWQUITTERFEMALE 
        elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                                AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                                AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                                AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11): 
                if gender==1:#1=male
                    subgroup=SubGroup.ONGOINGQUITTERMALE
                elif gender==2:#2=female:
                    subgroup=SubGroup.ONGOINGQUITTERFEMALE         
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')
        self.smoking_model.population_counts[subgroup]+=1    
    
    def count_agent_for_initiation_subgroups_by_ages_sex(self):
        #count this agent for subgroups by ages and sex for initiation based on its state
        cstate = self.get_current_state()
        if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
            if cstate == AgentState.NEVERSMOKE:
                if self.p_gender.get_value()==1 and g.agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound:
                        g.N_neversmokers_startyear_ages_M.add(self.get_id())
                elif self.p_gender.get_value()==2 and g.agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound:
                        g.N_neversmokers_startyear_ages_F.add(self.get_id())
        elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
                if cstate == AgentState.NEVERSMOKE:
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_neversmokers_endyear_ages_M += 1
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_neversmokers_endyear_ages_F += 1
                elif cstate == AgentState.SMOKER:                                                
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_smokers_endyear_ages_M += 1                     
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_smokers_endyear_ages_F += 1       
                elif cstate == AgentState.NEWQUITTER:
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_newquitter_endyear_ages_M += 1
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_newquitter_endyear_ages_F += 1  
                elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                                AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                                AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                                AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_ongoingquitter_endyear_ages_M += 1                   
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_ongoingquitter_endyear_ages_F += 1       
                elif cstate == AgentState.EXSMOKER:
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_exsmoker_endyear_ages_M += 1
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_exsmoker_endyear_ages_F += 1  
                elif cstate == AgentState.DEAD:
                    if self.get_id() in g.N_neversmokers_startyear_ages_M:
                            g.N_dead_endyear_ages_M += 1
                    elif self.get_id() in g.N_neversmokers_startyear_ages_F:
                            g.N_dead_endyear_ages_F += 1
                else:
                    raise ValueError(f'{cstate} is not an acceptable self state')

    def count_agent_for_initiation_subgroups_by_ages_imd(self):
        #count this agent for subgroups of ages and imd for initiation based on its state
        cstate = self.get_current_state()
        if self.smoking_model.current_time_step == self.smoking_model.start_year_tick:
            if cstate == AgentState.NEVERSMOKE:
                if g.agelowerbound <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound:
                            if self.p_imd_quintile.get_value()==1:
                                   g.N_neversmokers_startyear_ages_IMD1.add(self.get_id())
                            elif self.p_imd_quintile.get_value()==2:
                                    g.N_neversmokers_startyear_ages_IMD2.add(self.get_id())
                            elif self.p_imd_quintile.get_value()==3:
                                    g.N_neversmokers_startyear_ages_IMD3.add(self.get_id())
                            elif self.p_imd_quintile.get_value()==4:
                                    g.N_neversmokers_startyear_ages_IMD4.add(self.get_id())
                            else:
                                    g.N_neversmokers_startyear_ages_IMD5.add(self.get_id())
        elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
                if cstate == AgentState.NEVERSMOKE:
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                        g.N_neversmokers_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                        g.N_neversmokers_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                        g.N_neversmokers_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                        g.N_neversmokers_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                        g.N_neversmokers_endyear_ages_IMD5 += 1
                elif cstate == AgentState.SMOKER:                                                
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                    g.N_smokers_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                    g.N_smokers_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                    g.N_smokers_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                    g.N_smokers_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                    g.N_smokers_endyear_ages_IMD5 += 1                             
                elif cstate == AgentState.NEWQUITTER:
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                        g.N_newquitter_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                        g.N_newquitter_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                        g.N_newquitter_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                        g.N_newquitter_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                        g.N_newquitter_endyear_ages_IMD5 += 1  
                elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                            AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                        g.N_ongoingquitter_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                        g.N_ongoingquitter_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                        g.N_ongoingquitter_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                        g.N_ongoingquitter_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                        g.N_ongoingquitter_endyear_ages_IMD5 += 1
                elif cstate == AgentState.EXSMOKER:
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                        g.N_exsmoker_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                        g.N_exsmoker_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                        g.N_exsmoker_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                        g.N_exsmoker_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                        g.N_exsmoker_endyear_ages_IMD5 += 1  
                elif cstate == AgentState.DEAD:
                            if self.get_id() in g.N_neversmokers_startyear_ages_IMD1:
                                        g.N_dead_endyear_ages_IMD1 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD2:
                                        g.N_dead_endyear_ages_IMD2 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD3:
                                        g.N_dead_endyear_ages_IMD3 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD4:
                                        g.N_dead_endyear_ages_IMD4 += 1
                            elif self.get_id() in g.N_neversmokers_startyear_ages_IMD5:
                                        g.N_dead_endyear_ages_IMD5 += 1 
                else:
                    raise ValueError(f'{cstate} is not an acceptable self state')
        
    def count_agent_for_quit_subgroups_by_ages_sex(self):
        #count this agent for subgroups of ages and sex for quit based on its state
        cstate = self.get_current_state()
        if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
                if cstate in (AgentState.SMOKER,AgentState.NEWQUITTER,AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                            AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.p_gender.get_value()==1 and g.agelowerbound1 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound1:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M.add(self.get_id())
                    elif self.p_gender.get_value()==1 and g.agelowerbound2 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound2:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M.add(self.get_id()) 
                    elif self.p_gender.get_value()==2 and g.agelowerbound1 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound1:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F.add(self.get_id())
                    elif self.p_gender.get_value()==2 and g.agelowerbound2 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound2:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F.add(self.get_id())       
        elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
                if cstate == AgentState.SMOKER:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                            g.N_smokers_endyear_ages1_M +=1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                            g.N_smokers_endyear_ages2_M += 1                  
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                            g.N_smokers_endyear_ages1_F += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                            g.N_smokers_endyear_ages2_F += 1
                elif cstate == AgentState.NEWQUITTER:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                            g.N_newquitters_endyear_ages1_M +=1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                            g.N_newquitters_endyear_ages2_M += 1                  
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                            g.N_newquitters_endyear_ages1_F += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                            g.N_newquitters_endyear_ages2_F += 1
                elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                            AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                            g.N_ongoingquitters_endyear_ages1_M +=1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                            g.N_ongoingquitters_endyear_ages2_M += 1                  
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                            g.N_ongoingquitters_endyear_ages1_F += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                            g.N_ongoingquitters_endyear_ages2_F += 1
                elif cstate == AgentState.DEAD:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_M:
                            g.N_dead_endyear_ages1_M +=1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_M:
                            g.N_dead_endyear_ages2_M += 1                  
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages1_F:
                            g.N_dead_endyear_ages1_F += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages2_F:
                            g.N_dead_endyear_ages2_F += 1 

    def count_agent_for_quit_subgroups_by_ages_imd(self):
        #count this agent for subgroups of ages and imd for quit based on its state
        cstate = self.get_current_state()
        if self.smoking_model.current_time_step == self.smoking_model.start_year_tick: 
            if cstate in (AgentState.SMOKER,AgentState.NEWQUITTER,AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                            AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.p_imd_quintile.get_value()==1 and g.agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound3:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1.add(self.get_id())
                    elif self.p_imd_quintile.get_value()==2 and g.agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound3:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2.add(self.get_id())
                    elif self.p_imd_quintile.get_value()==3 and g.agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound3:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3.add(self.get_id())
                    elif self.p_imd_quintile.get_value()==4 and g.agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound3:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4.add(self.get_id())
                    elif self.p_imd_quintile.get_value()==5 and g.agelowerbound3 <= self.p_age.get_value() and self.p_age.get_value() <= g.ageupperbound3:
                            g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5.add(self.get_id())
        elif self.smoking_model.current_time_step == self.smoking_model.end_year_tick:
            if cstate == AgentState.SMOKER:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1:
                            g.N_smokers_endyear_ages3_IMD1 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2:
                            g.N_smokers_endyear_ages3_IMD2 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3:
                            g.N_smokers_endyear_ages3_IMD3 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4:
                            g.N_smokers_endyear_ages3_IMD4 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5:
                            g.N_smokers_endyear_ages3_IMD5 += 1
            elif cstate == AgentState.NEWQUITTER:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1:
                            g.N_newquitters_endyear_ages3_IMD1 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2:
                            g.N_newquitters_endyear_ages3_IMD2 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3:
                            g.N_newquitters_endyear_ages3_IMD3 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4:
                            g.N_newquitters_endyear_ages3_IMD4 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5:
                            g.N_newquitters_endyear_ages3_IMD5 += 1
            elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                            AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1:
                            g.N_ongoingquitters_endyear_ages3_IMD1 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2:
                            g.N_ongoingquitters_endyear_ages3_IMD2 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3:
                            g.N_ongoingquitters_endyear_ages3_IMD3 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4:
                            g.N_ongoingquitters_endyear_ages3_IMD4 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5:
                            g.N_ongoingquitters_endyear_ages3_IMD5 += 1
            elif cstate == AgentState.DEAD:
                    if self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD1:
                            g.N_dead_endyear_ages3_IMD1 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD2:
                            g.N_dead_endyear_ages3_IMD2 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD3:
                            g.N_dead_endyear_ages3_IMD3 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD4:
                            g.N_dead_endyear_ages3_IMD4 += 1
                    elif self.get_id() in g.N_smokers_ongoingquitters_newquitters_startyear_ages3_IMD5:
                            g.N_dead_endyear_ages3_IMD5 += 1

    def count_agent_for_ecig_diffusion_subgroups_and_add_to_deltaEtagents(self):
        #count this agent for the following e-cigarette diffusion subgroups
        #p_cohort: <1940 (0), 1941-1960 (1), 1961-1980 (2), 1981-1990 (3), 1991+ (4)
        #then, add this agent to the deltaEt_agent list of each diffusion model as appropriate
        cstate = self.get_current_state()
        if cstate == AgentState.EXSMOKER and self.p_cohort == 0:
                self.smoking_model.exsmoker_less_1940.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmokerless1940
        elif cstate == AgentState.EXSMOKER and self.p_cohort == 1:
                self.smoking_model.exsmoker_1941_1960.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1941_1960
        elif cstate == AgentState.EXSMOKER and self.p_cohort == 2:
                self.smoking_model.exsmoker_1961_1980.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1961_1980  
        elif cstate == AgentState.EXSMOKER and self.p_cohort == 3:
                self.smoking_model.exsmoker_1981_1990.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1981_1990
        elif cstate == AgentState.EXSMOKER and self.p_cohort == 4:
                self.smoking_model.exsmoker_over_1991.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker_over1991
        elif cstate == AgentState.SMOKER and self.p_cohort == 0:
                self.smoking_model.smoker_less_1940.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smokerless1940
        elif cstate == AgentState.SMOKER and self.p_cohort == 1:
                self.smoking_model.smoker_1941_1960.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1941_1960
        elif cstate == AgentState.SMOKER and self.p_cohort == 2:
                self.smoking_model.smoker_1961_1980.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1961_1980  
        elif cstate == AgentState.SMOKER and self.p_cohort == 3:
                self.smoking_model.smoker_1981_1990.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1981_1990
        elif cstate == AgentState.EXSMOKER and self.p_cohort == 4:
                self.smoking_model.smoker_over_1991.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker_over1991
        elif cstate == AgentState.NEVERSMOKE and self.p_cohort == 4:
                self.smoking_model.neversmoker_over_1991.add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Neversmoked_over1991
        if self.eCig_diff_subgroup!=None:
                for diffusion_model in self.smoking_model.diffusion_models_of_this_tick[self.eCig_diff_subgroup]:
                        if diffusion_model.deltaEt > 0 and self.p_ecig_use.get_value()==0 and (len(diffusion_model.deltaEt_agents) < diffusion_model.deltaEt):
                                diffusion_model.deltaEt_agents.append[self.get_id()]      
                        elif diffusion_model.deltaEt < 0 and self.p_ecig_use.get_value()==1 and diffusion_model.ecig_type == self.ecig_type and (len(diffusion_model.deltaEt_agents) < abs(diffusion_model.deltaEt)):
                                diffusion_model.deltaEt_agents.append[self.get_id()]
                    
                           
        