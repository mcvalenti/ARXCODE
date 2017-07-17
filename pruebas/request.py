'''
Created on 30/01/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.TLE import SetTLE
from TleAdmin.requestNORAD import norad_id
norad_id='37673'
tca0=datetime(2012,7,1)
tca1=datetime(2012,7,25)
crudo='pepebotella'
SetTLE(norad_id,tca0,tca1,crudo)
