'''
Created on 30/05/2017

@author: mcvalenti
'''

from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4
from sgp4.ext import days2mdhms
from sgp4.ext import jday
from datetime import datetime

linea1='1 15482U 85006A   07356.79571087 +.00000049 +00000-0 +27601-4 0  9997'
linea2='2 15482 074.0426 280.5566 0014149 010.5281 349.6172 14.32296840197528'

whichconst = wgs72
satrec = twoline2rv(linea1, linea2, whichconst)

fecha1=datetime(2007,12,21,15,21,38,9)
fecha2=datetime(2007,12,23,14,35,36,5)
minutes=(fecha2-fecha1).total_seconds()/60

r,v=sgp4(satrec, minutes)

print r
print v
