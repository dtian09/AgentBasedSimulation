#check the type of each element of a list is the specified class. If any element is not the specifed class e.g. Level2C, raise exception and exit system
from Level2Attribute import * 

def check_list_of_Level2C(test_list):
    c=0
    indxL_notLevel2C=[]
    for i in range(len(test_list)):
        if isinstance(test_list[i],Level2C):
            c+=1
        else:
            indxL_notLevel2C.append(i)
    if(c==len(test_list)):
        return True 
    else:
        print('indices of elements which are not Level2C attributes',indxL_notLevel2C)
        import sys
        sys.exit(-1)

def check_list_of_Level2O(test_list):
    c=0
    indxL_notLevel2O=[]
    for i in range(len(test_list)):
        if isinstance(test_list[i],Level2O):
            c+=1
        else:
            indxL_notLevel2O.append(i)
    if(c==len(test_list)):
        return True
    else:
        print('indices of elements which are not Level2O attributes',indxL_notLevel2O)
        import sys
        sys.exit(-1)

def check_list_of_Level2M(test_list):
    c=0
    indxL_notLevel2M=[]
    for i in range(len(test_list)):
        if isinstance(test_list[i],Level2M):
            c+=1
        else:
            indxL_notLevel2M.append(i)
    if(c==len(test_list)):
        return True 
    else:
        print('indices of elements which are not Level2O attributes',indxL_notLevel2M)
        import sys
        sys.exit(-1)

#test_list = [cAge('id0'), cEcigUse('id1'), oAge('id2')]
e=oEaseOfAccess('is0')
e.setValue(1)
a=oAge('id1')
a.setValue(30)
test_list=[e,a]
test_list=[mEnjoymentOfSmoking('id1'),mUseOfNRT('id0')]

print(check_list_of_Level2C(test_list))
