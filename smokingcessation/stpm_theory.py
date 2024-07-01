import pandas as pd
import random
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
        # increment age of the agent every 12 ticks
        if self.smoking_model.tick_counter == 12:
            agent.increment_age()
        # retrieve probability of relapse of the matching person from STPM transition probabilities file
        self.years_since_quit = agent.p_years_since_quit.get_value()
        if (agent.p_years_since_quit.get_value() > 0) and (agent.p_years_since_quit.get_value() < 10):
            matched = self.smoking_model.STPM_relapse_prob[
                (self.smoking_model.STPM_relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.STPM_relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.STPM_relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.STPM_relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.STPM_relapse_prob['time_since_quit'] == agent.p_years_since_quit.get_value())]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, 5])
            else:
                self.prob_behaviour = 0
                if self.smoking_model.running_mode == 'debug':
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(agent) + '. probability of relapse=0.\n')
        elif agent.p_years_since_quit.get_value() >= 10:  # retrieve the probability of years since quit of 10
            matched = self.smoking_model.STPM_relapse_prob[
                (self.smoking_model.STPM_relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.STPM_relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.STPM_relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.STPM_relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.STPM_relapse_prob['time_since_quit'] == 10)]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, 5])
            else:
                self.prob_behaviour = 0
                if self.smoking_model.running_mode == 'debug':
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(agent) + '. probability of relapse=0.\n')
        else:
            self.prob_behaviour = 0
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
        pass

    def do_action(self, agent: MicroAgent):
        pass


class QuitSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)

    def do_situation(self, agent: MicroAgent):
        pass

    def do_action(self, agent: MicroAgent):
        pass
