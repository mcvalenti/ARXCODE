'''
Created on 30/01/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.get_tle import importarSetTLE

tca0=datetime(2012,7,1)
tca1=datetime(2012,7,25)
usuario='macecilia'
clave='MaCeciliaSpace17'
norad_id='37673'
resultado=importarSetTLE(usuario,clave,norad_id,tca0,tca1)
print resultado