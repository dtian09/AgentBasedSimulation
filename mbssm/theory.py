from abc import abstractmethod, ABC

from mbssm.micro_agent import MicroAgent


class Theory(ABC):
    
    def __init__(self):
        self.agent: MicroAgent = None

    def set_agent(self, agent: MicroAgent):
        self.agent = agent

    @abstractmethod
    def do_situation(self):
        pass

    @abstractmethod
    def do_action(self):
        pass
