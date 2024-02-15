from abc import abstractmethod, ABC


class Theory(ABC):
    
    def __init__(self, name):
        self.name = name

        self.threshold = None
        self.prob_behaviour = None
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

    def theory_info(self):
        res = ['probability of behaviour: ' + str(self.prob_behaviour) + '\n',
               'threshold: ' + str(self.threshold) + '\n']
        return res
