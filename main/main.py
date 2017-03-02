'''
Created on 26/01/2017

@author: mcvalenti
'''
import os, glob
import numpy as np
from datetime import datetime
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from Comparar.TleVsCods import EjecutaComparacion, interpola, encuentraBordes
from SistReferencia.sist_deCoordenadas import vncSis

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
    lineaInterpol=[]
    print 'Procesando ...'
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
        inferior, superior= encuentraBordes(gpslista,fila)
        lineaInterpol.append(interpola(fila,inferior,superior))
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
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    sv_interp=sv_interpolados(tles)

    """
    Genero un diccionario de efemerides
    Cods para luego ordenarlas.
    """
    cods_dic={}
    fecha_int=[]
    m=0
    for li in sv_interp:
        nombre='cods_ephem_'+str(m)
        fecha=li[:19]
        fecha1=datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
#        fecha_int.append(fecha1) # ejecuta un metodo de la clase TLE
        cods_dic[fecha1]= li[19:]
        m=m+1
    cods_dic_ord=sorted(cods_dic.items(), reverse=True)

    print cods_dic
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print cods_dic_ord
  

    date_fmt = '%Y-%m-%d %H:%M:%S'
    whichconst=wgs72
    
    for k in cods_dic_ord:   
        salida.write('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
        fecha=k[0] 
        sv=k[1]
        r=np.array([float(sv.split()[0]),float(sv.split()[1]),float(sv.split()[2])])
        rp=np.array([float(sv.split()[3]),float(sv.split()[4]),float(sv.split()[5])])
        for t in tles:
            tle0=Tle(t)
            fecha_tle=tle0.epoca()
            if fecha_tle <= fecha:
                line1=tle0.linea1
                line2=tle0.linea2
                satrec = twoline2rv(line1, line2, whichconst)
                pos, vel=satrec.propagate(fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second)
                difx=[r[0]-float(pos[0]),r[1]-float(pos[1]),r[2]-float(pos[2])]
                difv=[rp[0]-float(vel[0]),rp[1]-float(vel[1]),rp[2]-float(vel[2])]
                v,n,c=vncSis(r,rp,difx)
                vv,nn,cc=vncSis(r,rp,difv)
                dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
                salida.write(dato)
                
    print 'FIN'