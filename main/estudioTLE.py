'''
Created on 12/06/2017
Voy a generar un crudo TLE con tles para el 1 de los meses de
Febrero, Abril, Junio, Agosto y Octubre del anio 2013.
Luego voy a propagar cada TLE por 3 dias (c/1seg) y comparar los resultados con 
los valores que ofrece cods. 
@author: mcvalenti
'''
import os, glob
import numpy as np
from datetime import datetime, timedelta
from TleAdmin.TleArchivos import setTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from pruebas.claseTle import Tle
from CodsAdmin.EphemCODS import EphemCODS
from SistReferencia.sist_deCoordenadas import teme2tod, vncSis

"""
Evaluo los TLE
"""
setTLE('37673', 'estudioTLE')
files=glob.glob('../TleAdmin/tle/*') 
dic_tle=generadorDatos(files)
ordenaTles(dic_tle)

"""
TLE JUNIO.
"""
print '*******************************'
print 'JUNIO'
print '*******************************'
tle_junio=Tle.creadoxArchivo('../TleAdmin/tle/37673tle4')
epoca_tlejunio=tle_junio.epoca()
y=epoca_tlejunio.year
mes=epoca_tlejunio.month
dia=epoca_tlejunio.day
hora=epoca_tlejunio.hour
minu=epoca_tlejunio.minute
seg=epoca_tlejunio.second
epoca_tlejunio=datetime(y,mes,1,0,0,0)
epoca_tlejunio3dias=epoca_tlejunio+timedelta(days=1) #(days=3)
print 'Epoca de Inicio = ', epoca_tlejunio
print 'Epoca de Fin = ', epoca_tlejunio3dias
"""
CODS - JUNIO
"""
#    archivo='CODS_20130605_135834_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
archivo='CODS_20130602_135850_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
ephem=EphemCODS('../CodsAdmin/sacDdensos/'+archivo)   
ephem_dic=ephem.genera_diccionario()



dif_r=[]
dif_v=[]
dif_n=[]
dif_c=[]

while epoca_tlejunio < epoca_tlejunio3dias:
    #propago
    r,v = tle_junio.propagaTLE(epoca_tlejunio)
    r_tod = teme2tod(epoca_tlejunio,r)
    
    #extraigo datos cods
    x=ephem_dic[epoca_tlejunio]['x']
    y=ephem_dic[epoca_tlejunio]['y']
    z=ephem_dic[epoca_tlejunio]['z']# 2013/06/04 03:10:54.00000000     655.253437     820.449815    6944.267558   7.1657472983  -2.2836022683  -0.4051912848
    vx=ephem_dic[epoca_tlejunio]['vx']
    vy=ephem_dic[epoca_tlejunio]['vy']
    vz=ephem_dic[epoca_tlejunio]['vz']
    r_cods=np.array([float(x),float(y),float(z)])
    v_cods=np.array([float(vx),float(vy),float(vz)])

    resta=r_cods[0]-r_tod.item(0),r_cods[1]-r_tod.item(1),r_cods[2]-r_tod.item(2)
    v,n,c=vncSis(r_cods,v_cods,resta)
    
    dif_r.append(resta)
    dif_v.append(v)
    dif_n.append(n)
    dif_c.append(c)
    
    epoca_tlejunio=epoca_tlejunio+timedelta(seconds=1)

print 'Promedio de dv = ', np.mean(dif_v), np.var(dif_v)
print 'Promedio de dn = ', np.mean(dif_n), np.var(dif_n)
print 'Promedio de dc = ', np.mean(dif_c), np.var(dif_c)















"""
Evaluo los datos CODS
"""
# files_cods=glob.glob('../CodsAdmin/sacDdensos/*')
# 
# for f in files_cods:
#     efemerides = EphemCODS(f)
#     anio, mes, dia, hora, minu, seg= efemerides.parsea_epoca_nombre()
#     epoca_ehem = datetime(int(anio), int(mes), int(dia), int(hora), int(minu), int(seg))
#     print datetime.strftime(epoca_ehem,'%Y-%m-%d %H:%M:%S')
#epoca_tleAbril3dias=datetime(y,mes,dia,hora,minu,seg,0)+timedelta(days=3)