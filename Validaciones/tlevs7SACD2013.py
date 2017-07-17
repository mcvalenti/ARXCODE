'''
Created on 17/07/2017

@author: mcvalenti
'''

import glob
from datetime import datetime, timedelta
from TleAdmin.TLE import Tle,SetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle

sat_id='37673'
ini_epoca=datetime(2013,1,1)
fin_epoca=datetime(2013,5,20)
crudo='37673_6meses.setTle'

set_sat=SetTLE(sat_id,ini_epoca,fin_epoca,crudo)
set_sat.divide_setTLE()

lista_tle=glob.glob('../TleAdmin/tle/*')
cant_tle=len(lista_tle)
dic_tle=generadorDatos(lista_tle) # genera un diccionario con las fechas
tle_ordenados=ordenaTles(dic_tle)

salida=open('../Validaciones/37673_xyz_6meses.val','w+')

for j in range(cant_tle):
    tle=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[j][0])
    ini_prop=datetime(tle.epoca().year,tle.epoca().month,tle.epoca().day,0,0,0)
    fin_prop=datetime(tle.epoca().year,tle.epoca().month,tle.epoca().day,23,59,59)
    while ini_prop <= fin_prop:
        r,v=tle.propagaTLE(ini_prop)
        ephem=ini_prop.strftime('%Y-%m-%d %H:%M:%s')+'\n'
        salida.write(ephem)
        ini_prop=ini_prop+timedelta(minutes=1)
    
