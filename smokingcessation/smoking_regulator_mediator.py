'''
defintion of the SmokingRegulatorMediator class which is a subclass of the RegulatorMediator abstract class.
This class is responsible for mediating the transformation and macro-macro mechanisms of the eCigDiffusion and GeographicSmokingPrevalence macro entities.
'''

from mbssm.macro_entity import MacroEntity, RegulatorMediator, Regulator
from typing import List
from smokingcessation.ecig_diffusion import eCigDiffusion
from smokingcessation.geographic_smoking_prevalence import GeographicSmokingPrevalence
from config.definitions import Regulators

class SmokingRegulatorMediator(RegulatorMediator):
    def __init__(self, regulator_list: List[Regulator]):
        super().__init__(regulator_list)
        if len(self.regulator_list) == 0:
            raise Exception(f"{__class__.__name__} require a regulator_list with length > 0")
        self.regulator_map = {}
        for regulator in regulator_list:
            if isinstance(regulator, Regulator):
                self.regulator_map[regulator.name] = regulator
            else:
                raise Exception(str(regulator)+' is not an instance of the class Regulator.')
            
    def mediate_transformation(self, macroEntity : MacroEntity):
        if isinstance(macroEntity, eCigDiffusion):
            self.regulator_map[Regulators.eCigDiffReg].do_transformation(macroEntity)
        elif isinstance(macroEntity, GeographicSmokingPrevalence):
            self.regulator_map[Regulators.geoSmokPrevReg].do_transformation(macroEntity)
        else:
            raise Exception('This macro entity is invalid.')
        
    def mediate_macro_macro(self, macroEntity : MacroEntity):
        if isinstance(macroEntity, eCigDiffusion):
            self.regulator_map[Regulators.eCigDiffReg].do_macro_macro(macroEntity)
        elif isinstance(macroEntity, GeographicSmokingPrevalence):
            self.regulator_map[Regulators.geoSmokPrevReg].do_macro_macro(macroEntity)
        else:
            raise Exception('This macro entity is invalid.')