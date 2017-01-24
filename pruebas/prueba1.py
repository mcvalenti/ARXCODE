'''
Created on 16/01/2017

@author: mcvalenti
'''
import ephem
from ephem import constellation

v=ephem.Saturn('2017')
    
print (constellation(v))