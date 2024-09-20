from typing import List

from config.definitions import Theories
from config.definitions import AgentState
from mbssm.theory_mediator import TheoryMediator
from mbssm.theory import Theory
from mbssm.micro_agent import MicroAgent
from smokingcessation.person import Person

class SmokingTheoryMediator(TheoryMediator):

    def __init__(self, theory_list: List [Theory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0:
            raise Exception(f"{__class__.__name__} require a theoryList with length > 0")
        self.theory_map = {}
        for theory in theory_list:
            if not isinstance(theory.name, Theories):
                raise ValueError(f'{theory.name} must be an instance of the class Theories.')
            self.theory_map[theory.name] = theory
    '''
    def get_current_theory_of_agent(self, agent: MicroAgent) -> Theory:
        cstate = agent.get_current_state()
        if cstate == AgentState.NEVERSMOKE:
            return self.theory_map[Theories.REGSMOKE]
        elif cstate == AgentState.SMOKER:
            return self.theory_map[Theories.QUITATTEMPT]
        elif cstate == AgentState.NEWQUITTER:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER1:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER2:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER3:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER4:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER5:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER6:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER7:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER8:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER9:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER10:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.ONGOINGQUITTER11:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.EXSMOKER:
            return self.theory_map[Theories.RELAPSESSTPM]
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')
    '''
    def mediate_situation(self, agent: Person):
        cstate = agent.get_current_state()
        if cstate == AgentState.NEVERSMOKE:
            self.theory_map[Theories.REGSMOKE].do_situation(agent)
        elif cstate == AgentState.SMOKER:
            self.theory_map[Theories.QUITATTEMPT].do_situation(agent)        
        elif cstate == AgentState.NEWQUITTER:
            self.theory_map[Theories.QUITSUCCESS].do_situation(agent)
        elif cstate in (AgentState.ONGOINGQUITTER1,AgentState.ONGOINGQUITTER2,AgentState.ONGOINGQUITTER3,
                        AgentState.ONGOINGQUITTER4,AgentState.ONGOINGQUITTER5,AgentState.ONGOINGQUITTER6,
                        AgentState.ONGOINGQUITTER7,AgentState.ONGOINGQUITTER8,AgentState.ONGOINGQUITTER9,
                        AgentState.ONGOINGQUITTER10,AgentState.ONGOINGQUITTER11):
            self.theory_map[Theories.QUITSUCCESS].do_situation(agent)
        elif cstate == AgentState.EXSMOKER:
            self.theory_map[Theories.RELAPSESSTPM].do_situation(agent)
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')

    def mediate_action(self, agent: Person):
        """
        A smoker transitions to an ex-smoker after maintaining quit (abstinence) for 12 months.
        The sequence of the agent's behaviours when transitioning from smoker to ex-smoker:
            quit attempt (at t=i, i > 0, state=smoker), quit success (at t=i+1, state=quitter),...,
            quit success (at t=i+11, state=quitter), relapse or no relapse (at t=i+12, state=ex-smoker)
        pseudocode of state transition model:
        At tick t:
            for a never smoker, 
                run the regular smoking theory to calculate the probability p of regular smoking;
                if p >= threshold {A transitions to a smoker at t+1} else { A stays as never smoker or ex-smoker at t+1}
            for a smoker A, 
                run the quit attempt theory to calculate the probability of making a quit attempt.
                if p >= threshold, { A transitions to a new quitter at t+1; k=1;} else {A stays as a smoker at t+1}
            for a new quitter A,
                run the quit success theory to calculate the probability of maintaining abstinence; 
                if p >= threshold {A stays as an ongoing quitter1 at t+1; k=k+1} else { A transitions to a smoker at t+1}
            for an ongoing quitter1,
                 run the quit success theory to calculate the probability of maintaining abstinence;
                if p >= threshold { A transitions to an ongoing quitter2 at t+1; k=0;} else {A transitions to a smoker at t+1}
            ...
            for an ongoing quitter11,
                 run the quit success theory to calculate the probability of maintaining abstinence;
                 if p >= threshold { A transitions to an ex-smoker at t+1; k=0;} else {A transitions to a smoker at t+1}
            for an ex-smoker A, run relapse theory of STPM theory to calculate the probability of relapse;
                if p>= threshold {A transitions to a smoker at t+1} else { A stays as ex-smoker at t+1}
            where threshold is a pseudo-random number drawn from uniform(0,1)
        """
        cstate = agent.get_current_state()
        if cstate == AgentState.NEVERSMOKE:
            self.theory_map[Theories.REGSMOKE].do_action(agent)
        elif cstate == AgentState.SMOKER:
            self.theory_map[Theories.QUITATTEMPT].do_action(agent)
        elif cstate == AgentState.NEWQUITTER:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER1:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER2:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER3:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER4:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER5:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER6:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER7:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER8:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER9:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER10:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.ONGOINGQUITTER11:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.EXSMOKER:
            self.theory_map[Theories.RELAPSESSTPM].do_action(agent)
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')