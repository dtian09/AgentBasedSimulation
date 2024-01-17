from __future__ import annotations
from typing import List
from abc import abstractmethod, ABC
from .MicroAgent import MicroAgent

class MacroEntity():

    def __init__(self):
        self.macroMediator = None

    def setMediator(self, macromediator: MacroMediator):
        self.macroMediator = macromediator
    
    def doTransformation(self):
        if self.macroMediator is not None:
            self.macroMediator.mediateTransformation()

    def doMacroMacro(self):
        if self.macroMediator is not None:
            self.macroMediator.mediateMacroToMacro()

class MacroMediator(ABC):
    def __init__(self, regulatorList:List[Regulator]):
        self.regulatorList:List[Regulator] = regulatorList
        self.macroEntity:MacroEntity = None

    # link macro entity to this mediator and all regulators in the regulator list
    def setMacroEntity(self, macroEntity:MacroEntity):
        self.macroEntity = macroentity
        for regulator in self.regulatorList:
            regulator.setMacroEntity(macroEntity)

    @abstractmethod
    def mediateTransformation(self):
        pass

    @abstractmethod
    def mediateMacroToMacro(self):
        pass

class Regulator(ABC):

    def __init__(self):
        self.macroEntity: MacroEntity = None
    
    def setMacroEntity(self, macroEntity: MacroEntity):
        self.macroEntity=macroEntity

    @abstractmethod
    def doTransformation(self):
        pass

    @abstractmethod
    def doMacroToMacro(self):
        pass