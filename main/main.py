'''
Created on 26/01/2017

@author: mcvalenti
'''
import os, glob
from datetime import datetime
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
    

    listaTle={}
    lineaInterpol=[]
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        l_tle = str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
        inferior, superior= encuentraBordes(gpslista,l_tle)
        lineaInterpol.append(interpola(l_tle,inferior,superior))
    
        return lineaInterpol, tles


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

    tles=glob.glob('../TleAdmin/tle/*')
    sv_interp=sv_interpolados(tles)

    date_fmt = '%Y-%m-%d %H:%M:%S'
    for li in sv_interp:
        fecha=li[:19]
        fecha1=datetime.strptime(fecha, date_fmt)
        for t in tles:
            tle0=Tle(t)
            tle0.propagaTLE()
#        pos, vel=satrec1.propagate(ffin_anno, ffin_mes, ffin_dia, ffin_hora, ffin_min, ffin_s)
