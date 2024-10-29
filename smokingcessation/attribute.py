from abc import abstractmethod, ABC
from typing import List


class Level2Attribute(ABC):

    def __init__(self, ontology_id: str = None, name: str = None):
        self.ontology_id: str = ontology_id
        self.name: str = name
        self.value = None
 
    @abstractmethod
    def set_value(self, value):
        self.value = value
    
    @abstractmethod
    def get_value(self):
        return self.value


class Level2AttributeInt(Level2Attribute):

    def __init__(self, ontology_id: str = None, name: str = None, value: int = None):
        super().__init__(ontology_id, name)
        self._value: int = value
        
    def set_value(self, value: int):
        self._value = value
    
    def get_value(self):
        return self._value


class Level2AttributeFloat(Level2Attribute):

    def __init__(self, ontology_id: str = None, name: str = None, value: float = None):
        super().__init__(ontology_id, name)
        self._value: float = value
        
    def set_value(self, value: float):
        self._value = value
    
    def get_value(self):
        return self._value


class Level1Attribute:

    def __init__(self, ontology_id: str = None, name: str = None):
        self.value: float = None
        self.ontology_id: str = ontology_id
        self.name: str = name
        self.list: List[Level2Attribute] = []
        self.value = None

    def add_level2_attribute(self, attr: Level2Attribute):
        self.list.append(attr)

    def set_value(self, value: float):
        self.value = value
    
    def get_value(self):
        return self.value


class PersonalAttribute:

    def __init__(self, ontology_id: str = None, name: str = None):
        self.ontology_id: str = ontology_id
        self.name: str = name
        self.list: List[Level2Attribute] = []  # list of the associated level 2 attributes
        self.value = None
    
    def add_level2_attribute(self, attr: Level2Attribute):
        self.list.append(attr)

    def set_value(self, value):
        self.value = value
        if len(self.list) > 0:
            for i in range(len(self.list)):
                self.list[i].set_value(self.value)

    def get_value(self):
        return self.value


if __name__ == '__main__':

    o = Level2AttributeInt(name='o_age')
    o2 = Level2AttributeInt(name='c_age')
    o3 = Level2AttributeInt(name='m_age')
    mydict = {'o_age': o, 'c_age': o2, 'm_age': o3}
    p = PersonalAttribute(name='p_age')
    p.add_level2_attribute(o)
    p.add_level2_attribute(o2)
    p.add_level2_attribute(o3)
    print('list')
    for i in range(3):
        print(p.l2att[i].get_value())
    print('dict')
    for key in ['o_age', 'c_age', 'm_age']:
        print(mydict[key].get_value())
    p.set_value(65)
    print('##########')
    print('list')
    for i in range(3):
        print(p.l2att[i].get_value())
    print('dict')
    for key in ['o_age', 'c_age', 'm_age']:
        print(mydict[key].get_value())
