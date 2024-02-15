import pandas as pd
import random
from abc import abstractmethod

from mbssm.theory import Theory
from smokingcessation.smoking_model import SmokingModel
from mbssm.micro_agent import MicroAgent


class STPMTheory(Theory):
    def __init__(self, name, smoking_model):
        super().__init__()
        self.smoking_model = smoking_model
        self.name = name

    @abstractmethod
    def do_situation(self, agent: MicroAgent):
        pass

    @abstractmethod
    def do_action(self, agent: MicroAgent):
        pass


class RelapseSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)
        self.prob_behaviour = None
        self.years_since_quit = None

    def do_situation(self, agent: MicroAgent):
        # increment age of the agent every 13 ticks
        if self.smoking_model.tick_counter == 13:
            agent.incrementAge()
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
                self.prob_behaviour = float(matched.iat[0, 5])
            else:
                self.prob_behaviour = 0
                if self.smoking_model.running_mode == 'debug':
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(agent) + '. probability of relapse=0.\n')
        elif agent.p_years_since_quit.get_value() >= 10:  # retrieve the probability of years since quit of 10
            matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.relapse_prob['sex'] == agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == 10)]
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
        if agent.tick_counter_ex_smoker == 13:
            agent.p_years_since_quit.set_value(agent.p_years_since_quit.get_value() + 1)
            agent.tick_counter_ex_smoker = 0
        threshold = random.uniform(0, 1)
        if self.prob_behaviour >= threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            del agent.behaviour_buffer[0]
            agent.behaviour_buffer.append('relapse')  # append the agent's new behaviour to its behaviour buffer
            agent.setStateOfNextTimeStep(state='smoker')
            agent.tick_counter_ex_smoker = 0
            agent.p_years_since_quit.set_value(-1)  # -1 denotes item not applicable in HSE data.
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            del agent.behaviour_buffer[0]
            # append the agent's new behaviour to its behaviour buffer
            agent.behaviour_buffer.append('no relapse')
            agent.setStateOfNextTimeStep(state='ex-smoker')

        # count the number of quit attempts in the last 12 months and update the
        # agent's variable pNumberOfRecentQuitAttempts
        agent.p_number_of_recent_quit_attempts.set_value(agent.behaviour_buffer.count('quit attempt'))
        if self.smoking_model.running_mode == 'debug':
            self.smoking_model.write_to_log_file(self)


class RegularSmokingSTPMTheory(STPMTheory):
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
