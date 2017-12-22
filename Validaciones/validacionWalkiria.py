'''
Created on 28 nov. 2017

@author: curso
'''
import glob
from TleAdmin.TLE import SetTLE, Tle
from datetime import datetime

N_ID='32315'
tca0=datetime(2013,03,10)
tca1=datetime(2013,03,18)
set1=SetTLE(N_ID,tca0,tca1,'11308prueba1.tle')
set1.divide_setTLE()

tle_files=glob.glob('../TleAdmin/tle/*')

for tle in tle_files:
    tle_test=Tle.creadoxArchivo(tle)
    print tle_test.epoca()
