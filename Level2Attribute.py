from abc import abstractmethod, ABC
from typing import List
    
class Level2Attribute(ABC):
    def __init__(self,ontologyID:str=None,name : str=None):
        self.ontologyID: str=ontologyID
        self.name : str = name
 
    @abstractmethod
    def setValue(self,value):
        self.value=value
    
    @abstractmethod
    def getValue(self):
        return self.value

class Level2AttributeInt(Level2Attribute):
    def __init__(self,ontologyID:str=None, name : str=None, value : int =None):
        super().__init__(ontologyID,name)
        self._value:int=value
        
    def setValue(self,value:int):
        self._value=value
    
    def getValue(self):
        return self._value

class Level2AttributeFloat(Level2Attribute):
    def __init__(self,ontologyID:str=None, name : str=None, value : float =None):
        super().__init__(ontologyID,name)
        self._value:float=value
        
    def setValue(self,value:float):
        self._value=value
    
    def getValue(self):
        return self._value

class Level1Attribute:
    def __init__(self, ontologyID:str=None, name : str=None):
        self.value: float=None
        self.ontologyID: str=ontologyID
        self.name : str = name
        self.list : List[Level2Attribute] = []
        self.value = None

    def addLevel2Attribute(self,attr : Level2Attribute):
        self.list.append(attr)

    def setValue(self,value:float):
        self.value=value
    
    def getValue(self):
        return self.value
    
class PersonalAttribute():
    def __init__(self,ontologyID:str=None, name : str=None):
        self.ontologyID: str=ontologyID
        self.name : str = name 
        self.list : List[Level2Attribute] = [] #list of the associated level 2 attributes
        self.value=None
    
    def addLevel2Attribute(self,attr : Level2Attribute):
        self.list.append(attr)

    def setValue(self,value):
        self.value=value
        if len(self.list)>0:
            for i in range(len(self.list)):
                self.list[i].setValue(self.value)

    def getValue(self):
        return self.value
            
if __name__ == '__main__':
    o=Level2AttributeInt(name='oAge')
    o2=Level2AttributeInt(name='cAge')
    o3=Level2AttributeInt(name='mAge')
    dict={}
    dict['oAge']=o
    dict['cAge']=o2
    dict['mAge']=o3
    p=PersonalAttribute(name='pAge')
    p.addLevel2Attribute(o)
    p.addLevel2Attribute(o2)
    p.addLevel2Attribute(o3)
    print('list')
    for i in range(3):
        print(p.l2att[i].getValue())
    print('dict')
    for key in ['oAge','cAge','mAge']:
        print(dict[key].getValue())
    p.setValue(65)
    print('##########')
    print('list')
    for i in range(3):
        print(p.l2att[i].getValue())
    print('dict')
    for key in ['oAge','cAge','mAge']:
        print(dict[key].getValue())
    


