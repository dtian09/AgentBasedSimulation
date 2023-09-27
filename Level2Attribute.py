class Level2Attribute:
    def __init__(self,ontologyID:str=None):
        self.value=None
        self.ontologyID: str=ontologyID
    
    def setValue(self,value):
        self.value=value
    
    def getValue(self):
        return self.value

class Level2C(Level2Attribute):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class Level2O(Level2Attribute):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class Level2M(Level2Attribute):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

#Level2C attributes
class EducationalLevel(Level2C,Level2O):
    def __init__(self,ontologyID:str=None):
        Level2Attribute.__init__(ontologyID)

class Age(Level2C,Level2O,Level2M):
    def __init__(self,ontologyID:str=None):
        Level2Attribute.__init__(ontologyID)

class cCigAddictionStrength(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cPsychoactiveSubstanceUse(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cEcigUse(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cImpulsivity(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cMentalHealthConditions(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cAlcoholConsumption(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cUnderstandingOfSmokingHarms(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cPrescriptionNRT(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cUseOfBehaviouralSupport(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cCigConsumptionPrequit(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cNoOfRecentQuitAttempts(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class cVareniclineUse(Level2C):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

#Level2O attributes
class oEaseOfAccess(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oPercentOfPeerSmokersInSocialNetwork(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oPrevalenceOfSmokingInGeographicLocality(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oSmokingCessationPromptsOrTriggers(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oNoOfSmokersInSocialNetwork(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oSocialHousing(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oEducationalLevel(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oExpenditurePerStick(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class oParentalSmoking(Level2O):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

#Level2M attributes
class mEnjoymentOfSmoking(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mMentalHealthConditions(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mUseOfNRT(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mSpendOnCig(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mIntentToQuit(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mProsmokingAttitude(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mSelfEfficacy(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mSmokerIdentity(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mExsmokerSelfIdentity(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mNoOfRecentQuitAttempts(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mDesireToStopSmoking(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mAge(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)

class mExpenditurePerStick(Level2M):
    def __init__(self,ontologyID:str=None):
        super().__init__(ontologyID)






