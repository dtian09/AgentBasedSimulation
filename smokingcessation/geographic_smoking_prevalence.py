'''
definition of GeographicSmokingPrevalence class which is a subclass the MacroEntity class
'''
from mbssm.macro_entity import MacroEntity
from smokingcessation.smoking_model import SmokingModel
import pandas as pd
import sys
import ipdb #python debugger

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

    def getRegionalPrevalence(self,month,region):
        '''get the smoking prevalence of this region for this month
           input: month e.g. Nov-06
                  region e.g. 1
           
           map region numbers (used by ABM) to region names (used by regional smoking prevalence data file):
        '''
        hash_region={1: "North East",
                     2: "North West",
                     3: "Yorkshire and the Humber",
                     4: "East Midlands",
                     5: "West Midlands",
                     6: "East of England",
                     7: "London",
                     8: "South East",
                     9: "South West"}
       
        smokprev=self.smoking_model.regionalSmokingPrevalence[(self.smoking_model.regionalSmokingPrevalence['month']==month) &
                                                              (self.smoking_model.regionalSmokingPrevalence['region']==hash_region[region])]
        smokprev = pd.DataFrame(smokprev)
        #ipdb.set_trace()#debug break point
        if len(smokprev) > 0:
            col_index = smokprev.columns.get_loc('prevalence')
            return (float(smokprev.iat[0,col_index]))
        else:
            raise ValueError('smoking prevalence of '+hash_region[region]+' for '+month+' is not found in regionalSmokingPrevalence dataframe.')