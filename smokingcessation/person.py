import random
from typing import List
from config.definitions import *
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.attribute import PersonalAttribute
from mbssm.micro_agent import MicroAgent
import config.global_variables as g
#import ipdb
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
                 prescription_nrt: int = None,
                 over_counter_nrt: int = None,
                 use_of_nrt : int = None,
                 varenicline_use: int = None,
                 cig_consumption: int = None,
                 ecig_use: int = None,
                 ecig_type: int = None,
                 states: List[AgentState] = None,
                 number_of_recent_quit_attempts = None,
                 months_since_quit=None,
                 years_since_quit=None,
                 reg_smoke_theory=None,
                 quit_attempt_theory=None,
                 quit_success_theory=None,
                 regular_smoking_behaviour=None,#regular smoking COMB model or STPM intiation transition probabilities
                 quitting_behaviour=None #quit attempt COMB model or STPM quitting transition probabilities
                 ):
        super().__init__(id=id, type=type, rank=rank)
        self.smoking_model = smoking_model        
        self.b_states = states #list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with t=0 representing the beginning of the simulation.
        self.b_months_since_quit = months_since_quit #number of months of maintaining the quit behhaviour; only tracked for the ongoing quitter state.
        self.b_cig_consumption = cig_consumption 
        self.b_number_of_recent_quit_attempts = number_of_recent_quit_attempts
        self.b_years_since_quit = years_since_quit        
        self.months_counter_ex_smoker = 0  # count number of consecutive months when the self stays as an ex-smoker
        #ipdb.set_trace()#debug
        self.init_behaviour_buffer() #initialize the behaviour buffer which stores the agent's behaviours (COMB and STPM behaviours) over the last 12 months                                           
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
        self.p_prescription_nrt = PersonalAttribute(name='pPrescriptionNRT')
        self.p_prescription_nrt.set_value(prescription_nrt)
        self.p_over_counter_nrt = PersonalAttribute(name='pOverCounterNRT')
        self.p_over_counter_nrt.set_value(over_counter_nrt)
        self.p_use_of_nrt = PersonalAttribute(name='pUseOfNRT')
        self.p_use_of_nrt.set_value(use_of_nrt)
        self.p_varenicline_use = PersonalAttribute(name='pVareniclineUse')
        self.p_varenicline_use.set_value(varenicline_use)
        self.p_ecig_use = PersonalAttribute(name='pECigUse')
        self.p_ecig_use.set_value(ecig_use)
        self.eCig_diff_subgroup=None
        self.preQuitAddictionStrength=None
        #pPercentile #range: [1,100]. percentile of quantity of cigarettes smoked per day
        if ecig_use == 1 and ecig_type == 1:
            self.ecig_type=eCigType.Disp
        elif ecig_use == 1 and ecig_type == 0:
            self.ecig_type=eCigType.Nondisp
        else:#ecig_use == 0
            self.ecig_type=None         
        if regular_smoking_behaviour=='COMB':#if the regular smoking COMB model is used by the ABM, add its Level 2 attributes associated with the personal attributes to their lists
            self.p_age.add_level2_attribute(reg_smoke_theory.level2_attributes['oAge'])
            self.p_age.set_value(age)
            self.p_difficulty_of_access = PersonalAttribute(name='pDifficultyOfAccess')       
            self.p_difficulty_of_access.add_level2_attribute(reg_smoke_theory.level2_attributes['oDifficultyOfAccess'])
            self.update_difficulty_of_access()
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
            self.p_ecig_use.add_level2_attribute(reg_smoke_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.set_value(ecig_use)
            self.p_expenditure.add_level2_attribute(reg_smoke_theory.level2_attributes['oExpenditurePerStick'])
            self.p_expenditure.set_value(expenditure)
        if quitting_behaviour=='COMB':#if quit attempt COM-B model and quit success COM-B model are used by this ABM, add their Level 2 attributes associated with the personal attributes to the personal attributes' lists
            self.preQuitAddictionStrength=quit_attempt_theory.level2_attributes['cCigAddictStrength'].get_value()
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
            self.p_alcohol_consumption.set_value(alcohol)
            self.p_ecig_use.add_level2_attribute(quit_success_theory.level2_attributes['cEcigaretteUse'])
            self.p_ecig_use.set_value(ecig_use)
            self.p_prescription_nrt.add_level2_attribute(quit_success_theory.level2_attributes['cPrescriptionNRT'])
            self.p_prescription_nrt.set_value(prescription_nrt)
            self.p_varenicline_use.add_level2_attribute(quit_success_theory.level2_attributes['cVareniclineUse'])
            self.p_varenicline_use.set_value(varenicline_use)
            
    def update_difficulty_of_access(self):
         #difficulty of access is 0 if agent's age >= age of sale and +1 for every year below.         
         if self.p_age.get_value() >= self.smoking_model.age_of_sale:
                self.p_difficulty_of_access.set_value(0)
         else:
             self.p_difficulty_of_access.set_value(self.smoking_model.age_of_sale - self.p_age.get_value())

    #def update_dynamic_variables(self): update dynamic personal attributes and other attributes e.g. bCigConsumption
        #call update_difficulty_of_access()
        #update bCigConsumption

    def init_behaviour_buffer(self):
        """
        The behaviour buffer stores this agent's 'quit attempt behaviours' (1) and 'not quit attempt behaviours' (0) over the last 12 months
        (12 ticks with each tick represents 1 month).
        The behaviour buffer is initialized at t=0 as follows:
        X: number of quit attempts in past 12 months
        1. Generate a random permutation of indices 0,...,11
        2. Take first X indices of the permutation
        3. Assign quit attempt behaviours (1s) to the X indices and 'not quit attempt behaviours (0s) to the other indices
        """
        self.behaviour_buffer = [0 for _ in range(0, 12)]#The behaviour buffer stores this agent's 'quit attempt behaviours' (1) and 'not quit attempt behaviours' (0) over the last 12 months
        perm = random.sample(range(12), 12)
        i=0
        while i < self.b_number_of_recent_quit_attempts:
              self.behaviour_buffer[perm[i]]=1
              i+=1

    def add_behaviour(self, behaviour: AgentBehaviour):
        if not isinstance(behaviour, AgentBehaviour):
            raise ValueError(f'{behaviour} is not an acceptable self behaviour')
        elif behaviour == AgentBehaviour.QUITATTEMPT:
            self.behaviour_buffer.append(1)
        else:
            self.behaviour_buffer.append(0)

    def delete_oldest_behaviour(self):
        if len(self.behaviour_buffer) > 0:
            del self.behaviour_buffer[0]
        else:
            raise ValueError('Attempting to delete a behaviour from an empty buffer')

    def count_quit_attempt_behaviour(self):
        return sum(self.behaviour_buffer)

    def update_ec_ig_use(self, eciguse: int):
        self.ecig_use = eciguse

    def set_state_of_next_time_step(self, state: AgentState):
        if not isinstance(state, AgentState):
            raise ValueError(f'{state} is not an acceptable self state')
        self.b_states.append(state)

    def get_previous_state(self):
        if self.smoking_model.current_time_step > 0:
            return self.b_states[self.smoking_model.get_current_time_step-1]
        else:
            return self.b_states[0]
        
    def get_current_state(self):  # get the self's state at the current time step
        return self.b_states[self.smoking_model.current_time_step]

    def get_current_time_step(self):
        return self.smoking_model.current_time_step

    def increment_age(self):
        self.p_age.set_value(self.p_age.value + 1)

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

    def count_agent_for_ecig_diffusion_subgroups(self):
        #count this agent for the following e-cigarette diffusion subgroups
        #p_cohort: <1940 (0), 1941-1960 (1), 1961-1980 (2), 1981-1990 (3), 1991+ (4)
        #then, add this agent to the deltaEt_agent list of each diffusion model as appropriate
        cstate = self.get_current_state()
        if cstate == AgentState.EXSMOKER and self.p_cohort.get_value() == 0:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Exsmokerless1940].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmokerless1940
        elif cstate == AgentState.EXSMOKER and self.p_cohort.get_value() == 1:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1941_1960].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1941_1960
        elif cstate == AgentState.EXSMOKER and self.p_cohort.get_value() == 2:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1961_1980].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1961_1980  
        elif cstate == AgentState.EXSMOKER and self.p_cohort.get_value() == 3:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker1981_1990].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker1981_1990
        elif cstate == AgentState.EXSMOKER and self.p_cohort.get_value() == 4:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Exsmoker_over1991].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Exsmoker_over1991
        elif cstate == AgentState.SMOKER and self.p_cohort.get_value() == 0:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Smokerless1940].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smokerless1940
        elif cstate == AgentState.SMOKER and self.p_cohort.get_value() == 1:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1941_1960].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1941_1960
        elif cstate == AgentState.SMOKER and self.p_cohort.get_value() == 2:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1961_1980].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1961_1980  
        elif cstate == AgentState.SMOKER and self.p_cohort.get_value() == 3:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Smoker1981_1990].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker1981_1990
        elif cstate == AgentState.SMOKER and self.p_cohort.get_value() == 4:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Smoker_over1991].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Smoker_over1991
        elif cstate == AgentState.NEVERSMOKE and self.p_cohort.get_value() == 4:
                self.smoking_model.ecig_diff_subgroups[eCigDiffSubGroup.Neversmoked_over1991].add(self.get_id())
                self.eCig_diff_subgroup = eCigDiffSubGroup.Neversmoked_over1991
        else:
               self.eCig_diff_subgroup = None #this agent not in any ecig subgroup                
                           
        