'''
Created on Aug 26, 2016

Toma 10 tles de un archivo y realiza un metodo de ajuste,
a fin de obtener una matriz de covarianza con el error.

@author: mcvalenti
'''
import glob
import operator
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4
from TleAdmin.TLE import tle_info
from visual.gegraf import gegraf
from SistReferencia.sist_deCoordenadas import uvwSis

def generadorDatos(lista):
    """
    ----------------------------------------------------------------------
    Genera un diccionario, cuyas claves son tle1, tle2, tle3...tle10
    y para cada campo, tiene una lista de 3 componentes, que son la fecha
    la linea1 y la linea2 del tle respectivamente.
    -----------------------------------------------------------------------
    input
        lista: lista de path de los archivos del directorio 'tles' - (string)
    output
        tledic: diccionario
    """
    tledic={}
    datos=[]
    for arch in lista:
        nombre=arch.split('/')[-1]
        tle=tle_info(arch)
        datos.append(tle.epoca())
#        datos.append(tle.linea1)
#        datos.append(tle.linea2)
        tledic[nombre]= datos
        datos=[]
    
    return tledic

def ordenaTles(tledic):
    """
    -----------------------------------------------------------------
    Toma el diccionario de TLEs y los ordena de acuerdo a sus fechas.
    -----------------------------------------------------------------
    input
        tledic: diccionario
    output
        tleOrdenados: lista de listas
            tleOrdenados[0]: 'tle#', numero de tle (string)
            tleOrdenados[1]: lista, (fecha, linea1, linea2)
    """
    ve=open('verif','w')
    ve1=open('verif1','w')
    for k,v in tledic.iteritems():
        info1=str(k)+' '+str(v)+'\n'
        ve.write(info1)
    tleOrdenados=sorted(tledic.items(), key=operator.itemgetter(1))
    for k in tleOrdenados:
        info2=str(k)+'\n'
        ve1.write(info2)
    return tleOrdenados



def tuplaFloat(tupla):
    """
    transforma las tuplas a sus componentes en flotante
    """
    x=float(tupla[0])
    y=float(tupla[1])
    z=float(tupla[2])
    
    return x,y,z

def tlePrimario(tlepri):
    """
    -----------------------------------------------------------------
    Devuelve el vector de estado y la epoca
    correspondiente a la referencia como dato primario
    -----------------------------------------------------------------
    input
        tlepri: nombre del archivo con el TLE primario (string)
    output
        r,v: vector posicion y velocidad para el TLE primario (array)
        ffin: epoca del TLE primario (datetime)
    """
    whichconst = wgs72
    archivotle=open('../tles/'+tlepri,'r')
    lineas=archivotle.readlines()
    line1=lineas[0]
    line2=lineas[1]
    satrec = twoline2rv(line1, line2, whichconst)
    r,v = sgp4(satrec,0)
    xf,yf,zf=tuplaFloat(r)
    xv,yv,zv=tuplaFloat(v)
    r=np.array([xf,yf,zf])
    v=np.array([xv,yv,zv])
    ffin=satrec.epoch
    return r,v,ffin

def tleSecundario(tlesec,ffin):
    """
    ---------------------------------------------------------------------------------
    Calcula la posicion del satelite propagada a la fecha del TLE primario.
    ---------------------------------------------------------------------------------
    input
        tlesec: nombre del archivo que contiene el TLE secundario (string)
    output
        pos,vel: vector posicion y velocidad que resultan de la propagacion del
                TLE secundario hasta la fecha del TLE primario (array)
        fsec: epoca del TLE secundario
    """
    whichconst = wgs72
    archivotle=open('../tles/'+tlesec,'r')
    lineas=archivotle.readlines()
    line1=lineas[0]
    line2=lineas[1]
    satrec1 = twoline2rv(line1, line2, whichconst)
    ffin_anno=ffin.year
    ffin_mes=ffin.month
    ffin_dia=ffin.day
    ffin_hora=ffin.hour
    ffin_min=ffin.minute
    ffin_s=ffin.second
    pos, vel=satrec1.propagate(ffin_anno, ffin_mes, ffin_dia, ffin_hora, ffin_min, ffin_s)
    x,y,z=tuplaFloat(pos)
    pos=np.array([x,y,z])
    fsec=satrec1.epoch
    return pos,vel,fsec

if __name__ == '__main__':
        
    """
    Administra los archivos TLEs
    """
    lista=glob.glob('../tles/*')
    tledic=generadorDatos(lista)

    """
    Ordena los TLEs segun sus fechas.
    """
    tleOrdenados=ordenaTles(tledic)

    """
    Propagacion de TLEs y calculo de las diferencias
    """
    tlepri=tleOrdenados[-1][0] # me quedo con el ultimo
    r,rp,ffin=tlePrimario(tlepri)
    print 'Vector Primario =',r,rp
    d=open('diferencias','w')
    dif=[]
    item=range(8,0,-1)
    for i in item:
        tlesec=tleOrdenados[i][0]
        pos,vel,fsec=tleSecundario(tlesec, ffin)
        print fsec,pos,vel
        dx,dy,dz=tuplaFloat(r-pos)
        dr=r-pos
        dif.append(dr)
        u,v,w=uvwSis(r, rp, dr)
        infodif=str(fsec)+' '+str(u)+' '+str(v)+' '+str(w)+'\n'
        d.write(infodif)
    d.close()
    
    """
    generacion de graficos
    """ 
#    gegraf('../AjustarTLE/diferencias')
    
    """
    Estimacion estadistica.
    """
    uu=[]
    vv=[]
    ww=[]
    for k in range(len(dif)):
        uu.append(dif[k][0])
#        vv.append(dif[k][1])
#        ww.append(dif[k][2])
        
    mu=np.mean(uu)
    varu=np.var(uu)
    sigmau=np.std(uu)
    print mu, varu,sigmau,np.sqrt(varu)