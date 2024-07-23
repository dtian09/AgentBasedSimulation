import pandas as pd
import random
import numpy as np
from abc import abstractmethod
from config.definitions import AgentState
from config.definitions import AgentBehaviour
from mbssm.theory import Theory
from mbssm.micro_agent import MicroAgent
from smokingcessation.smoking_model import SmokingModel


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


class RelapseSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)
        self.years_since_quit = None

    def do_situation(self, agent: MicroAgent):
        if self.smoking_model.tick_counter == 12:
            agent.increment_age()
        # retrieve probability of relapse of the matching person from STPM transition probabilities file
        self.years_since_quit = agent.p_years_since_quit.get_value()
        if (agent.p_years_since_quit.get_value() > 0) and (agent.p_years_since_quit.get_value() < 10):
            matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == agent.p_years_since_quit.get_value())]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, -1])
            else:
                self.prob_behaviour = 0
                #if self.smoking_model.running_mode == 'debug':
                #    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                #                                     str(agent) + '. probability of relapse=0.\n')
        elif agent.p_years_since_quit.get_value() >= 10:  # retrieve the probability of years since quit of 10
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
                #if self.smoking_model.running_mode == 'debug':
                #    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                #                                     str(agent) + '. probability of relapse=0.\n')
        else:
            self.prob_behaviour = 0
            '''
            if self.smoking_model.running_mode == 'debug':
                if agent.p_years_since_quit.get_value() <= 0:
                    sstr = 'The pYearsSinceQuit of this agent is =< 0. probability of relapse=0.\n'
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(agent) + '\n' + sstr)
                else:
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(agent) + '\n' +
                                                     'The pYearsSinceQuit of this agent is' +
                                                     str(agent.p_years_since_quit.get_value()) +
                                                     '. probability of relapse=0.\n')
            '''

    def do_action(self, agent: MicroAgent):
        agent.tick_counter_ex_smoker += 1
        if agent.tick_counter_ex_smoker == 12:
            agent.p_years_since_quit.set_value(agent.p_years_since_quit.get_value() + 1)
            agent.tick_counter_ex_smoker = 0
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            agent.delete_oldest_behaviour()
            # append the agent's new behaviour to its behaviour buffer
            agent.add_behaviour(AgentBehaviour.RELAPSE)
            agent.set_state_of_next_time_step(AgentState.SMOKER)
            agent.tick_counter_ex_smoker = 0
            agent.p_years_since_quit.set_value(-1)  # -1 denotes item not applicable in HSE data.
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
        if self.smoking_model.tick_counter == 12:
            agent.increment_age()
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
            #if self.smoking_model.running_mode == 'debug':
            #   self.smoking_model.logfile.write('no match in initiation probabilities file for this agent: ' +
            #                                    str(agent) + '. probability of initiation=0.\n')

    def do_action(self, agent: MicroAgent):
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
        if self.smoking_model.tick_counter == 12:
            agent.increment_age()
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
            #if self.smoking_model.running_mode == 'debug':
            #   self.smoking_model.logfile.write('no match in quit probabilities file for this agent: ' +
            #                                    str(agent) + '. probability of quit=0.\n')

    def do_action(self, agent: MicroAgent):
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
            agent.p_number_of_recent_quit_attempts.set_value(agent.count_behaviour(AgentBehaviour.QUITATTEMPT))
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
                agent.add_behaviour(AgentBehaviour.QUITSUCCESS)
                agent.k += 1
                if agent.k < 12:
                    if agent.k==1:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER1)
                    elif agent.k==2:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER2)
                    elif agent.k==3:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER3)
                    elif agent.k==4:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER4)
                    elif agent.k==5:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER5)
                    elif agent.k==6:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER6)
                    elif agent.k==7:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER7)
                    elif agent.k==8:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER8)
                    elif agent.k==9:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER9)
                    elif agent.k==10:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER10)
                    elif agent.k==11:
                        agent.set_state_of_next_time_step(AgentState.ONGOINGQUITTER11)
                else:#k==12
                    agent.set_state_of_next_time_step(AgentState.EXSMOKER)
                    agent.k=0
            else:
                # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
                agent.delete_oldest_behaviour()
                # append the agent's new behaviour to its behaviour buffer
                agent.add_behaviour(AgentBehaviour.QUITFAILURE)
                agent.set_state_of_next_time_step(AgentState.SMOKER)
                agent.k = 0
            agent.p_number_of_recent_quit_attempts.set_value(agent.count_behaviour(AgentBehaviour.QUITATTEMPT))
