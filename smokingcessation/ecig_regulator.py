'''
definition of eCigDiffusionRegulator class that is a subclass of Regulator abstract class.
'''

from mbssm.macro_entity import Regulator, MacroEntity
from smokingcessation.smoking_model import SmokingModel
from config.definitions import eCigType, Regulators

class eCigDiffusionRegulator(Regulator):
    def __init__(self, smoking_model : SmokingModel):
        super().__init__(Regulators.eCigDiffReg)#name of the e-cigarette regulator
        self.smoking_model=smoking_model
    
    def do_transformation(self, macro_entity: MacroEntity):
        macro_entity.calculate_Et()

    def do_macro_macro(self, macro_entity: MacroEntity):
        if macro_entity.ecig_type == eCigType.Nondisp:
            macro_entity.changeInE(self.smoking_model.current_time_step_of_non_disp_diffusions)
        else:
            macro_entity.changeInE(self.smoking_model.current_time_step_of_disp_diffusions)
 