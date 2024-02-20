from typing import Set

from config.definitions import Theories
from config.definitions import AgentState
from mbssm.theory_mediator import TheoryMediator
from mbssm.theory import Theory
from mbssm.micro_agent import MicroAgent


class SmokingTheoryMediator(TheoryMediator):

    def __init__(self, theory_list: Set[Theory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0:
            raise Exception(f"{__class__.__name__} require a theoryList with length > 0")
        self.theory_map = {}
        for theory in theory_list:
            if not isinstance(theory.name, Theories):
                raise ValueError(f'{theory.name} must be an instance of the class Theories.')
            self.theory_map[theory.name] = theory

    def get_agent_current_theory(self, agent: MicroAgent) -> Theory:
        cstate = agent.get_current_state()
        if cstate == AgentState.NEVERSMOKE:
            return self.theory_map[Theories.REGSMOKE]
        elif cstate == AgentState.SMOKER:
            return self.theory_map[Theories.QUITATTEMPT]
        elif cstate == AgentState.QUITTER:
            return self.theory_map[Theories.QUITSUCCESS]
        elif cstate == AgentState.EXSMOKER:
            return self.theory_map[Theories.RELAPSESSTPM]
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')

    def mediate_situation(self, agent: MicroAgent):
        cstate = agent.get_current_state()
        if cstate == AgentState.NEVERSMOKE:
            self.theory_map[Theories.REGSMOKE].do_situation(agent)
        elif cstate == AgentState.SMOKER:
            self.theory_map[Theories.QUITATTEMPT].do_situation(agent)
        elif cstate == AgentState.QUITTER:
            self.theory_map[Theories.QUITSUCCESS].do_situation(agent)
        elif cstate == AgentState.EXSMOKER:
            self.theory_map[Theories.RELAPSESSTPM].do_situation(agent)
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')

    def mediate_action(self, agent: MicroAgent):
        """
        definition of quitting smoking: a smoker transitions to an ex-smoker (i.e. achieve success in quitting) after
        maintaining a quit attempt for 13 consecutive ticks (52 weeks i.e. 12 months).
        The sequence of the agent's behaviours when transitioning from smoker to ex-smoker:
            quit attempt (at t=i, i > 0, state=smoker), quit success (at t=i+1, state=quitter),...,
            quit success (at t=i+12, state=quitter), relapse or no relapse (at t=i+13, state=ex-smoker)
        pseudocode of state transition
        At tick t:
            for a quitter A, if k < 13, run the quit success theory to calculate the probability of maintaining a quit
                attempt; if p >= threshold {A stays as a quitter at t+1; k=k+1} else { A transitions to a smoker at t+1}
            for a quitter A, if k==13, run the quit success theory to calculate the probability of maintaining a quit
                attempt; if p >= threshold { A transitions to an ex-smoker at t+1; k=0;} else {A transitions to a smoker at t+1}
            for a smoker A, run the quit attempt theory to calculate the probability of making a quit attempt.
                If p >= threshold, { A transitions to a quitter at t+1; k=1;} else {A stays as a smoker at t+1}
            for a never smoker, run the regular smoking theory to calculate the probability of regular smoking;
                if p >= threshold {A transitions to a smoker at t+1} else { A stays as never smoker or ex-smoker at t+1}
            for an ex-smoker A, run relapse theory of STPM theory to calculate the probability of relapse;
                if p>= threshold {A transitions to a smoker at t+1} else { A stays as ex-smoker at t+1}
            where threshold is a pseudo-random number drawn from uniform(0,1) and p is the probability from the latent
            composite model.
        """
        cstate = agent.get_current_state()
        if cstate == AgentState.QUITTER:
            self.theory_map[Theories.QUITSUCCESS].do_action(agent)
        elif cstate == AgentState.SMOKER:
            self.theory_map[Theories.QUITATTEMPT].do_action(agent)
        elif cstate == AgentState.NEVERSMOKE:
            self.theory_map[Theories.REGSMOKE].do_action(agent)
        elif cstate == AgentState.EXSMOKER:
            self.theory_map[Theories.RELAPSESSTPM].do_action(agent)
        else:
            raise ValueError(f'{cstate} is not an acceptable agent state')
