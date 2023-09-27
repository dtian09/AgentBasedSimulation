from __future__ import annotations
from typing import List
from .Regulator import Regulator
from .MacroMediator import MacroMediator

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