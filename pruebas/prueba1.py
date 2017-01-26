'''
Created on 16/01/2017

@author: mcvalenti
'''
import os,ephem, glob
from ephem import constellation
from funcionesUtiles.funciones import ensure_dir
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import tle_info


d1='../TleAdmin/tle'
if not os.path.exists(d1):
    os.mkdir(d1)

setTLE('8820', '8820_escenario11')

listaTle=glob.glob('../TleAdmin/tle/*')

for l in listaTle:
    t=tle_info(l)
    r,v=t.propagaTLE()
    print t.epoca(),r,v