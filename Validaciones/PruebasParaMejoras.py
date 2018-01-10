'''
Created on 20/10/2017
----------------------------------------------------
A partir de una lista de NORAD ID.
El codigo se trae un TLE de Space-track y verifica
si el satelite en cuestion es LEO o DEEP SPACE
----------------------------------------------------
@author: mcvalenti
'''

from datetime import datetime
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle

object_list=['25415','31445','20737','20738','27939','31588','11308','32315','17583']
epocaf=datetime(2013,03,15)
whichconst = wgs84
        
for sat_id in object_list:
    tle=Tle.creadoxParam(sat_id, epocaf)   
    satrec = twoline2rv(tle.linea1,tle.linea2, whichconst)
    if (satrec.a-1.0)*6378 < 5877.5:
        print 'LEO satellte: ',(satrec.a-1.0)*6378
    else:
        print 'DEEP SPACE OBJECT: ',(satrec.a-1.0)*6378
