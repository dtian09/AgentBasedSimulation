
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.attribute import PersonalAttribute
from mbssm.micro_agent import MicroAgent
import random
from typing import List


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
                 states: List = None,
                 years_since_quit=None,
                 reg_smoke_theory=None,
                 quit_attempt_theory=None,
                 quit_success_theory=None
                 ):
        super().__init__(id=id, type=type, rank=rank)
        self.smoking_model = smoking_model
        self.p_age = PersonalAttribute(name='pAge')
        self.p_age.add_level2_attribute(quit_success_theory.level2_attributes['cAge'])
        self.p_age.add_level2_attribute(reg_smoke_theory.level2_attributes['oAge'])
        self.p_age.add_level2_attribute(quit_attempt_theory.level2_attributes['mAge'])
        self.p_age.set_value(age)
        self.p_gender = PersonalAttribute(name='pGender')
        self.p_gender.add_level2_attribute(reg_smoke_theory.level2_attributes['mGender'])
        self.p_gender.set_value(gender)
        self.p_imd_quintile = PersonalAttribute(name='pIMDQuintile')
        self.p_imd_quintile.set_value(qimd)
        self.p_cohort = PersonalAttribute(name='pCohort')
        self.p_cohort.set_value(cohort)
        self.p_educational_level = PersonalAttribute(name='pEducationalLevel')
        self.p_educational_level.add_level2_attribute(reg_smoke_theory.level2_attributes['oEducationalLevel'])
        self.p_educational_level.add_level2_attribute(quit_success_theory.level2_attributes['oEducationalLevel'])
        self.p_educational_level.set_value(educational_level)
        self.p_sep = PersonalAttribute(name='pSEP')
        self.p_sep.add_level2_attribute(reg_smoke_theory.level2_attributes['oSEP'])
        self.p_sep.add_level2_attribute(quit_success_theory.level2_attributes['oSEP'])
        self.p_sep.set_value(sep)
        self.p_region = PersonalAttribute(name='pRegion')
        self.p_region.set_value(region)
        self.p_social_housing = PersonalAttribute(name='pSocialHousing')
        self.p_social_housing.add_level2_attribute(reg_smoke_theory.level2_attributes['oSocialHousing'])
        self.p_social_housing.add_level2_attribute(quit_attempt_theory.level2_attributes['oSocialHousing'])
        self.p_social_housing.add_level2_attribute(quit_success_theory.level2_attributes['oSocialHousing'])
        self.p_social_housing.set_value(social_housing)
        self.p_mental_health_conditions = PersonalAttribute(name='pMentalHealthConditions')
        self.p_mental_health_conditions.add_level2_attribute(reg_smoke_theory.level2_attributes['cMentalHealthConditions'])
        self.p_mental_health_conditions.add_level2_attribute(quit_success_theory.level2_attributes['cMentalHealthConditions'])
        self.p_mental_health_conditions.set_value(mental_health_conds)
        self.p_alcohol_consumption = PersonalAttribute(name='pAlcoholConsumption')
        self.p_alcohol_consumption.add_level2_attribute(reg_smoke_theory.level2_attributes['cAlcoholConsumption'])
        self.p_alcohol_consumption.add_level2_attribute(quit_success_theory.level2_attributes['cAlcoholConsumption'])
        self.p_alcohol_consumption.add_level2_attribute(quit_success_theory.level2_attributes['oAlcoholConsumption'])
        self.p_alcohol_consumption.set_value(alcohol)
        self.p_expenditure = PersonalAttribute(name='pExpenditure')
        self.p_expenditure.add_level2_attribute(quit_attempt_theory.level2_attributes['mSpendingOnCig'])
        self.p_expenditure.set_value(expenditure)
        self.p_nrt_use = PersonalAttribute(name='pNRTuse')
        self.p_nrt_use.add_level2_attribute(quit_success_theory.level2_attributes['cPrescriptionNRT'])
        self.p_nrt_use.add_level2_attribute(quit_attempt_theory.level2_attributes['mUseOfNRT'])
        self.p_nrt_use.set_value(nrt_use)
        self.p_varenicline_use = PersonalAttribute(name='pVareniclineUse')
        self.p_varenicline_use.add_level2_attribute(quit_success_theory.level2_attributes['cVareniclineUse'])
        self.p_varenicline_use.set_value(varenicline_use)
        self.p_cig_consumption_prequit = PersonalAttribute(name='pCigConsumptionPrequit')
        self.p_cig_consumption_prequit.add_level2_attribute(quit_success_theory.level2_attributes['cCigConsumptionPrequit'])
        self.p_cig_consumption_prequit.set_value(cig_consumption_prequit)
        self.p_ecig_use = PersonalAttribute(name='pECigUse')
        self.p_ecig_use.add_level2_attribute(reg_smoke_theory.level2_attributes['cEcigaretteUse'])
        self.p_ecig_use.add_level2_attribute(quit_success_theory.level2_attributes['cEcigaretteUse'])
        self.p_ecig_use.set_value(ecig_use)

        # pNumberOfRecentQuitAttempts is an imputed variable
        # (STPM does not have information on number of recent quit attempts)
        self.p_number_of_recent_quit_attempts = PersonalAttribute(name='pNumberOfRecentQuitAttempts')
        self.p_number_of_recent_quit_attempts.add_level2_attribute(
            quit_attempt_theory.level2_attributes['mNumberOfRecentQuitAttempts'])

        # list of states. states[t] is the agent's state at time step t (t=0,1,...,current time step) with
        # t=0 representing the beginning of the simulation.
        self.states = states
        self.init_behaviour_buffer_and_k_and_p_number_of_recent_quit_attempts()  # initialize:

        # behaviour buffer which stores the agent's behaviours (COMB and STPM behaviours) over the last 12 months
        # (13 ticks with each tick represents 4 weeks)
        # k: number of consecutive quit successes following the last quit attempt in the behaviourBuffer to end of the
        # behaviourBuffer pNumberOfRecentQuitAttempts

        self.p_years_since_quit = PersonalAttribute(
            # number of years since quit smoking for an ex-smoker, NA for quitter, never_smoker and smoker
            name='pYearsSinceQuit')
        self.p_years_since_quit.set_value(years_since_quit)
        self.tick_counter_ex_smoker = 0  # count number of consecutive ticks when the agent stays as an ex-smoker

    def init_behaviour_buffer_and_k_and_p_number_of_recent_quit_attempts(self):
        """
        The behaviour buffer stores the agent's behaviours (COMB and STPM behaviours) over the last 12 months
        (13 ticks with each tick represents 4 weeks)
        COMB behaviours: 'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure'
        STPM behaviours: 'relapse', 'no relapse'
        At each tick, the behaviour buffer (a list) stores one of the 8 behaviours:
        'uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure', 'relapse' and 'no relapse'
        (behaviours of a quitter over last 12 months (13 ticks):
            random behaviour (tick 1)..., random behaviour (tick i-1), quit attempt (tick i), quit success,..., quit success (tick 13)
            or
            random behaviour (tick 1),...,random behaviour (tick 12),quit attempt (tick 13))
        At tick 0, initialize the behaviour buffer of the agent to its historical behaviours as follows:
        or a quitter in the baseline population (i.e. at tick 0) {
            select a random index i of the buffer (0=< i =< 12);
            set the cell at i to 'quit attempt';
            set all the cells at i+1,i+2...,12 to 'quit success';
            set the cells at 0,...,i-1 to random behaviours;
        }
        for a non-quitter in the baseline population {
            set each cell of the behaviour buffer to a random behaviour;
        }
        k: count of number of consecutive quit successes done at the current state
        Initialize k to the number of consecutive quit successes following the last quit attempt in the behaviourBuffer
        to the end of the behaviourBuffer
        """

        behaviours = ['uptake', 'no uptake', 'quit attempt', 'no quit attempt', 'quit success', 'quit failure',
                      'relapse', 'no relapse']
        self.behaviour_buffer = [i for i in range(0, 13)]
        self.k = 0
        if self.states[0] == 'quitter':
            i = random.randint(0, 12)
            self.behaviour_buffer[i] = 'quit attempt'
            for j in range(i + 1, 13):
                self.behaviour_buffer[j] = 'quit success'
                self.k += 1
            for q in range(0, i):  # set random behaviours to indices: 0, 1,..., i-1
                self.behaviour_buffer[q] = behaviours[random.randint(0, len(behaviours) - 1)]
        elif self.states[0] == 'never_smoker':
            for i in range(0, 13):
                self.behaviour_buffer[i] = 'no uptake'
        elif self.states[0] == 'ex-smoker':
            for i in range(0, 13):
                self.behaviour_buffer[i] = 'no relapse'
        else:  # smoker
            for i in range(0, 13):
                self.behaviour_buffer[i] = behaviours[random.randint(0, len(behaviours) - 1)]
        self.p_number_of_recent_quit_attempts.set_value(self.behaviour_buffer.count('quit attempt'))

    def update_ec_ig_use(self, eciguse: int):
        self.ecig_use = eciguse

    def set_state_of_next_time_step(self, state=None):
        self.states.append(state)

    def get_current_state(self):  # get the agent's state at the current time step
        return self.states[self.smoking_model.current_time_step]

    def get_current_time_step(self):
        return self.smoking_model.current_time_step

    def increment_age(self):
        self.p_age.set_value(self.p_age.value + 1)
