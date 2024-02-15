from __future__ import annotations
import repast4py

from mbssm.theory_mediator import TheoryMediator


class MicroAgent(repast4py.core.Agent):

    def __init__(self, id: int, rank: int, type: int = None):
        """
        :param id: is the id from the rank on which it was generated
        :param rank: is the rank from which this agent was generated
        :param type: is the integer type of the agent within the simulation. i.e., MicroAgent.TYPE,
                     which should be distinct from a DerivedMicroAgent.TYPE.
        """
        super().__init__(id=id, type=type, rank=rank)

        self.mediator = None
        self.rank = None

    def get_id(self):
        return self.id

    def set(self, current_rank):
        self.rank = current_rank
        pass

    def set_mediator(self, mediator: TheoryMediator):
        self.mediator = mediator

    def get_mediator(self) -> TheoryMediator:
        return self.mediator

    def do_situation(self):
        if self.mediator is not None:
            self.mediator.mediate_situation(self)

    def do_action(self):
        if self.mediator is not None:
            self.mediator.mediate_action(self)
