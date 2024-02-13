import pandas as pd
import random
from abc import abstractmethod

from mbssm.theory import Theory
from smokingcessation.smoking_model import SmokingModel


class STPMTheory(Theory):
    def __init__(self, name, smoking_model):
        self.smoking_model = smoking_model
        self.name = name

    @abstractmethod
    def do_situation(self):
        pass

    @abstractmethod
    def do_action(self):
        pass


class RelapseSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)
        self.prob_behaviour = None
        self.years_since_quit = None

    def do_situation(self):
        # increment age of the agent every 13 ticks
        if self.smoking_model.tick_counter == 13:
            self.agent.incrementAge()
        # retrieve probability of relapse of the matching person from STPM transition probabilities file
        self.years_since_quit = self.agent.p_years_since_quit.get_value()
        if (self.agent.p_years_since_quit.get_value() > 0) and (self.agent.p_years_since_quit.get_value() < 10):
            matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == self.agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.relapse_prob['sex'] == self.agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == self.agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == self.agent.p_years_since_quit.get_value())]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, 5])
            else:
                self.prob_behaviour = 0
                if self.smoking_model.running_mode == 'debug':
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(self.agent) + '. probability of relapse=0.\n')
        elif self.agent.p_years_since_quit.get_value() >= 10:  # retrieve the probability of years since quit of 10
            matched = self.smoking_model.relapse_prob[
                (self.smoking_model.relapse_prob['age'] == self.agent.p_age.get_value()) &
                (self.smoking_model.relapse_prob['year'] == self.smoking_model.year_of_current_time_step) &
                (self.smoking_model.relapse_prob['sex'] == self.agent.p_gender.get_value()) &
                (self.smoking_model.relapse_prob['imd_quintile'] == self.agent.p_imd_quintile.get_value()) &
                (self.smoking_model.relapse_prob['time_since_quit'] == 10)]
            matched = pd.DataFrame(matched)
            if len(matched) > 0:
                self.prob_behaviour = float(matched.iat[0, 5])
            else:
                self.prob_behaviour = 0
                if self.smoking_model.running_mode == 'debug':
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(self.agent) + '. probability of relapse=0.\n')
        else:
            self.prob_behaviour = 0
            if self.smoking_model.running_mode == 'debug':
                if self.agent.p_years_since_quit.get_value() <= 0:
                    sstr = 'The pYearsSinceQuit of this agent is =< 0. probability of relapse=0.\n'
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(self.agent) + '\n' + sstr)
                else:
                    self.smoking_model.logfile.write('no match in relapse probabilities file for this agent: ' +
                                                     str(self.agent) + '\n' +
                                                     'The pYearsSinceQuit of this agent is' +
                                                     str(self.agent.p_years_since_quit.get_value()) +
                                                     '. probability of relapse=0.\n')

    def do_action(self):
        self.agent.tick_counter_ex_smoker += 1
        if self.agent.tick_counter_ex_smoker == 13:
            self.agent.p_years_since_quit.set_value(self.agent.p_years_since_quit.get_value() + 1)
            self.agent.tick_counter_ex_smoker = 0
        self.threshold = random.uniform(0, 1)
        if self.prob_behaviour >= self.threshold:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            del self.agent.behaviour_buffer[0]
            self.agent.behaviour_buffer.append('relapse')  # append the agent's new behaviour to its behaviour buffer
            self.agent.setStateOfNextTimeStep(state='smoker')
            self.agent.tick_counter_ex_smoker = 0
            self.agent.p_years_since_quit.set_value(-1)  # -1 denotes item not applicable in HSE data.
        else:
            # delete the agent's oldest behaviour (at 0th index) from the behaviour buffer
            del self.agent.behaviour_buffer[0]
            # append the agent's new behaviour to its behaviour buffer
            self.agent.behaviour_buffer.append('no relapse')
            self.agent.setStateOfNextTimeStep(state='ex-smoker')

        # count the number of quit attempts in the last 12 months and update the
        # agent's variable pNumberOfRecentQuitAttempts
        self.agent.p_number_of_recent_quit_attempts.set_value(self.agent.behaviour_buffer.count('quit attempt'))
        if self.smoking_model.running_mode == 'debug':
            self.smoking_model.write_to_log_file(self)


class RegularSmokingSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)

    def do_situation(self):
        pass

    def do_action(self):
        pass


class QuitSTPMTheory(STPMTheory):
    def __init__(self, name, smoking_model: SmokingModel):
        super().__init__(name, smoking_model)

    def do_situation(self):
        pass

    def do_action(self):
        pass
