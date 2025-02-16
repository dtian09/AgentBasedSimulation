from mbssm.macro_entity import Regulator, MacroEntity
from smokingcessation.smoking_model import SmokingModel
from config.definitions import eCigType

class GeographicSmokingPrevalenceRegulator(Regulator):
    def __init__(self, smoking_model : SmokingModel):
        super().__init__('GeographicSmokingPrevalenceRegulator')
        self.smoking_model=smoking_model
    
    def do_transformation(self, macro_entity: MacroEntity):
        pass

    def do_macro_macro(self, macro_entity: MacroEntity):
        macro_entity.readInAllPrevalenceOfMonth(self.smoking_model.formatted_month)