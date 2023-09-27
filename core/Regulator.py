from __future__ import annotations
from abc import abstractmethod, ABC
from .MacroEntity import MacroEntity

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