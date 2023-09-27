class Level1Attribute:
    def __init__(self,ontologyID:str=None):
        self.value: float=None
        self.ontologyID: str=ontologyID
    
    def setValue(self,value:float):
        self.value=value
    
    def getValue(self):
        return self.value
    
class CompositeC(Level1Attribute):
    def __init__(self, ontologyID: str = None):
        super().__init__(ontologyID)
    
class CompositeO(Level1Attribute):
    def __init__(self, ontologYID: str=None):
        super().__init__(ontologYID)

class CompositeM(Level1Attribute):
    def __init__(self,ontologYID: str = None):
        super().__init__(ontologYID)
