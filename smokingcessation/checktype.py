#check the type of each element of a list is the specified class. If any element is not the specifed class e.g. Level2C, raise exception and exit system
from attribute import *


def check_list_of_level2_c(test_list):
    c = 0
    indx_l_not_level2_c = []
    for i in range(len(test_list)):
        if isinstance(test_list[i], Level2C):
            c += 1
        else:
            indx_l_not_level2_c.append(i)
    if c == len(test_list):
        return True 
    else:
        print('indices of elements which are not Level2C attributes', indx_l_not_level2_c)
        import sys
        sys.exit(-1)


def check_list_of_level2_o(test_list):
    c = 0
    indx_l_not_level2_o = []
    for i in range(len(test_list)):
        if isinstance(test_list[i], Level2O):
            c += 1
        else:
            indx_l_not_level2_o.append(i)
    if c == len(test_list):
        return True
    else:
        print('indices of elements which are not Level2O attributes', indx_l_not_level2_o)
        import sys
        sys.exit(-1)


def check_list_of_level2_m(test_list):
    c = 0
    indx_l_not_level2_m = []
    for i in range(len(test_list)):
        if isinstance(test_list[i], Level2M):
            c += 1
        else:
            indx_l_not_level2_m.append(i)
    if c == len(test_list):
        return True 
    else:
        print('indices of elements which are not Level2O attributes', indx_l_not_level2_m)
        import sys
        sys.exit(-1)
