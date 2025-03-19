import pandas as pd
import random
from abc import abstractmethod
from config.definitions import AgentState
from config.definitions import AgentBehaviour
from config.definitions import Theories
from mbssm.theory import Theory
from mbssm.micro_agent import MicroAgent
from smokingcessation.smoking_model import SmokingModel
#import ipdb #debugger
class STPMTheory(Theory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name)
        self.smoking_model = smoking_model

    @abstractmethod
    def do_situation(self, agent: MicroAgent):
        pass

    @abstractmethod
    def do_action(self, agent: MicroAgent):
        pass
class DemographicsSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)
        
    def do_situation(self, agent: MicroAgent):
        if self.smoking_model.months_counter == 12:
            #if age > 89, kill the agent
            #else check for death conditioned on current age, smoking status and sex before running the smoking behavior models
            #     apply death or increment age
            #note: the smokers group in stpm death model includes quitters as well as smokers 
            if agent.p_age.get_value() > 89: 
                self.smoking_model.agents_to_kill.add(agent.uid)
            else:
                if agent.get_current_state() in {AgentState.SMOKER, AgentState.NEWQUITTER, 
                                                         AgentState.ONGOINGQUITTER1, AgentState.ONGOINGQUITTER2, AgentState.ONGOINGQUITTER3,
                                                         AgentState.ONGOINGQUITTER4, AgentState.ONGOINGQUITTER5, AgentState.ONGOINGQUITTER6,
                                                         AgentState.ONGOINGQUITTER7, AgentState.ONGOINGQUITTER8, AgentState.ONGOINGQUITTER9,
                                                         AgentState.ONGOINGQUITTER10, AgentState.ONGOINGQUITTER11}:
                     state='current'
                elif agent.get_current_state() == AgentState.EXSMOKER:
                      state='former'
                elif agent.get_current_state() == AgentState.NEVERSMOKE:
                      state='never'
                else:
                    import sys
                    sstr='no such state:'+agent.get_current_state()
                    sys.exit(sstr)
                matched_row = self.smoking_model.death_prob[
                                (self.smoking_model.death_prob["year"] == self.smoking_model.year_of_current_time_step) &
                                (self.smoking_model.death_prob["age"] == agent.p_age.get_value()) &
                                (self.smoking_model.death_prob["sex"] == agent.p_gender.get_value()) &
                                (self.smoking_model.death_prob["imd_quintile"] == agent.p_imd_quintile.get_value()) &
                                (self.smoking_model.death_prob["smk.state"] == state)
                                ]
                matched_row = pd.DataFrame(matched_row)
                #ipdb.set_trace()#debug break point
                if len(matched_row) > 0:
                    col_index = matched_row.columns.get_loc("qx")
                    self.prob_behaviour = float(matched_row.iat[0, col_index])
                else:#death probability file has no death probability for this agent 
                    self.prob_behaviour = 0
                self.threshold = random.uniform(0, 1)
                if self.prob_behaviour >= self.threshold:
                    self.smoking_model.agents_to_kill.add(agent.uid)
                else:
                    agent.increment_age()

    def do_action(self, agent: MicroAgent):        
        pass    

class RelapseSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)
        
    def do_situation(self, agent: MicroAgent):
        self.smoking_model.allocateDiffusionToAgent(agent)
        #update values of the dynamic variables of agents based on Harry's equations

    def do_action(self, agent: MicroAgent):
        agent.months_counter_ex_smoker += 1
        if agent.months_counter_ex_smoker == 12:
            agent.b_years_since_quit += 1
            agent.months_counter_ex_smoker = 0
        # retrieve probability of relapse of the matching person from STPM transition probabilities file
        if (agent.b_years_since_quit > 0) and (agent.b_years_since_quit < 10):
            if self.smoking_model.year_of_current_time_step < 2011:
                matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == 2011) &
                (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == agent.b_years_since_quit)]
            else:
                matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == agent.b_years_since_quit)]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, -1])
            else:
                self.prob_behaviour = 0
        elif agent.b_years_since_quit >= 10:  # retrieve the probability of 10 years since quit
            if self.smoking_model.year_of_current_time_step < 2011:
                matched = self.smoking_model.relapse_prob[
                    (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                    (self.smoking_model.relapse_prob['year'] == 2011) &
                    (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                    (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                    (self.smoking_model.relapse_prob['time_since_quit'] == 10)]
            else:
                  matched = self.smoking_model.relapse_prob[
                    (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                    (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                    (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                    (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                    (self.smoking_model.relapse_prob['time_since_quit'] == 10)]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0,-1])
            else:
                self.prob_behaviour = 0
        else:
            self.prob_behaviour = 0
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.RELAPSE)
            agent.set_state_of_next_time_step(AgentState.SMOKER)
            agent.b_years_since_quit = 0
            if agent.smoking_model.quitting_behaviour=='COMB':
                agent.mediator.theory_map[Theories.QUITATTEMPT].level2_attributes['cCigAddictStrength'].set_value(agent.preQuitAddictionStrength)
                agent.mediator.theory_map[Theories.QUITMAINTENANCE].level2_attributes['cCigAddictStrength'].set_value(agent.preQuitAddictionStrength)
                agent.mediator.theory_map[Theories.QUITATTEMPT].level2_attributes['mNonSmokerSelfIdentity'].set_value(0)
                agent.mediator.theory_map[Theories.QUITMAINTENANCE].level2_attributes['mNonSmokerSelfIdentity'].set_value(0)
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.NORELAPSE)
            agent.set_state_of_next_time_step(AgentState.EXSMOKER)           
            
class InitiationSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)

    def do_situation(self, agent: MicroAgent):
        self.smoking_model.allocateDiffusionToAgent(agent)

    def do_action(self, agent: MicroAgent):
        if self.smoking_model.year_of_current_time_step < 2011: #STPM initiation probabilites start from 2011, so match the agent with STPM 2011 data
            matched = self.smoking_model.initiation_prob[
                (self.smoking_model.initiation_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.initiation_prob['year'] == 2011) &
                (self.smoking_model.initiation_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.initiation_prob['imd_quintile'] == agent.p_imd_quintile.get_value())]
        else:    
            matched = self.smoking_model.initiation_prob[
                (self.smoking_model.initiation_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.initiation_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.initiation_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.initiation_prob['imd_quintile'] == agent.p_imd_quintile.get_value())]
        matched = pd.DataFrame(matched)        
        if len(matched) > 0:
            self.prob_behaviour = float(matched.iat[0,-1])
        else:
            self.prob_behaviour = 0
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.UPTAKE)
            agent.set_state_of_next_time_step(AgentState.SMOKER)
        else:
            agent.delete_oldest_behaviour()
            agent.add_behaviour(AgentBehaviour.NOUPTAKE)
            agent.set_state_of_next_time_step(AgentState.NEVERSMOKE)

class QuitSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)

    def do_situation(self, agent: MicroAgent):
        self.smoking_model.allocateDiffusionToAgent(agent)
        
    def do_action(self, agent: MicroAgent):
        if self.smoking_model.year_of_current_time_step < 2011: #STPM initiation probabilites start from 2011, so match this agent with STPM 2011 data
            matched = self.smoking_model.initiation_prob[
                (self.smoking_model.initiation_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.initiation_prob['year'] == 2011) &
                (self.smoking_model.initiation_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.initiation_prob['imd_quintile'] == agent.p_imd_quintile.get_value())]
        else:            
            matched = self.smoking_model.quit_prob[
                (self.smoking_model.quit_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.quit_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.quit_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.quit_prob['imd_quintile'] == agent.p_imd_quintile.get_value())]
        matched = pd.DataFrame(matched)
        if len(matched) > 0:
            self.prob_behaviour = float(matched.iat[0,-1])
        else:
            self.prob_behaviour = 0
        self.threshold = random.uniform(0, 1)
        if agent.get_current_state() == AgentState.SMOKER:            
            if self.prob_behaviour >= self.threshold:
                # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                agent.delete_oldest_behaviour()
                # append the agent's new behaviour to its behaviour buffer
                agent.add_behaviour(AgentBehaviour.QUITATTEMPT)
                agent.set_state_of_next_time_step(state=AgentState.NEWQUITTER)
            else:
                # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                agent.delete_oldest_behaviour()
                # append the agent's new behaviour to its behaviour buffer
                agent.add_behaviour(AgentBehaviour.NOQUITEATTEMPT)
                agent.set_state_of_next_time_step(state=AgentState.SMOKER)
            agent.b_number_of_recent_quit_attempts=agent.count_quit_attempt_behaviour()
        elif agent.get_current_state() in (AgentState.NEWQUITTER, AgentState.ONGOINGQUITTER1,
                                            AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3, 
                                            AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5, 
                                            AgentState.ONGOINGQUITTER6,AgentState.ONGOINGQUITTER7, 
                                            AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9, 
                                            AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
            if self.prob_behaviour >= self.threshold:
                # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                agent.delete_oldest_behaviour()
                # append the agent's new behaviour to its behaviour buffer
                agent.add_behaviour(AgentBehaviour.QUITMAINTENANCE)
                agent.b_months_since_quit += 1
                if agent.b_months_since_quit < 12:
                    if agent.b_months_since_quit==1:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER1)
                    elif agent.b_months_since_quit==2:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER2)
                    elif agent.b_months_since_quit==3:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER3)
                    elif agent.b_months_since_quit==4:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER4)
                    elif agent.b_months_since_quit==5:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER5)
                    elif agent.b_months_since_quit==6:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER6)
                    elif agent.b_months_since_quit==7:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER7)
                    elif agent.b_months_since_quit==8:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER8)
                    elif agent.b_months_since_quit==9:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER9)
                    elif agent.b_months_since_quit==10:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER10)
                    elif agent.b_months_since_quit==11:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER11)
                else:#b_months_since_quit==12
                    agent.set_state_of_next_time_step(AgentState.EXSMOKER)
                    agent.b_months_since_quit=0
            else:
                agent.delete_oldest_behaviour()
                agent.add_behaviour(AgentBehaviour.QUITFAILURE)
                agent.set_state_of_next_time_step(AgentState.SMOKER)
                agent.b_months_since_quit=0
            agent.b_number_of_recent_quit_attempts=agent.count_quit_attempt_behaviour()

