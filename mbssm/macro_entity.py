'''
definition of MacroEntity class, RegulatorMediator and Regulator abstract classes
'''
from __future__ import annotations
from typing import List
from abc import abstractmethod, ABC

class MacroEntity():
    def __init__(self):
        self.macro_mediator = None

    def set_mediator(self, macro_mediator: RegulatorMediator):
        self.macro_mediator = macro_mediator
    
    def do_transformation(self):
        if self.macro_mediator is not None:
            self.macro_mediator.mediate_transformation(self)

    def do_macro_macro(self):
        if self.macro_mediator is not None:
            self.macro_mediator.mediate_macro_macro(self)

class RegulatorMediator(ABC):
    def __init__(self, regulator_list: List[Regulator]):
        self.regulator_list: List[Regulator] = regulator_list

    @abstractmethod
    def mediate_transformation(self):
        pass

    @abstractmethod
    def mediate_macro_macro(self):
        pass

class Regulator(ABC):
    def __init__(self, name):
        self.name = name
        self.macro_entity: MacroEntity = None
    
    def set_macro_entity(self, macro_entity: MacroEntity):
        self.macro_entity = macro_entity

    @abstractmethod
    def do_transformation(self, macro_entity: MacroEntity):
        pass

    @abstractmethod
    def do_macro_macro(self, macro_entity: MacroEntity):
        pass
