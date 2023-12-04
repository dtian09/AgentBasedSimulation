from __future__ import annotations
#from typing import Tuple
#from repast4py import core
import repast4py

class MicroAgent(repast4py.core.Agent):

    def __init__(self, id: int, rank:int, type:int = None):
        super().__init__(id=id, type=type, rank=rank)
        # self.id is the id from the rank on which it was generated
        # self.type is the integer type of the agent within the simulation. I..e MicroAgent.TYPE, which should be distinct from a DerivedMicroAgent.TYPE.
        # self.rank is the rank from which this agent was generated
        # self.uid is the unique 3-tuple of (id, type, rank)
        self.mediator = None

    def get_id(self):
        return self.id

    def set(self, current_rank):
        self.rank = current_rank
        pass

    def set_mediator(self, mediator: TheoryMediator):
        self.mediator = mediator
    
    def do_situation(self):
        if self.mediator is not None:
            self.mediator.mediate_situation()

    def do_action(self):
        if self.mediator is not None:
            self.mediator.mediate_action()

# Include this at the end of the file to avoid circular import
from .TheoryMediator import TheoryMediator
