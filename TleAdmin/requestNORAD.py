'''
Created on 13/02/2017

@author: mcvalenti
'''

from get_tle import importarSetTLE
from datetime import datetime

print 'Ingrese fecha de inicio, ej: 2017,5,2'
fecha0=raw_input()
fecha0=fecha0.split(',')
anio0=int(fecha0[0])
mes0=int(fecha0[1])
dia0=int(fecha0[2])
print 'Ingrese fecha defin, ej: 2017,5,2'
fecha1=raw_input()
fecha1=fecha1.split(',')
anio1=int(fecha1[0])
mes1=int(fecha1[1])
dia1=int(fecha1[2])
tca0=datetime(anio0,mes0,dia0)
tca1=datetime(anio1,mes1,dia1)
usuario='macecilia'
clave='MaCeciliaSpace17'
norad_id='37673'
resultado=importarSetTLE(usuario,clave,norad_id,tca0,tca1)
