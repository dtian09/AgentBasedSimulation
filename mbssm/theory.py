from abc import abstractmethod, ABC


class Theory(ABC):
    
    def __init__(self):
        pass
    #     self.agent: MicroAgent = None
    #
    # def set_agent(self, agent: MicroAgent):
    #     self.agent = agent

    @abstractmethod
    def do_situation(self, agent):
        pass

    @abstractmethod
    def do_action(self, agent):
        pass
