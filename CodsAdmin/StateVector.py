'''
Created on 22/12/2016

@author: mcvalenti
'''

class StateVector:
    '''
    classdocs
    '''
    
    def __init__(self, arch):
        '''
        Constructor
        '''
        self.efem=open(arch,'r').readline()
        self.datos=self.efem.split(' ')
        self.fecha=self.datos[0]
        self.hora=self.datos[1]