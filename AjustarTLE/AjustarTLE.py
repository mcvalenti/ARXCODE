'''
Created on Aug 26, 2016

Toma 10 tles de un archivo y realiza un metodo de ajuste,
a fin de obtener una matriz de covarianza con el error.

@author: mcvalenti
'''
import os, glob
import operator
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import tle_info
from visual.gegraf import gegraf, gegrafTot
from SistReferencia.sist_deCoordenadas import uvwSis
from TleAdmin import TLE

def seleccionSat():
    """
    --------------------------------------------------------
    Preprocesamiento del dato crudo bajado de Space-track
    Preparacion de los archivos TLE, para el procesamiento.
    La funcion busca en la carpeta TleAdmin/crudosTLE.
    (el archivo debe contener solo las lineas de los tle)
    La funcion guarda los archivos tle generados en la carpeta
    TleAdmin/tle
    -------------------------------------------------------------
    input
        xxxx_fechainicio_fechafin:  archivo de texto plano 
        (xxxx corresponde al cat_id del satelite de interes)
    output
        tle#: lista de archivos con 1 TLE por fecha.
    """
    satelites_datos=glob.glob('../TleAdmin/crudosTLE/*')
    nombres=[]
    for arch in satelites_datos:
        nombre_archivo=arch.split('/')[-1]
        nombres.append(nombre_archivo)
    print nombres
    print "Seleccione el Satelite a analizar"
    
    crudo=raw_input()
    id_sat=crudo.split('_')[0]
    if crudo in nombres:
        setTLE(id_sat, crudo)
    else:
        print "Error en el nombre del archivo"
        
    return {}

def generadorDatos(lista):
    """
    ----------------------------------------------------------------------
    Genera un diccionario, cuyas claves son tle1, tle2, tle3...tle10
    y para cada campo, se indica la fecha del tle asociado.
    -----------------------------------------------------------------------
    input
        lista: lista de nombres de los archivos del directorio 'tle' - (string)
    output
        tledic: diccionario
    """
    tledic={}
    datos=[]
    for arch in lista:
        nombre=arch.split('/')[-1]
        tle=tle_info(arch)
        datos.append(tle.epoca())
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

def difTle(setID,tleOrdenados,cantidad_tles):
    """
    ---------------------------------------------------------------
    Calcula las diferencias entre TLE primario y secundarios
    en el sistema u,v y w. 
    Lo hace en forma iterativa, recorriendo todos los TLE a fin
    de que todos son primarios en algun momento.
    ---------------------------------------------------------------
    input:
        setID: numero de set a ser analizado (string)
        tleOrdeandos: lista de TLEs y sus 2-lineas (lista de lista)
    output:
        difTotal# : archivo de texto plano (4 columnas) para cada set
        [AjustarTLE/diferencias/difTotal#]
    """
    dtot=open('diferencias/difTotal'+setID,'w')
    for i in range(cantidad_tles-1,0,-1):
        tlepri=tleOrdenados[i][0]
        r,rp,ffin=tlePrimario(tlepri)        
        item=range(i-1,0,-1)
        for j in item:
            tlesec=tleOrdenados[j][0]
            pos,vel,fsec=tleSecundario(tlesec, ffin)
            dr=pos-r
            dt=abs(fsec-ffin)
            dtfracdias=dt.total_seconds()/86400.0
            u,v,w=uvwSis(r, rp, dr)
            infodiftot=str(dtfracdias)+' '+str(u)+' '+str(v)+' '+str(w)+'\n'
            dtot.write(infodiftot)
    return {}

def estimacionEstadistica(uu,vv,ww):
        """
        Estimacion estadistica.
        """
        mu_u=np.mean(uu)
        mu_v=np.mean(vv)
        mu_w=np.mean(ww)
        u_medio=[]
        v_medio=[]
        w_medio=[]
        for iu in uu:
            u_medio.append(iu-mu_u)
        for j in vv:
            v_medio.append(j-mu_v)
        for k in ww:
            w_medio.append(k-mu_w)
    
        # Ma. de Covarianza.
        sigma2_u=np.dot(u_medio,u_medio)/len(uu)
        sigma2_v=np.dot(v_medio,v_medio)/len(vv)
        sigma2_w=np.dot(w_medio,w_medio)/len(ww)
        sigma_uv=np.dot(u_medio,v_medio)/len(uu)
        sigma_uw=np.dot(u_medio,w_medio)/len(ww)
        sigma_vw=np.dot(v_medio,w_medio)/len(vv)
    
        cov=np.array([[sigma2_u,sigma_uv,sigma_uw],[sigma_uv,sigma2_v,sigma_uw],[sigma_uw,sigma_vw,sigma2_w]])
        salida2=open('Covarma','a')
        #   salida2.write('-------------'+tlesec+'------------------------------------'+'\n')
        salida2.write(str(cov)+'\n')
        return {}  
    

if __name__ == '__main__':   
    """
    Borro los archivos generados para otro satelite.
        carpeta de tles: TleAdmin/tle
        carpeta de diferencias: AjustarTLE/diferencias
        carpeta de graficos: Visual/graficos
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
        
    files=glob.glob('diferencias/*')
    for filename in files:
        os.unlink(filename)
        
    files=glob.glob('../visual/graficos/*')
    for filename in files:
        os.unlink(filename)
    """
    Se comienza el procesamiento
    Se elije el satelite a procesar entre los datos crudos disponibles.
    """
    seleccionSat() # se selecciona el satelite y se generan sus datos crudos

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

    """
    Propagacion de TLEs y calculo de las diferencias
    """
    cantidad_tles=len(tleOrdenados)
    print 'Cantidad de TLE a procesar= ',cantidad_tles
    print 'Procesando ...'

    set15=cantidad_tles/15
    for s in range(set15):
        a=s*15
        b=a+15
        tleOrdenados1=tleOrdenados[a:b]
        setID=str(s)
        cantidad_tles=len(tleOrdenados1)
        difTle(setID, tleOrdenados1, cantidad_tles)
        """
        generacion de graficos
        """ 
        gegrafTot('../AjustarTLE/diferencias/difTotal'+setID,setID)

#     #gegraf('../AjustarTLE/diferencias/diferencias'+tlepri,tlepri)

    print '--Fin del PROCESAMIENTO--'