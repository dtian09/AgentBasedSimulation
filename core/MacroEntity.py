from __future__ import annotations
from typing import List
from abc import abstractmethod, ABC
from .MicroAgent import MicroAgent

class MacroEntity():

    def __init__(self):
        self.macromediator = None

    def set_mediator(self, macromediator: MacroMediator):
        self.macromediator = macromediator
    
    def do_transformation(self):
        if self.macromediator is not None:
            self.macromediator.mediate_transformation()

    def do_macro_macro(self):
        if self.macromediator is not None:
            self.macromediator.mediate_macro_to_macro()

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

class Regulator(ABC):

    def __init__(self):
        self.macroentity: MacroEntity = None
    
    def set_macroentity(self, macroentity: MacroEntity):
        self.macroentity=macroentity

    @abstractmethod
    def do_transformation(self):
        pass

    @abstractmethod
    def do_macro_to_macro(self):
        pass