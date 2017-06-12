'''
Created on 12/06/2017
Voy a generar un crudo TLE con tles para el 1 de los meses de
Febrero, Abril, Junio, Agosto y Octubre del anio 2013.
Luego voy a propagar cada TLE por 3 dias (c/1seg) y comparar los resultados con 
los valores que ofrece cods. 
@author: mcvalenti
'''
import os, glob
from datetime import datetime, timedelta
from TleAdmin.TleArchivos import setTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from pruebas.claseTle import Tle
from CodsAdmin.EphemCODS import EphemCODS
from SistReferencia.sist_deCoordenadas import teme2tod


"""
Evaluo los TLE
"""
setTLE('37673', 'estudioTLE')

files=glob.glob('../TleAdmin/tle/*')
    
dic_tle=generadorDatos(files)
ordenaTles(dic_tle)



"""
Evaluo los datos CODS
"""
files_cods=glob.glob('../CodsAdmin/sacDdensos/*')

for f in files_cods:
    efemerides = EphemCODS(f)
    anio, mes, dia, hora, minu, seg= efemerides.parsea_epoca()
    epoca_ehem = datetime(int(anio), int(mes), int(dia), int(hora), int(minu), int(seg))
    print datetime.strftime(epoca_ehem,'%Y-%m-%d %H:%M:%S')

"""
TLE ABRIL.
"""
tle_abril=Tle.creadoxArchivo('../TleAdmin/tle/37673tle0')
epoca_tleAbril=tle_abril.epoca()
y=epoca_tleAbril.year
mes=epoca_tleAbril.month
dia=epoca_tleAbril.day
hora=epoca_tleAbril.hour
minu=epoca_tleAbril.minute
seg=epoca_tleAbril.second
#epoca_tleAbril3dias=datetime(y,mes,dia,hora,minu,seg,0)+timedelta(days=3)
epoca_tleAbril3dias=epoca_tleAbril+timedelta(days=3)
date_ephemAbril=datetime(2013,4,5,13,57,24)
r,v = tle_abril.propagaTLE(epoca_tleAbril3dias)
r_tod = teme2tod(epoca_tleAbril3dias,r)
print 'Epoca del TLE =', epoca_tleAbril
print 'Epoca del TLE mas 3 dias = ',epoca_tleAbril3dias
print 'SV en TOD', epoca_tleAbril3dias, r_tod

"""
Ephem ABRIL
"""
epoca_ephem_comparar=datetime(2013,4,4,12,44,41)
x_cods=1387.400421
y_cods=-6783.557720
z_cods=-1252.145786

print 'SV CODS = ', epoca_ephem_comparar, x_cods,y_cods,z_cods