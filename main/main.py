'''
Created on 26/01/2017

@author: mcvalenti
'''
import os, glob
from datetime import datetime
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from Comparar.TleVsCods import EjecutaComparacion, interpola, encuentraBordes

"""
listar las epocas de todos los tles.
interpolar el sv de cods para esas fechas
ordenarlas de mayor a menor
reproducir el metodo de Osweiler tomando como  dato el sv interpolado
"""


def sv_interpolados(tles):
    """
    Arma la lista de TLEs y busca los valores
    del Vector de Estado de CODS interpolado para las fechas
    correspondientes a los TLEs. 
    """
    gpsf=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    gpslista=gpsf.readlines()
    l_tle=[]
    lineaInterpol=[]
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        l_tle.append(str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2]))
        inferior, superior= encuentraBordes(gpslista,l_tle)
        lineaInterpol.append(interpola(l_tle,inferior,superior))
    
    return lineaInterpol


if __name__ == '__main__':
    
    """
    Se crean los directorios necesarios.
    """
    
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos'
    if not os.path.exists(d4):
        os.mkdir(d4)

    salida=open('codsOsweiler.dif','w')
    tles=glob.glob('../TleAdmin/tle/*')
    sv_interp=sv_interpolados(tles)

    date_fmt = '%Y-%m-%d %H:%M:%S'
    whichconst=wgs72
    for li in sv_interp:
        fecha=li[:19]
        fecha1=datetime.strptime(fecha, date_fmt)
        contenido=li.split()
        r=[contenido[2],contenido[3],contenido[4]]
        for t in tles:
            tle0=Tle(t)
            line1=tle0.linea1
            line2=tle0.linea2
            satrec = twoline2rv(line1, line2, whichconst)
            pos, vel=satrec.propagate(fecha1.year, fecha1.month, fecha1.day, fecha1.hour, fecha1.min, fecha1.sec)
            dif_pos=r-pos