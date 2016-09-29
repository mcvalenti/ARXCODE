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
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import tle_info
from visual.gegraf import gegraf
from SistReferencia.sist_deCoordenadas import uvwSis
from TleAdmin import TLE

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
    archivotle=open('../TleAdmin/tle/'+tlepri,'r')
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
    archivotle=open('../TleAdmin/tle/'+tlesec,'r')
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
    Preprocesamiento del dato crudo bajado de Space-track
    Preparacion de los archivos TLE, para el procesamiento
    """
    satelites_datos=glob.glob('../TleAdmin/crudosTLE/*')
    nombres=[]
    for arch in satelites_datos:
        nombre_archivo=arch.split('/')[-1]
        nombres.append(nombre_archivo)
    print satelites_datos
    print "Seleccione el Satelite a analizar"
    
    crudo=raw_input()
    id_sat=crudo.split('_')[0]
    if crudo in nombres:
        setTLE(id_sat, crudo)
    else:
        print "Error en el nombre del archivo"
    """
    Administra los archivos TLEs
    """
    lista=glob.glob('../TleAdmin/tle/*')
    total_tles=len(lista)
    tledic=generadorDatos(lista)
    """
    Ordena los TLEs segun sus fechas.
    """
    tleOrdenados=ordenaTles(tledic)
    print len(tleOrdenados)

    """
    Propagacion de TLEs y calculo de las diferencias
    """
    print len(tleOrdenados)
    for a in range(0,len(tleOrdenados),10):
        if a < total_tles-10:
            b=a+10
            dieztles=tleOrdenados[a:b]
            tlepri=dieztles[-1][0]
            print tlepri
            r,rp,ffin=tlePrimario(tlepri)
            print 'Vector Primario =',r,rp
            d=open('diferencias'+tlepri,'w')
            dif=[]
            uu=[]
            vv=[]
            ww=[]
            item=range(b,a,-1)
            for i in item:
                tlesec=tleOrdenados[i][0]
                pos,vel,fsec=tleSecundario(tlesec, ffin)
                print fsec,pos,vel
                dx,dy,dz=tuplaFloat(pos-r)
                dr=pos-r
                dif.append(dr)
                u,v,w=uvwSis(r, rp, dr)
                uu.append(u)
                vv.append(v)
                ww.append(w)
                infodif=str(fsec)+' '+str(u)+' '+str(v)+' '+str(w)+'\n'
                d.write(infodif)
            d.close()
        else:
            pass  
            """
        generacion de graficos
        """ 
        gegraf('../AjustarTLE/diferencias'+tlepri,tlepri)
    
    """
    Estimacion estadistica.
    """
    mu_u=np.mean(uu)
    mu_v=np.mean(vv)
    mu_w=np.mean(ww)
    print mu_u,mu_v,mu_w
    u_medio=[]
    v_medio=[]
    w_medio=[]
    for i in uu:
        u_medio.append(i-mu_u)
    for j in vv:
        v_medio.append(i-mu_v)
    for k in ww:
        w_medio.append(i-mu_w)
    
    # Ma. de Covarianza.
    sigma2_u=np.dot(u_medio,u_medio)/len(uu)
    sigma2_v=np.dot(v_medio,v_medio)/len(vv)
    sigma2_w=np.dot(w_medio,w_medio)/len(ww)
    sigma_uv=np.dot(u_medio,v_medio)/len(uu)
    sigma_uw=np.dot(u_medio,w_medio)/len(ww)
    sigma_vw=np.dot(v_medio,w_medio)/len(vv)
    
    cov=np.array([[sigma2_u,sigma_uv,sigma_uw],[sigma_uv,sigma2_v,sigma_uw],[sigma_uw,sigma_vw,sigma2_w]])
    print cov
    print sigma2_u, sigma2_v,sigma2_w