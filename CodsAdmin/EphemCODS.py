'''
Created on 17/03/2017

@author: mcvalenti
'''

class EphemCODS():
    '''
    Facilita la manipulacion de los datos CODS.
    '''


    def __init__(self, nombre_archivo):
        '''
        Constructor
        '''
        self.nombre_arch = nombre_archivo
        
    def parsea_epoca(self):
        campos      = self.nombre_arch.split('_')
        self.anio   = campos[1][0:4]
        self.mes    = campos[1][4:6]
        self.dia    = campos[1][6:8]
        self.hora   = campos[2][0:2]
        self.minu    = campos[2][2:4]
        self.seg    = campos[2][4:6]
        
        return self.anio, self.mes, self.dia, self.hora, self.minu, self.seg