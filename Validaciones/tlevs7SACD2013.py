'''
Created on 17/07/2017

@author: mcvalenti
'''

import glob
import numpy as np
import progressbar
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

# n=0
# with progressbar.ProgressBar(max_value=cant_tle) as progress:
#     for j in range(cant_tle):
#         #==============
#         sleep(0.1)
#         progress.update(n)
#         n=n+1
#         #==============
#         tle=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[j][0])
#         fecha_archivo=tle.epoca().strftime('%Y_%m_%d')
#         salida=open('../Validaciones/37673_xyz_'+fecha_archivo,'w+')
#         ini_prop=datetime(tle.epoca().year,tle.epoca().month,tle.epoca().day,0,0,0)
#         fin_prop=datetime(tle.epoca().year,tle.epoca().month,tle.epoca().day,23,59,59)
#         while ini_prop <= fin_prop:
#             r,v=tle.propagaTLE(ini_prop)
#             ephem=ini_prop.strftime('%Y-%m-%d %H:%M:%s')+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])+'\n'
#             salida.write(ephem)
#             ini_prop=ini_prop+timedelta(minutes=1)
#


n=0
with progressbar.ProgressBar(max_value=cant_tle*7*1440) as progress:
    #==============
    progress.update(n)
    n=n+1
    #==============             
    for k in range(cant_tle):
        dia_n=1
        while dia_n <=7:
            # Instancio el TLE
            tle0=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[k][0])
            dia_prop=tle0.epoca()+timedelta(days=dia_n)
            ini_prop=datetime(dia_prop.year,dia_prop.month,dia_prop.day,0,0,0)
            fin_prop=datetime(dia_prop.year,dia_prop.month,dia_prop.day,23,59,59)
            dia=dia_prop.strftime('%Y_%m_%d')
            # Abro el archivo donde busco para comparar
            nombre_archivo='../Validaciones/tle/37673_xyz_'+dia
            lista_archivos = glob.glob('../Validaciones/tle/*')
            if nombre_archivo in lista_archivos:
                archivo_tle=open('../Validaciones/tle/37673_xyz_'+dia,'r')
                contenido=archivo_tle.readlines()
                archivo_diferencias=open('../Validaciones/tle/37673_xyz_'+dia+'_'+str(dia_n),'w+')
                while ini_prop <= fin_prop:
                    r,v=tle0.propagaTLE(ini_prop)
                    for c in contenido:
                        campos=c.split()
                        if campos[0]+' '+campos[1] == ini_prop.strftime('%Y-%m-%d %H:%M:%s'):
                            r_a=np.array([float(campos[2]),float(campos[3]),float(campos[4])])
                            dif=r-r_a
                            info=ini_prop.strftime('%Y-%m-%d %H:%M:%s')+' '+str(dif[0])+' '+str(dif[1])+' '+str(dif[2])+'\n'
                            archivo_diferencias.write
                    ini_prop=ini_prop + timedelta(minutes=1)
                    progress.update(n)
                    n=n+1
                dia_n = dia_n +1  
            else:         
                dia_n = dia_n +1    
    
        
        
    
