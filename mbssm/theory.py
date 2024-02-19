from abc import abstractmethod, ABC


class Theory(ABC):
    
    def __init__(self, name):
        self.name = name
        self.threshold = None
        self.prob_behaviour = None

    @abstractmethod
    def do_situation(self, agent):
        pass

    @abstractmethod
    def do_action(self, agent):
        pass
