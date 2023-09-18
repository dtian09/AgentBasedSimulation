from abc import abstractmethod, ABCMeta
from .MicroAgent import MicroAgent

class Theory(metaclass=ABCMeta):
    
    def __init__(self):
        self.agent: MicroAgent = None

    def set_agent(self, agent:MicroAgent):
        self.agent = agent

    @abstractmethod
    def do_situation(self):
        pass

    @abstractmethod
    def do_action(self):
        pass