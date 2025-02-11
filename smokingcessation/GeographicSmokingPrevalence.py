
from mbssm.macro_entity import MacroEntity
from smokingcessation.smoking_model import SmokingModel
from smokingcessation.person import Person
import numpy as np
import random
import sys

class GeographicSmokingPrevalence(MacroEntity):
    def __init__(self, smoking_model : SmokingModel):
        super().__init__()
        self.regionalSmokingPrevalence=None #dataframe that contains the regional smoking prevalence of a specific month
        self.smoking_model = smoking_model

    def readInAllPrevalence(self,month):#read all the regional prevalences of this month into regionalSmokingPrevalence dataframe
        allprev=self.smoking_model.regionalSmokingPrevalence[self.smoking_model.regionalSmokingPrevalence['month']==month]
        if len(allprev) > 0:
            self.regionalSmokingPrevalence=allprev[['month','region','prevalence']]
        else:
            sys.exit('Smoking prevalences of regions for month: '+month+' are not found.')

    def getRegionalPrevalence(self,month,region):#get the smoking prevalence of this region for this month
        smokprev=self.smoking_model.regionalSmokingPrevalence[self.smoking_model.regionalSmokingPrevalence['month']==month &
                                                              self.smoking_model.regionalSmokingPrevalence['region']==region]
        if len(smokprev) > 0:
            return (float(smokprev.at[0,'prevalence']))
        else:
            sys.exit('smoking prevalence of '+region+' for '+month+' is not found in regionalSmokingPrevalence dataframe.')