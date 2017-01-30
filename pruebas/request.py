'''
Created on 30/01/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.get_tle import importar_tle

tca=datetime(2003,03,01,00,00,00)
importar_tle('37673',tca)
