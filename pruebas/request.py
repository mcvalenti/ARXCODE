'''
Created on 30/01/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.get_tle import importar_tle

tca0=datetime(2012,8,13)
tca1=datetime(2012,8,14)
resultado=importar_tle('perro','gato','5258',tca0,tca1)
print resultado