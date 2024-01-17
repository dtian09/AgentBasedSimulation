from abc import abstractmethod, ABC
from .MicroAgent import MicroAgent

class Theory(ABC):
    
    def __init__(self):
        self.agent: MicroAgent = None

    def setAgent(self, agent:MicroAgent):
        self.agent = agent

    @abstractmethod
    def doSituation(self):
        pass

    @abstractmethod
    def doAction(self):
        pass