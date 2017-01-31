'''
Created on 30/01/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.get_tle import importar_tle

tca0=datetime(2003,03,01)
tca1=datetime(2003,03,03)
importar_tle('37673',tca0,tca1)
