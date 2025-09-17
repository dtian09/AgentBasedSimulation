'''
definition of Theory abstract class
'''
from abc import abstractmethod, ABC

class Theory(ABC):
    
    def __init__(self, name):
        self.name = name
        self.threshold = None
        self.prob_behaviour = None

    def name(self):
        return self.name

    @abstractmethod
    def do_situation(self, agent):
        pass

    @abstractmethod
    def do_action(self, agent):
        pass
