
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

    def readInAllPrevalenceOfMonth(self,month):#read all the regional prevalences of this month into regionalSmokingPrevalence dataframe
        #format of month: Nov-06, Dec-10 etc.
        allprev=self.smoking_model.regionalSmokingPrevalence[self.smoking_model.regionalSmokingPrevalence['month']==month]
        if len(allprev) > 0:
            self.regionalSmokingPrevalence=allprev[['month','region','prevalence']]
        else:
            sys.exit('Smoking prevalences of regions for month: '+month+' are not found.')

    def getRegionalPrevalence(self,month,region):#get the smoking prevalence of this region for this month
        #format of month: Nov-06, Dec-10 etc.
        #format of region:
        #1 = North East
        #2 = North West
        #3 = Yorkshire and The Humber
        #4 = East Midlands
        #5 = West Midlands
        #6 = East of England
        #7 = London
        #8 = South East
        #9 = South West
        smokprev=self.smoking_model.regionalSmokingPrevalence[self.smoking_model.regionalSmokingPrevalence['month']==month &
                                                              self.smoking_model.regionalSmokingPrevalence['region']==region]
        if len(smokprev) > 0:
            return (float(smokprev.at[0,'prevalence']))
        else:
            sys.exit('smoking prevalence of '+region+' for '+month+' is not found in regionalSmokingPrevalence dataframe.')