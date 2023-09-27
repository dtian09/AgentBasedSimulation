from typing import List
from abc import abstractmethod, ABC
from .MacroEntity import MacroEntity
from .Regulator import Regulator

class MacroMediator(ABC):
    def __init__(self, regulator_list:List[Regulator]):
        self.regulator_list:List[Regulator] = regulator_list
        self.macroentity:MacroEntity = None

    # link macro entity to this mediator and all regulators in the regulator list
    def set_macro_entity(self, macroentity:MacroEntity):
        self.macroentity = macroentity
        for regulator in self.regulator_list:
            regulator.set_macroentity(macroentity)

    @abstractmethod
    def mediate_transformation(self):
        pass

    @abstractmethod
    def mediate_macro_to_macro(self):
        pass
