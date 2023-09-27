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
    '''
    def save(self):
        """ Save the state of this MicroAgent as a Tuple.
        
        Used to move MicroAgents between Ranks in Repast4py.
        This is analogous to AgentPackage::serialize int he RepastHPC implementation

        Returns:
            The saved state of this MicroAgent
        """
        return (self.id, self.mediator)
    '''
'''
def restore_agent(agent_data:Tuple):

    """ 
    Repast4py uses save() and restore_agent to migrate agents between ranks.
    The MBSSM core is only implemented for single-rank simulations, i.e. this method is not implemented.
    """
    raise NotImplementedError
'''
# Include this at the end of the file to avoid circular import
from .TheoryMediator import TheoryMediator
