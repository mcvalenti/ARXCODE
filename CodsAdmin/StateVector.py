'''
Created on 22/12/2016

@author: mcvalenti
'''

class StateVector:
    '''
    classdocs
    '''
    
    def __init__(self,linea):
        '''
        Constructor
        '''
        campo=linea.split()
        self.fecha=campo[0]
        self.hora=campo[1]
        self.x=campo[2]
        self.y=campo[3]
        self.z=campo[4]
        self.vx=campo[5]
        self.vy=campo[6]
        self.vz=campo[7]