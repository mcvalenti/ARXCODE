'''
Created on 17 nov. 2017

@author: curso
'''

class BaseClass(object):
    '''
    classdocs
    '''


    def __init__(self, p1, p2):
        '''
        Constructor
        '''
        print(p1, p2)


class HClass(BaseClass):
    
    def __init__(self, **kwargs):
        BaseClass.__init__(self, kwargs["p1"],  kwargs["p2"])
        print("HCLASS", kwargs)
        

hc = HClass(p1=1, p2=2)

        
        
            