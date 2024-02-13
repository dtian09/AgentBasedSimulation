from typing import List

from mbssm.theory_mediator import TheoryMediator
from smokingcessation.combined_theory import COMBTheory


class SmokingTheoryMediator(TheoryMediator):
        
    def __init__(self, theory_list: List[COMBTheory]):
        super().__init__(theory_list)
        if len(self.theory_list) == 0:
            raise Exception(f"{__class__.__name__} require a theoryList with length > 0")
        self.theory_map = {}
        for theory in theory_list:
            self.theory_map[theory.name] = theory

    def mediate_situation(self):
        if self.agent.getCurrentState() == 'never_smoker': 
           self.theory_map['regsmoketheory'].do_situation()
        elif self.agent.getCurrentState() == 'smoker': 
           self.theory_map['quitattempttheory'].do_situation()
        elif self.agent.getCurrentState() == 'quitter':
           self.theory_map['quitsuccesstheory'].do_situation()
        elif self.agent.getCurrentState() == 'ex-smoker':
            self.theory_map['relapseSTPMtheory'].do_situation()

    def mediate_action(self):
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
        if self.agent.getCurrentState() == 'quitter':
            self.theory_map['quitsuccesstheory'].do_action()
        elif self.agent.getCurrentState() == 'smoker':
            self.theory_map['quitattempttheory'].do_action()
        elif self.agent.getCurrentState() == 'never_smoker': 
            self.theory_map['regsmoketheory'].do_action()
        elif self.agent.getCurrentState() == 'ex-smoker':
            self.theory_map['relapseSTPMtheory'].do_action()
